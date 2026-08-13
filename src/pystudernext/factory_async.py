#! /usr/bin/env python3

##
# Definition of all parameters / constants used in the Xcom protocol
##

import asyncio
import binascii
from datetime import datetime, timedelta
import decimal
import logging
import math
import orjson

from aiofiles import open as aiofiles_open
from io import BufferedReader

from .datapoints import (
    NextDatapoint,
    NextDataset,
)


_LOGGER = logging.getLogger(__name__)


class AsyncNextFactory:

    @staticmethod
    async def create_dataset() -> NextDataset:
        """
        The actual NextDataset list is kept in separate json files to reduce the memory size needed to load the integration.
        The list is only loaded during config flow and during initial startup, and then released again.
        """
        datapoints = list()

        for item_path in NextDataset.PATHS:
            async with aiofiles_open(item_path, "r", encoding="UTF-8") as item_file:
                item_text = await item_file.read()

            item_values = orjson.loads(item_text)
            item_datapoints = list(filter(None, [NextDatapoint.from_dict(val) for val in item_values]))

            # Merge the datapoints from this file
            datapoints = datapoints + item_datapoints

        _LOGGER.info(f"Using {len(datapoints)} datapoints")

        return NextDataset(datapoints)
