"""Minimal async Modbus TCP client — no external dependencies."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

_MODBUS_PROTOCOL_ID = 0x0000
_FC_READ_HOLDING = 0x03
_FC_WRITE_MULTIPLE = 0x10


class ModbusTcpError(Exception):
    """Raised when the device returns a Modbus exception response."""


class ModbusClientBase:
    def __init__(self, host: str, port: int, timeout: float = 10.0) -> None:
        raise NotImplementedError()

    @property
    def connected(self) -> bool:
        raise NotImplementedError()

    async def connect(self) -> bool:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    async def read_holding_registers(self, address: int, count: int, slave: int) -> list[int]:
        raise NotImplementedError()

    async def write_holding_registers(self, address: int, registers: list[int], slave: int) -> None:
        raise NotImplementedError()


class ModbusTcpClient(ModbusClientBase):
    """Bare-bones async Modbus TCP client using raw sockets."""

    # TODO
