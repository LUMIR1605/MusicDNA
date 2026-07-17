def compare(original, generated):
    score = {}

    def pct(a, b):
        if a is None or b is None:
            return 0
        if a == 0:
            return 100 if b == 0 else 0
        return max(0, round((1 - abs(a - b) / abs(a)) * 100, 1))

    score["energy"] = pct(
        original["energy"]["avg"],
        generated["energy"]["avg"]
    )

    score["frames"] = pct(
        original["energy"]["frames"],
        generated["energy"]["frames"]
    )

    o = set(original["emotion"].get("labels", []))
    g = set(generated["emotion"].get("labels", []))

    score["emotion"] = round(
        len(o & g) / max(1, len(o | g)) * 100,
        1
    )

    score["structure"] = pct(
        len(original["structure"]),
        len(generated["structure"])
    )

    score["journey"] = pct(
        len(original["journey"]),
        len(generated["journey"])
    )

    total = round(sum(score.values()) / len(score), 1)

    print("\n========== RECONSTRUCTION ==========")
    for k, v in score.items():
        print(f"{k:<12}: {v}%")
    print("------------------------------------")
    print(f"TOTAL SCORE : {total}%")

    return total


if __name__ == "__main__":
    print("Reconstruction Engine v1")
