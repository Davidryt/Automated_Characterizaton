import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import glob

class FileProcessor:
    def __init__(self, download_dir, result_dir, old_dir):
        self.download_dir = download_dir
        self.result_dir = result_dir
        self.old_dir = old_dir
        self.file_counter = 10

    def process_files(self):
        i=10
        while True:
            if os.path.exists(os.path.join(self.old_dir, f'tap_0_qbv_be_s54m_{i}M.csv')):
                i+=10
            else:
                break
        self.file_counter = i
        path_tap_0 = os.path.join(self.download_dir, 'tap_0.csv')
        path_tap_1 = os.path.join(self.download_dir, 'tap_1.csv')

        # Check if both files exist
        if os.path.exists(path_tap_0) and os.path.exists(path_tap_1):
            df_tap_0 = pd.read_csv(path_tap_0, header=None)
            df_tap_1 = pd.read_csv(path_tap_1, header=None)

            df_tap_0 = df_tap_0.iloc[:, :2]
            df_tap_1 = df_tap_1.iloc[:, :2]

            df_tap_0.set_index(1, inplace=True)
            df_tap_1.set_index(1, inplace=True)

            df_tap_0.columns = ['Value']
            df_tap_1.columns = ['Value']

            matched_df = df_tap_0.join(df_tap_1, lsuffix='_tap_0', rsuffix='_tap_1')
            matched_df['Difference'] = (matched_df['Value_tap_1'] - matched_df['Value_tap_0']) / 1000000

            result_path = os.path.join(self.result_dir, f'results_qbv_be_s54m_{self.file_counter}M.csv')
            matched_df[['Difference']].to_csv(result_path, index_label='ID')
            print(f"Results saved to {result_path}.")

            # Move and rename original files
            shutil.move(path_tap_0, os.path.join(self.old_dir, f'tap_0_qbv_be_s54m_{self.file_counter}M.csv'))
            shutil.move(path_tap_1, os.path.join(self.old_dir, f'tap_1_qbv_be_s54m_{self.file_counter}M.csv'))
            print(f"Original files moved to {self.old_dir}.")

            self.file_counter += 10
        else:
            print("Required files not found.")

class Watcher:
    def __init__(self, directory_to_watch, processor):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch
        self.processor = processor

    def run(self):
        event_handler = Handler(self.processor)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Observer Stopped")
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.processor.process_files()

if __name__ == "__main__":
    import time
    
    DOWNLOAD_DIR = "/home/netcom-i11-16/Downloads/results"
    RESULT_DIR = "/home/netcom-i11-16/Downloads/results/tsn_lab"
    OLD_DIR = "/home/netcom-i11-16/Downloads/results/tsn_lab/old"

    # Ensure result and old directories exist
    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(OLD_DIR, exist_ok=True)

    processor = FileProcessor(DOWNLOAD_DIR, RESULT_DIR, OLD_DIR)
    path_watcher = Watcher(DOWNLOAD_DIR, processor)
    path_watcher.run()

