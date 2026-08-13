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
    parent: int | None
    addr: int
    size: int | None
    level_r: NextUserLevel | None
    level_w: NextUserLevel | None
    id: int | None
    label: str
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
        par = d.get('par', None)
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
        if not fam or not addr or not lvl or not lbl or not fmt:
            return None
        
        if type(par) is not int:
            return None

        if type(addr) is not int:
            return None

        # lvl might be split into a read and write part
        lvl_parts = lvl.split('/', maxsplit=1) if '/' in lvl else [lvl, lvl]

        # Compose the Datapoint
        family_id = str(fam)
        parent = int(par)
        addr = int(addr)
        size = int(size)
        level_r = NextUserLevel.from_str(lvl_parts[0])
        level_w = NextUserLevel.from_str(lvl_parts[1])
        id = str(id) if id is not None else None
        label = str(lbl).strip()
        default = float(dft) if (type(dft) is int or type(dft) is float) else None
        unit = unit if type(unit) is str else None
        min = float(min) if (type(min) is int or type(min) is float) else None
        max = float(max) if (type(max) is int or type(max) is float) else None
        format = NextFormat.from_str(fmt) if type(fmt) is str else None
        read_write = NextRW.from_str(rw) if type(rw) is str else None
        options = opt if type(opt) is dict else None
            
        return NextDatapoint(family_id, parent, addr, size, level_r, level_w, id, label, default, unit, min, max, format, read_write, options)

    @property
    def name(self):
        """Label is not unique enough within a device; i.e. Aux1 and Aux2 both have a datapoint 'position'"""
        # TODO lookup parent and use its label as prefix
        parent = None
        if parent is not None:
            return parent.label + " " + self.label
        else:
            return self.label


    @property
    def userlevel(self, action_rw:NextRW):
        # First check if this datapoint can be read and/or written
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

    PATHS = [
        __file__.replace('.py', '_sys.json'),
        __file__.replace('.py', '_bat.json'),
        __file__.replace('.py', '_acs.json'),
        __file__.replace('.py', '_acf.json'),
        __file__.replace('.py', '_nx3.json'),
        __file__.replace('.py', '_nx1.json'),
        __file__.replace('.py', '_nxg.json')
    ]

    def __init__(self, datapoints: list[NextDatapoint] | None = None):
        self._datapoints = datapoints


    def get_by_addr(self, addr: int, family_id: str|None = None) -> NextDatapoint:
        for point in self._datapoints:
            if point.addr == addr and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(addr, family_id)
    

    def get_by_name(self, name: str, family_id: str|None = None) -> NextDatapoint:
        for point in self._datapoints:
            if point.name == name and (point.family_id == family_id or family_id is None):
                return point

        raise NextDatapointUnknownException(name, family_id)
    

    def get_menu_items(self, parent: int = 0, family_id: str|None = None):
        datapoints = []
        for point in self._datapoints:
            if point.parent == parent and (point.family_id == family_id or family_id is None):
                datapoints.append(point)

        return datapoints
