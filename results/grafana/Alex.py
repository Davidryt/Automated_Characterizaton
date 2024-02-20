import matplotlib.pyplot as plt
import csv
import numpy as np
import itertools
from scipy import stats

# Configuración de los arrays de configuración
throughput = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
shaper = [25, 50, 75, 100]
qtimes = [25, 50, 75, 100]

for qtime in qtimes:
    combinations = [(qtime, s) for s in shaper]
    results = {comb: {'jitter_means': [], 'jitter_conf_intervals': [], 'loss_means': [], 'loss_conf_intervals': [], 'bitrate_means': [], 'bitrate_conf_intervals': []} for comb in combinations}

    for comb in combinations:
        for th in throughput:
            src_csv = f"grafana/Qbv_be_iperf_q{comb[0]}_s{comb[1]}_{th}.csv"
            
            jitter_temp, loss_temp, bitrate_temp = [], [], []

            try:
                with open(src_csv, 'r') as csvfile:
                    csvreader = csv.reader(csvfile)
                    next(csvreader)  # Saltar la cabecera
                    for row in csvreader:
                        jitter_temp.append(float(row[1]))
                        loss_temp.append(float(row[2].replace('%', '')))
                        bitrate_temp.append(float(row[3]))

                # Mean and conf value
                for metric_temp, metric_key in zip([jitter_temp, loss_temp, bitrate_temp], ['jitter', 'loss', 'bitrate']):
                    mean = np.mean(metric_temp)
                    ci = stats.sem(metric_temp) * stats.t.ppf((1 + 0.95) / 2., len(metric_temp)-1)
                    results[comb][f'{metric_key}_means'].append(mean)
                    results[comb][f'{metric_key}_conf_intervals'].append(ci)
            except FileNotFoundError:
                print(f"Archivo no encontrado: {src_csv}")
                continue

    # Crear gráficos
    plt.figure(figsize=(18, 12))

    # Función auxiliar para plotear con intervalos de confianza
    def plot_metric_with_confidence(ax, metric_means, metric_conf_intervals, title, ylabel):
        colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(combinations))))
        for comb, data in results.items():
            means = data[metric_means]
            conf_intervals = data[metric_conf_intervals]
            color = next(colors)
            ax.errorbar(throughput, means, yerr=conf_intervals, label=f'QTime {comb[0]}, Shaper {comb[1]}', fmt='-o', color=color, capsize=5)
        
        if 'jitter_means' in metric_means:
            ax.set_ylim(-3, 3)
        ax.set_title(title)
        ax.set_xlabel('Throughput (Mbits/sec)')
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True)

    # Jitter
    ax1 = plt.subplot(3, 1, 1)
    plot_metric_with_confidence(ax1, 'jitter_means', 'jitter_conf_intervals', f'Jitter Mean with Confidence Intervals, QTime={qtime}', 'Jitter (ms)')

    # Loss
    ax2 = plt.subplot(3, 1, 2)
    plot_metric_with_confidence(ax2, 'loss_means', 'loss_conf_intervals', f'Packet Loss Mean with Confidence Intervals, QTime={qtime}', 'Loss (%)')

    # Bitrate
    ax3 = plt.subplot(3, 1, 3)
    plot_metric_with_confidence(ax3, 'bitrate_means', 'bitrate_conf_intervals', f'Bitrate Mean with Confidence Intervals, QTime={qtime}', 'Bitrate (Mbits/sec)')

    plt.tight_layout()
    plt.savefig(f"grafana/plots/All_Metrics_Summary_Comprehensive_CI_qtime_{qtime}.png")
    plt.close()
