import os
import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

directory_to_watch = 'C:\\Users\\semir\\Desktop\\test'

'''
If you require timestamp file to be created elsewhere
timestamp_file_path = 'C:\\Users\\semir\\Desktop\\specified_directory\\timestamp.log'  # Change this to your desired directory

'''

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.checked_files = set()

    def check_existing_files(self):
        current_time = datetime.datetime.now()
        for filename in os.listdir(directory_to_watch):
            file_path = os.path.join(directory_to_watch, filename)
            file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            time_difference = current_time - file_creation_time
            if filename not in self.checked_files and time_difference.total_seconds() > 10:
                file_path = os.path.join(directory_to_watch, filename)
                if os.path.isfile(file_path):
                    self.checked_files.add(filename)

                    if time_difference.total_seconds() > 10:
                        print(f"File '{filename}' has been in the directory for more than ten seconds.")

    def on_created(self, event):
        if not event.is_directory:
            current_time = datetime.datetime.now()

            with open("timestamp.log", "a") as fh:
                fh.write(f"File {event.src_path} added at {current_time}\n")

if __name__ == "__main__":
    event_handler = MyHandler()
    time.sleep(5) #delay event by 5 seconds
    event_handler.check_existing_files()  # Initial check
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            event_handler.check_existing_files()  # Periodic check
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        observer.stop()

    observer.join()