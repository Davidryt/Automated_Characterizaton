import os
import csv
import re
import mysql.connector
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            self.process(event.src_path)
    
    def process(self, file_path):
        file_name = os.path.basename(file_path)
        pattern = r"([A-Za-z]+)_([A-Za-z]+)_iperf_\d+\.csv"
        match = re.match(pattern, file_name)
        
        if match:
            table_name = f"{match.group(1)}_{match.group(2)}".replace('+', '_')
        else:
            print(f"No se encontró una tabla correspondiente para {file_name}.")
            return
        
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='grafana_user',
                password='NetcomGrafanaUser',
                database='grafana_iperf_data'
            )
            cursor = connection.cursor()
            
            with open(file_path, 'r') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Saltar la cabecera
                for row in csv_reader:
                    loss_percentage = float(row[2].replace('%', '')) if '%' in row[2] else float(row[2])
                    
                    cursor.execute(
                        f"INSERT INTO {table_name} (`Second`, `Jitter_ms`, `Loss_Percentage`, `Bitrate`) VALUES (%s, %s, %s, %s)",
                        (row[0], row[1], loss_percentage, row[3])
                    )

                    
            connection.commit()
            print(f"Archivo {file_path} procesado y añadido a {table_name}.")
        except mysql.connector.Error as err:
            print(f"Error al insertar datos: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    path = '.'
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
