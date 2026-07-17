import sys
import numpy as np

from engines.bpm_engine import detect_transients

transients = detect_transients(sys.argv[1])

intervals = np.diff(transients)

print()
print("=== TRANSIENT STATS ===")
print()

print("Liczba:", len(intervals))
print("Min   :", round(intervals.min(), 4))
print("Max   :", round(intervals.max(), 4))
print("Średnia:", round(intervals.mean(), 4))
print("Mediana:", round(np.median(intervals), 4))

print()
print("Pierwsze 100 odstępów:")

for x in intervals[:100]:
    print(round(float(x),4))
