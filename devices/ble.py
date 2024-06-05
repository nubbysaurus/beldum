# -*- coding: utf-8 -*-
"""ble.py - Bluetooth Low-Energy Python interface.

A library containing BLE interfaces.

Usage:
    * To search for devices and connect to a single desired device:
        from ble import find_ble_devices, BLEClient
        ble_devices = find_ble_devices()
        for device in ble_devices:
            return device if DESIRED_NAME in device[0]

Todo:
    * How can we improve the polymorphism of it all?

"""
import argparse
import asyncio
import atexit
from datetime import datetime
import logging
import re
import sys
import time
from typing import Any, Awaitable, Callable, Optional, Union

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice


logger = logging.getLogger(__name__)

async def find_ble_devices() -> dict[str, BLEDevice]:
    """Search for all available BLE devices.
    
    Returns:
        ble_devices (dict)

    """
    RETRIES = 10
    for retry in range(RETRIES):
        try:
            # Scan for devices
            logger.info("Scanning for bluetooth devices...")

            # Map of discovered devices indexed by name
            devices: dict[str, BLEDevice] = {}

            # Scan callback to also catch nonconnectable scan responses
            # pylint: disable=cell-var-from-loop
            def _scan_callback(device: BLEDevice, _: Any) -> None:
                # Add to the dict if not unknown
                if device.name and device.name != "Unknown":
                    devices[device.name] = device

            for device in await BleakScanner.discover(
                timeout=5,
                detection_callback=_scan_callback
            ):
                if device.name and device.name != "Unknown":
                    devices[device.name] = device

            # Log every device we discovered
            for d in devices:
                logger.debug(f"\tDiscovered: {d}")
            return devices
        except:
            raise RuntimeError(
                f"Couldn't establish BLE connection after {RETRIES} retries"
            )
