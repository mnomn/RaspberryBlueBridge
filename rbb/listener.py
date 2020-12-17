from bluepy import btle
import sys
import dbm
import threading
import logging as log
import time
import struct

from rbb import scanner
from rbb import devices
from rbb import messenger

_message_queue = None

# Built in Characteristics, without interesting measurement data.
ignore_list  = [
    "00002a00-0000-1000-8000-00805f9b34fb", # Device Name
    "00002a01-0000-1000-8000-00805f9b34fb", # Appearence
    "00002a05-0000-1000-8000-00805f9b34fb", # Service Changed
]

def listen():
    devs = devices.getAll()
    message_queue = messenger.Messenger()
    global _message_queue
    _message_queue = message_queue
    _threads = []
    try:
        for dev in devs:
            mac = dev["mac"]
            name = dev.get(devices.kNAME, "")
            enabled = dev.get(devices.kENABLED, True)
            if not enabled:
                log.info(f"Device {mac} {name} not enabled")
                continue
            interval = dev.get(devices.kREAD_INTERVAL, 0)
            t = threading.Thread(target=_listen, args=(mac, name, interval))
            _threads.append(t)

        if len(_threads) == 0:
            log.warn("No devices paired/active")
        for t in _threads:
            t.start()
    except dbm.error:
        log.error("No devices scanned.")
    except KeyboardInterrupt:
        log.error("KBD INTERRUPT!!!.")


class NotifyDelegate(btle.DefaultDelegate):
    def __init__(self, mac, name, char_guids):
        self.mac = mac.replace(':', '')
        self.name = name
        self.char_guids = char_guids
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # TODO: Store "serviceGuid:characteristicGuid" so it can be sent here
        if cHandle not in self.char_guids:
            log.error("Error: No guid for this handle")
        char_name = self.char_guids[cHandle]
        log.info(f"Notification received data: {data} size: {len(data)}")

        try:
            signed_int = convert_bytes_to_signed(data)
            _message_queue.sendMessage(
                self.mac, self.name, char_name, signed_int
            )

        except UnicodeDecodeError as ex:
            log.error(f"Cannot convert bytes to signed int: {data} {ex}")


def convert_bytes_to_signed(bytes):
    data_len = len(bytes)
    dataInt = int.from_bytes(bytes, byteorder='little', signed=True)
    log.debug(f"Notification received dataInt L: {dataInt} Len: {data_len}")
    return dataInt


def _listen(mac, name, interval):
    while True:
        try:
            if interval:
                _read_characteristics(mac, name)
                log.info(f"Listen done, sleep for {interval} s")
                time.sleep(interval)
            else:
                _listen_notify(mac, name)
        except btle.BTLEDisconnectError:
            print("* Disconnect error Retry", sys.exc_info()[0])
            time.sleep(5)


def _listen_notify(mac, name):
    log.info(f"Connect to {mac} {name}")
    arduinoBle = btle.Peripheral(mac)

    log.debug("Get services and characteristics")
    services = arduinoBle.getServices()
    # For each handle, save uuid so it can be used in notify
    char_guids = {}
    for s in services:
        log.debug(f"Service:, {s}, {s.uuid}")
        schars = s.getCharacteristics()
        for sc in schars:
            log.debug(
                f"Char: {sc}, {sc.uuid}, Readable: {sc.supportsRead()}"
            )

            cccd = sc.getDescriptors(forUUID="2902")
            if cccd:
                log.debug(f"Listen to notify for {sc.uuid}")
                for d in cccd:
                    setup_data = b"\x01\x00"  # Activate nofigications
                    if d.handle:
                        arduinoBle.writeCharacteristic(
                            d.handle, setup_data, withResponse=True
                        )
                    else:
                        print("Handle is None")
                if sc.supportsRead():
                    char_guids[sc.getHandle()] = sc.uuid

    arduinoBle.withDelegate(
        NotifyDelegate(mac, name, char_guids))

    while True:
        if arduinoBle.waitForNotifications(1.0):
            continue


def _read_characteristics(mac, name):
    log.info(f"Connect to {mac} {name}")
    arduinoBle = btle.Peripheral(mac)

    log.debug("Get services and characteristics")
    services = arduinoBle.getServices()

    for s in services:
        log.debug(f"Service:, {s}, {s.uuid}")
        schars = s.getCharacteristics()
        for sc in schars:
            if sc.uuid in ignore_list:
                continue

            supportsRead = sc.supportsRead()
            log.debug(
                f"Char: {sc}, {sc.uuid}, Readable: {supportsRead}"
            )
            if sc.supportsRead():
                val = sc.read()
                log.info(f"READ VAL: {val}")

            try:
                signed_int = convert_bytes_to_signed(val)
                _message_queue.sendMessage(
                    mac, name, sc.uuid, signed_int
                )

            except UnicodeDecodeError as ex:
                log.error(f"Cannot convert bytes to signed int: {sc.uuid} {val} {ex}")

    arduinoBle.disconnect()


if __name__ == "__main__":
    listen()
