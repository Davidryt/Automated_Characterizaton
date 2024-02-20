import matplotlib.pyplot as plt
import csv
import os

# Ruta al archivo CSV (modifica esto con la ruta a tu archivo)
percentaje = [11,54,81]
throughput = [10,20,30,40,50,60,70,80,90,100, 110, 120, 130]
for j in percentaje:
    for i in throughput: 
        src_csv = "grafana/Qbv_be_iperf_s"+str(j)+"m_"+str(i)+".csv"
        if not os.path.exists(src_csv):
            print(f"Archivo no encontrado: {src_csv}")
            continue  
        
        seconds = []
        jitter = []
        loss = []
        bitrate = []

        # Leer los datos del archivo CSV
        with open(src_csv, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Salta la cabecera
            for row in csvreader:
                seconds.append(float(row[0]))
                jitter.append(float(row[1]))
                loss.append(float(row[2].replace('%', '')))
                bitrate.append(float(row[3]))

        # Crear gráficos
        plt.figure(figsize=(10, 7))

        # Gráfico para Jitter
        plt.subplot(3, 1, 1)  # 3 filas, 1 columna, posición 1
        plt.plot(seconds, jitter, label='Jitter (ms)')
        plt.xlabel('Seconds')
        plt.ylabel('Jitter (ms)')
        plt.ylim(0,12)
        plt.xlim(0, 80)
        plt.title('Jitter for Best Effort Traffic with No Qbv over time for '+str(i)+' Mbits/sec and Shaper of '+str(j)+'% Mbits/sec')
        plt.legend()

        # Gráfico para Loss
        plt.subplot(3, 1, 2)  # 3 filas, 1 columna, posición 2
        plt.plot(seconds, loss, label='Loss (%)', color='red')
        plt.xlabel('Seconds')
        plt.ylabel('Loss (%)')
        plt.ylim(0, 100)
        plt.xlim(0, 80)
        plt.title('Packet Loss for Best Effort Traffic with No Qbv over time for '+str(i)+' Mbits/sec and Shaper of '+str(j)+'% of Mbits/sec')
        plt.legend()

        # Gráfico para Bitrate
        plt.subplot(3, 1, 3)  # 3 filas, 1 columna, posición 3
        plt.plot(seconds, bitrate, label='Bitrate (Mbits/sec)', color='green')
        plt.xlabel('Seconds')
        plt.ylabel('Receiver Bitrate (Mbits/sec)')
        plt.xlim(0, 80)
        plt.title('Bitrate for Best Effort Traffic with No Qbv over time for '+str(i)+' Mbits/sec and Shaper of '+str(j)+'% of Mbits/sec')
        plt.legend()

        # Ajusta el layout y muestra los gráficos
        plt.tight_layout()


        plt.savefig("grafana/plots/"+"Qbv_be_iperf_s"+str(j)+"m_"+str(i)+".png")
        plt.close()
