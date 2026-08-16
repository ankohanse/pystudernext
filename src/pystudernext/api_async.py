"""xcom_api.py: communication api to Studer Next via LAN."""

import asyncio
import binascii
import logging

from datetime import datetime, timedelta
import struct
from typing import Any


from .const import (
    CONNECT_TIMEOUT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    REQ_TIMEOUT,
    REQ_RETRIES,
    REQ_BURST_PERIOD,
    NextApiConnectException,
    NextPackException,
    NextParamException,
    NextUnpackException,
)
from .data import (
    NextData,
    NextDiscoveredDevice,
)
from .datapoints import (
    NextDatapoint,
)
from .families import (
    NextDeviceFamilies
)
from .modbus_client_async import (
    AsyncModbusClientBase,
    AsyncModbusTcpClient,
    ModbusTcpError
)
from .modbus_client_sync import (
    ModbusClientBase,
    ModbusTcpClient,
)


_LOGGER = logging.getLogger(__name__)

_MODBUS_PROTOCOL_ID = 0x0000
_FC_READ_HOLDING = 0x03
_FC_WRITE_MULTIPLE = 0x10


class AsyncNextApi:
    """
    The actual Api for requesting and updating parameters via an async modbus tcp client.
    """

    def __init__(self, host:str=DEFAULT_HOST, port:int=DEFAULT_PORT):
        """
        We connect to the MX Gateway.
        Once it is connected we can send Modbus requests.
        """
        self._host = host
        self._port = port

        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

        # Diagnostics gathering
        self._diag_retries = {}
        self._diag_durations = {}


    async def start(self) -> bool:
        """
        Connect the client.
        """
        try:
            await self._get_connected_client()
            return True
        
        except Exception as err:
            return False


    async def stop(self):
        """
        Close the client
        """
        try:
            if self._client:
                self._client.close()

        except Exception:
            pass

        finally:
            self._client = None


    @property
    def connected(self) -> bool:
        """Returns True if the Next client is connected, otherwise False"""
        return self._client is not None and self._client.connected
    

    @property
    def remote_host(self) -> str|None:
        """Returns the Host or IP address of the Next Gateway we connect to, otherwise None"""
        return self._host
    
    @property
    def remote_port(self) -> str|None:
        """Returns the port of the Next Gateway we connect to, otherwise None"""
        return self._port
    

    async def request_value(self, parameter: NextDatapoint, device: NextDiscoveredDevice=None, slave: int=None, code:str=None, retries = None, timeout = None, verbose=False):
        """
        Request a parameter.
        One of device, slave or code needs to be passed.
        Returns None if not connected, otherwise returns the requested value

        Throws
            NextParamException
            NextApiConnectException
            NextApiTimeoutException
            NextUnpackException
        """

        # Sanity check
        if parameter is None:
            return None
            
        if isinstance(device, NextDiscoveredDevice):
            slave = device.slave
        elif isinstance(device, int):
            slave = device
        elif isinstance(device, str):  
            slave = NextDeviceFamilies.get_slave_by_code(code=device)
        else:
            raise NextParamException(f"Device parameter must be a NextDiscoverdDevice, a slave number or a device code in call to request_value")

        # Send the request
        try:
            client = await self._get_connected_client()
            regs = await client.read_holding_registers(parameter.address, parameter.size, slave)

        except ModbusTcpError as err:
            _LOGGER.warning(f"Modbus error reading '{parameter.name}' ({parameter.address} via {slave}): {err}")
            return None

        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.warning(f"Network error reading '{parameter.name}' ({parameter.address} via {slave}): {err}")
            self._client = None
            return None

        if regs is None:
            _LOGGER.warning(f"No data in response for '{parameter.name}' ({parameter.address} via {slave})")
            return None
        
        if len(regs) < parameter.size:
            _LOGGER.warning(f"Insufficient data in response for '{parameter.name}' ({parameter.address} via {slave}): expected {parameter.size} got {len(regs)}")
            return None

        # Unpack the data
        try:
            return NextData.unpack(regs, parameter.format)
        
        except Exception as e:
            _LOGGER.warning(f"Failed to unpack response registers for '{parameter.name}' ({parameter.address} via {slave}): registers={regs.hex()}, format={parameter.format}, size={parameter.size}")
            raise NextUnpackException() from None


    async def update_value(self, parameter: NextDatapoint, value: Any, device: NextDiscoveredDevice|int|str=None, retries = None, timeout = None, verbose=False):
        """
        Update a parameter
        Returns None if not connected, otherwise returns True on success

        Throws
            NextParamException
            NextApiConnectException
            NextApiTimeoutException
            NextPackException
        """
        # Sanity check
        if parameter is None or value is None:
            return None
            
        if isinstance(device, NextDiscoveredDevice):
            slave = device.slave
        elif isinstance(device, int):
            slave = device
        elif isinstance(device, str):  
            slave = NextDeviceFamilies.get_slave_by_code(code=device)
        else:
            raise NextParamException(f"Device parameter must be a NextDiscoverdDevice, a slave number or a device code in call to update_value")

        _LOGGER.debug(f"Update '{parameter.name}' ({parameter.address} via {slave}) to {value}")

        # Pack the data
        try:
            regs = NextData.pack(value, parameter.format)

        except Exception as e:
            _LOGGER.warning(f"Failed to pack request registers for '{parameter.name}' ({parameter.address} via {slave}): value={value}, format={parameter.format}, size={parameter.size}")
            raise NextPackException() from None
        
        # Send the request
        try:
            client = await self._get_connected_client()
            await client.write_holding_registers(parameter.address, regs, slave)
        
        except ModbusTcpError as err:
            _LOGGER.warning(f"Modbus error writing '{parameter.name}' ({parameter.address} via {slave}): {err}")
            return None

        except (OSError, asyncio.TimeoutError) as err:
            _LOGGER.warning(f"Network error writing '{parameter.name}' ({parameter.address} via {slave}): {err}")
            self._client = None
            return None
        
        return None


    async def _get_connected_client(self):
        """
        Return a connected client, reconnecting if needed.
        """
        if not self.connected:
            self._client = self._create_client(self._host, self._port, timeout=CONNECT_TIMEOUT)

            if not await self._client.connect():
                self._client = None
                raise NextApiConnectException(f"Cannot connect to Studer Gateway at {self._host}:{self._port}")
            
        return self._client            


    def _create_client(self, host, port, timeout):
        """
        Helper to create the Modbus Client.
        In a separate function to make it easier to replace the client with a stub for unit-tests.
        """
        return ModbusTcpClient(host, port, timeout)


    async def _add_diagnostics(self, retries: int = None, duration: timedelta = None):
        if retries is not None:
            if retries not in self._diag_retries:
                self._diag_retries[retries] = 1
            else:
                self._diag_retries[retries] += 1

        if duration is not None:
            duration = round(duration.total_seconds(), 1)
            if duration not in self._diag_durations:
                self._diag_durations[duration] = 1
            else:
                self._diag_durations[duration] += 1


    async def get_diagnostics(self):
        return {
            "statistics": {
                "retries": dict(sorted(self._diag_retries.items())),
                "durations": dict(sorted(self._diag_durations.items())),
            }
        }

