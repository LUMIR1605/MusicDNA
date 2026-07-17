import json

def sample(fusion,dna,event="Release",window=5.0):

    out=[]

    for j in dna["journey"]:

        if j["emotion"]!=event:
            continue

        start=j["start"]

        frames=[
            x for x in fusion
            if start-window<=x["time"]<=start
        ]

        out.append({
            "event":event,
            "time":start,
            "frames":frames
        })

    return out
