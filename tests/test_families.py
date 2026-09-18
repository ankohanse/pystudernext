
import pytest
from pystudernext import NextDeviceFamilies
from pystudernext import StuderDeviceFamilyUnknownException


async def test_create_async():
    families = await NextDeviceFamilies.async_get_instance()

    assert isinstance(families, NextDeviceFamilies)
    assert len(families) == 9


def test_create_sync():
    families = NextDeviceFamilies.get_instance()

    assert isinstance(families, NextDeviceFamilies)
    assert len(families) == 9


def test_id():
    families = NextDeviceFamilies.get_instance()
    for family in families:
        assert family == families.get_by_id(family.id)

    with pytest.raises(StuderDeviceFamilyUnknownException):
        family = families.get_by_id("XXX")


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
        ("pwr", "PWR_1", 89),
        ("pwr", "PWR_6", 94),
    ]
)
def test_code(family_id, code, slave):

    families = NextDeviceFamilies.get_instance()
    family = families.get_by_id(family_id)

    if code is not None:
        assert families.get_by_code(code) == family
    else:
        assert families.get_by_code(code) is None

    assert families.get_slave_by_code(code) == slave
    assert families.get_code_by_slave(slave) == code


