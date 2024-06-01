# -*- coding: utf-8 -*-
"""beldum.py - Setup and control cameras.

This is a test suite for evaluating the control of different cameras.

Todo:
    * Integrate BLE pairing.
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
from bleak.backends.device import BLEDevice as BleakDevice


DURATION_POLL = 15 * 60 # Duration of period in seconds.
logger = logging.getLogger(__name__)


noti_handler_T = Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]]


def _get_timestamp() -> str:
    """Generate a timestamp.
    
    Returns:
        timestamp (str): Format of YYYYmmDD_HHMMSS.
    """
    return datetime.today().strftime("%Y%m%d_%H%M%S")

def exception_handler(
        loop: asyncio.AbstractEventLoop,
        context: dict[str, Any]
    ) -> None:
    """Catch exceptions from non-main thread

    Args:
        loop (asyncio.AbstractEventLoop): loop to catch exceptions in
        context (Dict[str, Any]): exception context
    """
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception {str(loop)}: {msg}")
    logger.critical("This is unexpected and unrecoverable.")


async def poll() -> None:
    logger.info("Image captured to {}".format(_get_timestamp()+".png"))

async def connect_ble(
        notification_handler: noti_handler_T,
        identifier: str
    ) -> BleakClient:
    """Pair with and enable notifications from a BLE device."""
    asyncio.get_event_loop().set_exception_handler(exception_handler)

    RETRIES = 10
    for retry in range(RETRIES):
        try:
            # Map of discovered devices indexed by name
            devices: dict[str, BleakDevice] = {}

            # Scan for devices
            logger.info("Scanning for bluetooth devices...")

            # Scan callback to also catch nonconnectable scan responses
            # pylint: disable=cell-var-from-loop
            def _scan_callback(device: BleakDevice, _: Any) -> None:
                # Add to the dict if not unknown
                if device.name and device.name != "Unknown":
                    devices[device.name] = device

            # Scan until we find devices
            matched_devices: list[BleakDevice] = []
            while len(matched_devices) == 0:
                # Now get list of connectable advertisements
                for device in await BleakScanner.discover(timeout=5, detection_callback=_scan_callback):
                    if device.name and device.name != "Unknown":
                        devices[device.name] = device
                # Log every device we discovered
                for d in devices:
                    logger.info(f"\tDiscovered: {d}")
                # Now look for our matching device(s)
                token = re.compile(identifier or r"GoPro [A-Z0-9]{4}")
                matched_devices = [device for name, device in devices.items() if token.match(name)]
                logger.info(f"Found {len(matched_devices)} matching devices.")

            # Connect to first matching Bluetooth device
            device = matched_devices[0]

            logger.info(f"Establishing BLE connection to {device}...")
            client = BleakClient(device)
            await client.connect(timeout=15)
            logger.info("BLE Connected!")

            # Try to pair (on some OS's this will expectedly fail)
            logger.info("Attempting to pair...")
            try:
                await client.pair()
            except NotImplementedError:
                # This is expected on Mac
                pass
            logger.info("Pairing complete!")

            # Enable notifications on all notifiable characteristics
            logger.info("Enabling notifications...")
            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        logger.info(f"Enabling notification on char {char.uuid}")
                        await client.start_notify(char, notification_handler)
            logger.info("Done enabling notifications")
            logger.info("BLE Connection is ready for communication.")

            return client
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(f"Connection establishment failed: {exc}")
            logger.warning(f"Retrying #{retry}")

    raise RuntimeError(f"Couldn't establish BLE connection after {RETRIES} retries")

async def beldum(identifier: Optional[str]):
    """Communicate with camera/s."""
    async def dummy_notification_handler(*_: Any) -> None: ...
    device_client = await connect_ble(
        dummy_notification_handler,
        args.identifier
    )

    while (1<2):
        await poll()
        time.sleep(DURATION_POLL)

        
def exit_handler():
    logger.info("Good bye.")

if __name__ == "__main__":
    """Capture an image from the camera periodically."""
    logging.basicConfig(level=logging.INFO)
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

    try:
        asyncio.run(beldum(args.identifier))
    except Exception as e:
        # TODO(nubby): Make this more specific.
        logger.error(e)
        sys.exit(-1)
    else: 
        sys.exit(0)

atexit.register(exit_handler)
