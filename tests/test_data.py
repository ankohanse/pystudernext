from datetime import datetime
import math
import pytest
import pytest_asyncio
from pystudernext import NextData
from pystudernext import NextFormat


@pytest.mark.parametrize(
    "name, value, format, expected_length",
    [
        ("bool",       True,  NextFormat.BOOL, 1),
        ("signal",     True,  NextFormat.SIGNAL, 1),
        ("int",        1234,  NextFormat.INT, 4),
        ("uint",       1234,  NextFormat.UINT, 4),
        ("float",      123.4, NextFormat.FLOAT, 4),
        ("int64",      1234,  NextFormat.INT64, 8),
        ("uint64",     1234,  NextFormat.UINT64, 8),
        ("float64",    123.4, NextFormat.FLOAT64, 8),
        ("string",     "123456789ABCDEF", NextFormat.STRING, 15),
    ]
)
def test_data(name, value, format, expected_length):
    # test pack
    buf = NextData.pack(value, format)

    assert buf is not None
    assert len(buf) == expected_length

    # test unpack
    clone = NextData.unpack(buf, format)

    assert type(clone) == type(value)
    match format:
        case NextFormat.FLOAT | NextFormat.FLOAT64:
            # carefull with comparing floats
            assert clone == pytest.approx(value, abs=0.01)
        case _:
            assert clone == value
