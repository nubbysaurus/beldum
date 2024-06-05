# -*- coding: utf-8 -*-
"""beldum.py - Setup and control cameras.

This is a test suite for evaluating the control of different cameras.

Todo:
    * Create individual Camera classes to encapsulate functionality.
    * Integrate GoPro capture.
    * Integrate Realsense capture.
    * Integrate Genius WideCam capture.
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

from devices.gopro import GoPro
from devices.ble import find_ble_devices

DURATION_POLL = 15 * 60 # Duration of period in seconds.
logger = logging.getLogger(__name__)

T_DeviceList = dict[str, BLEDevice]

def _get_timestamp() -> str:
    """Generate a timestamp.
    
    Returns:
        timestamp (str): Format of YYYYmmDD_HHMMSS.
    """
    return datetime.today().strftime("%Y%m%d_%H%M%S")

async def find_devices():
    """Scan for ALL available devices (outside of this machine).
    
    Todo:
        * Add LWS and Android interfaces.

    """
    devices: T_DeviceList = {}
    ble_devices = await find_ble_devices()
    devices.update(ble_devices)
    return devices

async def beldum():
    """Main entry point for LWS app.

    1. Scan for available devices.
    2. Connect to devices of interest.
    3. Capture sensor data (LWS and camera) at regular intervals.
    4. Clean up.

    Currently, we are supporting comms with:
        * GoPro cameras (BLE)
        * Android phones (USB?)
        * LWSs (serial?)
    """
    device_whitelist_lut = {
        "gopro": re.compile(r"GoPro [0-9]{4}")
    }
    # Scan for and filter devices.
    found_devices = await(find_devices())
    devices = {}    # Filtered device list.
    # TODO(nubby): This is ugly, but functional; pls make prettier?
    [devices.update({dev: found_devices[dev]}) for dev in found_devices if any(
        device_whitelist_lut[key].match(dev) for key in device_whitelist_lut
    )]

    # Connect to narrowed, found devices.
    logging.info(devices)
    return 0
        
def exit_handler():
    logger.info("Good bye.")

if __name__ == "__main__":
    """Capture an image from the camera periodically."""
    logging.basicConfig(level=logging.INFO)
    """
    parser = argparse.ArgumentParser(
        description="Connect to a BLE device, pair, and enable notifications."
    )
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="Last 4 digits of BLE device serial number, which is the last 4 \
                digits of the default camera SSID. If not used, first \
                discovered GoPro will be connected to",
        default=None,
    )
    args = parser.parse_args()
    """

    try:
        asyncio.run(beldum())
    except Exception as e:
        # TODO(nubby): Make this more specific.
        logger.error(e)
        sys.exit(-1)
    else: 
        sys.exit(0)

atexit.register(exit_handler)
