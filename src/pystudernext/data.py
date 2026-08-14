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
    def unpack(value: bytes, format):
        match format:
            case NextFormat.BOOL: return struct.unpack("<?", value)[0]          # 1 byte, little endian, bool
            case NextFormat.SIGNAL: return struct.unpack("<?", value)[0]        # 1 byte, little endian, bool
            case NextFormat.INT:  return struct.unpack("<i", value)[0]          # 4 bytes, little endian, signed short/int32
            case NextFormat.UINT: return struct.unpack("<I", value)[0]          # 4 bytes, little endian, unsigned short/int32
            case NextFormat.FLOAT: return struct.unpack("<f", value)[0]         # 4 bytes, little endian, float
            case NextFormat.INT64: return struct.unpack("<q", value)[0]         # 8 bytes, little endian, signed long/int64
            case NextFormat.UINT64: return struct.unpack("<Q", value)[0]        # 8 bytes, little endian, unsigned long/int64
            case NextFormat.FLOAT64: return struct.unpack("<d", value)[0]       # 8 bytes, little endian, float64
            case NextFormat.STRING: return value.decode('iso-8859-15')          # n bytes, ISO_8859-15 string of 8 bit characters
            case NextFormat.BYTES: return int.from_bytes(value, byteorder='little') # n bytes, little endian
            case _: 
                msg = "Unknown data format '{format}"
                raise TypeError(msg)

    @staticmethod
    def pack(value, format) -> bytes:
        match format:
            case NextFormat.BOOL: return struct.pack("<?", int(value))          # 1 byte, little endian, bool
            case NextFormat.SIGNAL: return struct.pack("<?", int(value))        # 1 byte, little endian, bool
            case NextFormat.INT: return struct.pack("<i", int(value))           # 4 bytes, little endian, unsigned short/int32
            case NextFormat.UINT: return struct.pack("<I", int(value))          # 4 bytes, little endian, unsigned short/int32
            case NextFormat.FLOAT: return struct.pack("<f", float(value))       # 4 bytes, little endian, float
            case NextFormat.INT64: return struct.pack("<q", int(value))         # 8 bytes, little endian, signed long/int64
            case NextFormat.UINT64: return struct.pack("<Q", int(value))        # 8 bytes, little endian, unsigned long/int64
            case NextFormat.FLOAT64: return struct.pack("<d", float(value))     # 8 bytes, little endian, float64
            case NextFormat.STRING: return value.encode('iso-8859-15')          # n bytes, ISO_8859-15 string of 8 bit characters
            case NextFormat.BYTES: return int(value).to_bytes(8, byteorder='little') # n bytes, little endian
            case _: 
                msg = "Unknown data format '{format}"
                raise TypeError(msg)

    @staticmethod
    def cast(value: Any, format):
        match format:
            case NextFormat.BOOL: return bool(value)
            case NextFormat.SIGNAL: return bool(value)
            case NextFormat.INT: return int(value)
            case NextFormat.UINT: return int(value)
            case NextFormat.FLOAT: return float(value)
            case NextFormat.INT64: return int(value)
            case NextFormat.UINT64: return int(value)
            case NextFormat.FLOAT64: return float(value)
            case NextFormat.STRING: return value.decode('iso-8859-15') 
            case NextFormat.BYTES: return value.to_bytes(8, byteorder='little')
            case _: 
                msg = f"Unknown data format '{format}"
                raise TypeError(msg)
