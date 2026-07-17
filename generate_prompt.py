import json
import sys
from engines.prompt_engine import build_prompt

with open(sys.argv[1], encoding="utf-8") as f:
    dna = json.load(f)

print("=" * 60)
print("SUNO PROMPT")
print("=" * 60)
print(build_prompt(dna))
