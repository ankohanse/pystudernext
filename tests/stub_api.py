import logging


from pystudernext import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    AsyncNextApi,
    NextApi,
    NextData,
)
from . import (
    AsyncModbusClientStub,
    ModbusClientStub,
)


_LOGGER = logging.getLogger(__name__)


class AsyncNextApiStub(AsyncNextApi):
    """
    Derived class to help test the parent class.
    Is using a stub modbus client to skip actual communication
    """
    def __init__(self, on_read_handler=None, on_write_handler=None):
        super().__init__(host="127.0.0.1", port=DEFAULT_PORT)
        self._on_read = on_read_handler
        self._on_write = on_write_handler

    def _create_client(self, host, port, timeout):
        client = AsyncModbusClientStub(host, port, timeout)
        client._on_read = self._on_read
        client._on_write = self._on_write
        return client


class NextApiStub(NextApi):
    """
    Derived class to help test the parent class.
    Is using a stub modbus client to skip actual communication
    """
    def __init__(self, on_read_handler=None, on_write_handler=None):
        super().__init__(host="127.0.0.1", port=DEFAULT_PORT)
        self._on_read = on_read_handler
        self._on_write = on_write_handler

    def _create_client(self, host, port, timeout):
        client = ModbusClientStub(host, port, timeout)
        client._on_read = self._on_read
        client._on_write = self._on_write
        return client
