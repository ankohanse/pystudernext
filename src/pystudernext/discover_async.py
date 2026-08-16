"""xcom_api.py: communication api to Studer Next via LAN."""

import asyncio
import httpx
import ipaddress
import logging
import os
import struct

from dataclasses import dataclass

from .api_async import (
    AsyncNextApi,
)
#from .api_sync import (
#    NextApi,
#)
from .const import (
    NextDiscoverNotConnected,
)
from .data import (
    NextDiscoveredDevice,
    NextDiscoveredGateway,
)
from .datapoints import (
    NextDatapoint,
    NextDataset,
    NextDatapointUnknownException,
)
from .families import (
    NextDeviceFamilies
)

_LOGGER = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class AsyncNextDiscover:

    def __init__(self, api: AsyncNextApi, dataset: NextDataset):
        """
        We connect to the NX Gateway.
        Once it is connected we can send package requests.
        """
        self._api = api
        self._dataset = dataset


    async def discover_devices(self, getExtendedInfo = False, verbose = False) -> list[NextDiscoveredDevice]:
        """
        Discover which Studer devices can be reached via the Next client
        """
        devices: list[NextDiscoveredDevice] = []

        # Sanity check
        if not self._api.connected:
            raise NextDiscoverNotConnected("NextApi is not connected to remote NX Gateway; please connect first.")
        
        # Check presence of devices for each family
        for family in NextDeviceFamilies.get_list():

            _LOGGER.info(f"Trying family {family.id} ({family.model})")

            # Get value for the specific discovery address
            if family.address_discover is None:
                continue

            # Iterate all slaves in the family, up to the first slave that is not found
            for device_slave in range(family.slaves_start, family.slaves_end+1):

                device_code = family.get_code(device_slave)

                # Have we already discovered a device for this address?
                device_found = next((d for d in devices if d.slave == device_slave), None)
                if device_found is not None:
                    # Do not test further device addresses in this family
                    _LOGGER.info(f"  Skip device {device_code}; already found device {device_found.code}")
                    break

                # Send the test request to the device. This will return None in case:
                # - the device does not exist (DEVICE_NOT_FOUND)
                # - the device does not support the param (INVALID_DATA), used to distinguish BSP from BMS
                try:
                    address_discover = family.address_discover
                    param_discover = self._dataset.get_by_address(address_discover, family.id)

                    _LOGGER.info(f"Trying device {device_code} (slave {device_slave}) for address {address_discover}")

                    value = await self._api.request_value(param_discover, device_slave, verbose=verbose)
                    if value is not None:
                        _LOGGER.info(f"  Found device {device_code}")

                        device = NextDiscoveredDevice(device_code, device_slave, family.id, family.model)
                        if getExtendedInfo:
                            device = await self.get_extended_device_info(device, verbose=verbose)
                        
                        devices.append(device)

                    else:
                        _LOGGER.info(f"  No device {device_code}; no value returned from NX Gateway")

                except Exception as e:
                    _LOGGER.info(f"  No device {device_code}; no value returned from NX Gateway: {e}")

                    # Do not test further device addresses in this family
                    break

        return devices


    async def get_extended_device_info(self, device: NextDiscoveredDevice, verbose=False) -> NextDiscoveredDevice:
        """
        Rough code taken from pystuderxcom.
        Still needs to have appropriate datapoint names set.
        """
        # ID type
        # ID HW
        # ID HW PWR
        # ID SOFT msb/lsb
        # ID SID
        try:
            _LOGGER.info(f"Trying to get extended device info for device {device.code})")
            family = NextDeviceFamilies.get_by_id(device.family_id)

            param_serial     = self._dataset.get_by_address(family.address_serial,     family.id) if family.address_serial is not None else None
            param_sw_version = self._dataset.get_by_address(family.address_sw_version, family.id) if family.address_sw_version is not None else None
            param_om_version = self._dataset.get_by_address(family.address_om_version, family.id) if family.address_om_version is not None else None

            value_serial     = await self._api.request_value(param_serial,     device.slave, verbose=verbose)
            value_sw_version = await self._api.request_value(param_sw_version, device.slave, verbose=verbose)
            value_om_version = await self._api.request_value(param_om_version, device.slave, verbose=verbose)

            device.serial       = value_serial # String
            device.sw_version   = self._decode_sw_version(value_sw_version) # Major.Middle.Minor.Patch
            device.om_version   = self._decode_om_version(value_om_version) # Major.Minor

            _LOGGER.info(f"  Found extended device info: Serial: {device.serial}, Software version: {device.sw_version}, ObjectModel version: {device.om_version}")

        except Exception as e:
            _LOGGER.warning(f"  Exception in getExtendedDeviceInfo: {e}")

        return device


    def _decode_sw_version(self, val):
        """
        Decode a 4 byte uint into a major.middle.minor.patch version number
        """
        if val is None:
            return None
        
        bytes = struct.pack(">H", int(val))
        return f"{int(bytes[0])}.{int(bytes[1])}.{int(bytes[2])}.{int(bytes[3])}"


    def _decode_om_version(self, val):
        """
        Decode a 4 byte uint into a major.minor version number
        """
        if val is None:
            return None
        
        bytes = struct.pack(">H", int(val))
        return f"{int.from_bytes(bytes[0:2], byteorder='big')}.{int.from_bytes(bytes[2:4], byteorder='big')}"


    async def discover_gateway_info(self, verbose=False) -> NextDiscoveredGateway:
        """
        Discover extended info about the remote NX Gateway we're connected to
        """

        # Sanity checks
        if not self._api.connected:
            raise NextDiscoverNotConnected("NextApi is not connected to remote NX Gateway; please connect first.")

        if not self._api.remote_ip:
            raise NextDiscoverNotConnected("No IP address was detected for the remote NX Gateway")

        _LOGGER.info(f"Trying to get gateway info")
        gateway_ip = None
        gateway_port = None
        gateway_guid = None

        try:
            gateway_ip = str(ipaddress.ip_address(self._api.remote_ip))
            gateway_port = self._api.remote_port

            _LOGGER.info(f"  Found ip: {gateway_ip}, port: {gateway_port}")

        except Exception as e:
            _LOGGER.warning(f"  Exception in discoverClientInfo: {e}")

        try:
            param = self._dataset.get_by_address(NextDataset.ID_INSTALLATION_GUID)
            gateway_guid = await self._api.request_value(param, NextDeviceFamilies.SYSTEM.slaves_start, verbose)

            _LOGGER.info(f"  Found guid: {gateway_guid}")

        except Exception as e:
            _LOGGER.warning(f"  Exception in discover_gateway_info: {e}")

        return NextDiscoveredGateway(
            ip = gateway_ip,
            port = gateway_port,
            guid = gateway_guid,
        )


    @staticmethod
    async def discover_gateway_webconfig(hint: str = None) -> str:
        """
        Discover if NX Gateway Config page can be found on the local network
        """

        # Find all device IP addresses to check
        urls: list[str] = [hint] if hint else []
        urls.append("http://192.168.127.254")   # default if using static address

        for line in os.popen('arp -a'):     # arp seems to be available on Linux, Windows and Pi
            try:
                # Linux:  
                #   ? (192.168.88.250) at 00:90:e8:3c:f8:7e [ether] on end0
                #   ...
                # Windows: 
                #   Interface: 192.168.88.100 --- 0x4
                #     Internet Address      Physical Address      Type
                #     192.168.88.250        00-90-e8-3c-f8-7e     dynamic 
                #     ...
                
                device = line.strip('?').split()[0].strip('()')
                ip = ipaddress.ip_address(device)
                urls.append(f"http://{str(ip)}")
            except:
                pass

        # Define helper function to check for Moxa Web Config page
        async def check_url(client:httpx.AsyncClient, url:str) -> str|None:
            _LOGGER.info(f"Trying {url}")
            try:
                rsp = await client.get(url)
                if rsp and rsp.is_success and rsp.headers.get("Server", "").startswith("Studer"):
                    return url
                else:
                    return None
            except:
                return None

        # Parallel check for NX Gateway Config page on all found device url's
        # No need to SSL verify plain HTTP GET calls, this also keeps Home Assistant happy
        async with httpx.AsyncClient(verify=False) as client:
            async with asyncio.TaskGroup() as task_group:
                tasks = [task_group.create_task(check_url(client, url)) for url in urls]

                # Start checking completed tasks immediately. Cancel remaining tasks if our url was found
                for task in asyncio.as_completed(tasks):
                    url = task.result() if hasattr(task, 'result') and callable(task.result) else await task
                    if url is not None:
                        for t in tasks:
                            t.cancel()

                        return url
                     
        return None
    
