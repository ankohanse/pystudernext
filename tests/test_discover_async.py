import asyncio
import copy
import threading
import pytest
import pytest_asyncio

from pystudernext import AsyncNextDiscover, NextDiscover
from pystudernext import AsyncNextFactory, NextFactory
from pystudernext import NextDataset
from pystudernext import NextDeviceFamilies
from pystudernext import NextFormat
from pystudernext import NextData

from . import AsyncTestApi, TestApi


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, rsp_slaves, rsp_dict, exp_devices",
    [
        ("SYS",               [1],          { 
                                                "2103": "00112233-4455-6677-8899-aabbccddeeff" 
                                            },  ["SYS"]),
        ("BAT_1",             [2],          { 
                                                "318": 1234.0 
                                            },  ["BAT_1"]),
        ("BAT_1,BAT_2,BAT_3", [2,3,4],      { 
                                                "318": 1234.0 
                                            },  ["BAT_1", "BAT_2", "BAT_3"]),
        ("ACS_1",             [7],          { 
                                                "0": 1234.0 
                                            },  ["ACS_1"]),
        ("ACS_1,ACS_2",       [7,8],        { 
                                                "0": 1234.0 
                                            },  ["ACS_1", "ACS_2"]),
        ("ACF_1",             [9],          { 
                                                "0": 1234.0 
                                            },  ["ACF_1"]),
        ("ACF_1,ACF_2,ACF_3", [9,10,11],    { 
                                                "0": 1234.0 
                                            },  ["ACF_1", "ACF_2","ACF_3"]),
        ("NX3_1",             [14],         { 
                                                "4": "1122334455667788" 
                                            },  ["NX3_1"]),
        ("NX3_1,NX3_2,NX3_3", [14,15,16],   { 
                                                "4": "1122334455667788" 
                                            },  ["NX3_1", "NX3_2", "NX3_3"]),
        ("NX1_1",             [29],         { 
                                                "4": "1122334455667788" 
                                            },  ["NX1_1"]),
        ("NX1_1,NX1_2,NX1_3", [29,30,31],   { 
                                                "4": "1122334455667788" 
                                            },  ["NX1_1", "NX1_2", "NX1_3"]),
        ("NXG_1",             [59],         { 
                                                "4": "1122334455667788" 
                                            },  ["NXG_1"]),
        ("NXG_1,NXG_2",       [59,60],      { 
                                                "4": "1122334455667788" 
                                            },  ["NXG_1", "NXG_2"]),
    ]
)
async def test_discover_devices(name, rsp_slaves, rsp_dict, exp_devices, request):

    dataset = await AsyncNextFactory.create_dataset()

    async def on_read(api: AsyncTestApi, address: int, count: int, slave: int):
        """Helper to return the registers for a read"""
        if slave in rsp_slaves and str(address) in rsp_dict:
            family = NextDeviceFamilies.get_by_slave(slave)
            param = dataset.get_by_address(address, family.id)
            rsp_val = rsp_dict[str(address)]
            rsp_format = param.format

            return NextData.pack(rsp_val, rsp_format)
        else:
            return None

    # Perform the discover
    api = AsyncTestApi(on_read_handler=on_read)
    await api.start()

    discover = AsyncNextDiscover(api, dataset)   
    devices = await discover.discover_devices(getExtendedInfo=False)

    # Check discovered devices
    assert len(devices) == len(exp_devices)
    for device in devices:
        assert device.code in exp_devices
        assert device.slave in rsp_slaves
        assert device.family_id is not None
        assert device.family_model is not None
      
        assert device.serial is None
        assert device.sw_version is None
        assert device.om_version is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, rsp_slaves, rsp_dict, exp_devices, exp_serial, exp_sw_version, exp_om_version",
    [
        ("SYS none",    [1],    { 
                                    "2103": "00112233-4455-6677-8899-aabbccddeeff" 
                                },  ["SYS"], None, None, None),
        ("BAT none",    [2],    { 
                                    "318": 1234.0 
                                },  ["BAT_1"], None, None, None),
        ("ACS none",    [7],    { 
                                    "0": 1234.0 
                                },  ["ACS_1"], None, None, None),
        ("ACF none",    [9],    { 
                                    "0": 1234.0 
                                },  ["ACF_1"], None, None, None),
        ("NX3 ext",     [14],   { 
                                    "4": "1122334455667788",
                                    "14": 0x01020304,
                                    "30": 0x00010002
                                }, ["NX3_1"], "1122334455667788", "1.2.3.4", "1.2"),
        ("NX1 ext",     [29],   { 
                                    "4": "1122334455667788",
                                    "14": 0x01020304,
                                    "30": 0x00010002
                                }, ["NX1_1"], "1122334455667788", "1.2.3.4", "1.2"),
        ("NXG ext",     [59],   { 
                                    "4": "1122334455667788",
                                    "14": 0x01020304,
                                    "30": 0x00010002
                                }, ["NXG_1"], "1122334455667788", "1.2.3.4", "1.2"),
    ]
)
async def test_discover_extendedinfo(name, rsp_slaves, rsp_dict, exp_devices, exp_serial, exp_sw_version, exp_om_version, request):

    dataset = await AsyncNextFactory.create_dataset()

    async def on_read(api: AsyncTestApi, address: int, count: int, slave: int):
        """Helper to return the registers for a read"""
        if slave in rsp_slaves and str(address) in rsp_dict:
            family = NextDeviceFamilies.get_by_slave(slave)
            param = dataset.get_by_address(address, family.id)
            rsp_val = rsp_dict[str(address)]
            rsp_format = param.format

            return NextData.pack(rsp_val, rsp_format)
        else:
            return None

    # Perform the discover
    api = AsyncTestApi(on_read_handler=on_read)
    await api.start()

    discover = AsyncNextDiscover(api, dataset)   
    devices = await discover.discover_devices(getExtendedInfo=True)

    # Check discovered devices
    assert len(devices) == len(exp_devices)
    for device in devices:
        assert device.code in exp_devices
        assert device.slave in rsp_slaves
        assert device.family_id is not None
        assert device.family_model is not None
      
        assert device.serial == exp_serial
        assert device.sw_version == exp_sw_version
        assert device.om_version == exp_om_version


