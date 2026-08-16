import logging


from pystudernext import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    AsyncNextApi,
    NextApi,
    AsyncNextApiBase,
    NextApiBase,
    NextData,
)
from . import (
    AsyncFakeModbusClient,
    FakeModbusClient,
)


_LOGGER = logging.getLogger(__name__)


class AsyncTestApi(AsyncNextApiBase):
    """
    Derived class to help test the parent class.
    Is using a fake modbus client to skip actual communication
    """
    def __init__(self, on_read_handler=None, on_write_handler=None):
        super().__init__(AsyncFakeModbusClient, remote_host="127.0.0.1", remote_port=DEFAULT_PORT)
        self._on_read = on_read_handler
        self._on_write = on_write_handler

    async def _get_client(self):
        client = await super()._get_client()
        client._on_read = self._on_read
        client._on_write = self._on_write

        return client


class TestApi(NextApiBase):
    """
    Derived class to help test the parent class.
    Is using a fake modbus client to skip actual communication
    """
    def __init__(self, on_read_handler=None, on_write_handler=None):
        super().__init__(FakeModbusClient, remote_host="127.0.0.1", remote_port=DEFAULT_PORT)
        self._on_read = on_read_handler
        self._on_write = on_write_handler

    def _get_client(self):
        client = super()._get_client()
        client._on_read = self._on_read
        client._on_write = self._on_write

        return client

