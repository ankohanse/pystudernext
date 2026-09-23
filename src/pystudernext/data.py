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

from pystudernext import (
    StuderDataType,
    StuderUserLevel,
    StuderParamException,
)


_LOGGER = logging.getLogger(__name__)


class NextApiConnectException(Exception):
    """Exception to indicate failure while connecting to the Next Gateway"""

class NextApiTimeoutException(Exception):
    """Exception to indicate a timeout while reading from the Next gateway"""

class NextApiReadException(Exception):
    """Exception to indicate failure to read data from the Next gateway"""

class NextApiUpdateException(Exception):
    """Exception to indicate failure to update data via the Next gateway"""

class NextApiUnpackException(Exception):
    """Exception to indicate faulure to unpack a response value"""

class NextApiPackException(Exception):
    """Exception to indicate faulure to pack a update value"""


class NextUserLevel():
    """Helper to read User-Level from the dataset structures"""

    @staticmethod
    def from_str(s: str, default: int|None = None) -> StuderUserLevel:
        match s.upper():
            case 'VIEWONLY': return StuderUserLevel.VIEWONLY
            case 'BASIC': return StuderUserLevel.BASIC
            case 'EXPERT': return StuderUserLevel.EXPERT
            case 'STUDER': return StuderUserLevel.STUDER
            case _: 
                if default is not None:
                    return default
                else:
                    raise Exception(f"Unknown user-level: '{s}'")


class NextDataType():

    @staticmethod
    def to_datatype(data_type: StuderDataType) -> ModbusTcpClient.DATATYPE:
        match data_type:
            case StuderDataType.BOOL:       return ModbusTcpClient.DATATYPE.UINT16 
            case StuderDataType.SIGNAL:     return ModbusTcpClient.DATATYPE.UINT16 
            case StuderDataType.INT16:      return ModbusTcpClient.DATATYPE.INT16  
            case StuderDataType.UINT16:     return ModbusTcpClient.DATATYPE.UINT16 
            case StuderDataType.INT32:      return ModbusTcpClient.DATATYPE.INT32  
            case StuderDataType.UINT32:     return ModbusTcpClient.DATATYPE.UINT32 
            case StuderDataType.FLOAT32:    return ModbusTcpClient.DATATYPE.FLOAT32
            case StuderDataType.ENUM32:     return ModbusTcpClient.DATATYPE.UINT32 
            case StuderDataType.BITFIELD:   return ModbusTcpClient.DATATYPE.BITS   
            case StuderDataType.INT64:      return ModbusTcpClient.DATATYPE.INT64  
            case StuderDataType.UINT64:     return ModbusTcpClient.DATATYPE.UINT64 
            case StuderDataType.FLOAT64:    return ModbusTcpClient.DATATYPE.FLOAT64
            case StuderDataType.STRING:     return ModbusTcpClient.DATATYPE.STRING 
            case _:
                raise StuderParamException(f"Cannot convert data-type {data_type} into a DATATYPE")
