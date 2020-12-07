import argparse
import logging
import sys
import os


def parse():
    parser = argparse.ArgumentParser()

    default_conf_dir = "/usr/local/etc/raspberry_blue_bridge"

    parser.add_argument(
        "--scan",
        "-s",
        dest="scan",
        action="store_true",
        default=False,
        help="Scan for devices to use.",
    )

    parser.add_argument(
        "--list", "-l", dest="listscan", action="store_true",
        default=False, help="List scanned BLE devices."
    )

    parser.add_argument(
        "--loglevel", "-v", dest="loglevel", action="store", nargs='?',
        default='WARNING', help="Log level, defauly WARNING."
    )

    parser.add_argument(
        "--dir", dest="confdir", action="store",
        default=default_conf_dir,
        help="Configuration directory."
    )

    # print("ARGV: ", sys.argv)
    args = parser.parse_args()

    if not args.confdir:
        # Default path is where program started from
        args.confdir = os.path.dirname(sys.argv[0])

    logging.info(f"Set LogLevel: {args.loglevel}")
    logging.getLogger().setLevel(args.loglevel)

    return args
