from typing import Literal
import pytest
import pytest_asyncio

from pystudernext import NextUserLevel, NextFormat


@pytest.mark.parametrize(
    "description, inp_str, inp_default, exp_val, exp_except",
    [
        ("ViewOnly", "ViewOnly", None, NextUserLevel.VIEWONLY, None),
        ("Basic",    "Basic",    None, NextUserLevel.BASIC,    None),
        ("Expert",   "Expert",   None, NextUserLevel.EXPERT,   None),
        ("Inst",     "Inst",     None, NextUserLevel.INST,     None),
        ("QSP",      "QSP",      None, NextUserLevel.QSP,      None),

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
        ("bool",          "bool",          None, NextFormat.BOOL,     None),
        ("signal",        "signal",        None, NextFormat.SIGNAL,   None),
        ("int",           "int",           None, NextFormat.INT,      None),
        ("uint",          "uint",          None, NextFormat.UINT,     None),
        ("float",         "float",         None, NextFormat.FLOAT,    None),
        ("enum",          "enum",          None, NextFormat.ENUM,     None),
        ("bitfield",      "bitfield",      None, NextFormat.BITFIELD, None),
        ("int64",         "int64",         None, NextFormat.INT64,    None),
        ("uint64",        "uint64",        None, NextFormat.UINT64,   None),
        ("float64",       "float64",       None, NextFormat.FLOAT64,  None),
        ("string",        "string",        None, NextFormat.STRING,   None),
        ("bytes",         "bytes",         None, NextFormat.BYTES,    None),
        ("BYTES",         "BYTES",         None, NextFormat.BYTES,    None),
        ("MENU",          "MENU",          None, NextFormat.MENU,     None),
        ("NOT SUPPORTED", "NOT SUPPORTED", None, NextFormat.INVALID,  None),

        ("value",         "int",   NextFormat.FLOAT, NextFormat.INT,   None),
        ("default",       "xxxxx", NextFormat.FLOAT, NextFormat.FLOAT, None),
        ("except",        "xxxxx", None,             None,             Exception),
    ]
)
def test_format(description:str, inp_str:str, inp_default: NextFormat|None, exp_val: NextFormat|None, exp_except: type[Exception]|None):

    if exp_except is None:
        val = NextFormat.from_str(inp_str, inp_default)
        assert val == exp_val
        assert type(val) is NextFormat
    else:
        with pytest.raises(exp_except):
            val = NextFormat.from_str(inp_str, inp_default)
