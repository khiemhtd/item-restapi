import argparse
import ipaddress
import json
import logging
import os
import sys

from .config import setup_logging
from .restapi import ItemServer

LOGGER = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Item's Rest API")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase log output verbosity")
    parser.add_argument('--ip', '-i', type=str, default="127.0.0.1", help="The ip address to serve the Rest API")
    parser.add_argument('--port', '-p', type=int, default=8080, help="The port to serve the Rest API")
    parser.add_argument('--log-file', '-l', type=str, help="Output logs to specified file")
    parser.add_argument('--data-file', '-d', type=str, help="Path to data file containing json data")

    args = parser.parse_args()

    # Sanitize arguments
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    if args.log_file:
        # Check if path is valid
        dir_path = os.path.dirname(os.path.abspath(args.log_file))
        if dir_path:
            setup_logging(args.log_file, log_level)
    else:
        setup_logging(level=log_level)

    if args.ip:
        try:
            ipaddress.ip_address(args.ip)
        except ValueError as e:
            LOGGER.error(f"Invalid IP address: {e}")
            sys.exit(1)

    if args.port:
        if not (1 <= args.port <= 65535):
            LOGGER.error(f"Invalid port: {args.port}")

    data = {}
    if args.data_file:
        if os.path.isfile(args.data_file):
            with open(args.data_file) as f:
                data = json.load(f)

    server = ItemServer(args.ip, args.port, data)
    server.run()

if __name__ == "__main__":
    main()
