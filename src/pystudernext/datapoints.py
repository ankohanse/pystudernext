##
# Definition of all parameters / constants used in the Next protocol
##

import logging

from dataclasses import dataclass

from .const import (
    NextCategory,
    NextFormat,
    NextRW,
    NextUserLevel,
)
from .families import (
    NextDeviceFamilies,
)


_LOGGER = logging.getLogger(__name__)


class NextDatapointUnknownException(Exception):
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
    format: NextFormat = None
    read_write: str = None
    options: dict = None

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
        min = d.get('min', None)
        max = d.get('max', None)
        fmt = d.get('fmt', None)
        rw = d.get('rw', None)
        opt = d.get('opt', None)

        # Check and convert properties
        if fam is None or pid is None or addr is None or lvl is None or id is None or lbl is None or fmt is None:
            return None
        
        if type(fam) is not str or type(pid) is not str or type(lvl) is not str or type(id) is not str or type(lbl) is not str or type(fmt) is not str:
            return None

        if type(addr) is not int or type(size) is not int:
            return None

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
        default = float(dft) if (type(dft) is int or type(dft) is float) else None
        unit = unit if type(unit) is str else None
        min = float(min) if (type(min) is int or type(min) is float) else None
        max = float(max) if (type(max) is int or type(max) is float) else None
        format = NextFormat.from_str(fmt) if type(fmt) is str else None
        read_write = NextRW.from_str(rw) if type(rw) is str else None
        options = opt if type(opt) is dict else None
            
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
            format = format,
            read_write = read_write, 
            options = options
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

            
    @property
    def category(self) -> NextCategory:
        if self.read_write in [NextRW.READ]:
            return NextCategory.INFO

        if self.read_write in [NextRW.READ_WRITE, NextRW.WRITE]:
            return NextCategory.PARAMETER
            
        _LOGGER.debug(f"Unknown category for datapoint {self.nr} with level {self.level} and format {self.format}")
        return NextCategory.INFO


    def enum_value(self, key):
        if self.format not in [NextFormat.ENUM]:
            return None
        
        key = str(key)
        if not isinstance(self.options, dict) or key not in self.options:
            return key
        else:
            return self.options[key]
    
    def enum_key(self, value):
        if self.format not in [NextFormat.ENUM]:
            return None
        
        if not isinstance(self.options, dict) or value not in self.options.values():
            return None
        else:
            key = next((key for key,val in self.options.items() if val==value), None)
            return int(key)



class NextDataset:

    # Paths to all files definining the datapoints
    PATHS = [
        __file__.replace('.py', '_sys.json'),
        __file__.replace('.py', '_bat.json'),
        __file__.replace('.py', '_acs.json'),
        __file__.replace('.py', '_acf.json'),
        __file__.replace('.py', '_nx3.json'),
        __file__.replace('.py', '_nx1.json'),
        __file__.replace('.py', '_nxg.json')
    ]

    # Some known datapoint ID's
    ID_INSTALLATION_GUID = "0.1.6.2"    # family="System", address=2103


    def __init__(self, datapoints: list[NextDatapoint] | None = None):
        """
        Datapoints are read from file(s) in (Async)NextFactory.create_dataset()
        """
        self._datapoints = datapoints


    def get_by_address(self, address: int, family_id: str|None = None) -> NextDatapoint:
        for point in self._datapoints:
            if point.address == address and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(address, family_id)
    

    def get_by_id(self, id: str, family_id: str|None = None) -> NextDatapoint:
        for point in self._datapoints:
            if point.id == id and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(id, family_id)
    

    def get_by_name(self, name: str, family_id: str|None = None) -> NextDatapoint:
        for point in self._datapoints:
            if point.name == name and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(name, family_id)
    

    def get_menu_items(self, family_id:str=None, parent_id:str=""):
        datapoints = []
        for point in self._datapoints:
            if point.parent_id == parent_id and (point.family_id == family_id or family_id is None):
                datapoints.append(point)

        return datapoints
