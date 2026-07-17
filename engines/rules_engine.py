import sys


def analyze(dna):

    print("=== RULES ENGINE v1 ===")
    print()

    rules = []

    harmony = dna.get("harmony", {})
    emotion = dna.get("emotion", {})
    energy = dna.get("energy", {})
    vocal = dna.get("vocal", {})
    structure = dna.get("structure", {})

    if harmony.get("mode") == "minor":
        rules.append(
            "Melancholijna tonacja buduje głębokie emocje."
        )

    if harmony.get("mode") == "major":
        rules.append(
            "Durowa tonacja wzmacnia poczucie nadziei."
        )

    labels = emotion.get("labels", [])

    if "Hope" in labels:
        rules.append(
            "Utwór prowadzi słuchacza w kierunku nadziei."
        )

    if "Longing" in labels:
        rules.append(
            "Silny element tęsknoty zwiększa emocjonalną więź."
        )

    if "Power" in labels:
        rules.append(
            "Kulminacja opiera się na sile wykonania."
        )

    if energy.get("avg", 0) < 3500:
        rules.append(
            "Średnia energia jest umiarkowana — emocje budowane są stopniowo."
        )

    if vocal.get("max", 0) > 10000:
        rules.append(
            "Wokal posiada bardzo mocny potencjał kulminacyjny."
        )

    sections = structure

    if sections:
        first = sections[0]

        if first.get("type") == "INTRO":
            duration = first["end"] - first["start"]

            if duration > 30:
                rules.append(
                    "Długie intro opóźnia emocjonalną nagrodę."
                )

    print("Odkryte reguły:")
    print()

    for i, rule in enumerate(rules, 1):
        print(f"{i}. {rule}")

    return rules


if __name__ == "__main__":

    print(
        "Rules Engine działa jako moduł dna_builder."
    )
