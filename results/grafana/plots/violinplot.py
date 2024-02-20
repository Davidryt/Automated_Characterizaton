import matplotlib.pyplot as plt
import csv

def generate_violinplot(data, title, ylabel, save_as):
    plt.figure(figsize=(10, 7))
    # Prepare data for violinplot
    data_values = [data[i] for i in data.keys()]
    plt.violinplot(data_values, showmeans=False, showmedians=True)
    plt.xticks(range(1, len(data.keys()) + 1), [str(i) for i in data.keys()])
    plt.title(title)
    plt.xlabel('Throughput (Mbits/sec)')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(save_as)
    plt.close()

# Lista de throughputs
throughput = [10,20,30,40,50,60,70,80,90,100, 110, 120, 130]

# Diccionarios para almacenar los datos de cada métrica
data_jitter = {i: [] for i in throughput}
data_loss = {i: [] for i in throughput}
data_bitrate = {i: [] for i in throughput}

# Procesar cada archivo CSV y acumular los datos en los diccionarios
for i in throughput:
    src_csv = "grafana/NoQbv_be_iperf_"+str(i)+".csv"
    with open(src_csv, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Salta la cabecera
        for row in csvreader:
            # Añadir los datos al diccionario correspondiente
            data_jitter[i].append(float(row[1]))
            data_loss[i].append(float(row[2].replace('%', '')))
            data_bitrate[i].append(float(row[3]))

generate_violinplot(data_jitter, 'Jitter for Different Throughputs', 'Jitter (ms)', 'grafana/plots/violinplot_jitter.png')
generate_violinplot(data_loss, 'Packet Loss for Different Throughputs', 'Loss (%)', 'grafana/plots/violinplot_loss.png')
generate_violinplot(data_bitrate, 'Bitrate for Different Throughputs', 'Bitrate (Mbits/sec)', 'grafana/plots/violinplot_bitrate.png')
