from bluepy import btle
import logging
import rbb.configuration
import os
import stat

from rbb import devices


def scan():
    logging.info("Scanning for suitable ble devices")
    scanner = btle.Scanner().withDelegate(btle.DefaultDelegate())
    scanner.start()
    scanner.process()
    devs = scanner.getDevices()
    deviceId = 0

    for device in devs:
        dump(device)
        if not device.connectable:
            continue
        if not device.getValueText(9):
            continue
        deviceId += 1
        localName = device.getValueText(9)
        devices.putOne(device.addr, localName)
    print(f"Found {deviceId} devices")


def list_scanned_devices():
    devs = devices.getAll()
    _show_list(devs)


def _show_list(devs):
    if len(devs) < 1:
        print("No devices scanned")
        return

    for dev in devs:
        mac = dev.get("mac", "")
        name = dev.get(devices.kNAME, "")
        print(f'- {mac} "{name}"')

    print("Configure devices in ")


_knownMacs = []


def dump(dev):
    global _knownMacs
    if dev.addr in _knownMacs:
        return
    _knownMacs.append(dev.addr)
    logging.debug(f"###########  {dev.addr}")

    for (adtype, desc, value) in dev.getScanData():
        logging.debug("  %s (%d) = %s" % (desc, adtype, value))
    logging.debug(f"connectable {dev.connectable}")
