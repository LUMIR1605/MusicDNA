from engines.energy_pcm import analyze as energy_analyze
from engines.bpm_engine import detect_transients
from engines.spectrum_engine import analyze as spectrum_analyze
from engines.structure_engine import analyze as structure_analyze
from engines.pitch_engine import analyze_pitch
from engines.melody_tracker import analyze as melody_analyze
from engines.harmony_engine import analyze as harmony_analyze
from engines.emotion_engine import analyze as emotion_analyze
from engines.rules_engine import analyze as rules_analyze
from engines.knowledge_engine import analyze as knowledge_analyze
from engines.dna_store import save as save_dna
from engines.emotion_journey_engine import analyze as journey_analyze
from engines.emotion_curve_engine import analyze as curve_analyze
from engines.production_engine import analyze as production_analyze

def build(audio_file, title=None, metadata=None):
    dna = {
        "audio": {},
        "energy": {},
        "beats": {},
        "spectrum": {},
        "pitch": {},
        "melody": {},
        "structure": {},
        "harmony": {},
        "emotion": {},
        "journey": {},
        "curve": {},
        "production": {},
        "rules": {},
    }

    print("Loading Energy...")
    energy = energy_analyze(audio_file)
    dna["energy"] = {
        "frames": len(energy),
        "min": min(energy),
        "max": max(energy),
        "avg": sum(energy) / len(energy),
    }

    print("Loading Beats...")
    beats = detect_transients(audio_file)
    dna["beats"] = {
        "count": len(beats),
        "first": beats[0] if beats else None,
        "last": beats[-1] if beats else None,
    }

    print("Loading Spectrum...")
    dna["spectrum"] = spectrum_analyze(audio_file)

    print("Loading Structure...")
    dna["structure"] = structure_analyze(audio_file)

    print("Loading Pitch...")
    dna["pitch"] = analyze_pitch(audio_file)

    print("Loading Melody...")
    melody = melody_analyze(audio_file)
    dna["melody"] = {
        "frames": len(melody),
        "first": melody[0] if melody else None,
        "last": melody[-1] if melody else None,
    }

    print("Loading Harmony...")
    dna["harmony"] = harmony_analyze(audio_file)

    print("Loading Emotion...")
    dna["emotion"] = emotion_analyze(dna)

    print("Loading Emotion Journey...")
    dna["journey"] = journey_analyze(dna)

    print("Loading Production...")
    dna["production"] = production_analyze(audio_file)

    print("Loading Emotion Curve...")
    dna["curve"] = curve_analyze(dna)

    print("Loading Rules...")
    dna["rules"] = rules_analyze(dna)

    print("Loading Knowledge...")
    knowledge_analyze(title or audio_file, dna, metadata)

    path = save_dna(title or audio_file, dna)
    return dna, path

if __name__ == "__main__":
    import sys
    from pprint import pprint

    title = sys.argv[2] if len(sys.argv) > 2 else None
    pprint(build(sys.argv[1], title))
