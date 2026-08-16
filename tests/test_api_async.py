import asyncio
import copy
from datetime import datetime
import pytest
import pytest_asyncio

from pystudernext import AsyncNextFactory, NextFactory
from pystudernext import NextData, NextFormat

from . import AsyncNextApiStub, NextApiStub


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

    read_called = False
    read_address = None
    read_count = None
    read_slave = None

    async def on_read(api: AsyncNextApiStub, address: int, count: int, slave: int):
        """Helper to return the registers for a read"""
        nonlocal read_called
        nonlocal read_address
        nonlocal read_count
        nonlocal read_slave

        read_called = True
        read_address = address
        read_count = count
        read_slave = slave

        return NextData.pack(test_value, test_format)

    dataset = await AsyncNextFactory.create_dataset()
    param = dataset.get_by_address(test_addr, test_fam)

    api = AsyncNextApiStub(on_read_handler=on_read)

    if exp_except == None:
        rsp_value = await api.request_value(param, test_slave)

        assert read_called
        assert read_slave == test_slave
        assert read_address == param.address
        assert read_count == param.size

        assert rsp_value == test_value

    else:
        with pytest.raises(exp_except):
            rsp_value = await api.request_value(param, test_slave)


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
async def test_write_value(name, test_fam, test_slave, test_addr, test_value, test_format, exp_except):

    write_called = False
    write_address = None
    write_regs = None
    write_slave = None

    async def on_write(api: AsyncNextApiStub, address: int, regs: list[int], slave: int):
        """Helper to return the registers for a read"""
        nonlocal write_called
        nonlocal write_address
        nonlocal write_regs
        nonlocal write_slave

        write_called = True
        write_address = address
        write_regs = regs
        write_slave = slave

        return None

    dataset = await AsyncNextFactory.create_dataset()
    param = dataset.get_by_address(test_addr, test_fam)

    api = AsyncNextApiStub(on_write_handler=on_write)

    if exp_except == None:
        rsp_value = await api.update_value(param, test_value, test_slave)

        assert write_called
        assert write_slave == test_slave
        assert write_address == param.address
        assert write_regs is not None

        write_value = NextData.unpack(write_regs, test_format)
        assert write_value == test_value

    else:
        with pytest.raises(exp_except):
            rsp_value = await api.update_value(param, test_value, test_slave)

 