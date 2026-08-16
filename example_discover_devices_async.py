import asyncio
from dataclasses import asdict
import logging
import sys

from pystudernext import AsyncNextApi, NextApi
from pystudernext import AsyncNextDiscover, NextDiscover
from pystudernext import AsyncNextFactory, NextFactory
from pystudernext import NextDataset
from helper import RunHelper

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    api = AsyncNextApi(host="192.186.1.50", port=502)    # port number configured in Next-LAN/Moxa NPort
    dataset = await AsyncNextFactory.create_dataset()

    try:
        if not await api.start():
            logger.info(f"Did not connect to Next Gateway")
            return
        
        helper = AsyncNextDiscover(api, dataset)

        # Discover NX Gateway info
        gw_info = await helper.discover_gateway_info()

        logger.info(f"\n\n")
        logger.info(f"Discovered {gw_info}")

        # Discover NX devices
        devices = await helper.discover_devices(getExtendedInfo=True, verbose=False)

        logger.info(f"\n\n")
        for device in devices:
            logger.info(f"Discovered {device}")

        # Log diagnostic information
        diag = await api.get_diagnostics()
        logger.info(f"Diagnostics: {diag}")

    finally:
        await api.stop()
        dataset = None


RunHelper.run(main)  # main loop
