from bluepy import btle
import sys
import threading
import logging as log

from rbb import scanner
from rbb import listener
from rbb import messenger
from rbb import arguments
from rbb import configuration


DEBUG = False

arguments = arguments.parse()
settings = configuration.read(arguments.confdir)

if arguments.scan:
    scanner.scan()
    exit()

if arguments.listscan:
    scanner.list_scanned_devices()
    exit()

listener.listen()

log.debug("Leaving... ")
