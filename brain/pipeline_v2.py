import json

from engines.schema_builder import build
from engines.fact_engine import build as build_facts

dna = build()

facts = build_facts("dna/U2 - With Or Without You (TEEMID Edit).json")

dna["facts"] = facts

print("="*60)
print("PIPELINE V2")
print("="*60)

print(json.dumps(dna,indent=2,ensure_ascii=False))
