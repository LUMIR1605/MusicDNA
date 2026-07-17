import json
from copy import deepcopy

SCHEMA=json.load(open("schema_v1.json",encoding="utf-8"))

def build():
    return deepcopy(SCHEMA)

if __name__=="__main__":
    dna=build()
    print(json.dumps(dna,indent=2,ensure_ascii=False))
