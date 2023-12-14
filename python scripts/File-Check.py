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
    parser.add_argument("--directory", "-d", required=True, type=str, default='.',
                        dest="dirToW", help="directory to watch, specify path")
    parser.add_argument("--log-file", "-lf", required=True, type=str, default='.',
                        dest="lf", help="log file location, specify path")
    parser.add_argument("--interval", "-i", type=int, default=60,
                        dest="int", help="interval for periodic checks (in seconds)")
    # interval argparse
    return parser.parse_args()

def configure_logging(log_file_path):
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        filemode='a+')

    # Add a stream handler to display log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


def check_existing_files(checked_files, directory_to_watch, log_file_path):
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
                log_msg = f"File '{filename}' has been in the directory for more than ten seconds."
                logging.info(log_msg)
                checked_files.add(filename)
                log_created_file(filename, log_file_path)

    return checked_files

def log_created_file(file_path, lf):
    current_time = datetime.datetime.now()
    log_message = f"File {file_path} added at {current_time}"

    try:
        logging.info(log_message)
    except Exception as e:
        print(f"Error logging message: {e}")

if __name__ == "__main__":
    args = parse_arguments()

    # Configure logging, logs are appended to a file
    configure_logging(args.lf)

    # Initial check for existing files
    checked_files = set()
    checked_files = check_existing_files(checked_files, args.dirToW, args.lf)
    print("Initial checked_files:", checked_files)

    print(f"Log file path: {args.lf}")
    logging.info("Script started")

    try:
        while True:
            # Periodic check, specify in argument, default 60 seconds
            time.sleep(args.int)
            checked_files = check_existing_files(checked_files, args.dirToW, args.lf)
            print("another loop")
    except Exception as e:
        print(f"Error in main loop: {e}")
    except KeyboardInterrupt:
        pass
