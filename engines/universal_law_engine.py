import json

coverage=json.load(open("function_coverage.json",encoding="utf-8"))

print("="*60)
print("UNIVERSAL LAW ENGINE")
print("="*60)

for f,c in coverage.items():

    if c>=100:
        label="CORE LAW"

    elif c>=80:
        label="STRONG LAW"

    elif c>=50:
        label="CONDITIONAL LAW"

    else:
        label="GENRE SPECIFIC"

    print(f"{f:6} {c:5.1f}%   {label}")