@pytest.mark.asyncio
@pytest.mark.usefixtures("unused_tcp_port")
@pytest.mark.parametrize(
    "name, rsp_slaves, rsp_dict, exp_host, exp_guid",
    [
        ("guid none",   [1],    {
                                    "0": "00112233-4455-6677-8899-aabbccddeeff",      
                                }, "127.0.0.1", None),
        ("guid ok",     [1],    {
                                    "2103": "00112233-4455-6677-8899-aabbccddeeff",      
                                }, "127.0.0.1", "00112233-4455-6677-8899-aabbccddeeff"),
    ]        
)
async def test_gateway_info(name, rsp_slaves, rsp_dict, exp_host, exp_guid, request):

    dataset = await AsyncNextFactory.create_dataset()

    async def on_read(api: AsyncTestApi, address: int, count: int, slave: int):
            """Helper to return the registers for a read"""
            if slave in rsp_slaves and str(address) in rsp_dict:
                family = NextDeviceFamilies.get_by_slave(slave)
                param = dataset.get_by_address(address, family.id)
                rsp_val = rsp_dict[str(address)]
                rsp_format = param.format
    
                return NextData.pack(rsp_val, rsp_format)
            else:
                return None
    
    api = AsyncTestApi(on_read_handler=on_read)
    await api.start()
    
    discover = AsyncNextDiscover(api, dataset) 

    # Perform the discover
    gateway_info = await discover.discover_gateway_info()

    # Check discovered info
    assert gateway_info is not None
    assert gateway_info.host == exp_host
    assert gateway_info.guid == exp_guid
