import logging

from pymodbus.pdu import ModbusPDU


_LOGGER = logging.getLogger(__name__)


class AsyncModbusClientStub():

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._connected = False
        
        self._on_read = None
        self._on_write = None

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        self._connected = True
        return True

    def close(self) -> None:
        self._connected = False

    async def read_holding_registers(self, address: int, count: int, device_id: int) -> ModbusPDU:
        if self._on_read:
            return await self._on_read(self, address, count, device_id)
        else:
            return None

    async def write_registers(self, address: int, values: list[int], device_id: int) -> None:
        if self._on_write:
            return await self._on_write(self, address, values, device_id)
        else:
            return None



class ModbusClientStub():

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._connected = False
        
        self._on_read = None
        self._on_write = None

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        self._connected = True
        return True

    def close(self) -> None:
        self._connected = False

    def read_holding_registers(self, address: int, count: int, device_id: int) -> list[int]:
        if self._on_read:
            return self._on_read(self, address, count, device_id)
        else:
            return None

    def write_registers(self, address: int, values: list[int], device_id: int) -> None:
        if self._on_write:
            return self._on_write(self, address, values, device_id)
        else:
            return None


