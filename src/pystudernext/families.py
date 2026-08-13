##
# Definition of all known device families used in the Next protocol
##

import logging

from dataclasses import dataclass


_LOGGER = logging.getLogger(__name__)


class NextDeviceFamilyUnknownException(Exception):
    pass

class NextDeviceCodeUnknownException(Exception):
    pass

class NextDeviceSlaveUnknownException(Exception):
    pass
    
@dataclass
class NextDeviceFamily:
    id: str
    model: str
    slaves_start: int
    slaves_end: int
    address_discover: int

    def get_code(self, slave):
        if self.slaves_start == slave == self.slaves_end:
            return self.id.upper()
        
        if self.slaves_start <= slave <= self.slaves_end:
            idx = slave - self.slaves_start + 1
            return f"{self.id.upper()}_{idx}"
        
        msg = f"Slave {slave} is not in range for family {self.id} ({self.slaves_start}-{self.slaves_end})"
        raise NextDeviceSlaveUnknownException(msg)


class NextDeviceFamilies:
    SYSTEM = NextDeviceFamily(
        "sys",              # id
        "System",           # model 
        1, 1,               # modbus device slaves,  start to end
        2103,               # address for discovery
    )
    BATTERY = NextDeviceFamily(
        "bat",              # id
        "Battery",          # model 
        2, 6,               # modbus device slaves,  start to end
        318,                # address for discovery
    )
    AC_SOURCE = NextDeviceFamily(
        "acs",              # id
        "AcSource",         # model 
        7, 8,               # modbus device slaves,  start to end
        2,                  # nr for discovery
    )
    AC_FLEX_LOAD = NextDeviceFamily(
        "acf",              # id
        "AcFlexLoad",       # model 
        9, 13,              # modbus device slaves,  start to end
        0,                  # address for discovery
    )
    NEXT3 = NextDeviceFamily(
        "nx3",              # id
        "Next3",            # model 
        14, 28,             # modbus device slaves,  start to end
        4,                  # address for discovery
    )
    NEXT1 = NextDeviceFamily(
        "nx1",              # id
        "Next1",            # model 
        29, 58,             # modbus device slaves,  start to end
        4,                  # address for discovery
    )
    NEXT_GATEWAY = NextDeviceFamily(
        "nxg",              # id
        "NextGateway",      # model 
        59, 60,             # modbus device slaves,  start to end
        4,                  # address for discovery
    )


    @staticmethod
    def get_by_id(id: str) -> NextDeviceFamily:
        for f in NextDeviceFamilies.get_list():
            if id == f.id:
                return f

        raise NextDeviceFamilyUnknownException(id)


    @staticmethod
    def get_list() -> list[NextDeviceFamily]:
        return [val for val in NextDeviceFamilies.__dict__.values() if type(val) is NextDeviceFamily]


    # Static variables to cache helper mappings
    _code_to_family_map: dict[str,NextDeviceFamily] = None
    _code_to_slave_map: dict[str,int] = None
    _slave_to_code_map: dict[str,int] = None

    @staticmethod
    def _build_static_maps():
        """Fill static variable once"""
        if NextDeviceFamilies._code_to_family_map is None:

            NextDeviceFamilies._code_to_family_map = {}
            NextDeviceFamilies._code_to_slave_map = {}
            NextDeviceFamilies._slave_to_code_map = {}

            for f in NextDeviceFamilies.get_list():
                for slave in range(f.slaves_start, f.slaves_end+1):
                    code = f.get_code(slave)
                    
                    NextDeviceFamilies._code_to_family_map[code] = f
                    NextDeviceFamilies._code_to_slave_map[code] = slave # BAT_1-BAT_5 -> 2-6,  NEXT3_1-NEXT3_15 -> 14-28,  etc
                    NextDeviceFamilies._slave_to_code_map[slave] = code # 2-6 -> BAT_1-BAT_5,  14-28 -> NEXT3_1-NEXT3_15,  etc


    @staticmethod
    def get_by_code(code: str) -> NextDeviceFamily:
        """
        Lookup the code to find the device family
        """
        NextDeviceFamilies._build_static_maps()

        return  NextDeviceFamilies._code_to_family_map.get(code, None)
    

    @staticmethod
    def get_slave_by_code(code: str) -> int:
        """
        Lookup the code to find the addr
        """
        NextDeviceFamilies._build_static_maps()

        return NextDeviceFamilies._code_to_slave_map.get(code, None)


    @staticmethod
    def get_code_by_slave(addr: str) -> int:
        """
        Lookup the code to find the addr
        """
        NextDeviceFamilies._build_static_maps()

        return NextDeviceFamilies._slave_to_code_map.get(addr, None)
