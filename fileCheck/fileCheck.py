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
                        help="list of files or directories to exclude from fileCheck")
    parser.add_argument("--expired-folder", "-exp", type=str, required=True, dest="exp_folder",
                        help="folder to move expired files to")
    parser.add_argument("--metadata-file", "-meta", type=str, required=True, dest="meta_file",
                        help="metadata file to help delete expired files")
    parser.add_argument("--maxfileage", "-age", type=int, required=True, dest="maxfileage",
                        help="The time when a file is considered aged")

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
                for line in file:
                    exclude_path = Path(line.strip()).resolve()
                    exclude_list.add(exclude_path)
                    if exclude_path.is_dir():
                        for sub_path in exclude_path.rglob('*'):
                            exclude_list.add(sub_path)
        except Exception as e:
            print(f"Error reading exclude file: {e}")
    return exclude_list

def check_files(directory_to_watch, log_file_path, exclusion_list, exp_folder, meta_file, file_timestamps, maxfileage):
    current_time = datetime.datetime.now()

    # Create a set to store file paths from the metadata file
    processed_files = set()
    if Path(meta_file).is_file():
        with open(meta_file, 'r') as f:
            for line in f:
                parts = line.strip().split(", ")
                if len(parts) == 2:
                    timestamp = parts[0]
                    file_path = Path(parts[1]).resolve()
                    processed_files.add(file_path)
                    file_timestamps[file_path] = datetime.datetime.strptime(timestamp, "%Y-%m-%d_%H:%M:%S")

    directory_to_watch_path = Path(directory_to_watch).resolve()

    # Set to store files in directory
    current_files = set()
    for root, subdirs, files in os.walk(directory_to_watch_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            full_path = Path(file_path).resolve()
            current_files.add(full_path)

            if full_path not in exclusion_list:
                stats = full_path.stat()
                mtime = datetime.datetime.fromtimestamp(stats.st_mtime)
                file_creation_time = file_timestamps.get(full_path, mtime)
                file_timestamps[full_path] = file_creation_time

                time_difference = current_time - file_creation_time

                if int(time_difference.total_seconds()) > maxfileage and full_path not in processed_files:
                    log_msg = f"File '{full_path}' has been in the directory for more than {maxfileage} seconds."
                    logging.info(log_msg)
                    log_created_file(full_path, log_file_path, exp_folder, meta_file, file_creation_time)
                    processed_files.add(full_path)

def log_created_file(file_path, lf, exp_folder, meta_file, creation_time):
    log_message = f"File '{file_path}' added at {creation_time}"
    log_timestamp = creation_time.strftime("%Y-%m-%d_%H:%M:%S")

    try:
        logging.info(log_message)
        # Copy the file to the expired files folder
        expired_file_path = Path(exp_folder) / f"{log_timestamp}_{Path(file_path).stem}.txt"
        Path(expired_file_path).write_text(f"{file_path}\n")

        # Write to metadata file
        with open(meta_file, 'a') as f:
            f.write(f"{log_timestamp}, {file_path}\n")

    except Exception as e:
        print(f"Error logging message: {e}")

def delete_files(directory_to_watch, exp_folder, meta_file, log_file):
    checked_files = set()
    for root, subdirs, files in os.walk(directory_to_watch):
        for filename in files:
            file_path = os.path.join(root, filename)
            checked_files.add(Path(file_path).resolve())

    # Update metadata file to remove entries for files no longer in directory
    if Path(meta_file).is_file():
        with open(meta_file, 'r') as f:
            lines = f.readlines()
        with open(meta_file, 'w') as f:
            for line in lines:
                file_path = Path(line.strip().split(", ")[1])
                if file_path.resolve() in checked_files:
                    f.write(line)
                else:
                    # Remove the file from expired folder
                    expired_files = os.listdir(exp_folder)
                    for expired_file in expired_files:
                        expired_file_path = os.path.join(exp_folder, expired_file)
                        if os.path.isfile(expired_file_path):
                            with open(expired_file_path, 'r') as ef:
                                expired_content = ef.read().strip()
                            if expired_content == str(file_path):
                                os.remove(expired_file_path)
                                logging.info(f"Deleted expired file: {expired_file_path}")

                    # Remove entry from log file
                    if Path(log_file).is_file():
                        with open(log_file, 'r') as lf:
                            log_lines = lf.readlines()
                        with open(log_file, 'w') as lf:
                            for log_line in log_lines:
                                if str(file_path) not in log_line:
                                    lf.write(log_line)

def main():
    args = parse_arguments()

    # Ensure the directories and files specified in arguments exist
    Path(args.dirToW).mkdir(parents=True, exist_ok=True)
    Path(args.exp_folder).mkdir(parents=True, exist_ok=True)
    Path(args.lf).parent.mkdir(parents=True, exist_ok=True)

    if args.excl_file:
        Path(args.excl_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.excl_file).touch(exist_ok=True)

    Path(args.meta_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.meta_file).touch(exist_ok=True)

    # Configure logging, logs are appended to a file
    configure_logging(args.lf)

    # Initial check for existing files
    file_timestamps = {}
    exclude_list = read_exclude_list(args.excl_file)
    check_files(args.dirToW, args.lf, exclude_list, args.exp_folder, args.meta_file, file_timestamps, args.maxfileage)
    print(f"Log file path: {args.lf}")

    try:
        while True:
            # Periodic check, specify in argument, default 60 seconds
            time.sleep(args.intl)
            exclude_list = read_exclude_list(args.excl_file)
            check_files(args.dirToW, args.lf, exclude_list, args.exp_folder, args.meta_file, file_timestamps, args.maxfileage)
            delete_files(args.dirToW, args.exp_folder, args.meta_file, args.lf)
            print("another loop")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
