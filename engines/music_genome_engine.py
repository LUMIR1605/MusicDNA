import json

laws=json.load(open("function_coverage.json",encoding="utf-8"))

genome={
    "core":[],
    "strong":[],
    "conditional":[],
    "genre_specific":[]
}

for f,c in laws.items():

    if c>=100:
        genome["core"].append(f)

    elif c>=80:
        genome["strong"].append(f)

    elif c>=50:
        genome["conditional"].append(f)

    else:
        genome["genre_specific"].append(f)

json.dump(
    genome,
    open("music_genome.json","w",encoding="utf-8"),
    indent=2,
    ensure_ascii=False
)

print("="*60)
print("MUSIC GENOME")
print("="*60)

for k,v in genome.items():
    print()
    print(k.upper())

    for x in v:
        print(" ",x)
