import matplotlib.pyplot as plt
import csv
import numpy as np

# Inicializa listas para almacenar las medias y varianzas
jitter_means = []
#jitter_variances = []
loss_means = []
#loss_variances = []
bitrate_means = []
#bitrate_variances = []

throughput = [10,20,30,40,50,60,70,80,90,100, 110, 120]
shaper = [25,50,75,100]
qtime = [25,50,75,100]
for s in shaper:
    for q in qtime:
        for i in throughput: 
            src_csv = "grafana/Qbv_be_iperf_q"+str(q)+"_s"+str(s)+"_"+str(i)+".csv"

            jitter_temp = []
            loss_temp = []
            bitrate_temp = []


            with open(src_csv, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)
                for row in csvreader:
                    jitter_temp.append(float(row[1]))
                    loss_temp.append(float(row[2].replace('%', '')))
                    bitrate_temp.append(float(row[3]))

            jitter_means.append(np.mean(jitter_temp))
            #jitter_variances.append(np.var(jitter_temp))
            loss_means.append(np.mean(loss_temp))
            #loss_variances.append(np.var(loss_temp))
            bitrate_means.append(np.mean(bitrate_temp))
            #bitrate_variances.append(np.var(bitrate_temp))

        plt.figure(figsize=(12, 18))

# Jitter
        plt.subplot(3, 1, 1)  
#plt.errorbar(throughput, jitter_means, yerr=np.sqrt(jitter_variances), label='Jitter Mean with Variance', fmt='-o', color='blue', ecolor='orange', elinewidth=3, capsize=0)
        plt.xlabel('Throughput (Mbits/sec)')
        plt.ylabel('Jitter (ms)')
        plt.ylim(0, 12)
        plt.title('Jitter Mean with Variance for Different Throughputs')
        plt.legend()
        plt.grid(True)

# Loss
        plt.subplot(3, 1, 2)
        plt.errorbar(throughput, loss_means, yerr=np.sqrt(loss_variances), label='Loss Mean with Variance', fmt='-o', color='red', ecolor='orange', elinewidth=3, capsize=0)
        plt.xlabel('Throughput (Mbits/sec)')
        plt.ylabel('Loss (%)')
        plt.ylim(0, 100)
        plt.title('Packet Loss Mean with Variance for Different Throughputs')
        plt.legend()
        plt.grid(True)

# Bitrate
        plt.subplot(3, 1, 3)
        plt.errorbar(throughput, bitrate_means, yerr=np.sqrt(bitrate_variances), label='Bitrate Mean with Variance', fmt='-o', color='green', ecolor='orange', elinewidth=3, capsize=0)
        plt.xlabel('Throughput (Mbits/sec)')
        plt.ylabel('Bitrate (Mbits/sec)')
        plt.title('Bitrate Mean with Variance for Different Throughputs')
        plt.legend()
        plt.grid(True)


        plt.tight_layout()
        plt.savefig("grafana/plots/All_Metrics_Summary.png")
        plt.close()
