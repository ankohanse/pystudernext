import asyncio
import logging
import sys

from pystudernext import AsyncNextFactory
from pystudernext import NextFactory
from pystudernext import NextFormat
from pystudernext import NextDeviceFamilies
from helper import RunHelper

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    # Print entire menu structure
    dataset = await AsyncNextFactory.create_dataset()

    # Helper function to recursively print the entire menu
    async def print_menu(family_id, parent_id, indent=""):
        items = dataset.get_menu_items(family_id, parent_id)
        for item in items:
            if item.format == NextFormat.MENU:
                logger.info(f"{indent}{item.id} {item.label}")
                
                await print_menu(family_id, item.id, indent+"  ")
            else:
                logger.info(f"{indent}{item.id} {item.label} ({item.addr})")

    for family in NextDeviceFamilies.get_list():
        logger.info(f"")
        logger.info(f"{family.model}")
        await print_menu(family.id, "", "  ")

    dataset = None  # Release memory of the dataset


RunHelper.run(main)  # main loop