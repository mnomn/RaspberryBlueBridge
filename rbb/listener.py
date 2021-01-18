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

_abort = False

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
            t = threading.Thread(target=_listen, args=(mac, name))
            _threads.append(t)

        if len(_threads) == 0:
            log.warn("No devices paired/active")
        for t in _threads:
            t.start()
        
        tlen = len(_threads)
        log.debug(f"Wait for {tlen} threads")
        for t in _threads:
            t.join()
        log.debug("All threads ended")

    except dbm.error:
        log.error("No devices scanned.")
    except KeyboardInterrupt:
        log.error("Kbd interrupt")
        global _abort
        _abort = True


class NotifyDelegate(btle.DefaultDelegate):
    def __init__(self, mac, name, char_guids):
        self.mac = mac.replace(':', '')
        self.name = name
        self.char_guids = char_guids
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
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
        except:
            e = sys.exc_info()[0]
            log.error(f"NotifyDelegate {self.mac} exception: {e}")


def convert_bytes_to_signed(bytes):
    data_len = len(bytes)
    dataInt = int.from_bytes(bytes, byteorder='little', signed=True)
    log.debug(f"Notification received dataInt: {dataInt} Len: {data_len}")
    return dataInt


def _listen(mac, name):
    while not _abort:
        try:
            _listen_notify(mac, name)
        except btle.BTLEDisconnectError:
            if _abort:
                break
            print("* Disconnect error Retry", sys.exc_info()[0])
            time.sleep(5)
        except:
            e = sys.exc_info()[0]
            log.error(f"_listen {mac} exception: {e}")
            time.sleep(5)

# Use last bit of mac (msb) to determine if it is a public or random address
def getAddressType(mac):
    if len(mac) > 2:
        lastByteStr = mac[0:2]
        lastByte = int(lastByteStr, 16)
        log.debug (f"LAST BYTE {lastByte}")
        odd = lastByte%2 == 1
        if odd:
            log.debug (f"LAST BYTE ODD RANDOM ADDR")
            return btle.ADDR_TYPE_RANDOM

    return btle.ADDR_TYPE_PUBLIC

def _listen_notify(mac, name):
    log.info(f"Connect to {mac} {name}")

    addressType = getAddressType(mac)

    arduinoBle = btle.Peripheral(mac, addressType)

    _message_queue.sendMessage(mac, name, "connected", None)

    log.debug("Get services and characteristics")
    services = arduinoBle.getServices()

    # For each handle, save uuid so it can be used in notify
    char_guids = {}
    for s in services:
        log.debug(f"Service:, {s}, {s.uuid}")
        if s.hndStart == s.hndEnd:
            continue
        schars = s.getCharacteristics()
        for sc in schars:
            log.debug(
                f"Char: h={sc.valHandle}, {sc.uuid}, Readable: {sc.supportsRead()}"
            )

            h = sc.getHandle()
            if h > s.hndEnd:
                log.debug(f"Service handle too high {h}")
                continue

            props = sc.propertiesToString()
            if not "READ" in props or not "NOTIFY" in props:
                log.debug("Characteristic is not 'read notify'")
                continue

            cccd = sc.getDescriptors(forUUID="2902")
            if cccd:
                log.debug(f"Listen to notify for {sc.uuid}")
                for d in cccd:
                    setup_data = b"\x01\x00"  # Activate notifications
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

    while not _abort:
        if arduinoBle.waitForNotifications(1.0):
            continue


if __name__ == "__main__":
    listen()
