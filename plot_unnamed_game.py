import os
import csv
import statistics
import matplotlib.pyplot as plt

# Script to plot results.csv
# Produces a line graph: x-axis n, y-axis avg_time
# d=4 -> green, d=6 -> magenta

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, 'results.csv')
PNG_OUT = os.path.join(HERE, 'results_plot.png')

if not os.path.exists(CSV_PATH):
    print(f"No se encontró {CSV_PATH}")
    raise SystemExit(1)

# Read CSV and group by (d, n)
data = {}  # data[d][n] = [times]
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            n = int(row['n'])
            d = int(row['d'])
            t = float(row['tiempo_promedio'])
        except Exception:
            # skip bad rows
            continue
        data.setdefault(d, {}).setdefault(n, []).append(t)

# Prepare series for d=4 and d=6
series = {}
for d in (4, 6):
    if d not in data:
        series[d] = ([], [])
        continue
    ns = sorted(data[d].keys())
    avg_times = [statistics.mean(data[d][n]) for n in ns]
    series[d] = (ns, avg_times)

# Plot
plt.figure(figsize=(9, 6))
if series[4][0]:
    plt.plot(series[4][0], series[4][1], marker='o', color='green', label='d=4')
if series[6][0]:
    plt.plot(series[6][0], series[6][1], marker='o', color='magenta', label='d=6')

plt.xlabel('n (tamaño del tablero)')
plt.ylabel('avg_time (s)')
plt.title('Tiempo medio por jugada vs tamaño del tablero')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig(PNG_OUT)
print(f'Gráfico guardado en: {PNG_OUT}')
try:
    plt.show()
except Exception:
    # In headless env, just exit after saving
    pass
