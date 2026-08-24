##
## Class implementing Next protocol data objects
##
## See the studer document: "Technical Specification - Next Modbus"
## Download from:
##   https://studer-innotec.com/downloads/ 
##   -> Downloads -> software + updates -> communication protocol next modbus
##

import logging

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pymodbus.client import ModbusTcpClient


_LOGGER = logging.getLogger(__name__)


class NextApiConnectException(Exception):
    """Exception to indicate failure while connecting to the Next Gateway"""

class NextApiTimeoutException(Exception):
    """Exception to indicate a timeout while reading from the Next gateway"""

class NextApiReadException(Exception):
    """Exception to indicate failure to read data from the Next gateway"""

class NextApiUpdateException(Exception):
    """Exception to indicate failure to update data via the Next gateway"""

class NextUnpackException(Exception):
    """Exception to indicate faulure to unpack a response value"""

class NextPackException(Exception):
    """Exception to indicate faulure to pack a update value"""

class NextDiscoverNotConnected(Exception):
    """Exception to indicate that remote next gateway is not connected"""

class NextParamException(Exception):
    """Exeption to indicaye that something is wrong with the parameters passed to a call"""


@dataclass
class NextDiscoveredGateway:
    host: str = None
    port: int = None
    guid: str = None


@dataclass
class NextDiscoveredDevice:
    # Base info
    code: str
    slave: int
    family_id: str
    family_model: str

    # Extended info
    serial: str = None      # Serial number
    sw_version: str = None  # Softwate version
    om_version: str = None  # ObjectModel version


class NextUserLevel(IntEnum):
    VIEWONLY = 0x0000
    BASIC    = 0x0010
    EXPERT   = 0x0020
    STUDER   = 0x0040 # Studer Qualified Service Person
    DENIED   = 0xFFFF # Used to indicate that a read or write action is not allowed

    @staticmethod
    def from_str(s: str, default: int|None = None):
        match s.upper():
            case 'VIEWONLY': return NextUserLevel.VIEWONLY
            case 'BASIC': return NextUserLevel.BASIC
            case 'EXPERT': return NextUserLevel.EXPERT
            case 'STUDER': return NextUserLevel.STUDER
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


class NextDataType(StrEnum):
    BOOL       = "bool"         # 1 register  / 2 bytes
    SIGNAL     = "signal"       # 1 register  / 2 bytes
    INT        = "int"          # 2 registers / 4 bytes
    UINT       = "uint"         # 2 registers / 4 bytes
    FLOAT      = "float"        # 2 registers / 4 bytes
    ENUM       = "enum"         # 2 registers / 4 bytes
    BITFIELD   = "bitfield"     # 2 registers / 4 bytes
    INT64      = "int64"        # 4 registers / 8 bytes
    UINT64     = "uint64"       # 4 registers / 8 bytes
    FLOAT64    = "float64"      # 4 registers / 8 bytes
    STRING     = "string"       # n registers / 2n bytes
    MENU       = "menu"         # n.a.
    INVALID    = "invalid"      # n.a.

    @staticmethod
    def from_str(s: str, default: str|None = None):
        match s.lower():
            case 'bool': return NextDataType.BOOL
            case 'signal': return NextDataType.SIGNAL
            case 'int': return NextDataType.INT
            case 'uint': return NextDataType.UINT
            case 'float': return NextDataType.FLOAT
            case 'enum': return NextDataType.ENUM
            case 'bitfield': return NextDataType.BITFIELD
            case 'int64': return NextDataType.INT64
            case 'uint64': return NextDataType.UINT64
            case 'float64': return NextDataType.FLOAT64
            case 'string': return NextDataType.STRING
            case 'menu': return NextDataType.MENU
            case 'not supported': return NextDataType.INVALID
            case _: 
                if default is not None:
                    return default
                else:
                    raise Exception(f"Unknown data-type: '{s}'")

    @staticmethod
    def to_datatype(format: 'NextDataType') -> ModbusTcpClient.DATATYPE:
        match format:
            case NextDataType.BOOL:       return ModbusTcpClient.DATATYPE.UINT16 
            case NextDataType.SIGNAL:     return ModbusTcpClient.DATATYPE.UINT16 
            case NextDataType.INT:        return ModbusTcpClient.DATATYPE.INT32  
            case NextDataType.UINT:       return ModbusTcpClient.DATATYPE.UINT32 
            case NextDataType.FLOAT:      return ModbusTcpClient.DATATYPE.FLOAT32
            case NextDataType.ENUM:       return ModbusTcpClient.DATATYPE.UINT32 
            case NextDataType.BITFIELD:   return ModbusTcpClient.DATATYPE.BITS   
            case NextDataType.INT64:      return ModbusTcpClient.DATATYPE.INT64  
            case NextDataType.UINT64:     return ModbusTcpClient.DATATYPE.UINT64 
            case NextDataType.FLOAT64:    return ModbusTcpClient.DATATYPE.FLOAT64
            case NextDataType.STRING:     return ModbusTcpClient.DATATYPE.STRING 
            case _:
                raise NextParamException(f"Cannot convert format {format} into a DATATYPE")

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
