from brain.scanner import scan
from brain.pipeline import analyze
from brain.registry import exists, add
import sys


def run(folder):

    files = scan(folder)

    print()

    for i, file in enumerate(files, 1):

        file = str(file)

        if exists(file):
            print(f"[{i}/{len(files)}] Pomijam: {file}")
            continue

        print("=" * 60)
        print(f"[{i}/{len(files)}] {file}")
        print("=" * 60)

        analyze(file)

        add(file)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("python -m brain.scan_all <folder>")
        raise SystemExit(1)

    run(sys.argv[1])
