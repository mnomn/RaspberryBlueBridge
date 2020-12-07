#!/bin/bash

[ $USER == root ] || {
    echo "Run as sudo"
    exit
}

NAME=raspberry-blue-bridge
BASE_DIR="/usr/local"
ETC=$BASE_DIR/etc/$NAME
BIN=$BASE_DIR/bin
SYSD_FILE=/etc/systemd/system/raspberry-blue-bridge.service

echo "Install $NAME to $ETC and $BIN"

mkdir -p $ETC
cp rbb.py $ETC
cp -r rbb $ETC
cp requirements.txt $ETC

[ -f  $ETC/raspberry-blue-bridge.conf ] || {
    # Do not overwrite config file when-installing
    cp raspberry-blue-bridge.conf $ETC
}

mkdir -p $BIN
cp raspberry-blue-bridge $BIN

# Copy systemd file and set executable path.
sudo sed  "s|_BIN_|$BIN|g" raspberry-blue-bridge.service > $SYSD_FILE
echo "Installation done"
