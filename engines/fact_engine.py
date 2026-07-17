import json
import sys

def build(path):

    dna=json.load(open(path,encoding="utf-8"))

    facts=[]

    facts.append({"name":"release_count","value":sum(1 for j in dna["journey"] if j["emotion"]=="Release")})
    facts.append({"name":"tension_count","value":sum(1 for j in dna["journey"] if j["emotion"]=="Tension")})
    facts.append({"name":"reflection_count","value":sum(1 for j in dna["journey"] if j["emotion"]=="Reflection")})
    facts.append({"name":"longing_count","value":sum(1 for j in dna["journey"] if j["emotion"]=="Longing")})
    facts.append({"name":"song_duration","value":round(dna["journey"][-1]["end"],1)})
    facts.append({"name":"primary_emotions","value":dna["emotion"]["labels"]})

    return facts

if __name__=="__main__":

    facts=build(sys.argv[1])

    print("="*60)
    print("FACT ENGINE")
    print("="*60)

    for f in facts:
        print(f["name"],":",f["value"])
