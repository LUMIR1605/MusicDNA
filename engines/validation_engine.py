import json

def validate(law,total,supported):

    confidence=(supported/total)*100 if total else 0

    if total<5:
        level="HYPOTHESIS"
    elif total<20:
        level="CANDIDATE LAW"
    elif total<100:
        level="STRONG LAW"
    else:
        level="UNIVERSAL LAW"

    return{
        "law":law,
        "tested":total,
        "supported":supported,
        "confidence":round(confidence,1),
        "level":level
    }

if __name__=="__main__":

    from pprint import pprint

    pprint(validate(
        "Reward follows anticipation",
        1,
        1
    ))
