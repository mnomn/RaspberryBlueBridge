# RaspberryBlueBridge
Raspberry Pi script that listens to bluetooth data and resends it as mqtt.

Example: A BLE device with mac *f1:76:a1:1a:b3:94* and local name *MySensor* has a characteristic with GUID *19b10112-e8f2-537e-4f6c-d104768a1214*.
When the BLE device writes *-4* to the characteristic, this program will listen and create an MQTT message like this:

Mqtt Topic: `f176a11ab394/MySensor/19b10112-e8f2-537e-4f6c-d104768a1214`  
Data payload: `-4`

Write characteristics are not supported.

## Ble devices
Bluetooth devices must peripehral, connectable, have a characteristic that is readable and that notifies when data is available. Channels can have different number of bytes (1,2 or 4).
Data will be formatted as signed (int8/int16/int32).

Tested devices:
- Arduino Nano 33 BLE: Peripheral sketch with one or more charactersitics with NOTIFY and READ.
- Micro:bit (original): Create bluetooth sketch in makecode.microbit.org. For example temperature or button service. Pairing is not supported.

## Install on Raspberry pi
### Install prerequisite
* Raspberry pi running Raspberry OS or similar. Only tested on Raspberry pi 3 (Raspbian 10)

* An mqtt server. Can be on the same raspberry pi or another machine.

Download software to a temporary folder on your raspberry pi and run `sudo install.sh`.
After that you can delete the temporary folder.

```
curl -L  https://github.com/mnomn/RaspberryBlueBridge/archive/main.zip -o rbb.zip
unzip rbb.zip
cd RaspberryBlueBridge-main
sudo bash install.sh
````

## Configure
### Configure MQTT
Configuration is done in /usr/local/etc/raspberry-blue-bridge.

The file raspberry-blue-bridge.conf configures MQTT server.

### Configure BLE devices
We must first get a list of devices that we shall read data from. It is done by scannng.

`sudo raspberry-blue-bridge -s`

Devices with readable, notifiable characteristics will be stored in /usr/local/etc/raspberry-blue-bridge/devices.
Devices are not overwritten, only new devices are added.

## Start
### Run manually
`sudo raspberry-blue-bridge` starts normal operation in the terminal window.

### Run automatically
Use systemd
```
systemctl enable raspberry-blue-bridge.service
systemctl restart raspberry-blue-bridge.service
```

## Help
For more options: `raspberry-blue-bridge -h`

## MQTT
MQTTT messages are sent as one topic per relevant characteristic. A device can have many characteristics.
MQTT topics are named: `{mac}/{LocalName}/{CharacteristicGuid}` with data as payload in signed integer format.
Example: `f176a11ab394/MySensor/19b10112-e8f2-537e-4f6c-d104768a1214` payload: `-4`

There is also a message sent when the devices is connected.
`{mac}/{LocalName}/connected` without any data.
Example: `f176a11ab394/MySensor/connected`
