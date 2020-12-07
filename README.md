# RaspberryBlueBridge
Raspberry Pi script that listens to bluetooth data and resends it as mqtt 

Example: A device with mac *f1:76:a1:1a:b3:94* and local name *MySensor* has a service with GUID *19b10112-e8f2-537e-4f6c-d104768a1214*.
When the BLE device writes *-4* to the channel this program will create an MQTT message like this.

Mqtt Topic: `f176a11ab394/MySensor/19b10112-e8f2-537e-4f6c-d104768a1214`  
Data payload: `-4`

## Supported/tested hardware
Only tested on Raspberry pi 3 (Raspbian 10) and Arduino Nano 33 BLE.
Bluetooth devices must be connectable, have a characteristic that is readable and that notifies when data is available. Channels can have different number of bytes (1,2 or 4).
Data will be formatted as signed (int8/int16/int32).

## Install
### Install prerequisite
* Raspberry pi running Raspberry OS or similar.
* An mqtt server. Can be on the same raspberry pi or another machine.

Download software to a temporary folder on your raspberry pi and run `sudo install.sh`.
After that you can delete the temporary folder.

### Configure MQTT
Configuration is done in /usr/local/etc/raspberry-blue-bridge.

The file raspberry-blue-bridge.conf configures MQPP server.

### Scan for devices
Before listening to bluetooth we must scan for devices.

`sudo raspberry-blue-bridge -s`

[Arduino example code](https://github.com/arduino-libraries/ArduinoBLE/tree/master/examples/Peripheral)

### Run manually
`sudo raspberry-blue-bridge` starts normal operation in the terminal window.

### Run automatically
TBD

## Help
For more options: `raspberry-blue-bridge -h`
