"""
Definition of all parameters / constants used in the Next protocol
"""

import logging

from dataclasses import dataclass

from .data import (
    NextDataType,
    NextRW,
    NextUserLevel,
    NextParamException,
)
from .families import (
    NextDeviceFamilies,
    NextDeviceFamily,
)


_LOGGER = logging.getLogger(__name__)


class NextDatapointSyntaxException(Exception):
    pass

class NextDatapointUnknownException(Exception):
    pass

class NextDatapointEnumNotFoundException(Exception):
    pass


@dataclass
class NextDatapoint:
    family_id: str
    parent_id: str
    address: int
    size: int
    level_r: NextUserLevel
    level_w: NextUserLevel
    id: int
    label: str
    name: str = None
    default: float|str = None
    unit: str = None
    min: float = None
    max: float = None
    data_type: NextDataType = None
    read_write: NextRW = None
    enum_id: str = None
    enum_options: dict[str,str] = None

    @staticmethod
    def from_dict(d):
        fam = d.get('fam', None)
        pid = d.get('pid', None)
        addr  = d.get('addr', None)
        size = d.get('size', None)
        lvl = d.get('lvl', None)
        id = d.get('id', None)
        lbl = d.get('lbl', None)
        dft = d.get('def', None)
        unit = d.get('unit', None)
        rng = d.get('rng', None)
        dt = d.get('type', None)
        rw = d.get('rw', None)
        eid = d.get('enum_id', None)
        opt = d.get('opt', None)

        # Check and convert properties
        if "_rem" in d and len(d)==1:
            return None # Line only contains a comment
        
        if fam is None or pid is None or addr is None or lvl is None or id is None or lbl is None or dt is None:
            raise NextDatapointSyntaxException(f"Missing required field in dataset; fam={fam}, pid={pid}, addr={addr}")
        
        if not isinstance(fam, str) or not isinstance(pid, str) or not isinstance(lvl, str) or not isinstance(id, str) or not isinstance(lbl, str) or not isinstance(dt, str):
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset, expected str; fam={fam}, pid={pid}, addr={addr}")

        if not isinstance(addr, int) or not isinstance(size, int):
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset, expected int; fam={fam}, pid={pid}, addr={addr}")

        if rng is not None and not isinstance(rng, list) and len(rng)!=2:
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset, expected list[min,max]; fam={fam}, pid={pid}, addr={addr}")
        
        if eid is not None and not isinstance(eid, str):
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset, expected str; fam={fam}, pid={pid}, addr={addr}")

        if dt in ['bitfield','enum'] and eid is None:
            raise NextDatapointSyntaxException(f"Missing required field 'enum_id' in dataset; fam={fam}, pid={pid}, addr={addr}")
        
        if opt is not None and not isinstance(opt, dict):
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset, expected dict; fam={fam}, pid={pid}, addr={addr}")

        # lvl might be split into a read and write part
        lvl_parts = lvl.split('/', maxsplit=1) if '/' in lvl else [lvl, lvl]

        # Compose the Datapoint
        family_id = fam
        parent_id = pid
        address = addr
        size = size
        level_r = NextUserLevel.from_str(lvl_parts[0])
        level_w = NextUserLevel.from_str(lvl_parts[1])
        id = '.'.join(filter(None, [pid,id]))
        label = lbl.strip()
        default = float(dft) if isinstance(dft, (int,float)) else None
        unit = unit if isinstance(unit, str) else None
        min = float(rng[0]) if isinstance(rng, list) else None
        max = float(rng[1]) if isinstance(rng, list) else None
        data_type = NextDataType.from_str(dt) if isinstance(dt, str) else None
        read_write = NextRW.from_str(rw) if isinstance(rw, str) else None
        enum_id = eid if isinstance(eid, str) else None
            
        return NextDatapoint(
            family_id = family_id, 
            parent_id = parent_id, 
            address = address, 
            size = size, 
            level_r = level_r, 
            level_w = level_w,
            id = id, 
            label = label,
            name = None,    # Will be resolved later as it needs label from parent
            default = default, 
            unit = unit, 
            min = min, 
            max = max, 
            data_type = data_type,
            read_write = read_write, 
            enum_id = enum_id,
            enum_options = None,  # will be resolved later from associated json file
        )


    @property
    def userlevel(self, action_rw:NextRW):
        """
        Check if this datapoint can be read and/or written
        """
        match action_rw:
            case NextRW.READ:
                if self.read_write not in [NextRW.READ, NextRW.READ_WRITE]:
                    return NextUserLevel.DENIED
                else:
                    return self.level_r

            case NextRW.WRITE:
                if self.read_write not in [NextRW.WRITE, NextRW.READ_WRITE]:
                    return NextUserLevel.DENIED
                else:
                    return self.level_w

            case NextRW.READ_WRITE:
                if self.read_write not in [NextRW.READ_WRITE]:
                    return NextUserLevel.DENIED
                else:
                    return self.level_w

            
    def enum_value(self, key):
        if self.data_type not in [NextDataType.ENUM, NextDataType.BITFIELD]:
            return None
        
        key = str(key)
        if not isinstance(self.enum_options, dict) or key not in self.enum_options:
            return key
        else:
            return self.enum_options[key]
    
    def enum_key(self, value):
        if self.data_type not in [NextDataType.ENUM, NextDataType.BITFIELD]:
            return None
        
        if not isinstance(self.enum_options, dict) or value not in self.enum_options.values():
            return None
        else:
            key = next((key for key,val in self.enum_options.items() if val==value), None)
            return int(key)


