'''
    This program is designed to walk a directory tree
    & check each file within it to see if it has been in the directory
    for more than a specified time
    This program is run using the CLI & its required arguments
    Language: Python
'''

import os
import time
import datetime
import logging
from pathlib import Path
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='directory tree & file logging')
    parser.add_argument("--directory", "-d", required=True, type=str, default=['.'],
                    dest="dirToW", help="directory to watch, specify path")
    parser.add_argument("--log-file", "-lf", required=True, type=str, default=['.'],
                    dest="lf", help="log file location, specify path")
    parser.add_argument("--interval", "-i", type=int, default=60,
                        dest="int", help="interval for periodic checks (in seconds)")
    #interval argparse
    return parser.parse_args()

def check_existing_files(checked_files, directory_to_watch):
    current_time = datetime.datetime.now()

    directory_to_watch_path = Path(directory_to_watch).resolve()

    for root, subdirs, files in os.walk(directory_to_watch_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            except FileNotFoundError:
                continue

            time_difference = current_time - file_creation_time
            if time_difference.total_seconds() > 10 and filename not in checked_files:
                logging.info(f"File '{filename}' has been in the directory for more than ten seconds.")
                checked_files.add(filename)

    return checked_files

def log_created_file(file_path, lf):
    current_time = datetime.datetime.now()
    with open(lf, "a") as fh:
        fh.write(f"File {file_path} added at {current_time}\n")

if __name__ == "__main__":
    args = parse_arguments()

    # Initial check for existing files
    checked_files = set()
    checked_files = check_existing_files(checked_files, args.dirToW)
    print("Initial checked_files:", checked_files)

    # Configure logging, logs are appended to a file
    logging.basicConfig(filename=args.lf, level=logging.DEBUG,
                    format='%(asctime)s - %(message)s')

try:
    while True:
        checked_files = check_existing_files(checked_files, args.dirToW)

        print("Updated checked_files:", checked_files)

        for root, subdirs, files in os.walk(args.dirToW):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path) and filename not in checked_files:
                    checked_files.add(filename)
                    log_created_file(file_path, args.lf)

        # Periodic check, specify in argument, default 60 seconds
        time.sleep(args.int)
except KeyboardInterrupt:
    pass