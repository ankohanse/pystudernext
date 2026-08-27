from typing import Literal
import pytest
import pytest_asyncio

from pystudernext import NextUserLevel, NextDataType


@pytest.mark.parametrize(
    "description, inp_str, inp_default, exp_val, exp_except",
    [
        ("ViewOnly", "ViewOnly", None, NextUserLevel.VIEWONLY, None),
        ("Basic",    "Basic",    None, NextUserLevel.BASIC,    None),
        ("Expert",   "Expert",   None, NextUserLevel.EXPERT,   None),
        ("Studer",   "Studer",   None, NextUserLevel.STUDER,   None),

        ("value",    "Expert",   NextUserLevel.BASIC, NextUserLevel.EXPERT, None),
        ("default",  "xxxxxx",   NextUserLevel.BASIC, NextUserLevel.BASIC,  None),
        ("except",   "xxxxxx",   None,                None,                 Exception),
    ]
)
def test_level(description:str, inp_str:str, inp_default: NextUserLevel|None, exp_val: NextUserLevel|None, exp_except: type[Exception]|None):

    if exp_except is None:
        val = NextUserLevel.from_str(inp_str, inp_default)
        assert val == exp_val
        assert type(val) is NextUserLevel
    else:
        with pytest.raises(exp_except):
            val = NextUserLevel.from_str(inp_str, inp_default)


@pytest.mark.parametrize(
    "description, inp_str, inp_default, exp_val, exp_except",
    [
        ("bool",          "bool",          None, NextDataType.BOOL,     None),
        ("signal",        "signal",        None, NextDataType.SIGNAL,   None),
        ("int",           "int",           None, NextDataType.INT,      None),
        ("uint",          "uint",          None, NextDataType.UINT,     None),
        ("float",         "float",         None, NextDataType.FLOAT,    None),
        ("enum",          "enum",          None, NextDataType.ENUM,     None),
        ("bitfield",      "bitfield",      None, NextDataType.BITFIELD, None),
        ("int64",         "int64",         None, NextDataType.INT64,    None),
        ("uint64",        "uint64",        None, NextDataType.UINT64,   None),
        ("float64",       "float64",       None, NextDataType.FLOAT64,  None),
        ("string",        "string",        None, NextDataType.STRING,   None),
        ("MENU",          "MENU",          None, NextDataType.MENU,     None),
        ("NOT SUPPORTED", "NOT SUPPORTED", None, NextDataType.INVALID,  None),

        ("value",         "int",   NextDataType.FLOAT, NextDataType.INT,   None),
        ("default",       "xxxxx", NextDataType.FLOAT, NextDataType.FLOAT, None),
        ("except",        "xxxxx", None,             None,             Exception),
    ]
)
def test_format(description:str, inp_str:str, inp_default: NextDataType|None, exp_val: NextDataType|None, exp_except: type[Exception]|None):

    if exp_except is None:
        val = NextDataType.from_str(inp_str, inp_default)
        assert val == exp_val
        assert type(val) is NextDataType
    else:
        with pytest.raises(exp_except):
            val = NextDataType.from_str(inp_str, inp_default)
