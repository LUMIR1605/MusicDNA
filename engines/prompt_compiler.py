import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import sys
from engines.prompt_engine_v8 import build_prompt

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("PROMPT DNA")
print("="*60)
print(build_prompt(dna))
