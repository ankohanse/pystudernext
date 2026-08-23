
import pytest
from pystudernext import NextDeviceFamilies
from pystudernext import NextDeviceFamilyUnknownException, NextDeviceCodeUnknownException, NextDeviceSlaveUnknownException, NextParamException


def test_list():
    families = NextDeviceFamilies.get_list()
    assert len(families) == 8


def test_id():
    families = NextDeviceFamilies.get_list()
    for family in families:
        assert family == NextDeviceFamilies.get_by_id(family.id)

    with pytest.raises(NextDeviceFamilyUnknownException):
        family = NextDeviceFamilies.get_by_id("XXX")


@pytest.mark.parametrize(
    "family_id, code, slave",
    [
        ("sys", "SYS", 1),
        ("bat", "BAT_1", 2),
        ("bat", "BAT_5", 6),
        ("acs", "ACS_1", 7),
        ("acs", "ACS_2", 8),
        ("flx", "FLX_1", 9),
        ("flx", "FLX_5", 13),
        ("nx3", "NX3_1", 14),
        ("nx3", "NX3_15", 28),
        ("nx1", "NX1_1", 29),
        ("nx1", "NX1_30", 58),
        ("nxg", "NXG_1", 59),
        ("nxg", "NXG_2", 60),
    ]
)
def test_code(family_id, code, slave):

    family = NextDeviceFamilies.get_by_id(family_id)

    if code is not None:
        assert NextDeviceFamilies.get_by_code(code) == family
    else:
        assert NextDeviceFamilies.get_by_code(code) is None

    assert NextDeviceFamilies.get_slave_by_code(code) == slave
    assert NextDeviceFamilies.get_code_by_slave(slave) == code


