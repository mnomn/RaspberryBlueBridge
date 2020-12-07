import configparser
import logging

mqtt_setttings = []

_default_shelve_file = "devices.db"
_default_config_file = "raspberry-blue-bridge.conf"
shelve_file = ""
dir = ""


def read(_dir):
    global dir
    dir = _dir
    config = configparser.ConfigParser()
    filename = dir + "/" + _default_config_file
    config.read(filename)

    logging.info("Config file: " + filename)

    global mqtt_setttings
    if 'MQTT' in config:
        mqtt_setttings = config['MQTT']

    global shelve_file
    shelve_file = dir + "/" + _default_shelve_file
