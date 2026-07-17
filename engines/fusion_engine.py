import json

def nearest(timeline,time,key):

    best=min(timeline,key=lambda x:abs(x["time"]-time))
    return best.get(key)

def build(energy,brightness):

    out=[]

    for e in energy["timeline"]:

        t=e["time"]

        out.append({
            "time":t,
            "energy":e["value"],
            "brightness":nearest(brightness["timeline"],t,"centroid")
        })

    return out
