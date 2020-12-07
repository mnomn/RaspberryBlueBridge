import dbm
import logging as log
import sys
import os
from configparser import ConfigParser
import pathlib

from rbb import configuration

kNAME = "name"
kREAD_INTERVAL = "read_interval"
kENABLED = "enabled"


def getAll():
    retval = []
    try:
        d = _getDevicesDir()
        all_files = os.listdir(d)
        log.info(f"All files: {all_files}")
        device_files = [f for f in all_files if f.endswith(".conf")]
        config = ConfigParser()
        for f in device_files:
            config.read(d + "/" + f)
            device_info = _parseOneConfig(config)
            if device_info:
                retval.append(device_info)

    except Exception as exception:
        log.error("Failed to read devices.")
        print(type(exception))
    return retval


# Add or update
def putOne(mac, name):
    dir = _getDevicesDir()
    filename = mac.replace(":", "")
    filename = f"{dir}/{filename}.conf"
    if os.path.exists(filename):
        log.info(f"Device {mac} is already scanned. Do not overrite.")
        return

    config = ConfigParser()
    config["device"] = {
        "mac": mac,
        "name": name,
        kREAD_INTERVAL: 0,  # Configured manually in file
        kENABLED: True      # Configured manually in file
    }

    try:
        with open(filename, 'w') as f:
            log.info(f'Device {mac} "{name}" saved.')
            config.write(f)
    except Exception as e:
        log.error(f"Failed to save device file {filename}")
        print(e)


def _parseOneConfig(conf):
    if "device" not in conf:
        log.warning('[device] not found in configuration')
        print(conf)
        return

    dev = conf["device"]
    # Format values
    interval = dev.get(kREAD_INTERVAL, 0)
    interval = _toNumber(interval)
    enabled = dev.get(kENABLED, True)
    if isinstance(enabled, str):
        t = enabled.lower()
        enabled = t.startswith("t") or t.startswith("y") or t.startswith("1")
    try:
        device_info = {
            "mac": dev["mac"],
            "name": dev["name"],
            kREAD_INTERVAL: interval,
            kENABLED: enabled
        }

        log.debug(f"Device Info {device_info}")

        return device_info
    except Exception as ex:
        print("Exception ", type(ex))
        return None


def _toNumber(n):
    try:
        return int(n)
    except ValueError:
        return 0


def _getDevicesDir():
    if not configuration.dir:
        log.error("Configuration dir not set!")
        sys.exit()
    devdir = configuration.dir + "/devices"
    log.info("Devices dir: " + devdir)
    pathlib.Path(devdir).mkdir(parents=True, exist_ok=True)
    return devdir
