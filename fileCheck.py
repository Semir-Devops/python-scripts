'''
    This program is designed to walk a directory tree
    & check each file within it to see if it has been in the directory
    for more than a specified time, if the file meets the condition, three events are executed:
    1.the event is logged with the timestamp
    2. The file path is taken and written to a file created in the expired-folder, named with a timestamp format
    3. The file path in the directory_To_watch is written along with the corresponding filename in expired-folder inside a metadata-file
    The program can delete files in the expired-folder when files in the directory_to_watch are deleted as well,
    along with its reference in the metadata-file
    This program is run using the CLI & its required arguments.
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
                        dest="lf", help="log file location with full path")
    parser.add_argument("--interval", "-i", type=int, default=60, dest="intl",
                        help="interval for periodic checks (in seconds)")
    parser.add_argument("--exclude-file", "-ef", type=str, dest="excl_file",
                        help="list of files to exclude from fileCheck")
    parser.add_argument("--expired-folder", "-exp", type=str, required=True, dest="exp_folder",
                        help="folder to move expired files to")
    parser.add_argument("--metadata-file", "-meta", type=str, required=True, dest="meta_file",
                        help="metadata file to help delete expired files")

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

def read_exclude_list(exclude_file):
    exclude_list = set()
    if exclude_file:
        try:
            with open(exclude_file, 'r') as file:
                # Read full file paths and resolve them
                exclude_list.update(Path(line.strip()).resolve() for line in file)
        except Exception as e:
            print(f"Error reading exclude file: {e}")
    return exclude_list

def check_existing_files(directory_to_watch, log_file_path, exclusion_list, exp_folder, meta_file):
    current_time = datetime.datetime.now()

    # Create a set to store file paths from the metadata file
    processed_files = set()
    if Path(meta_file).is_file():
        with open(meta_file, 'r') as f:
            processed_files.update(Path(line.strip().split(", ")[1]).resolve() for line in f)

    directory_to_watch_path = Path(directory_to_watch).resolve()

    # Set to store files in directory
    current_files = set()
    for root, subdirs, files in os.walk(directory_to_watch_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            current_files.add(file_path)

            try:
                file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            except FileNotFoundError:
                continue

            time_difference = current_time - file_creation_time
            full_path = Path(file_path).resolve()
            if (int(time_difference.total_seconds()) > 10 and full_path not in processed_files and full_path not in exclusion_list):
                log_msg = f"File '{full_path}' has been in the directory for more than ten seconds."
                logging.info(log_msg)
                log_created_file(full_path, log_file_path, exp_folder, meta_file)
                processed_files.add(full_path)

def log_created_file(file_path, lf, exp_folder, meta_file):
    current_time = datetime.datetime.now()
    log_message = f"File '{file_path}' added at {current_time}"
    log_timestamp = current_time.strftime("%Y.%m.%d_%H.%M.%S.%f")

    try:
        logging.info(log_message)
        # Copy the file to the expired files folder
        expired_file_path = Path(exp_folder) / f"{log_timestamp}_{Path(file_path).stem}.txt"
        Path(expired_file_path).write_text(f"{file_path}\n")

        # Write to metadata file
        with open(meta_file, 'a') as f:
            f.write(f"{Path(expired_file_path).name}, {file_path}\n")

    except Exception as e:
        print(f"Error logging message: {e}")

def delete_files(directory_to_watch, exp_folder, meta_file):
    checked_files = set()
    for root, subdirs, files in os.walk(directory_to_watch):
        for filename in files:
            file_path = os.path.join(root, filename)
            checked_files.add(file_path)

    expired_files = os.listdir(exp_folder)
    for expired_file in expired_files:
        expired_file_path = os.path.join(exp_folder, expired_file)
        if os.path.isfile(expired_file_path):
            # Read the content of the expired file
            with open(expired_file_path, 'r') as f:
                expired_content = f.read().strip()

            # Check if the expired content (full path) is not in the checked_files (full path of dirToW files)
            if expired_content not in checked_files:
                os.remove(expired_file_path)
                logging.info(f"Deleted expired file: {expired_file_path}")

                with open(meta_file, 'r') as f:
                    lines = f.readlines()
                with open(meta_file, 'w') as f:
                    for line in lines:
                        if expired_file in line:
                            continue
                        f.write(line)

def main():
    args = parse_arguments()

    # Configure logging, logs are appended to a file
    configure_logging(args.lf)

    # Initial check for existing files
    checked_files = set()
    exclude_list = read_exclude_list(args.excl_file)
    check_existing_files(args.dirToW, args.lf, exclude_list, args.exp_folder, args.meta_file)
    print(f"Log file path: {args.lf}")

    try:
        while True:
            # Periodic check, specify in argument, default 60 seconds
            time.sleep(args.intl)
            exclude_list = read_exclude_list(args.excl_file)
            check_existing_files(args.dirToW, args.lf, exclude_list, args.exp_folder, args.meta_file)
            delete_files(args.dirToW, args.exp_folder, args.meta_file)
            print("another loop")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
