import json

schema=json.load(open("schema_v1.json",encoding="utf-8"))

print("="*60)
print("MUSIC DNA SCHEMA v1")
print("="*60)

for k in schema.keys():
    print("-",k)
