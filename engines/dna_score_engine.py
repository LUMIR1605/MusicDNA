import json
import sys

a=json.load(open(sys.argv[1],encoding="utf-8"))
b=json.load(open(sys.argv[2],encoding="utf-8"))

score=0
total=0

def add(name,val):
    global score,total
    total+=1
    score+=val
    print(f"{name:<22}{val:3d}%")

# Harmony
add("Harmony",100 if a["harmony"]["mode"]==b["harmony"]["mode"] else 0)

# Emotion
ea=set(a["emotion"]["labels"])
eb=set(b["emotion"]["labels"])
inter=len(ea&eb)
union=max(len(ea|eb),1)
add("Emotion",round(inter/union*100))

# Structure
sa=[x["type"] for x in a["structure"]]
sb=[x["type"] for x in b["structure"]]
same=sum(x==y for x,y in zip(sa,sb))
add("Structure",round(same/max(len(sa),len(sb))*100))

# Energy
ea=a["energy"]["avg"]
eb=b["energy"]["avg"]
diff=abs(ea-eb)/max(ea,eb)
add("Energy",max(0,round((1-diff)*100)))

print("="*40)
print(f"OVERALL DNA SCORE : {round(score/total,1)}%")
