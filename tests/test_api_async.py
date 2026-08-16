import asyncio
import copy
from datetime import datetime
import pytest
import pytest_asyncio

from pystudernext import AsyncNextFactory
from pystudernext import NextData, NextFormat

from . import AsyncTestApi


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, test_fam, test_slave, test_addr, test_value, test_format, exp_except",
    [
        ("request bool ok",      'sys', 1,  2121, True,   NextFormat.BOOL, None),
        ("request int ok",       'sys', 1,  2122, 1234,   NextFormat.INT, None),
        ("request uint ok",      'nx3', 14, 14,   1234,   NextFormat.UINT, None),
        ("request float ok",     'sys', 1,  3908, 1234.0, NextFormat.FLOAT, None),
        ("request float64 ok",   'sys', 1,  3924, 1234.0, NextFormat.FLOAT64, None),
        ("request string ok",    'sys', 1,  2103, "00112233-4455-6677-8899-aabbccddeeff", NextFormat.STRING, None),
    ]
)
async def test_request_value(name, test_fam, test_slave, test_addr, test_value, test_format, exp_except):

    async def on_read(api: AsyncTestApi):
        """Helper to return the registers for a read"""
        return NextData.pack(test_value, test_format)

    dataset = await AsyncNextFactory.create_dataset()
    param = dataset.get_by_address(test_addr, test_fam)

    api = AsyncTestApi(on_read_handler=on_read)

    if exp_except == None:
        rsp_value = await api.request_value(param, slave=test_slave)

        assert api.read_called
        assert api.read_slave == test_slave
        assert api.read_address == param.address
        assert api.read_count == param.size

        assert rsp_value == test_value

    else:
        with pytest.raises(exp_except):
            rsp_value = await api.request_value(param, test_slave)

 