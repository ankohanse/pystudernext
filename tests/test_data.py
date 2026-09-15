from typing import Literal
import pytest
import pytest_asyncio

from pystudernext import StuderUserLevel, NextUserLevel


@pytest.mark.parametrize(
    "description, inp_str, inp_default, exp_val, exp_except",
    [
        ("ViewOnly", "ViewOnly", None, StuderUserLevel.VIEWONLY, None),
        ("Basic",    "Basic",    None, StuderUserLevel.BASIC,    None),
        ("Expert",   "Expert",   None, StuderUserLevel.EXPERT,   None),
        ("Studer",   "Studer",   None, StuderUserLevel.STUDER,   None),

        ("value",    "Expert",   StuderUserLevel.BASIC, StuderUserLevel.EXPERT, None),
        ("default",  "xxxxxx",   StuderUserLevel.BASIC, StuderUserLevel.BASIC,  None),
        ("except",   "xxxxxx",   None,                None,                 Exception),
    ]
)
def test_level(description:str, inp_str:str, inp_default: StuderUserLevel|None, exp_val: StuderUserLevel|None, exp_except: type[Exception]|None):

    if exp_except is None:
        val = NextUserLevel.from_str(inp_str, inp_default)
        assert val == exp_val
        assert type(val) is StuderUserLevel
    else:
        with pytest.raises(exp_except):
            val = NextUserLevel.from_str(inp_str, inp_default)


