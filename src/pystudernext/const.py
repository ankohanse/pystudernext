#! /usr/bin/env python3

##
# Definition of all parameters / constants used in the Next protocol
##

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Iterable


class NextApiConnectException(Exception):
    """Exception to indicate failure while connecting to the Next Gateway"""

class NextApiTimeoutException(Exception):
    """Exception to indicate a timeout while reading from the next gateway"""

class NextUnpackException(Exception):
    """Exception to indicate faulure to unpack a response value"""

class NextPackException(Exception):
    """Exception to indicate faulure to pack a update value"""

class NextDiscoverNotConnected(Exception):
    """Exception to indicate that remote next gateway is not connected"""

class NextParamException(Exception):
    """Exeption to indicaye that something is wrong with the parameters passed to a call"""


DEFAULT_HOST = ""
DEFAULT_PORT = 502

CONNECT_TIMEOUT = 10 # seconds
CLOSE_TIMEOUT = 5
REQ_TIMEOUT = 3
REQ_RETRIES = 3
REQ_BURST_PERIOD = 5 # do burst of requests for 5 seconds, then wait a second, then the next burst


class NextUserLevel(IntEnum):
    VIEWONLY = 0x0000
    BASIC    = 0x0010
    EXPERT   = 0x0020
    INST     = 0x0030 # Installer
    QSP      = 0x0040 # Qualified Service Person
    DENIED   = 0xFFFF # Used to indicate that a read or write action is not allowed

    @staticmethod
    def from_str(s: str, default: int|None = None):
        match s.upper():
            case 'VIEWONLY': return NextUserLevel.VIEWONLY
            case 'BASIC': return NextUserLevel.BASIC
            case 'EXPERT': return NextUserLevel.EXPERT
            case 'INST': return NextUserLevel.INST
            case 'QSP': return NextUserLevel.QSP
            case _: 
                if default is not None:
                    return default
                else:
                    msg = f"Unknown level: '{s}'"
                    raise Exception(msg)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name


class NextFormat(StrEnum):
    BOOL       = "bool"         # 1 register / 1 byte
    SIGNAL     = "signal"       # 1 register / 1byte
    INT        = "int"          # 2 registers / 4 bytes
    UINT       = "uint"         # 2 registers / 4 bytes
    FLOAT      = "float"        # 2 registers / 4 bytes
    ENUM       = "enum"         # 2 registers / 4 bytes
    BITFIELD   = "bitfield"     # 2 registers / 4 bytes
    INT64      = "int64"        # 4 registers / 8 bytes
    UINT64     = "uint64"       # 4 registers / 8 bytes
    FLOAT64    = "float64"      # 4 registers / 8 bytes
    STRING     = "string"       # n registers / 2n bytes
    BYTES      = "bytes"        # n registers / 2n bytes
    MENU       = "menu"         # n.a.
    INVALID    = "invalid"      # n.a.

    @staticmethod
    def from_str(s: str, default: str|None = None):
        match s.lower():
            case 'bool': return NextFormat.BOOL
            case 'signal': return NextFormat.SIGNAL
            case 'int': return NextFormat.INT
            case 'uint': return NextFormat.UINT
            case 'float': return NextFormat.FLOAT
            case 'enum': return NextFormat.ENUM
            case 'bitfield': return NextFormat.BITFIELD
            case 'int64': return NextFormat.INT64
            case 'uint64': return NextFormat.UINT64
            case 'float64': return NextFormat.FLOAT64
            case 'string': return NextFormat.STRING
            case 'bytes': return NextFormat.BYTES
            case 'menu': return NextFormat.MENU
            case 'not supported': return NextFormat.INVALID
            case _: 
                if default is not None:
                    return default
                else:
                    msg = f"Unknown format: '{s}'"
                    raise Exception(msg)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
       

class NextRW(StrEnum):
    READ       = "R"
    WRITE      = "W"
    READ_WRITE = "R/W"

    @staticmethod
    def from_str(s: str, default: str|None = None):
        match s.upper():
            case 'R': return NextRW.READ
            case 'W': return NextRW.WRITE
            case 'R/W': return NextRW.READ_WRITE
            case _: 
                if default is not None:
                    return default
                else:
                    msg = f"Unknown read-write flag: '{s}'"
                    raise Exception(msg)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name


class NextCategory:
    INFO       = 0x0001
    PARAMETER  = 0x0002


def safe_len(lst: Iterable):
    try:
        return len(lst)
    except:
        return sum(1 for i in lst) 
