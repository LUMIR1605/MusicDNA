def energy(avg):
    if avg < 2500:
        return "Very soft emotional dynamics."
    elif avg < 5000:
        return "Gentle emotional dynamics with gradual evolution."
    elif avg < 9000:
        return "Medium-high dynamic energy with progressive emotional build."
    return "Very powerful dynamic energy with strong emotional impact."

def harmony(h):
    mood={
        "major":"bright, hopeful and uplifting",
        "minor":"melancholic, emotional and introspective"
    }.get(h.get("mode"),"balanced")
    return f"{h.get('key')} {h.get('mode')}, {mood}"

def emotions(labels):
    mapping={
        "Hope":"hopeful",
        "Power":"powerful",
        "Epic":"cinematic",
        "Longing":"longing",
        "Dark":"dark",
        "Reflection":"reflective"
    }
    return ", ".join(mapping.get(x,x.lower()) for x in labels)

def journey(data):
    out=[]
    emo=[x["emotion"] for x in data]

    if emo and emo[0]=="Reflection":
        out.append("Begins with an atmospheric reflective intro.")
    if "Story" in emo:
        out.append("Gradually introduces emotional storytelling.")
    if "Tension" in emo:
        out.append("Builds repeated emotional tension.")
    if "Release" in emo:
        out.append("Creates powerful emotional releases.")
    if emo and emo[-1]=="Reflection":
        out.append("Ends with a calm reflective outro.")

    return " ".join(out)

def build_prompt(dna):
    h=dna["harmony"]
    e=dna["energy"]
    emo=dna["emotion"]["labels"]
    j=dna["journey"]
    p=dna.get("production",{})

    dynamics=p.get("dynamics","medium dynamics")
    loudness=p.get("mean_volume",-10)

    return f"""
Original cinematic melodic house.

122 BPM.

{harmony(h)}

{energy(e['avg'])}

Emotion:
{emotions(emo)}

{journey(j)}

Hook Strategy:

Emotional Architecture:

Listener Memory:
Compose one unforgettable melodic phrase that listeners can remember after a single listen.
Keep the hook simple, emotional and repeatable.

Alternate tension and release repeatedly.
Never stay at maximum energy for too long.
Every climax must be earned through anticipation.

Repeat one memorable melodic hook throughout the song.
Each repetition should become slightly larger, wider and more emotional.
Never repeat it identically.
Increase emotional intensity with every return.


Production:
{dynamics}.
Integrated loudness around {loudness} LUFS.
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
    print("Prompt Engine v6")
