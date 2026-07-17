"""
engines/feedback_engine.py

Porównanie dwóch utworów w formacie Music DNA.
Zwraca szczegółowe metryki podobieństwa i rekomendacje.

Użycie:
    from engines.feedback_engine import compare
    result = compare(track_a, track_b)

Uruchomienie:
    python -m engines.feedback_engine
"""

import statistics
from typing import Any

DNA = dict[str, Any]
FeatureResult = dict[str, Any]


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> int:
    return round(max(lo, min(hi, value)))


def _section_durations(track: DNA, section_type: str) -> list[float]:
    return [
        s["end"] - s["start"]
        for s in track["structure"]
        if s["type"] == section_type
    ]


def _mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def _first_start(track: DNA, section_type: str) -> float | None:
    for s in track["structure"]:
        if s["type"] == section_type:
            return s["start"]
    return None


def _section_sequence(track: DNA) -> list[str]:
    return [s["type"] for s in track["structure"]]


def _sequence_similarity(seq_a: list[str], seq_b: list[str]) -> float:
    if not seq_a and not seq_b:
        return 100.0
    if not seq_a or not seq_b:
        return 0.0
    n, m = len(seq_a), len(seq_b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq_a[i - 1] == seq_b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[n][m]
    return lcs / max(n, m) * 100.0


def _label_overlap(labels_a: list[str], labels_b: list[str]) -> float:
    set_a, set_b = set(labels_a), set(labels_b)
    if not set_a and not set_b:
        return 100.0
    if not set_a or not set_b:
        return 0.0
    overlap = len(set_a & set_b)
    union = len(set_a | set_b)
    return overlap / union * 100.0


def _compare_energy(a: DNA, b: DNA) -> FeatureResult:
    avg_a = a["energy"]["avg"]
    avg_b = b["energy"]["avg"]
    diff = avg_b - avg_a
    pct_diff = abs(diff) / max(avg_b, 1e-9) * 100
    sim = _clamp(100.0 - pct_diff * 2)
    if abs(diff) < 0.02:
        rec = "Energia jest dobrze dopasowana."
    elif diff > 0:
        rec = f"Zwiększ średnią energię o około {pct_diff:.0f}% (cel: {avg_b:.3f})."
    else:
        rec = f"Zmniejsz średnią energię o około {pct_diff:.0f}% (cel: {avg_b:.3f})."
    return {
        "similarity": sim,
        "difference": f"generated={avg_a:.3f}, target={avg_b:.3f}, delta={diff:+.3f}",
        "recommendation": rec,
    }


def _compare_key(a: DNA, b: DNA) -> FeatureResult:
    key_a = a["harmony"]["key"]
    mode_a = a["harmony"]["mode"]
    key_b = b["harmony"]["key"]
    mode_b = b["harmony"]["mode"]
    key_match = key_a == key_b
    mode_match = mode_a == mode_b
    if key_match and mode_match:
        sim = 100
        rec = "Tonacja i tryb są identyczne."
    elif mode_match:
        sim = 60
        rec = f"Tryb ({mode_a}) się zgadza, ale klucz różni się: generated={key_a}, target={key_b}."
    elif key_match:
        sim = 50
        rec = f"Klucz ({key_a}) się zgadza, ale tryb różni się: generated={mode_a}, target={mode_b}."
    else:
        sim = 10
        rec = f"Zmień tonację z {key_a} {mode_a} na {key_b} {mode_b}."
    return {
        "similarity": sim,
        "difference": f"generated={key_a} {mode_a}, target={key_b} {mode_b}",
        "recommendation": rec,
    }


def _compare_emotions(a: DNA, b: DNA) -> FeatureResult:
    labels_a = a["emotion"]["labels"]
    labels_b = b["emotion"]["labels"]
    sim = _clamp(_label_overlap(labels_a, labels_b))
    only_b = sorted(set(labels_b) - set(labels_a))
    only_a = sorted(set(labels_a) - set(labels_b))
    parts: list[str] = []
    if only_b:
        parts.append(f"Brakuje emocji: {', '.join(only_b)}.")
    if only_a:
        parts.append(f"Nadmiarowe emocje: {', '.join(only_a)}.")
    rec = " ".join(parts) if parts else "Zestaw emocji jest dobrze dopasowany."
    return {
        "similarity": sim,
        "difference": f"generated={labels_a}, target={labels_b}",
        "recommendation": rec,
    }


def _compare_journey(a: DNA, b: DNA) -> FeatureResult:
    journey_a: list[str] = a.get("journey", [])
    journey_b: list[str] = b.get("journey", [])
    sim = _clamp(_sequence_similarity(journey_a, journey_b))
    if sim >= 90:
        rec = "Przebieg emocji jest bardzo zbliżony."
    elif sim >= 60:
        rec = f"Przebieg emocji częściowo się zgadza. Cel: {' → '.join(journey_b)}."
    else:
        rec = f"Przebieg emocji znacznie się różni. Zmień sekwencję na: {' → '.join(journey_b)}."
    return {
        "similarity": sim,
        "difference": (
            f"generated=[{', '.join(journey_a)}], "
            f"target=[{', '.join(journey_b)}]"
        ),
        "recommendation": rec,
    }


def _compare_structure(a: DNA, b: DNA) -> FeatureResult:
    seq_a = _section_sequence(a)
    seq_b = _section_sequence(b)
    sim = _clamp(_sequence_similarity(seq_a, seq_b))
    if sim >= 90:
        rec = "Układ sekcji jest bardzo zbliżony."
    elif sim >= 60:
        rec = f"Struktura częściowo zgodna. Docelowy układ: {' → '.join(seq_b)}."
    else:
        rec = f"Struktura znacznie się różni. Przebuduj układ na: {' → '.join(seq_b)}."
    return {
        "similarity": sim,
        "difference": (
            f"generated={' → '.join(seq_a)}, "
            f"target={' → '.join(seq_b)}"
        ),
        "recommendation": rec,
    }


def _compare_section_duration(
    a: DNA,
    b: DNA,
    section_type: str,
) -> FeatureResult:
    durs_a = _section_durations(a, section_type)
    durs_b = _section_durations(b, section_type)
    mean_a = _mean(durs_a)
    mean_b = _mean(durs_b)
    if mean_a is None and mean_b is None:
        return {
            "similarity": 100,
            "difference": f"Brak sekcji {section_type} w obu utworach.",
            "recommendation": f"Brak sekcji {section_type} — bez rekomendacji.",
        }
    if mean_a is None:
        return {
            "similarity": 0,
            "difference": f"Brak sekcji {section_type} w generated.",
            "recommendation": f"Dodaj sekcję {section_type} (cel: {mean_b:.1f}s).",
        }
    if mean_b is None:
        return {
            "similarity": 0,
            "difference": f"Brak sekcji {section_type} w target.",
            "recommendation": f"Usuń lub skróć {section_type} — nie występuje w docelowym.",
        }
    diff = mean_b - mean_a
    pct_diff = abs(diff) / max(mean_b, 1e-9) * 100
    sim = _clamp(100.0 - pct_diff * 1.5)
    if abs(diff) < 1.0:
        rec = f"Długość {section_type} jest dobrze dopasowana ({mean_a:.1f}s)."
    elif diff > 0:
        rec = (
            f"Wydłuż {section_type} o około {diff:.1f}s "
            f"(generated={mean_a:.1f}s, target={mean_b:.1f}s)."
        )
    else:
        rec = (
            f"Skróć {section_type} o około {abs(diff):.1f}s "
            f"(generated={mean_a:.1f}s, target={mean_b:.1f}s)."
        )
    return {
        "similarity": sim,
        "difference": (
            f"generated={mean_a:.2f}s, target={mean_b:.2f}s, delta={diff:+.2f}s"
        ),
        "recommendation": rec,
    }


def _compare_beats(a: DNA, b: DNA) -> FeatureResult:
    cnt_a = a["beats"]["count"]
    cnt_b = b["beats"]["count"]
    diff = cnt_b - cnt_a
    pct_diff = abs(diff) / max(cnt_b, 1) * 100
    sim = _clamp(100.0 - pct_diff * 1.5)
    if abs(diff) <= 2:
        rec = f"Liczba beatów jest dobrze dopasowana ({cnt_a})."
    elif diff > 0:
        rec = f"Zwiększ liczbę beatów o {diff} (generated={cnt_a}, target={cnt_b})."
    else:
        rec = f"Zmniejsz liczbę beatów o {abs(diff)} (generated={cnt_a}, target={cnt_b})."
    return {
        "similarity": sim,
        "difference": f"generated={cnt_a}, target={cnt_b}, delta={diff:+d}",
        "recommendation": rec,
    }


def _contextual_recommendations(
    a: DNA,
    b: DNA,
    feature_results: dict[str, FeatureResult],
) -> list[str]:
    recs: list[str] = []

    chorus_start_a = _first_start(a, "CHORUS")
    chorus_start_b = _first_start(b, "CHORUS")
    if chorus_start_a is not None and chorus_start_b is not None:
        delta = chorus_start_a - chorus_start_b
        if delta > 8:
            recs.append(
                f"Refren pojawia się zbyt późno — przesuń go wcześniej "
                f"o około {delta:.0f}s (cel: ~{chorus_start_b:.0f}s)."
            )
        elif delta < -8:
            recs.append(
                f"Refren pojawia się zbyt wcześnie — przesuń go o "
                f"~{abs(delta):.0f}s później (cel: ~{chorus_start_b:.0f}s)."
            )

    seq_a = _section_sequence(a)
    seq_b = _section_sequence(b)
    has_build_before_chorus_b = any(
        seq_b[i] == "BUILD" and seq_b[i + 1] == "CHORUS"
        for i in range(len(seq_b) - 1)
    )
    has_build_before_chorus_a = any(
        seq_a[i] == "BUILD" and seq_a[i + 1] == "CHORUS"
        for i in range(len(seq_a) - 1)
    )
    if has_build_before_chorus_b and not has_build_before_chorus_a:
        recs.append("Dodaj więcej napięcia przed CHORUS — dodaj sekcję BUILD.")

    build_durs_a = _section_durations(a, "BUILD")
    build_durs_b = _section_durations(b, "BUILD")
    mean_build_a = _mean(build_durs_a)
    mean_build_b = _mean(build_durs_b)
    if mean_build_a is not None and mean_build_b is not None:
        if mean_build_b - mean_build_a > 4:
            recs.append(
                f"Wydłuż BUILD o około {mean_build_b - mean_build_a:.0f}s "
                f"aby zwiększyć napięcie przed refrenem."
            )

    energy_sim = feature_results["energy"]["similarity"]
    avg_a = a["energy"]["avg"]
    avg_b = b["energy"]["avg"]
    if energy_sim < 60:
        pct = abs(avg_b - avg_a) / max(avg_b, 1e-9) * 100
        if avg_b > avg_a:
            recs.append(f"Zwiększ średnią energię o około {pct:.0f}%.")
        else:
            recs.append(f"Zmniejsz średnią energię o około {pct:.0f}%.")

    emotion_sim = feature_results["emotions"]["similarity"]
    if emotion_sim < 50:
        recs.append(
            "Zestaw emocji znacznie odbiega od oryginału — "
            "przejrzyj parametry generowania nastroju."
        )

    seen: set[str] = set()
    unique: list[str] = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique


def _duration_delta(a: DNA, b: DNA, section_type: str) -> float:
    mean_a = _mean(_section_durations(a, section_type))
    mean_b = _mean(_section_durations(b, section_type))
    if mean_a is None and mean_b is None:
        return 0.0
    if mean_a is None:
        return round(mean_b, 2)  # type: ignore[arg-type]
    if mean_b is None:
        return round(-mean_a, 2)
    return round(mean_b - mean_a, 2)


def _chorus_shift(a: DNA, b: DNA) -> float:
    start_a = _first_start(a, "CHORUS")
    start_b = _first_start(b, "CHORUS")
    if start_a is None and start_b is None:
        return 0.0
    if start_a is None:
        return round(-(start_b or 0.0), 2)
    if start_b is None:
        return round(start_a, 2)
    return round(start_b - start_a, 2)


def _build_fixes(a: DNA, b: DNA) -> dict[str, Any]:
    avg_a = a["energy"]["avg"]
    avg_b = b["energy"]["avg"]
    energy_pct = round((avg_b - avg_a) / max(avg_b, 1e-9) * 100, 2)
    beats_delta = b["beats"]["count"] - a["beats"]["count"]
    sections_a = {s["type"] for s in a["structure"]}
    sections_b = {s["type"] for s in b["structure"]}
    missing = sorted(sections_b - sections_a)
    extra   = sorted(sections_a - sections_b)
    return {
        "energy_percent":        energy_pct,
        "beats_delta":           beats_delta,
        "target_key":            b["harmony"]["key"],
        "target_mode":           b["harmony"]["mode"],
        "target_emotions":       list(b["emotion"]["labels"]),
        "journey_target":        list(b.get("journey", [])),
        "structure_target":      [s["type"] for s in b["structure"]],
        "chorus_shift_seconds":  _chorus_shift(a, b),
        "intro_duration_delta":  _duration_delta(a, b, "INTRO"),
        "verse_duration_delta":  _duration_delta(a, b, "VERSE"),
        "build_duration_delta":  _duration_delta(a, b, "BUILD"),
        "chorus_duration_delta": _duration_delta(a, b, "CHORUS"),
        "missing_sections":      missing,
        "extra_sections":        extra,
    }


def compare(track_a: DNA, track_b: DNA) -> dict[str, Any]:
    """
    Porównuje utwór wygenerowany (track_a) z docelowym (track_b).

    Args:
        track_a: DNA wygenerowanego utworu.
        track_b: DNA docelowego utworu.

    Returns:
        Słownik z podobieństwami, różnicami, rekomendacjami i fixes.
    """
    print("\n" + "=" * 60)
    print("[feedback_engine] START PORÓWNANIA")
    print(
        f"  generated : {track_a.get('title', 'brak tytułu')}\n"
        f"  target    : {track_b.get('title', 'brak tytułu')}"
    )
    print("=" * 60)

    features: dict[str, FeatureResult] = {
        "energy":          _compare_energy(track_a, track_b),
        "key":             _compare_key(track_a, track_b),
        "emotions":        _compare_emotions(track_a, track_b),
        "journey":         _compare_journey(track_a, track_b),
        "structure":       _compare_structure(track_a, track_b),
        "duration_INTRO":  _compare_section_duration(track_a, track_b, "INTRO"),
        "duration_BUILD":  _compare_section_duration(track_a, track_b, "BUILD"),
        "duration_VERSE":  _compare_section_duration(track_a, track_b, "VERSE"),
        "duration_CHORUS": _compare_section_duration(track_a, track_b, "CHORUS"),
        "beats":           _compare_beats(track_a, track_b),
    }

    for name, res in features.items():
        print(f"  [{res['similarity']:3d}/100] {name}: {res['difference']}")

    similarities = [res["similarity"] for res in features.values()]
    overall = round(statistics.mean(similarities), 1)

    sorted_features = sorted(features.items(), key=lambda x: x[1]["similarity"])
    largest_diff_name, largest_diff = sorted_features[0]
    strongest_match_name, strongest_match = sorted_features[-1]

    auto_recs: list[str] = [
        res["recommendation"]
        for res in features.values()
        if res["similarity"] < 95
        and "dobrze dopasowana" not in res["recommendation"]
        and "identyczne" not in res["recommendation"]
        and "bardzo zbliżony" not in res["recommendation"]
    ]

    contextual_recs = _contextual_recommendations(track_a, track_b, features)

    all_recs: list[str] = []
    seen: set[str] = set()
    for r in contextual_recs + auto_recs:
        if r not in seen:
            seen.add(r)
            all_recs.append(r)

    fixes = _build_fixes(track_a, track_b)

    result: dict[str, Any] = {
        "features": features,
        "overall_similarity": overall,
        "strongest_match": {
            "feature":    strongest_match_name,
            "similarity": strongest_match["similarity"],
            "detail":     strongest_match["difference"],
        },
        "largest_difference": {
            "feature":    largest_diff_name,
            "similarity": largest_diff["similarity"],
            "detail":     largest_diff["difference"],
        },
        "recommendations": all_recs,
        "fixes": fixes,
    }

    print("\n" + "=" * 60)
    print(f"[feedback_engine] Overall similarity: {overall}/100")
    print(f"  Najsilniejsze dopasowanie : {strongest_match_name} ({strongest_match['similarity']}/100)")
    print(f"  Największa różnica        : {largest_diff_name} ({largest_diff['similarity']}/100)")
    print(f"  Rekomendacje ({len(all_recs)}):")
    for r in all_recs:
        print(f"    • {r}")
    print(f"  Fixes:")
    for k, v in fixes.items():
        print(f"    {k}: {v}")
    print("=" * 60 + "\n")

    return result


if __name__ == "__main__":
    _demo_a: DNA = {
        "title": "Generated Track",
        "energy": {"frames": 100, "min": 0.1, "max": 0.8, "avg": 0.45},
        "beats": {"count": 64, "first": 0.2, "last": 28.0},
        "structure": [
            {"start": 0.0,  "end": 12.0, "type": "INTRO"},
            {"start": 12.0, "end": 44.0, "type": "VERSE"},
            {"start": 44.0, "end": 72.0, "type": "CHORUS"},
        ],
        "harmony": {"key": "C", "mode": "minor", "confidence": 0.85},
        "emotion": {"labels": ["sad", "tense"], "scores": {"sad": 0.7, "tense": 0.3}},
        "journey": ["tense", "sad", "melancholic"],
        "rules": [], "pitch": {}, "melody": {}, "spectrum": None, "curve": [],
    }
    _demo_b: DNA = {
        "title": "Target Track",
        "energy": {"frames": 120, "min": 0.2, "max": 0.95, "avg": 0.72},
        "beats": {"count": 80, "first": 0.1, "last": 30.0},
        "structure": [
            {"start": 0.0,  "end": 8.0,  "type": "INTRO"},
            {"start": 8.0,  "end": 32.0, "type": "VERSE"},
            {"start": 32.0, "end": 40.0, "type": "BUILD"},
            {"start": 40.0, "end": 64.0, "type": "CHORUS"},
        ],
        "harmony": {"key": "A", "mode": "major", "confidence": 0.92},
        "emotion": {"labels": ["happy", "energetic", "euphoric"], "scores": {"happy": 0.6, "energetic": 0.4}},
        "journey": ["energetic", "happy", "euphoric"],
        "rules": [], "pitch": {}, "melody": {}, "spectrum": None, "curve": [],
    }
    compare(_demo_a, _demo_b)
