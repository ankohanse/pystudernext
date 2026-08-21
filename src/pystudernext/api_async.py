"""
api.py: communication api to Studer Next via Modbus over TCP.
"""

import logging

from datetime import datetime, timedelta
from pymodbus.client import AsyncModbusTcpClient, ModbusTcpClient
from typing import Any


from .const import (
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from .data import (
    NextApiConnectException,
    NextApiReadException,
    NextApiUpdateException,
    NextDataType,
    NextPackException,
    NextParamException,
    NextUnpackException,
    NextDiscoveredDevice,
)
from .datapoints import (
    NextDatapoint,
)
from .families import (
    NextDeviceFamilies
)


_LOGGER = logging.getLogger(__name__)
logging.getLogger("pymodbus").setLevel(logging.WARNING)


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
                await self._client.close()

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
    

    async def request_value(self, parameter: NextDatapoint, device: NextDiscoveredDevice=None, retries = None, timeout = None, verbose=False):
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
            if verbose:
                _LOGGER.debug(f"Modbus read registers for '{parameter.name}' ({parameter.address} via {slave})")
            
            client = await self._get_connected_client()
            result = await client.read_holding_registers(address=parameter.address, count=parameter.size, device_id=slave)

        except Exception as err:
            raise NextApiReadException(f"Modbus exception while requesting value for slave {slave}, address {parameter.address}, count {parameter.size}, error: {err}")

        if result.isError():
            raise NextApiReadException(f"Modbus error while requesting value for slave {slave}, address {parameter.address}, count {parameter.size}, error: {result.exception_code}")

        # Unpack the response value
        try:
            return AsyncModbusTcpClient.convert_from_registers(result.registers, data_type=NextDataType.to_datatype(parameter.data_type))

        except Exception as e:
            raise NextPackException(f"Failed to unpack response value for slave {slave}, address {parameter.address}: registers={result.registers}, format={parameter.data_type}, size={parameter.size}") from None


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
            client = await self._get_connected_client()
            regs = AsyncModbusTcpClient.convert_to_registers(value, data_type=NextDataType.to_datatype(parameter.data_type))

        except Exception as e:
            raise NextPackException(f"Failed to pack value for slave {slave}, address {parameter.address}: value={value}, format={parameter.data_type}, size={parameter.size}") from None
        
        # Send the request
        try:
            if verbose:
                _LOGGER.debug(f"Modbus update registers for '{parameter.name}' ({parameter.address} via {slave})")
            
            result = await client.write_registers(address=parameter.address, values=regs, device_id=slave)

        except Exception as err:
            raise NextApiUpdateException(f"Modbus exception while updating value for slave {slave}, address {parameter.address}, error: {err}")

        if result.isError():
            raise NextApiReadException(f"Modbus error while updating value for slave {slave}, address {parameter.address}, count {parameter.size}, error: {result.exception_code}")    

        return None


    async def _get_connected_client(self) -> AsyncModbusTcpClient:
        """
        Return a connected client, reconnecting if needed.
        """
        if not self.connected:
            client = self._create_client()

            if await client.connect():
                self._client = client
            else:
                self._client = None
                raise NextApiConnectException(f"Cannot connect to Studer Gateway at {self._host}:{self._port}")
            
        return self._client            


    def _create_client(self):
        """
        Helper to create the Modbus Client.
        In a separate function to make it easier to replace the client with a stub for unit-tests.
        """
        return AsyncModbusTcpClient(host=self._host, port=self._port)


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

