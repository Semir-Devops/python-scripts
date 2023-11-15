import os
import time
import datetime

directory_to_watch = 'C:\\Users\\semir\\Desktop\\test'
timestamp_file_path = 'C:\\Users\\semir\\Desktop\\test\\timestamp.log'

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
                print(f"File '{filename}' has been in the directory for more than ten seconds.")


def log_created_file(file_path):
    current_time = datetime.datetime.now()
    with open(timestamp_file_path, "a") as fh:
        fh.write(f"File {file_path} added at {current_time}\n")

if __name__ == "__main__":
    checked_files = set()
    time.sleep(5)

    try:
        while True:
            check_existing_files(checked_files)  # Periodic check
            time.sleep(30)  # Check every 30 seconds

            for root, subdirs, files in os.walk(directory_to_watch):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if os.path.isfile(file_path) and filename not in checked_files:
                        checked_files.add(filename)
                        log_created_file(file_path)
    except KeyboardInterrupt:
        pass