import json
import glob
from collections import defaultdict

graph=defaultdict(lambda:{
    "supported":[],
    "contradicted":[],
})

files=sorted(glob.glob("dna/*.json"))

all_rules=set()

for f in files:
    dna=json.load(open(f,encoding="utf-8"))
    all_rules.update(dna.get("rules",[]))

for rule in all_rules:

    for f in files:

        dna=json.load(open(f,encoding="utf-8"))

        title=f.split("/")[-1].replace(".json","")

        if rule in dna.get("rules",[]):
            graph[rule]["supported"].append(title)
        else:
            graph[rule]["contradicted"].append(title)

knowledge=[]

for rule,data in graph.items():

    tested=len(data["supported"])+len(data["contradicted"])

    confidence=round(len(data["supported"])/tested*100,1)

    knowledge.append({
        "statement":rule,
        "confidence":confidence,
        "supported":len(data["supported"]),
        "contradicted":len(data["contradicted"]),
        "support_titles":data["supported"],
        "counter_titles":data["contradicted"]
    })

knowledge.sort(key=lambda x:x["confidence"],reverse=True)

json.dump(
    knowledge,
    open("knowledge_graph.json","w",encoding="utf-8"),
    indent=2,
    ensure_ascii=False
)

print("="*60)
print("KNOWLEDGE GRAPH")
print("="*60)

for k in knowledge:

    print()
    print(k["statement"])
    print("Confidence :",k["confidence"],"%")
    print("Supported  :",k["supported"])
    print("Counter    :",k["contradicted"])

print()
print("Saved: knowledge_graph.json")
