"""
Definition of all parameters / constants used in the Next protocol
"""

import logging
import orjson

from aiofiles import open as aiofiles_open
from dataclasses import dataclass
from enum import StrEnum

from .shared.helpers import (
    HybridLock,
)
from .shared.studer_dataset import (
    StuderDatapoint,
    StuderDatapointEnumNotFoundException,
    StuderDatapointSyntaxException,
    StuderDataset,
)
from .shared.studer_types import (
    StuderAccess,
    StuderDataType,
    StuderTarget,
)
from .data import (
    NextUserLevel,
)
from .families import (
    NextDeviceFamilies,
)


_LOGGER = logging.getLogger(__name__)


@dataclass
class NextDatapoint(StuderDatapoint):

    @staticmethod
    def from_dict(d) -> StuderDatapoint:
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
            raise StuderDatapointSyntaxException(f"Missing required field in dataset; fam={fam}, pid={pid}, addr={addr}")
        
        if not isinstance(fam, str) or not isinstance(pid, str) or not isinstance(lvl, str) or not isinstance(id, str) or not isinstance(lbl, str) or not isinstance(dt, str):
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset, expected str; fam={fam}, pid={pid}, addr={addr}")

        if not isinstance(addr, int) or not isinstance(size, int):
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset, expected int; fam={fam}, pid={pid}, addr={addr}")

        if rng is not None and not isinstance(rng, list) and len(rng)!=2:
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset, expected list[min,max]; fam={fam}, pid={pid}, addr={addr}")
        
        if eid is not None and not isinstance(eid, str):
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset, expected str; fam={fam}, pid={pid}, addr={addr}")

        if dt in ['bitfield','enum'] and eid is None:
            raise StuderDatapointSyntaxException(f"Missing required field 'enum_id' in dataset; fam={fam}, pid={pid}, addr={addr}")
        
        if opt is not None and not isinstance(opt, dict):
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset, expected dict; fam={fam}, pid={pid}, addr={addr}")

        # lvl might be split into a read and write part
        lvl_parts = lvl.split('/', maxsplit=1) if '/' in lvl else [lvl, lvl]

        # Compose the Datapoint
        family_id = fam
        parent_id = pid
        id = '.'.join(filter(None, [pid,id]))
        userlevel_r = NextUserLevel.from_str(lvl_parts[0])
        userlevel_w = NextUserLevel.from_str(lvl_parts[1])
        address = addr
        label = lbl.strip()
        unit = unit if isinstance(unit, str) else None
        data_type = NextDatapoint._resolve_datatype(dt) if isinstance(dt, str) else None
        size = size
        access = NextDatapoint._resolve_access(rw) if isinstance(rw, str) else None
        default = float(dft) if isinstance(dft, (int,float)) else None
        min = float(rng[0]) if isinstance(rng, list) else None
        max = float(rng[1]) if isinstance(rng, list) else None
        enum_id = eid if isinstance(eid, str) else None
            
        return StuderDatapoint(
            family_id = family_id, 
            parent_id = parent_id, 
            id = id, 
            userlevel_r = userlevel_r, 
            userlevel_w = userlevel_w,
            nr_or_addr = address, 
            name = None,    # Will be resolved later as it needs label from parent
            label = label,
            unit = unit, 
            data_type = data_type,
            size = size, 
            access = access,
            target = StuderTarget.STANDARD,
            default = default, 
            min = min, 
            max = max, 
            inc = None,
            enum_id = enum_id,
            enum_options = None,  # will be resolved later from associated json file
        )


    @classmethod
    def _resolve_access(cls, s:str) -> StuderAccess:
        match s.upper():
            case 'R': return StuderAccess.READ
            case 'W': return StuderAccess.WRITE
            case 'R/W': return StuderAccess.READ_WRITE
            case _: 
                raise Exception(f"Unknown read-write flag: '{s}'")


    @classmethod
    def _resolve_datatype(cls, s: str, default: StuderDataType = None) -> StuderDataType:
        match s.lower():
            case 'bool': return StuderDataType.BOOL
            case 'signal': return StuderDataType.SIGNAL
            case 'int16': return StuderDataType.INT16
            case 'uint16': return StuderDataType.UINT16
            case 'enum16': return StuderDataType.ENUM16
            case 'int32' | 'int': return StuderDataType.INT32
            case 'uint32' | 'uint': return StuderDataType.UINT32
            case 'float': return StuderDataType.FLOAT32
            case 'enum': return StuderDataType.ENUM32
            case 'bitfield': return StuderDataType.BITFIELD
            case 'int64': return StuderDataType.INT64
            case 'uint64': return StuderDataType.UINT64
            case 'float64': return StuderDataType.FLOAT64
            case 'string': return StuderDataType.STRING
            case 'menu': return StuderDataType.MENU
            case 'not supported': return StuderDataType.INVALID
            case _: 
                if default is not None:
                    return default
                else:
                    raise Exception(f"Unknown data-type: '{s}'")
                               

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
            raise StuderDatapointSyntaxException(f"Missing required field in dataset; enum_id={enum_id}")
        
        if not isinstance(enum_id, str) or not isinstance(options, dict):
            raise StuderDatapointSyntaxException(f"Unexpected field type in dataset; enum_id={enum_id}")

        # Compose the DatapointEnum
        return NextDatapointEnum(
            enum_id = enum_id, 
            options = options
        )


