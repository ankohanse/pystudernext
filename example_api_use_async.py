import asyncio
import logging
import sys

from pystudernext import AsyncNextApi, NextApi
from pystudernext import AsyncNextFactory, NextFactory
from pystudernext import NextDataset, NextDatapoint, NextData
from pystudernext import NextFormat
from pystudernext import DEFAULT_PORT
from helper import RunHelper

# Setup logging to StdOut
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    dataset = await AsyncNextFactory.create_dataset()
    param_2103 = dataset.get_by_address(2103, "sys")  # System, the "sys" part is optional but usefull for detecting mistakes
    param_0318 = dataset.get_by_address(318,  "bat")  # Battery
    param_1815 = dataset.get_by_address(1815, "acs")  # AC Source
    param_5100 = dataset.get_by_address(5100, "nx3")  # Next 3
    param_6900 = dataset.get_by_address(6900, "nx3")
    param_6902 = dataset.get_by_address(6902, "nx3")

    api = AsyncNextApi("192.168.1.123", DEFAULT_PORT)    # host and port number of the Next Gateway
    try:
        if not await api.start():
            logger.info(f"Did not connect to Next Gateway")
            return

        # Retrieve individual infos and params
        logger.info(f"")
        logger.info(f"Retrieve infos and params via individual calls")

        value = await api.request_value(param_2103, "SYS")    # System slave range is 1 to 1, or use "SYS"
        logger.info(f"SYS {param_2103.address}: {value} {param_2103.unit or ''} ({param_2103.name})")

        value = await api.request_value(param_0318, "BAT_1")  # Battery slave range is 2 to 6, or use "BAT_1" to "BAT_5"
        logger.info(f"BAT_1 {param_0318.address}: {value} {param_0318.unit or ''} ({param_0318.name})")

        value = await api.request_value(param_5100, "NX3_1")  # Next3 slave range is 14 to 28, or use "NX3_1" to "NX3_15"
        logger.info(f"NZ3_1 {param_5100.address}: {param_5100.enum_value(value)} {param_5100.unit or ''} ({param_5100.name})")

        value = await api.request_value(param_6900, "NX3_1")  # Next3 slave range is 14 to 28, or use "NX3_1" to "NX3_15"
        logger.info(f"NZ3_1 {param_6900.address}: {value} {param_6900.unit or ''} ({param_6900.name})")

        value = await api.request_value(param_6902, "NX3_1")  # Next3 slave range is 14 to 28, or use "NX3_1" to "NX3_15"
        logger.info(f"NZ3_1 {param_6902.address}: {value} {param_6902.unit or ''} ({param_6902.name})")

        # Retrieve and Update param 1815 (Grid feedin allowed))
        logger.info(f"")
        logger.info(f"Retrieve and then update a param")

        value = await api.request_value(param_1815, "ACS_1")  # AC Source slave range is 7 to 8, or use "ACS_1" to "ACS_2"
        logger.info(f"ACS_1 {param_1815.address}: {value} {param_1815.unit} ({param_1815.name})")

        value = True
        if await api.update_value(param_1815, value, "ACS_1"):
            logger.info(f"ACS_1 {param_1815.address} updated to {value} {param_1815.unit} ({param_1815.name})")

    except Exception as e:
        logger.info(f"Unexpected exception: {str(e)}")

    finally:
        logger.info(f"")
        await api.stop()



RunHelper.run(main)  # main loop