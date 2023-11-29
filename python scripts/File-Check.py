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
import argparse # handle multi directory trees

directory_to_watch = 'C:\\Users\\semir\\Desktop\\test'
timestamp_file_path = 'C:\\Users\\semir\\Desktop\\test\\timestamp(checked).log'

# Configure logging, loggins is appended to a file
logging.basicConfig(filename=timestamp_file_path, level=logging.DEBUG, format='%(asctime)s - %(message)s')


def check_existing_files(checked_files):
    current_time = datetime.datetime.now()

    for root, subdirs, files in os.walk(directory_to_watch):
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

def log_created_file(file_path):
    current_time = datetime.datetime.now()
    with open(timestamp_file_path, "a") as fh:
        fh.write(f"File {file_path} added at {current_time}\n")

if __name__ == "__main__":
    # Initial check for existing files
    checked_files = set()
    checked_files = check_existing_files(checked_files)
    print("Initial checked_files:", checked_files)

    try:
        while True:
            checked_files = check_existing_files(checked_files)  # Periodic check
            
            print("Updated checked_files:", checked_files)

            for root, subdirs, files in os.walk(directory_to_watch):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if os.path.isfile(file_path) and filename not in checked_files:
                        checked_files.add(filename)
                        log_created_file(file_path)

            time.sleep(20)  # Check every 20 seconds
    except KeyboardInterrupt:
        pass
