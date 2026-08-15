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
        ("int",        1234,  NextFormat.INT, 2),
        ("uint",       1234,  NextFormat.UINT, 2),
        ("float",      123.4, NextFormat.FLOAT, 2),
        ("int64",      1234,  NextFormat.INT64, 4),
        ("uint64",     1234,  NextFormat.UINT64, 4),
        ("float64",    123.4, NextFormat.FLOAT64, 4),
        ('bytes',      b'123456789ABCDEF', NextFormat.BYTES, 8),   
        ("string",     "123456789ABCDEF", NextFormat.STRING, 8),
    ]
)
def test_data(name, value, format, expected_length):
    # test pack
    registers = NextData.pack(value, format)

    assert registers is not None
    assert len(registers) == expected_length

    # test unpack
    clone = NextData.unpack(registers, format)

    assert type(clone) == type(value)
    match format:
        case NextFormat.FLOAT | NextFormat.FLOAT64:
            # carefull with comparing floats
            assert clone == pytest.approx(value, abs=0.01)

        case NextFormat.BYTES:
            # Could contain additional b'/x00' after unpack
            clone = clone.rstrip(b"\x00")
            assert clone == value

        case _:
            assert clone == value
