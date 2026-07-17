import sys
from pprint import pprint

from core.runtime import RuntimeCapabilityError, require_core_capabilities


def main(audio_file):
    try:
        require_core_capabilities()
    except RuntimeCapabilityError as error:
        print(f"MusicDNA cannot start analysis: {error}")
        print("Install the project requirements and make ffmpeg available on PATH.")
        return 2

    from engines.dna_builder import build
    from engines.discovery_engine import analyze as discovery
    from engines.hypothesis_engine import analyze as hypothesis
    from engines.pattern_engine import analyze as patterns
    from brain.comparison_engine import analyze as compare
    from engines.statistics_engine import analyze as stats

    print("\n==============================")
    print("      LUMIR MUSIC DNA")
    print("==============================\n")

    dna, saved_path = build(audio_file)

    print("\n==============================")
    print("DNA")
    print("==============================")
    pprint(dna)
    print(f"\nDNA zapisane do: {saved_path}")

    print("\n==============================")
    print("DISCOVERY")
    print("==============================")
    discovery()

    print("\n==============================")
    print("HYPOTHESES")
    print("==============================")
    hypothesis(dna)

    print("\n==============================")
    print("PATTERNS")
    print("==============================")
    patterns()

    print("\n==============================")
    print("COMPARISON")
    print("==============================")
    compare()

    print("\n==============================")
    print("STATISTICS")
    print("==============================")
    stats()

    print("\n==============================")
    print("KONIEC")
    print("==============================")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie:")
        print('python main.py "/ścieżka/do/utworu.mp3"')
        sys.exit(1)

    sys.exit(main(sys.argv[1]))
