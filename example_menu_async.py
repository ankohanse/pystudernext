
# Notes:
# 1 Before running the example, install the 'pystudernext' library locally:
#   - Open a command prompt at the root of this project
#   - run: pip install -e .    (or python -m pip install -e .)
#

import asyncio
import logging
import sys

from helper import RunHelper

from pystudershared import StuderDataType
from pystudernext import NextDeviceFamilies
from pystudernext import NextDataset
from pystudernext.datapoints import NextDatasetFlag
from pystudernext.families import NextDeviceFamiliesFlag

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    # Print entire menu structure
    families = await NextDeviceFamilies.async_get_instance(flags={ NextDeviceFamiliesFlag.ADD_TEST: True })
    dataset = await NextDataset.async_get_instance(flags={ NextDatasetFlag.ADD_TEST: True })
    units = set()
    
    # Helper function to recursively print the entire menu
    async def print_menu(family, parent_id, indent=""):
        items = dataset.get_menu_items(family, parent_id)
        for item in items:
            if item.data_type == StuderDataType.MENU:
                logger.info(f"{indent}{item.label}")

                await print_menu(family, item.id, indent+"  ")
            else:
                logger.info(f"{indent}{item.label} ({item.address})")

    for family in families:
        logger.info(f"")
        logger.info(f"{family.model}")
        await print_menu(family, "", "  ")

    dataset = None  # Release memory of the dataset


RunHelper.run(main)  # main loop