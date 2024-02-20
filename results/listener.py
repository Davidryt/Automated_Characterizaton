import os
import csv
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class MyHandler(FileSystemEventHandler):
    def process(self, event):
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        
        base_file_name = os.path.basename(event.src_path)
        grafana_folder_path = os.path.join('.', 'grafana')
        
        if not os.path.exists(grafana_folder_path):
            os.makedirs(grafana_folder_path)
        
        csv_file_path = os.path.join(grafana_folder_path, base_file_name.replace('.txt', '.csv'))
        
        with open(event.src_path, 'r') as txt_file:
            lines = txt_file.readlines()[:-1]  # Ignora la última línea
        
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Second', 'Jitter', 'Loss', 'Bitrate'])

            for line in lines:
                if 'sec' in line and "Mbits/sec" in line:
                    parts = line.split()
                    if len(parts) > 9:
                        second = parts[2].split('-')[0]
                        jitter = parts[8]
                        # Extrae el porcentaje de pérdida desde "Lost/Total Datagrams"
                        loss_match = re.search(r'(\d+)/(\d+)', parts[10])
                        if loss_match:
                            loss_percent = float(loss_match.group(1)) / float(loss_match.group(2)) * 100
                        else:
                            loss_percent = 0.0
                        bitrate = parts[6]  # Asume que el bitrate está siempre en la posición 6
                        csv_writer.writerow([second, jitter, f"{loss_percent:.2f}%", bitrate])

        print(f'Archivo {csv_file_path} creado correctamente.')

    def on_created(self, event):
        self.process(event)

if __name__ == "__main__":
    path = '.'  # Directorio a monitorear
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
