import pytest
import pytest_asyncio

from pystudernext import (
    NextDataset, 
    NextDatasetFlag,
    NextDeviceFamilies,
    StuderDataType, 
    StuderDatapointUnknownException,
    StuderParamException,
)


FLAGS_DEFAULT = None
FLAGS_TEST = { NextDatasetFlag.ADD_TEST: True }


def test_init():
    NextDataset.del_instance()
    with pytest.raises(RuntimeError):
        dataset = NextDataset() 


@pytest.mark.parametrize(
    "name, flags, exp_len",
    [
        ("default", FLAGS_DEFAULT, 2034),
        ("test",    FLAGS_TEST,    2046)
    ]
)
async def test_get_instance_async(name, flags, exp_len):
    NextDataset.del_instance()
    dataset = await NextDataset.async_get_instance(flags) 

    assert len(dataset._datapoints) == exp_len


@pytest.mark.parametrize(
    "name, flags, exp_len",
    [
        ("default", FLAGS_DEFAULT, 2034),
        ("test",    FLAGS_TEST,    2046)
    ]
)
def test_get_instance_sync(name, flags, exp_len):
    NextDataset.del_instance()
    dataset = NextDataset.get_instance(flags) 

    assert len(dataset._datapoints) == exp_len


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "addr, family, exp_addr, exp_family_id, exp_data_type, exp_except",
    [
        (6900,  NextDeviceFamilies.NEXT3,   6900, "nx3", StuderDataType.FLOAT32, None),
        (1200,  NextDeviceFamilies.SYSTEM,  1200, "sys", StuderDataType.ENUM32,  None),
        (6900,  "nx3",                      6900, "nx3", StuderDataType.FLOAT32, None),
        (1200,  "sys",                      1200, "sys", StuderDataType.ENUM32,  None),
        (None,  'nx3',                      None, None,  None,                   StuderParamException),
        (6900,  None,                       None, None,  None,                   StuderParamException),
        (5100,  NextDeviceFamilies.BATTERY, None, None,  None,                   StuderDatapointUnknownException),
        (9999,  "sys",                      None, None,  None,                   StuderDatapointUnknownException),
    ]
)
async def test_address(addr, family, exp_addr, exp_family_id, exp_data_type, exp_except):
    NextDataset.del_instance()
    dataset = NextDataset.get_instance()

    if not exp_except:
        param = dataset.get_by_address(addr, family)
    
        assert param.address == exp_addr
        assert param.family_id == exp_family_id
        assert param.data_type == exp_data_type

        if exp_data_type == StuderDataType.ENUM32:
            assert param.enum_options != None
            assert type(param.enum_options) is dict
            assert len(param.enum_options) > 0

    else:
        with pytest.raises(exp_except):
            param = dataset.get_by_address(addr, family)


def test_id():
    NextDataset.del_instance()
    dataset = NextDataset.get_instance()

    param = dataset.get_by_id(NextDataset.ID_INSTALLATION_GUID)
    assert param.family_id == "sys"
    assert param.address == 2103
    assert param.data_type == StuderDataType.STRING

    with pytest.raises(StuderParamException):
        param = dataset.get_by_id(None)

    with pytest.raises(StuderDatapointUnknownException):
        param = dataset.get_by_id("")

    with pytest.raises(StuderDatapointUnknownException):
        param = dataset.get_by_id("9.9.9.9")

    with pytest.raises(StuderDatapointUnknownException):
        param = dataset.get_by_id("dummy")


def test_enum():
    NextDataset.del_instance()
    dataset = NextDataset.get_instance()

    param = dataset.get_by_address(8130, NextDeviceFamilies.SYSTEM)
    assert param.data_type == StuderDataType.ENUM32
    assert param.enum_options != None
    assert type(param.enum_options) is dict
    assert len(param.enum_options) == 5

    assert param.enum_value(0) == "No warning(s) or error(s)"
    assert param.enum_value("0") == "No warning(s) or error(s)"
    assert param.enum_value(9) == "9"
    assert param.enum_value("9") == "9"

    assert param.enum_key("No warning(s) or error(s)") == 0
    assert param.enum_key("Unknown") == None
    assert param.enum_key(9) == None
    assert param.enum_key("9") == None


def test_bitfield():
    NextDataset.del_instance()
    dataset = NextDataset.get_instance()

    param = dataset.get_by_address(1205, NextDeviceFamilies.SYSTEM)
    assert param.data_type == StuderDataType.BITFIELD
    assert param.enum_options != None
    assert type(param.enum_options) is dict
    assert len(param.enum_options) == 10

    assert param.bitfield_value([False,False,False,False,False,False,False,False]) == ["End of error"]
    assert param.bitfield_value([False,False,True, False,False,False,False,False]) == ["Relay continuity failed"]
    assert param.bitfield_value([False,False,True, True, False,False,False,False]) == ["Relay continuity failed","Discontinuity failed"]

    with pytest.raises(StuderParamException):
        param.bitfield_value(None)

    with pytest.raises(StuderParamException):
        param.bitfield_value(0)


@pytest.mark.parametrize(
    "family_id, exp_len",
    [
        ("sys", 25),
        ("bat",  5),
        ("acs",  8),
        ("flx", 14),
        ("nx3", 33),
        ("nx1", 23),
        ("nxg", 30),
        ("pwr",  3),
        (NextDeviceFamilies.SYSTEM,          25),
        (NextDeviceFamilies.BATTERY,          5),
        (NextDeviceFamilies.AC_SOURCE,        8),
        (NextDeviceFamilies.AC_FLEX_LOAD,    14),
        (NextDeviceFamilies.NEXT3,           33),
        (NextDeviceFamilies.NEXT1,           23),
        (NextDeviceFamilies.NEXT_GATEWAY,    30),
        (NextDeviceFamilies.NEXT_POWERMETER,  3),
    ]
)
def test_menu(family_id, exp_len):
    NextDataset.del_instance()
    dataset = NextDataset.get_instance()
    
    root_items = dataset.get_menu_items(family_id)
    assert len(root_items) == exp_len

    for item in root_items:
        sub_items = dataset.get_menu_items(family_id, item.id)
        assert len(sub_items) >= 0

