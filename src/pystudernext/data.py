##
## Class implementing Next protocol data objects
##
## See the studer document: "Technical Specification - Next Modbus"
## Download from:
##   https://studer-innotec.com/downloads/ 
##   -> Downloads -> software + updates -> communication protocol next modbus
##


import asyncio
from dataclasses import dataclass
import io
import logging
import math
import struct
import uuid

from io import BufferedWriter, BufferedReader, BytesIO
from typing import Any, Iterable

from .const import (
    NextFormat,
    NextParamException,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class NextDiscoveredGateway:
    ip: str = None
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


class NextData:
    NONE = b''

    @staticmethod
    def unpack(registers: list[int], format: NextFormat) -> Any:
        """
        Unpack registers (list of uint16) into a value of specified type
        """
        # Convert from list[uint16] into bytes
        bytes = struct.pack(f">{len(registers)}H", *registers)

        match format:
            case NextFormat.BOOL: return struct.unpack(">?", bytes[:1])[0]      # 1 byte,  big endian, bool
            case NextFormat.SIGNAL: return struct.unpack(">?", bytes[:1])[0]    # 1 byte,  big endian, bool
            case NextFormat.INT:  return struct.unpack(">i", bytes)[0]          # 4 bytes, big endian, signed short/int32
            case NextFormat.UINT: return struct.unpack(">I", bytes)[0]          # 4 bytes, big endian, unsigned short/int32
            case NextFormat.FLOAT: return struct.unpack(">f", bytes)[0]         # 4 bytes, big endian, float
            case NextFormat.INT64: return struct.unpack(">q", bytes)[0]         # 8 bytes, big endian, signed long/int64
            case NextFormat.UINT64: return struct.unpack(">Q", bytes)[0]        # 8 bytes, big endian, unsigned long/int64
            case NextFormat.FLOAT64: return struct.unpack(">d", bytes)[0]       # 8 bytes, big endian, float64
            case NextFormat.BYTES: return bytes                                 # n bytes, big endian, array of bytes
            case NextFormat.STRING:                                             # n bytes, string of 8 bit characters                           
                str = bytes.decode('utf-8')
                return str.rstrip("\x00")                                   
            case _: 
                msg = "Unknown data format '{format}'"
                raise NextParamException(msg)


    @staticmethod
    def pack(value: Any, format: NextFormat) -> list[int]:
        """
        Pack a value of specified type into registers (list of uint16)
        """
        match format:
            case NextFormat.BOOL: bytes = struct.pack(">?", int(value))          # 1 byte, big endian, bool
            case NextFormat.SIGNAL: bytes = struct.pack(">?", int(value))        # 1 byte, big endian, bool
            case NextFormat.INT: bytes = struct.pack(">i", int(value))           # 4 bytes, big endian, unsigned short/int32
            case NextFormat.UINT: bytes = struct.pack(">I", int(value))          # 4 bytes, big endian, unsigned short/int32
            case NextFormat.FLOAT: bytes = struct.pack(">f", float(value))       # 4 bytes, big endian, float
            case NextFormat.INT64: bytes = struct.pack(">q", int(value))         # 8 bytes, big endian, signed long/int64
            case NextFormat.UINT64: bytes = struct.pack(">Q", int(value))        # 8 bytes, big endian, unsigned long/int64
            case NextFormat.FLOAT64: bytes = struct.pack(">d", float(value))     # 8 bytes, big endian, float64
            case NextFormat.BYTES: bytes = value                                 # n bytes, big endian, array of bytes
            case NextFormat.STRING: bytes = value.encode('utf-8', errors="ignore") # n bytes, string of 8 bit characters                           
            case _: 
                msg = "Unknown data format '{format}"
                raise NextParamException(msg)

        # Make sure the byte array length is a multiple of 2
        len16   = math.ceil(len(bytes)/2)
        bytes16 = bytes.ljust(len16*2, b"\x00")                     

        # Convert into array of uint16
        return list(struct.unpack(f">{len16}H", bytes16))

