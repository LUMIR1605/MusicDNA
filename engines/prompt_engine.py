def energy(avg):
    if avg < 2500:
        return "Very soft emotional dynamics."
    elif avg < 5000:
        return "Gentle emotional dynamics with gradual evolution."
    elif avg < 9000:
        return "Medium-high dynamic energy with progressive emotional build."
    else:
        return "Very powerful dynamic energy with strong emotional impact."


def harmony(h):
    key = h.get("key", "")
    mode = h.get("mode", "")

    if mode == "major":
        mood = "bright, hopeful and uplifting"
    elif mode == "minor":
        mood = "melancholic, emotional and introspective"
    else:
        mood = "balanced"

    return f"{key} {mode}, {mood}"


def emotions(labels):
    if not labels:
        return "Emotional"

    mapping = {
        "Hope": "hopeful",
        "Power": "powerful",
        "Epic": "cinematic",
        "Longing": "longing",
        "Dark": "dark",
        "Reflection": "reflective"
    }

    return ", ".join(mapping.get(x, x.lower()) for x in labels)


def journey(data):
    txt = []

    if not data:
        return ""

    first = data[0]["emotion"]
    last = data[-1]["emotion"]

    if first == "Reflection":
        txt.append("Begins with an atmospheric reflective intro.")

    if "Story" in [x["emotion"] for x in data]:
        txt.append("Gradually introduces emotional storytelling.")

    if "Tension" in [x["emotion"] for x in data]:
        txt.append("Builds repeated emotional tension.")

    if "Release" in [x["emotion"] for x in data]:
        txt.append("Creates powerful emotional releases.")

    if last == "Reflection":
        txt.append("Ends with a calm reflective outro.")

    return " ".join(txt)


def build_prompt(dna):

    h = dna["harmony"]
    e = dna["energy"]
    emo = dna["emotion"]["labels"]
    j = dna["journey"]

    return f"""
Original cinematic melodic house.

122 BPM.

{harmony(h)}

{energy(e['avg'])}

Emotion:
{emotions(emo)}

{journey(j)}

Production:
Wide stereo image.
Warm analog synthesizers.
Deep emotional bass.
Atmospheric pads.
Emotional piano.
Cinematic strings.
Large reverbs.
Professional modern mix.

Create a completely NEW original composition.

Do NOT imitate any existing melody.

Recreate only the emotional architecture, dynamics and atmosphere.
""".strip()


if __name__ == "__main__":
    print("Prompt Engine v3")
