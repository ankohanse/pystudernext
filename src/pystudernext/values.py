

import logging

from dataclasses import dataclass
from typing import Any, Iterable

from .families import NextDeviceFamilies
from .shared.helpers import safe_isinstance
from .shared.studer_dataset import StuderDatapoint
from .shared.studer_types import StuderDiscoveredDevice, StuderParamException
from .shared.studer_valueset import StuderValueItem, StuderValueSet


_LOGGER = logging.getLogger(__name__)


@dataclass
class NextValueItem(StuderValueItem):
    # From parent class:
    #    datapoint: StuderDatapoint                  # Both in request and response, for request_infos and request_values
    #    code: str                                   # Both in request and response, for request_infos and request_values
    #    address_or_slave: int                       # Both in request and response, for request_infos and request_values
    #    value: Any                                  # Only in response from request_values()
    #    error: str|None                             # Only in response from request_values()


    def __init__(self, datapoint: StuderDatapoint, device: StuderDiscoveredDevice|int|str, value:Any=None, error:str|None=None):

        # Convert from code, addr and aggr. Code trumps addr and aggr, while addr trumps aggr.
        families = NextDeviceFamilies.get_instance() # singleton instance

        if safe_isinstance(device, StuderDiscoveredDevice):
            code = device.code
            slave = device.slave
        elif isinstance(device, int):
            slave = device
            code = families.get_code_by_slave(slave, datapoint.family_id)
        elif isinstance(device, str):  
            code = device
            slave = families.get_slave_by_code(code)
        else:
            raise StuderParamException(f"Parameter 'device' must be a XcomDiscoverdDevice, device address or a device code in call to request_value")

        # Set properties
        self.datapoint = datapoint
        self.code = code
        self.address_or_slave = slave
        self.value = value
        self.error = error


@dataclass
class NextValueSet(StuderValueSet):
    # From parent
    #    items: Iterable[StuderValuesItem] # Both in request and response

    def __init__(self, items: Iterable[StuderValueItem]):
        self.items = items

