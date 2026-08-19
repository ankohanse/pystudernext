#! /usr/bin/env python3

##
# Definition of all parameters / constants used in the Next protocol
##

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pymodbus.client import AsyncModbusTcpClient
from typing import Iterable


DEFAULT_HOST = ""
DEFAULT_PORT = 502

   
def safe_len(lst: Iterable):
    try:
        return len(lst)
    except:
        return sum(1 for i in lst) 
