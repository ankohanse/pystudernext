
"""
Definition of all known device families used in the Next protocol
"""

import logging

from dataclasses import dataclass

from .shared.studer_families import (
    StuderDeviceFamilies,
    StuderDeviceFamily,
    StuderDeviceSlaveUnknownException,
)


_LOGGER = logging.getLogger(__name__)


@dataclass
class NextDeviceFamily(StuderDeviceFamily):
    # From super class
    # id: str               # Short id
    # model: str            # Model name

    # Specific for Next device family
    slaves_start: int       # First possible slave number
    slaves_end: int         # Last possible slave number
    address_discover: int   # Address used to discover presence of the device
    address_model: int      # Model name
    address_serial: int     # Serial number
    address_sw_version: int # Software version
    address_om_version: int # ObjectModel version

    def get_code(self, slave):
        if self.slaves_start == slave == self.slaves_end:
            return self.id.upper()
        
        if self.slaves_start <= slave <= self.slaves_end:
            idx = slave - self.slaves_start + 1
            return f"{self.id.upper()}_{idx}"
        
        msg = f"Slave {slave} is not in range for family {self.id} ({self.slaves_start}-{self.slaves_end})"
        raise StuderDeviceSlaveUnknownException(msg)

    def __str__(self):
        return self.id
    
    def __repr__(self):
        return self.id
    

class NextDeviceFamilies(StuderDeviceFamilies):

    # Static known families
    TEST = NextDeviceFamily(            # Fake device to be able to test against Victron Cerbo GX
        "tst",              # id
        "Test",             # model (default) 
        100, 100,           # modbus device slaves,  start to end
        800,                # address for discovery
        None,               # Address for Model
        800,                # address for Serial number
        834,                # address for Software version
        None,               # address for ObjectModel version
    )

    SYSTEM = NextDeviceFamily(
        "sys",              # id
        "System",           # model (default) 
        1, 1,               # modbus device slaves,  start to end
        1200,               # address for discovery
        None,               # Address for Model
        None,               # address for Serial number
        None,               # address for Software version
        None,               # address for ObjectModel version
    )
    BATTERY = NextDeviceFamily(
        "bat",              # id
        "Battery",          # model (default) 
        2, 6,               # modbus device slaves,  start to end
        0,                  # address for discovery
        395,                # Address for Model
        None,               # address for Serial number
        None,               # address for Software version
        None,               # address for ObjectModel version
    )
    AC_SOURCE = NextDeviceFamily(
        "acs",              # id
        "AC Source",        # model (default) 
        7, 8,               # modbus device slaves,  start to end
        0,                  # address for discovery
        None,               # Address for Model
        None,               # address for Serial number
        None,               # address for Software version
        None,               # address for ObjectModel version
    )
    AC_FLEX_LOAD = NextDeviceFamily(
        "flx",              # id
        "AC FlexLoad",      # model (default) 
        9, 13,              # modbus device slaves,  start to end
        0,                  # address for discovery
        None,               # Address for Model
        None,               # address for Serial number
        None,               # address for Software version
        None,               # address for ObjectModel version
    )
    NEXT3 = NextDeviceFamily(
        "nx3",              # id
        "Next3",            # model (default)
        14, 28,             # modbus device slaves,  start to end
        4,                  # address for discovery
        None,               # Address for Model
        4,                  # address for Serial number
        14,                 # address for Software version
        30,                 # address for ObjectModel version
    )
    NEXT1 = NextDeviceFamily(
        "nx1",              # id
        "Next1",            # model (default)
        29, 58,             # modbus device slaves,  start to end
        4,                  # address for discovery
        None,               # Address for Model
        4,                  # address for Serial number
        14,                 # address for Software version
        30,                 # address for ObjectModel version
    )
    NEXT_GATEWAY = NextDeviceFamily(
        "nxg",              # id
        "Next Gateway",     # model (default)
        59, 60,             # modbus device slaves,  start to end
        4,                  # address for discovery
        None,               # Address for Model
        4,                  # address for Serial number
        14,                 # address for Software version
        30,                 # address for ObjectModel version
    )
    NEXT_POWERMETER = NextDeviceFamily(
        "pwr",             # id
        "Powermeter",      # model (default)
        89, 94,            # modbus device slaves,  start to end
        0,                 # address for discovery
        0,                 # Address for Model
        None,              # address for Serial number
        None,              # address for Software version
        None,              # address for ObjectModel version
    )


    def __init__(self, list: list[NextDeviceFamily]):
        super().__init__(list)

        # Fill helper variables once
        self._code_to_family_map: dict[str,NextDeviceFamily]  = {}
        self._code_to_slave_map: dict[str,int] = {}
        self._slave_to_code_map: dict[str,int] = {}

        for f in self:
            for slave in range(f.slaves_start, f.slaves_end+1):
                code = f.get_code(slave)
                
                self._code_to_family_map[code] = f
                self._code_to_slave_map[code] = slave # BAT_1-BAT_5 -> 2-6,  NEXT3_1-NEXT3_15 -> 14-28,  etc
                self._slave_to_code_map[slave] = code # 2-6 -> BAT_1-BAT_5,  14-28 -> NEXT3_1-NEXT3_15,  etc


    def get_by_id(self, id: str) -> NextDeviceFamily:
        """
        Lookup the id to find the device family
        """
        return super().get_by_id(id)


    def get_by_code(self, code: str) -> NextDeviceFamily:
        """
        Lookup the code to find the device family
        """
        return self._code_to_family_map.get(code, None)
    

    def get_by_slave(self, slave: int) -> NextDeviceFamily:
        """
        Lookup the slave to find the device family
        """
        code = self._slave_to_code_map.get(slave, None)
        return self._code_to_family_map.get(code, None)
    

    def get_slave_by_code(self, code: str) -> int:
        """
        Lookup the code to find the slave
        """
        return self._code_to_slave_map.get(code, None)


    def get_code_by_slave(self, slave: str) -> int:
        """
        Lookup the slave to find the code
        """
        return self._slave_to_code_map.get(slave, None)
