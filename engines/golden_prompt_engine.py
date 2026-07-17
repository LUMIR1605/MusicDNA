import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

emotion=", ".join(dna["emotion"]["labels"])
key=dna["harmony"]["key"]
mode=dna["harmony"]["mode"]
bpm=122

print("="*60)
print("GOLDEN PROMPT")
print("="*60)

print(f"""Compose a completely NEW original cinematic melodic house track.

{bpm} BPM.

Key: {key} {mode}.

Create an emotional journey from curiosity to hope.

Delay gratification.

Build emotional attachment before introducing full energy.

Create one unforgettable melodic hook.

Repeat the hook several times.

Every repetition should become slightly bigger, wider and emotionally stronger.

Never reveal the full arrangement too early.

Increase brightness, width and energy gradually.

Alternate tension and emotional release continuously.

Every climax must feel earned.

During emotional peaks use:

Deep bass.
Warm analog synths.
Wide stereo image.
Atmospheric pads.
Emotional piano.
Cinematic strings.
Large reverbs.

Finish with a spacious reflective outro.

Target emotions:
{emotion}

Do NOT imitate any melody, harmony or lyrics.

Recreate only the emotional architecture and psychological journey.""")
