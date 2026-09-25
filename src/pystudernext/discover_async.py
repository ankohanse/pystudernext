"""
Discover Next Gateway and Next Devices
"""

import asyncio
import re
import httpx
import logging
import struct

from ipaddress import IPv4Address, IPv6Address
from dataclasses import dataclass

from .shared.helpers import StuderNetworkHelper
from .shared.studer_interfaces_async import AsyncStuderDiscover
from .shared.studer_interfaces_sync import StuderDiscover
from .shared.studer_dataset import StuderDataset, StuderDatapoint, StuderDatapointUnknownException, StuderDatapointSyntaxException
from .shared.studer_types import StuderDataType, StuderDiscoveredDevice, StuderDiscoveredGateway, StuderDiscoverNotConnected
from .api_async import AsyncNextApi
from .api_sync import NextApi
from .datapoints import NextDatapoint, NextDataset
from .families import NextDeviceFamilies

_LOGGER = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class AsyncNextDiscover(AsyncStuderDiscover):

    def __init__(self, api: AsyncNextApi, dataset: StuderDataset):
        """
        We connect to the NX Gateway.
        Once it is connected we can send package requests.
        """
        self._api = api
        self._dataset = dataset
        self._families = NextDeviceFamilies.get_instance()   # singleton instance


    async def discover_devices(self, getExtendedInfo = False, verbose = False) -> list[StuderDiscoveredDevice]:
        """
        Discover which Studer devices can be reached via the Next client
        """
        devices: list[StuderDiscoveredDevice] = []

        # Sanity check
        if not self._api.connected:
            raise StuderDiscoverNotConnected("NextApi is not connected to remote NX Gateway; please connect first.")
        
        # Check presence of devices for each family
        for family in self._families:

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
                    param_discover = self._dataset.get_by_address(address_discover, family)

                    _LOGGER.info(f"Trying device {device_code} (slave {device_slave}) for address {address_discover}")

                    value = await self._api.request_value(param_discover, device_slave, verbose=verbose)
                    if value is not None:
                        _LOGGER.info(f"  Found device {device_code}")

                        device = StuderDiscoveredDevice(device_code, device_slave, family.id, family.model)
                        if getExtendedInfo:
                            device = await self.get_extended_device_info(device, verbose=verbose)
                        
                        devices.append(device)

                    else:
                        _LOGGER.info(f"  No device {device_code}; no value returned from Next Gateway")
                        break # Do not test further device addresses in this family

                except Exception as e:
                    _LOGGER.info(f"  No device {device_code}; no value returned from Next Gateway: {e}")
                    break # Do not test further device addresses in this family

        return devices


    async def get_extended_device_info(self, device: StuderDiscoveredDevice, verbose=False) -> StuderDiscoveredDevice:
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
            family = self._families.get_by_id(device.family_id)

            param_model      = self._dataset.get_by_address(family.address_model,      family) if family.address_model is not None else None
            param_serial     = self._dataset.get_by_address(family.address_serial,     family) if family.address_serial is not None else None
            param_sw_version = self._dataset.get_by_address(family.address_sw_version, family) if family.address_sw_version is not None else None
            param_om_version = self._dataset.get_by_address(family.address_om_version, family) if family.address_om_version is not None else None

            value_model      = await self._api.request_value(param_model,      device.slave, verbose=verbose)
            value_serial     = await self._api.request_value(param_serial,     device.slave, verbose=verbose)
            value_sw_version = await self._api.request_value(param_sw_version, device.slave, verbose=verbose)
            value_om_version = await self._api.request_value(param_om_version, device.slave, verbose=verbose)

            device.model        = str(value_model) if value_model is not None else None
            device.serial       = str(value_serial) if value_serial is not None else None
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

        bytes = struct.pack(">I", int(val))
        return f"{int(bytes[0])}.{int(bytes[1])}.{int(bytes[2])}.{int(bytes[3])}"


    def _decode_om_version(self, val):
        """
        Decode a 4 byte uint into a major.minor version number
        """
        if val is None:
            return None
        
        bytes = struct.pack(">I", int(val))
        return f"{int.from_bytes(bytes[0:2], byteorder='big')}.{int.from_bytes(bytes[2:4], byteorder='big')}"


    async def discover_gateway_info(self, verbose=False) -> StuderDiscoveredGateway:
        """
        Discover extended info about the remote NX Gateway we're connected to
        """

        # Sanity checks
        if not self._api.connected:
            raise StuderDiscoverNotConnected("NextApi is not connected to remote NX Gateway; please connect first.")

        if not self._api.remote_host:
            raise StuderDiscoverNotConnected("No IP address was detected for the remote NX Gateway")

        _LOGGER.info(f"Trying to get gateway info")
        gateway_host = None
        gateway_port = None
        gateway_guid = None

        try:
            gateway_host = self._api.remote_host
            gateway_port = self._api.remote_port

            _LOGGER.info(f"  Found host: {gateway_host}, port: {gateway_port}")

        except Exception as e:
            _LOGGER.info(f"  Warning, could not determine gateway host and port")

        try:
            param = self._dataset.get_by_id(NextDataset.ID_INSTALLATION_GUID)
            gateway_guid = await self._api.request_value(param, NextDeviceFamilies.SYSTEM.slaves_start, verbose=verbose)

            _LOGGER.info(f"  Found guid: {gateway_guid}")

        except Exception as e:
            _LOGGER.info(f"  Warning, could not determine gateway guid")

        return StuderDiscoveredGateway(
            host = gateway_host,
            port = gateway_port,
            guid = gateway_guid,
        )


    @staticmethod
    async def discover_gateway_webconfig(hint: str = None) -> str:
        """
        Discover if NX Gateway Config page can be found on the local network
        """

        # Find all potential urls to check while keeping the right order:
        # first from hint, then from arp, then others
        urls_hint: set[str] = {hint} if hint else set()
        urls_arp: set[str] = { f"http://{str(ip)}" for ip in StuderNetworkHelper.get_local_ips_via_arp() } - urls_hint
        urls_net: set[str] = { f"http://{str(ip)}" for ip in StuderNetworkHelper.get_local_ips_via_network() } - urls_hint - urls_arp
        urls :list[str] = list(urls_hint) + list(urls_arp) + list(urls_net)

        # Define helper function to check for Next Gateway Config page
        async def check_url(client:httpx.AsyncClient, url:str) -> str|None:
            _LOGGER.info(f"Trying {url}")
            try:
                rsp = await client.get(url, follow_redirects=True)
                if rsp and rsp.is_success:
                    match = re.search(r"<title>\s*(.+?)\s*</title>", rsp.text, re.IGNORECASE | re.DOTALL)

                    if match and match.group(1).startswith("nextOS"):
                        return url

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
    
