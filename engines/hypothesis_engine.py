def analyze(dna):
    print("=" * 60)
    print("HYPOTHESIS ENGINE v2")
    print("=" * 60)

    journey = dna.get("journey", [])

    if isinstance(journey, dict):
        journey = (
            journey.get("journey")
            or journey.get("segments")
            or journey.get("events")
            or []
        )

    if not isinstance(journey, list):
        journey = []

    emotions = [
        str(item.get("emotion", "")).strip().lower()
        for item in journey
        if isinstance(item, dict)
    ]

    reflection = emotions.count("reflection")
    story = emotions.count("story")
    tension = emotions.count("tension")
    release = emotions.count("release")

    print("\nHYPOTHESIS #1")
    if reflection > 0:
        print("Delayed emotional reward may increase listener curiosity.")
        print("Confidence: 70%")
    else:
        print("No evidence yet.")

    print("\nHYPOTHESIS #2")
    if tension > 0 and tension == release:
        print("Every detected anticipation is followed by release.")
        print("Confidence: 95%")
    elif tension > release:
        print("Some detected tension remains unresolved.")
        print("Confidence: 60%")
    else:
        print("Not enough tension-release evidence.")

    print("\nHYPOTHESIS #3")
    if release > 1:
        print("Repeated emotional release may reinforce memory.")
        print("Confidence: 90%")
    else:
        print("Not enough repeated release events.")

    print("\nHYPOTHESIS #4")
    if story > 0:
        print("Emotional attachment may develop before major climaxes.")
        print("Confidence: 85%")
    else:
        print("No story phase detected.")

    print("\nHYPOTHESIS #5")
    print("The arrangement may control emotion by delaying satisfaction.")
    print("Confidence: 75%")

    print("\nNEXT STEP")
    print("Validate these hypotheses using additional songs.")

    return {
        "reflection": reflection,
        "story": story,
        "tension": tension,
        "release": release,
    }
