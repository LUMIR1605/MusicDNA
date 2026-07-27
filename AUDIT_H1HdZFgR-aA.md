# Audyt źródłowy pomiarów: H1HdZFgR-aA

Zakres: pomiar na znormalizowanym, mono, 48 kHz PCM WAV dla `H1HdZFgR-aA`. Ten dokument nie ustala muzycznych cech utworu; opisuje wyłącznie wykryte błędy pomiaru i granice wiarygodności.

## Dane referencyjne i walidacja

- **H1 transient reference:** rzeczywisty rozkład 660 odstępów zawiera modalny odstęp około `0.64 s`; odpowiada to około `93.75 BPM`. Test `test_h1_like_transient_intervals_do_not_return_the_autocorrelation_subharmonic` zawiera jego dyskretny, bezplikowy odpowiednik.
- **EBU R128 reference:** końcowe podsumowanie ffmpeg dla H1: `I = -17.5 LUFS`, `LRA = 1.8 LU`, crest factor `5.716167`. Test zawiera również wcześniejszą mylącą chwilową linię `I = -70.0 LUFS`.
- **Structure reference:** test umieszcza czteroklatkowy (0.4 s) skok energii pomiędzy stabilnymi odcinkami; wynik nie może zawierać segmentu krótszego niż 2 s.
- **Tonal reference:** test wykorzystuje ciszę, sinus 220 Hz, szerokopasmowy szum oraz sinus 440 Hz. Akceptowane są wyłącznie dwa ciągłe fragmenty tonalne.
- **Harmony reference:** deterministyczny szum o płaskiej chromie nie może zwrócić potwierdzonej tonacji.

## FAKT / BŁĄD / PRZYCZYNA / POPRAWKA / TEST / WYNIK

| Silnik | FAKT | BŁĄD | PRZYCZYNA | POPRAWKA | TEST | WYNIK H1 po poprawce |
|---|---|---|---|---|---|---|
| `structure_engine` | Poprzednio 103 segmenty: 49 `CHORUS`, 50 `BUILD`, minimum 0.1 s. | Poziom energii był raportowany jako forma muzyczna. | Przejście przez stałe progi i brak minimalnego czasu segmentu. | Scalanie zmian krótszych niż 2 s; wynik ma `type=UNKNOWN`, `energy_band`, `status=uncertain`. | `test_structure_rejects_sub_two_second_energy_flicker` | 34 stabilne segmenty energii, minimum 2.0 s; brak twierdzeń o zwrotce/refrenie. |
| `production_engine` | Log EBU R128 ma chwilowe `I=-70.0`, lecz końcowe `I=-17.5 LUFS`; końcowe `LRA=1.8 LU`. | Zwracał −70 LUFS, 94.878658 jako „dynamic range” i `null` centroid. | Regex wybierał pierwszą linię, `astats` dynamic range nie jest LRA, a `aspectralstats` pisał metadane bez tekstu do parsowania. | Parsowanie wyłącznie końcowego podsumowania EBU R128; `dynamic_range` to LRA w LU; centroid to mediana z niecichych ramek FFT. | `test_production_reads_final_ebu_summary_not_initial_silence_frame` | `-17.5 LUFS`, `1.8 LU`, crest `5.716167`, centroid `2939.33 Hz`, `estimated`. |
| `rhythm_engine` | Najczęstszy wiarygodny odstęp transientów H1 wynosi około 0.64 s. | 62.5 BPM miało status `estimated`. | Niewycentrowana autokorelacja energii wybrała długi lag obwiedni zamiast modalnego odstępu onsetów. | Histogram/mediana modalnego odstępu 0.30–1.00 s; confidence = udział wspierających odstępów. | `test_h1_like_transient_intervals_do_not_return_the_autocorrelation_subharmonic` | `93.75 BPM`, confidence `0.262`, `uncertain` — brak twierdzenia o pewnym tempie. |
| `harmony_engine` | Dominacja chromy C# wynosiła 0.118. | `C# minor` był pokazywany jak ustalona tonacja. | Brak progu dominacji i rozdzielenia major/minor. | `candidate_key`/`candidate_mode` są zachowane diagnostycznie; `key` i `mode` są `null` przy niskiej pewności. | `test_harmony_with_flat_chroma_is_not_reported_as_a_key` | kandydat `C# minor`, confidence `0.118`, `uncertain`; bez raportowanej tonacji. |
| `pitch_engine`, `melody_tracker` | Dominujący pik FFT może należeć do perkusji, ciszy lub alikwotu. | Każda rama z pikiem 50–2000 Hz była traktowana jako pitch/melody. | Brak bramki energii, płaskości spektralnej i ciągłości tonalnej. | Odrzucanie ciszy i ramek szerokopasmowych; wymagane co najmniej 4 kolejne ramki tonalne. | `test_pitch_and_melody_reject_silence_and_broadband_percussion` | 725/7216 ramek tonalnych, confidence `0.053`, `uncertain`; brak pewnego pitch/melody. |
| `emotion_engine` | Emocje zależą od pitch i tonacji. | Etykiety emocji powstawały mimo niskiej pewności tonacji i pitch. | Brak zależności od statusów pomiarów wejściowych. | Etykiety są puste przy niepewnym pitch lub harmony. | `test_emotion_and_journey_do_not_label_uncertain_measurements` | `labels=[]`, `uncertain`. |
| `emotion_journey_engine`, `emotion_curve_engine` | Forma H1 pochodzi wyłącznie z energii i jest `uncertain`. | Zwracały opowieść typu `Release`/`Tension` i score 35–90. | Sztywne mapowanie nazw sekcji na emocje i liczby. | Zwracają `UNKNOWN`/`null` oraz `unavailable`, gdy struktura nie jest potwierdzona. | `test_emotion_and_journey_do_not_label_uncertain_measurements`, `test_emotion_curve_console_output_is_safe_for_cp1250` | Brak narracji emocjonalnej i brak liczbowej krzywej. |

## Metody obecne po audycie

- **Structure:** stabilne segmentowanie energii; nie jest klasyfikatorem formy muzycznej.
- **Production:** końcowe statystyki EBU R128 i medianowy centroid FFT z ramek niecichych.
- **Rhythm:** modalny odstęp transientów z jawnym wsparciem statystycznym.
- **Harmony:** dominacja chromy oraz różnica między tercją małą i wielką; wynik poniżej progów jest kandydatem, nie tonacją.
- **Pitch/melody:** pik tonalny tylko w niecichej, niepłaskiej spektralnie ramce i tylko w ciągłym fragmencie.
- **Emotion/journey/curve:** blokada wnioskowania, gdy dane wejściowe są niepewne.
