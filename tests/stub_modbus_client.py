import logging

from pystudernext import AsyncModbusClientBase, ModbusClientBase


_LOGGER = logging.getLogger(__name__)


class AsyncModbusClientStub(AsyncModbusClientBase):

    def __init__(self, host: str, port: int, timeout: float = 10.0) -> None:
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

    async def read_holding_registers(self, address: int, count: int, slave: int) -> list[int]:
        if self._on_read:
            return await self._on_read(self, address, count, slave)
        else:
            return None

    async def write_holding_registers(self, address: int, registers: list[int], slave: int) -> None:
        if self._on_write:
            return await self._on_write(self, address, registers, slave)
        else:
            return None



class ModbusClientStub(ModbusClientBase):

    def __init__(self, host: str, port: int, timeout: float = 10.0) -> None:
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

    def read_holding_registers(self, address: int, count: int, slave: int) -> list[int]:
        if self._on_read:
            return self._on_read(self, address, count, slave)
        else:
            return None

    def write_holding_registers(self, address: int, registers: list[int], slave: int) -> None:
        if self._on_write:
            return self._on_write(self, address, registers, slave)
        else:
            return None


