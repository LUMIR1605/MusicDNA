import statistics
from engines.bpm_engine import get_beats
import sys

def analyze_rhythm(audio_file):
    beats = get_beats(audio_file)

    if len(beats) < 2:
        print("Za mało beatów.")
        return

    intervals = [
        beats[i+1] - beats[i]
        for i in range(len(beats)-1)
    ]

    avg = statistics.mean(intervals)
    minimum = min(intervals)
    maximum = max(intervals)
    deviation = statistics.pstdev(intervals)

    print("=== RHYTHM ANALYZER ===")
    print(f"Liczba beatów      : {len(beats)}")
    print(f"Średni odstęp      : {avg:.4f} s")
    print(f"Najszybszy beat    : {minimum:.4f} s")
    print(f"Najwolniejszy beat : {maximum:.4f} s")
    print(f"Odchylenie         : {deviation:.5f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python rhythm_analyzer.py <plik>")
        sys.exit(1)

    analyze_rhythm(sys.argv[1])