class NextDatasetFlag(StrEnum):
    """Extra flags to pass to Api"""
    ADD_TEST     = "add_test"       # bool


class NextDataset(StuderDataset):

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


    def __init__(self):
        raise RuntimeError("Use 'NextDataset.get_instance()' or 'await NextDataset.async_get_instance()' instead of direct instantiation.")

    # Single instance of the NextDataset
    _instance = None
    _instance_lock = HybridLock()

    @classmethod
    async def async_get_instance(cls, flags:dict=None) -> 'NextDataset':
        """
        Async helper function to get singleton instance of NextDataset
        """
        async with cls._instance_lock:
            if cls._instance is None:
                # Create a bare instance without calling __init__
                self = super().__new__(cls)
                await self._async_init(flags)
                cls._instance = self

        return cls._instance

    @classmethod
    def get_instance(cls, flags:dict=None) -> 'NextDataset':
        """
        Sync helper function to get singleton instance of NextDataset
        """
        with cls._instance_lock:
            if cls._instance is None:
                # Create a bare instance without calling __init__
                self = super().__new__(cls)
                self._init(flags)
                cls._instance = self
            
        return cls._instance

    @classmethod
    def del_instance(cls):
        """Used for intermediate cleanup during unit tests"""
        cls._instance = None


    async def _async_init(self, flags:dict=None):
        """
        Perform the actual async initialization
        """
        datapoints = list()
        flags = flags or {}
        add_test = flags.get(NextDatasetFlag.ADD_TEST, False)

        for (item_path, enum_path) in NextDataset.PATHS:

            # Normally we skip the test family
            if not add_test and 'tst' in item_path:
                continue

            async with aiofiles_open(item_path, "r", encoding="UTF-8") as item_file:
                item_text = await item_file.read()

            async with aiofiles_open(enum_path, "r", encoding="UTF-8") as enum_file:
                enum_text = await enum_file.read()

            item_values = orjson.loads(item_text)
            enum_values = orjson.loads(enum_text)

            # Merge the datapoints from this file
            datapoints += self._get_datapoints_from_values(item_values, enum_values)

        _LOGGER.info(f"Using {len(datapoints)} datapoints")

        families = await NextDeviceFamilies.async_get_instance() # singleton instance
        super().__init__(datapoints, families)


    def _init(self, flags:dict=None):
        """
        Perform the actual async initialization
        """
        datapoints = list()
        flags = flags or {}
        add_test = flags.get(NextDatasetFlag.ADD_TEST, False)

        for (item_path, enum_path) in NextDataset.PATHS:

            # Normally we skip the test family
            if not add_test and 'tst' in item_path:
                continue

            with open(item_path, "r", encoding="UTF-8") as item_file:
                item_text = item_file.read()

            with open(enum_path, "r", encoding="UTF-8") as enum_file:
                enum_text = enum_file.read()

            item_values = orjson.loads(item_text)
            enum_values = orjson.loads(enum_text)

            # Merge the datapoints from this file
            datapoints += self._get_datapoints_from_values(item_values, enum_values)

        _LOGGER.info(f"Using {len(datapoints)} datapoints")

        families = NextDeviceFamilies.get_instance() # singleton instance
        super().__init__(datapoints, families)


    def _get_datapoints_from_values(self, item_values: dict, enum_values: dict):
        """
        """
        item_datapoints = list(filter(None, [NextDatapoint.from_dict(val) for val in item_values]))
        item_enums = list(filter(None, [NextDatapointEnum.from_dict(val) for val in enum_values]))

        dp_parent = None
        for dp in item_datapoints:
            # Resolve Name for each datapoint. It is composed of the parent label and the datapoint label.
            # Datapoints are clustered with ones sharing the same parent next to each other.
            # Therefore we often do not need to search the entire set for the parent but can use the last used one.
            if dp_parent is None or dp_parent.id != dp.parent_id:
                # Resolve next parent. Should be in the same file.
                dp_parent = next( (d for d in item_datapoints if d.id==dp.parent_id), None)

            dp.name = dp_parent.name + ' - ' + dp.label if dp_parent is not None else dp.label

            # Resolve enum options for each datapoint (if needed).
            if dp.enum_id is not None:
                enum_id = f"{dp.parent_id}.enum{dp.enum_id}"
                enum_def = next( (e for e in item_enums if e.enum_id==enum_id), None)
                if enum_def is None:
                    raise StuderDatapointEnumNotFoundException(f"Missing definition for enum {dp.enum_id}; fam={dp.family_id}, pid={dp.parent_id}, addr={dp.address}")

                dp.enum_options = enum_def.options

        return item_datapoints

