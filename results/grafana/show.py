import matplotlib.pyplot as plt
import csv

throughput = [10,20,30,40,50,60,70,80,90,100, 110, 120]
shaper = [25,50,75,100]
qtime = [25,50,75,100]
for s in shaper:
    for q in qtime:
        for i in throughput: 
            src_csv = "grafana/Qbv_be_iperf_q"+str(q)+"_s"+str(s)+"_"+str(i)+".csv"
            seconds = []
            jitter = []
            loss = []
            bitrate = []

            with open(src_csv, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  
                for row in csvreader:
                    seconds.append(float(row[0]))
                    jitter.append(float(row[1]))
                    loss.append(float(row[2].replace('%', '')))
                    bitrate.append(float(row[3]))


            plt.figure(figsize=(10, 7))

    # # Gráfico para Jitter
            plt.subplot(3, 1, 1)  # 3 filas, 1 columna, posición 1
            plt.plot(seconds, jitter, label='Jitter (ms)')
            plt.xlabel('Seconds')
            plt.ylabel('Jitter (ms)')
            plt.ylim(0,12)
            plt.xlim(0, 80)
            plt.title('Jitter for BE with Qbv over time for '+str(i)+' Mbits/sec')
            plt.legend()


            plt.subplot(3, 1, 2)  # 3 filas, 1 columna, posición 2
            plt.plot(seconds, loss, label='Loss (%)', color='red')
            plt.xlabel('Seconds')
            plt.ylabel('Loss (%)')
            plt.ylim(0, 100)
            plt.xlim(0, 80)
            plt.title('Packet Loss for BE with Qbv over time for '+str(i)+' Mbits/sec')
            plt.legend()

    # # Gráfico para Bitrate
            plt.subplot(3, 1, 3)  # 3 filas, 1 columna, posición 3
            plt.plot(seconds, bitrate, label='Bitrate (Mbits/sec)', color='green')
            plt.xlabel('Seconds')
            plt.ylabel('Receiver Bitrate (Mbits/sec)')
            plt.xlim(0, 80)
            plt.title('Bitrate for BE with Qbv over time for '+str(i)+' Mbits/sec')
            plt.legend()

    # Ajusta el layout y muestra los gráficos
            plt.tight_layout()


            plt.savefig("grafana/plots/all_measures_plot/Qbv_be_iperf_q"+str(q)+"_s"+str(s)+"_"+str(i)+".png")
            plt.close()

    
