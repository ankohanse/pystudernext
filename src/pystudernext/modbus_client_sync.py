"""Minimal async Modbus TCP client — no external dependencies."""
from abc import ABC, abstractmethod

import logging


_LOGGER = logging.getLogger(__name__)

_MODBUS_PROTOCOL_ID = 0x0000
_FC_READ_HOLDING = 0x03
_FC_WRITE_MULTIPLE = 0x10


class ModbusTcpError(Exception):
    """Raised when the device returns a Modbus exception response."""


class ModbusClientBase(ABC):
    """
    Interface definition for any Async Modbus Client
    """

    @property
    @abstractmethod
    def connected(self) -> bool:
        pass

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def read_holding_registers(self, address: int, count: int, slave: int) -> list[int]:
        pass

    @abstractmethod
    def write_holding_registers(self, address: int, registers: list[int], slave: int) -> None:
        pass


class ModbusTcpClient(ModbusClientBase):
    """
    Bare-bones async Modbus TCP client using raw sockets.
    """

    # TODO
