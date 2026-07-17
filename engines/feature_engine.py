import json
import sys

def build(facts):

    data={f["name"]:f["value"] for f in facts}

    duration=data["song_duration"]/60

    features=[]

    features.append({
        "name":"reward_density",
        "value":round(data["release_count"]/duration,2)
    })

    features.append({
        "name":"tension_density",
        "value":round(data["tension_count"]/duration,2)
    })

    features.append({
        "name":"reward_ratio",
        "value":round(data["release_count"]/max(data["tension_count"],1),2)
    })

    return features

if __name__=="__main__":

    from fact_engine import build as facts_build

    facts=facts_build(sys.argv[1])

    features=build(facts)

    print("="*60)
    print("FEATURE ENGINE")
    print("="*60)

    for f in features:
        print(f["name"],":",f["value"])