@dataclass
class NextDatapointEnum:
    enum_id: str
    options: dict = None

    @staticmethod
    def from_dict(d):
        enum_id = d.get('enum_id', None)
        options = d.get('options', None)

        # Check and convert properties
        if "_rem" in d and len(d)==1:
            return None # Line only contains a comment
        
        if enum_id is None or options is None:
            raise NextDatapointSyntaxException(f"Missing required field in dataset; enum_id={enum_id}")
        
        if not isinstance(enum_id, str) or not isinstance(options, dict):
            raise NextDatapointSyntaxException(f"Unexpected field type in dataset; enum_id={enum_id}")

        # Compose the DatapointEnum
        return NextDatapointEnum(
            enum_id = enum_id, 
            options = options
        )


class NextDataset:

    # Paths to all files definining the datapoints
    PATHS = [
        (__file__.replace('.py', '_sys.json'), __file__.replace('.py', '_sys_enums.json') ), 
        (__file__.replace('.py', '_bat.json'), __file__.replace('.py', '_bat_enums.json') ), 
        (__file__.replace('.py', '_acs.json'), __file__.replace('.py', '_acs_enums.json') ), 
        (__file__.replace('.py', '_flx.json'), __file__.replace('.py', '_flx_enums.json') ), 
        (__file__.replace('.py', '_nx3.json'), __file__.replace('.py', '_nx3_enums.json') ), 
        (__file__.replace('.py', '_nx1.json'), __file__.replace('.py', '_nx1_enums.json') ), 
        (__file__.replace('.py', '_nxg.json'), __file__.replace('.py', '_nxg_enums.json') ), 
        (__file__.replace('.py', '_pwr.json'), __file__.replace('.py', '_pwr_enums.json') ), 

        # To be able to develop this library without access to a Studer Next device...
        (__file__.replace('.py', '_tst.json'), __file__.replace('.py', '_tst_enums.json') ),       
    ]

    # Some known datapoint ID's
    ID_INSTALLATION_GUID = "0.1.6.2"    # family="System", address=2103


    def __init__(self, datapoints: list[NextDatapoint] | None = None):
        """
        Datapoints are read from file(s) in (Async)NextFactory.create_dataset()
        """
        self._datapoints = datapoints


    def get_by_address(self, address: int, family: NextDeviceFamily|str) -> NextDatapoint:

        # Sanity check
        if address is None:
            raise NextParamException(f"Parameter 'address' must be provided in call to get_by_address")
            
        if isinstance(family, NextDeviceFamily):
            family_id = family.id
        elif isinstance(family, str):  
            family_id = family
        else:
            raise NextParamException(f"Family parameter must be a NextDeviceFamilies or a family id in call to get_by_address")

        # Now lookup the datapoint
        for point in self._datapoints:
            if point.address == address and point.family_id == family_id:
                return point

        raise NextDatapointUnknownException(address, family_id)
    

    def get_by_id(self, id: str, family: NextDeviceFamily|str|None = None) -> NextDatapoint:

        # Sanity check
        if id is None:
            raise NextParamException(f"Parameter 'id' must be provided in call to get_by_id")
            
        if isinstance(family, NextDeviceFamily):
            family_id = family.id
        elif isinstance(family, str):  
            family_id = family
        else:
            family_id = None

        # Now lookup the datapoint
        for point in self._datapoints:
            if point.id == id and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(id, family_id)
    

    def get_menu_items(self, family: NextDeviceFamily|str|None=None, parent_id:str=""):

        # Sanity check
        if isinstance(family, NextDeviceFamily):
            family_id = family.id
        elif isinstance(family, str):  
            family_id = family
        else:
            family_id = None

        # Now lookup the datapoints
        datapoints = []
        for point in self._datapoints:
            if point.parent_id == parent_id and (point.family_id == family_id or family_id is None):
                datapoints.append(point)

        return datapoints
