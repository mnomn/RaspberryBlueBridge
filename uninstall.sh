#!/bin/bash

[ $USER == root ] || {
    echo "Run as sudo"
    exit
}

NAME=raspbery-blue-bridge
BASE_DIR="/usr/local"
ETC=$BASE_DIR/etc/$NAME
BIN=$BASE_DIR/bin
SYSD_FILE=/etc/systemd/system/raspberry-blue-bridge.service

echo "Uninstall $NAME to $ETC and $BIN"

rmdir $ETC

rmdir $BIN/raspberry-blue-bridge
systemctl disable raspberry-blue-bridge.service
systemctl stop raspberry-blue-bridge.service

echo "Uninstallation done"
