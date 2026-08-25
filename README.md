[![license](https://img.shields.io/github/license/ankohanse/pystudernext?style=for-the-badge)](LICENSE)
[![buy_me_a_coffee](https://img.shields.io/badge/If%20you%20like%20it-Buy%20me%20a%20coffee-yellow.svg?style=for-the-badge)](https://www.buymeacoffee.com/ankohanse)


# pystudernext

Python library for retrieving sensor information from Studer-Innotec devices.
This component connects directly over the local network using the Studer Next modbus protocol.

The custom component is comfirmed to be compatible with:
- Next3 (three-phase)
- Next1 (single-phase)

Disclaimer: this library is NOT created by Studer-Innotec, but is based on their documentation of the Studer Next modbus protocol.
That documentation can be found on:
[Studer-Innotec Download Center](https://www.studer-innotec.com/en/downloads/) *-> Openstuder -> Communication protocol next modbus*

# Prerequisites

This library depends on the Next3/Next1 configured have modbus TCP enabled:
- Open the Studer Next Web Config
- Go to 'Monitoring'
- To the right of 'Modbus' press the 'Config' button
- Turn 'Modbus mode' On
- Use the following properties:
    * Modbus mode: TCP
    * Base address: 0
- Make a note of the other properties:
    * IP address (address of the Next3 or Next1)
    * Port (default is 502)

After a few seconds, the Studer modbus configuration should indicate status: 'Ready and listening'.

# Usage

The library is available from PyPi using:
`pip install pystudernext`

To read or write to a param:

```
import logging
from pystudernext import NextApi, NextFactory, NextDeviceFamilies

logger = logging.getLogger(__name__)

# Set these values before running this example
# Host/ip address and port number of the Next Gateway
GATEWAY_HOST = "192.168.1.123"
GATEWAY_PORT = 502

dataset = NextFactory.create_dataset()
param_2103 = dataset.get_by_address(2103, NextDeviceFamilies.SYSTEM)
param_0318 = dataset.get_by_address(318,  NextDeviceFamilies.BATTERY)
param_5100 = dataset.get_by_address(5100, NextDeviceFamilies.NEXT3)
param_1815 = dataset.get_by_address(1815, NextDeviceFamilies.AC_SOURCE)

api = NextApi(GATEWAY_HOST, GATEWAY_PORT)    
try:
    if not api.start():
        logger.info(f"Did not connect to Next Gateway")
        return

    # Retrieve individual params
    value = api.request_value(param_2103, "SYS")    # System slave range is 1 to 1, or use "SYS"
    logger.info(f"SYS {param_2103.address}: {value} {param_2103.unit or ''} ({param_2103.name})")

    value = api.request_value(param_0318, "BAT_1")  # Battery slave range is 2 to 6, or use "BAT_1" to "BAT_5"
    logger.info(f"BAT_1 {param_0318.address}: {value} {param_0318.unit or ''} ({param_0318.name})")

    value = api.request_value(param_5100, "NX3_1")  # Next3 slave range is 14 to 28, or use "NX3_1" to "NX3_15"
    logger.info(f"NZ3_1 {param_5100.address}: {param_5100.enum_value(value)} {param_5100.unit or ''} ({param_5100.name})")

    # Retrieve and Update param 1815 (Grid feedin allowed))
    logger.info(f"")
    logger.info(f"Retrieve and then update a param")

    value = api.request_value(param_1815, "ACS_1")  # AC Source slave range is 7 to 8, or use "ACS_1" to "ACS_2"
    logger.info(f"ACS_1 {param_1815.address}: {value} {param_1815.unit} ({param_1815.name})")

    value = True
    if api.update_value(param_1815, value, "ACS_1"):
        logger.info(f"ACS_1 {param_1815.address} updated to {value} {param_1815.unit} ({param_1815.name})")


except Exception as e:
    logger.info(f"Unexpected exception: {str(e)}")

finally:
    logger.info(f"")
    api.stop()
```

A complete list of param addresses can be found in the source of this library:
| filename | (sub-)device |
| ---------| ------------ |
| `src/pystudernext/datapoints_sys.json` | System |
| `src/pystudernext/datapoints_bat.json` | Battery |
| `src/pystudernext/datapoints_acs.json` | AC Source |
| `src/pystudernext/datapoints_acf.json` | AC FlexLoads |
| `src/pystudernext/datapoints_nx3.json` | Next3 |
| `src/pystudernext/datapoints_nx1.json` | Next1 |
| `src/pystudernext/datapoints_nxg.json` | Next Gateway |

Several other coding examples are provided:
| Synchronous code | Asynchronous code | Description |
| ---------------- | ----------------- | ------- |
| example_api_use.py | example_api_use_async.py | read & write params |
| example_menu.py | example_menu_async.py | display menu structure |
| example_discover_devices.py | example_discover_devices_async.py | discover local (sub-)devices |
| example_discover_gateway.py | example_discover_gateway_async.py | discover url to Studer Next Web-config |

# Param writes are to device RAM

When the value of a Studer param is changed via this library, these are written to the affected device. 
Changes are stored in the device's on the volatile memory (RAM), not in its persistant/non-volatile memory as you can only write to persistent memory a limited number of times over its lifetime.

After a restart/reboot of the Studer installation the properties are reset to the original values contained in persistent memory. So you may want to periodically repeat the write of changed param values via an automation.

**IMPORTANT**:

Be very carefull in changing params marked as having level Expert or Studer. If you do not know what the effect of a Studer param change is, then do not change it.

# Credits

Special thanks to the following people for providing the information this library is based on and helping out with testing it:
- [t-baum](https://github.com/t-baum)
- [anakinch75](https://github.com/anakinch75)
