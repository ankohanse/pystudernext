import logging


from pystudernext import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    AsyncNextApi,
    NextData,
)


_LOGGER = logging.getLogger(__name__)


class AsyncTestApi(AsyncNextApi):
    """
    Derived class to help test the parent class
    """
    def __init__(self, on_read_handler=None, on_write_handler=None, rsp_slaves=None, rsp_dict=None):
        
        super().__init__(remote_host=DEFAULT_HOST, remote_port=DEFAULT_PORT)
        self._on_read = on_read_handler
        self._on_write = on_write_handler
        self.rsp_slaves = rsp_slaves
        self.rsp_dict = rsp_dict

        # Internal variables to keep track of what happened during the test
        self.read_called: bool = False
        self.read_address: int = None
        self.read_slave: int = None
        self.read_count: int = None
        
        self.write_called: bool = False
        self.write_address: int = None
        self.write_slave: int = None
        self.write_reg: list[int] = None


    async def close(self):
        pass


    @property
    def connected(self) -> bool:
        return self._client is not None


    async def _get_client(self):
        self._client = self
        return self


    async def read_holding_registers(self, address: int, count: int, slave: int) -> list[int]:
        self.read_called = True
        self.read_address = address
        self.read_count = count
        self.read_slave = slave

        if self._on_read:
            return await self._on_read(self)
        else:
            return None


    async def write_holding_registers(self, address: int, registers: list[int], slave: int) -> None:
        self.write_called = True
        self.write_address = address
        self.write_slave = slave
        self.write_reg = registers

        if self._on_write:
            return await self._on_write(self)
        else:
            return None
