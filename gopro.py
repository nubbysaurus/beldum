# -*- coding: utf-8 -*-
"""gopro.py - API for controlling a [compatible] GoPro camera.

Todo:
    * Understand Bleak. 
    * Create individual Camera classes to encapsulate functionality.
    * Integrate GoPro capture.
"""
from camera import Camera

# Used for communication decoding with GoPro cameras.
GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
class GoProUUID:
    COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
    COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
    SETTINGS_REQ_UUID = GOPRO_BASE_UUID.format("0074")
    SETTINGS_RSP_UUID = GOPRO_BASE_UUID.format("0075")
    QUERY_REQ_UUID = GOPRO_BASE_UUID.format("0076")
    QUERY_RSP_UUID = GOPRO_BASE_UUID.format("0077")
    WIFI_AP_SSID_UUID = GOPRO_BASE_UUID.format("0002")
    WIFI_AP_PASSWORD_UUID = GOPRO_BASE_UUID.format("0003")
    NETWORK_MANAGEMENT_REQ_UUID = GOPRO_BASE_UUID.format("0091")
    NETWORK_MANAGEMENT_RSP_UUID = GOPRO_BASE_UUID.format("0092")


class GoPro(Camera):
    """Connect with and control a GoPro device."""
    def __init__(self):
        super().__init__()
