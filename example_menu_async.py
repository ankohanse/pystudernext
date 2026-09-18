
# Notes:
# 1 Before running the example, install the 'pystudernext' library locally:
#   - Open a command prompt at the root of this project
#   - run: pip install -e .    (or python -m pip install -e .)
#

import asyncio
import logging
import sys

from helper import RunHelper

from pystudernext import NextDeviceFamilies
from pystudernext import StuderDataType
from pystudernext import NextDataset

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    # Print entire menu structure
    families = await NextDeviceFamilies.async_get_instance()
    dataset = await NextDataset.async_get_instance()

    # Helper function to recursively print the entire menu
    async def print_menu(family_id, parent_id, indent=""):
        items = dataset.get_menu_items(family_id, parent_id)
        for item in items:
            if item.data_type == StuderDataType.MENU:
                logger.info(f"{indent}{item.label}")

                await print_menu(family_id, item.id, indent+"  ")
            else:
                logger.info(f"{indent}{item.label} ({item.address})")

    for family in families:
        logger.info(f"")
        logger.info(f"{family.model}")
        await print_menu(family.id, "", "  ")

    dataset = None  # Release memory of the dataset


RunHelper.run(main)  # main loop