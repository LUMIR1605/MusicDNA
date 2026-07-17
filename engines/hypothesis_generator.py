import sys

from fact_engine import build as build_facts
from feature_engine import build as build_features

def build(path):

    facts=build_facts(path)
    features=build_features(facts)

    hypotheses=[]

    f={x["name"]:x["value"] for x in features}

    if f["reward_density"]>1.5:
        hypotheses.append(
            "High reward density may improve listener engagement."
        )

    if f["reward_ratio"]>0.6:
        hypotheses.append(
            "Frequent reward after tension may reinforce musical memory."
        )

    if f["tension_density"]>2:
        hypotheses.append(
            "Frequent tension cycles may maintain anticipation."
        )

    return hypotheses

if __name__=="__main__":

    h=build(sys.argv[1])

    print("="*60)
    print("HYPOTHESIS GENERATOR")
    print("="*60)

    for i,x in enumerate(h,1):
        print(i,x)
