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
    p=dna["production"]

    return f"""
Compose a completely NEW original song.

122 BPM.

Key:
{harmony(h)}

Primary emotional goal:

Build hope through gradual emotional escalation.

Composition instructions:

Start with only atmospheric pads and emotional piano.

Keep the opening intimate.

Delay drums.

Delay the emotional payoff.

Introduce bass and groove naturally.

Increase brightness gradually.

Open filters before every major release.

Expand stereo width progressively.

Keep one memorable melodic hook throughout the song.

Repeat the hook several times.

Never repeat it exactly.

Each repetition must feel larger, wider and emotionally stronger.

Alternate tension and release continuously.

Never remain at maximum intensity for long.

Every climax must be earned.

Use powerful vocal delivery only during emotional peaks.

Production:

{p.get("dynamics","medium dynamics")}.

Integrated loudness around {p.get("mean_volume",-11.5)} LUFS.

Warm analog synthesizers.

Deep emotional bass.

Atmospheric pads.

Emotional piano.

Cinematic strings.

Large reverbs.

Professional modern mix.

Finish with a spacious reflective outro.

Do NOT imitate any existing melody.

Recreate only the emotional architecture and psychological journey.
""".strip()

if __name__=="__main__":
    print("Prompt Engine v8")
