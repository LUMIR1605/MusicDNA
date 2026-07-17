# MusicDNA Technical Audit - TASK-001

Audit date: 2026-07-18  
Repository: `C:\Users\lukas\Nowy folder\MusicDNA`  
Scope: repository inspection only. No production code, architecture, file names, or runtime behaviour were changed.

## 1. Executive summary

MusicDNA has a promising research-oriented layout, but it is not currently reproducible or reliable enough to support the claims in `VISION.md`. The immediate failures are operational and contractual rather than aesthetic: there is no dependency manifest, the primary command fails before analysis because `numpy` is unavailable, the main pipeline writes to a home-directory database without creating its parent directory, and the rhythm path records transient timestamps as "beats" without calculating BPM.

The repository contains a large collection of signal-processing and research scripts, but only a narrow path is wired into `main.py` through `engines/dna_builder.py`. Several outputs use incompatible schemas and paths. Many research conclusions are derived from uncalibrated heuristics but are stored or worded as evidence-supported laws. There are no automated tests.

Recommended outcome of the next repair package: make one analysis run reproducible, schema-valid, path-safe, and testable before changing any model, measurement, or product behaviour.

## 2. Audit method and limits

Inspected evidence:

- all 169 repository files outside `.git` were enumerated;
- all 133 Python files were parsed with Python AST (no syntax parse errors);
- import relationships and direct entry-point references were statically inspected;
- JSON files and schemas were parsed;
- the primary command, test discovery, dependency/tool availability, repository status, and git history were checked;
- the main pipeline, audio core, analysis engines, persistence engines, schemas, research engines, collectors, and documentation were manually reviewed.

Checks were intentionally non-destructive. No audio collection or analysis was started. Therefore, measurement quality findings are source-code findings, not a substitute for calibrated fixture-based experiments.

## 3. Architecture overview

```text
main.py
  -> engines.dna_builder.build(audio_path)
       -> core.ffmpeg_engine.load_pcm()
       -> energy, transient, spectrum, structure, pitch, melody, harmony engines
       -> emotion, journey, curve, production, rules engines
       -> engines.knowledge_engine.analyze()
       -> JSON written through engines.dna_store

Secondary / research paths
  analyze_all.py -> separate subprocess research engines -> dna/*.json
  knowledge_graph_engine.py -> reads dna/*.json -> knowledge_graph.json
  brain/*, discovery/*, collectors/*, music_worker.py -> separate or legacy workflows
```

The principal production-like path is `main.py -> engines/dna_builder.py`. It does not use most engine modules in the repository. Data storage is split between relative project paths (`dna/`, `research/`, root JSON files) and `%USERPROFILE%\music_dna\knowledge.json`; these locations are not governed by a single configuration contract.

## 4. Complete engine inventory

| Area | Main files | Current role and audit status |
|---|---|---|
| Entry points | `main.py`, `analyze_all.py`, `generate_prompt.py`, `music_worker.py` | `main.py` is the primary entry point. `analyze_all.py` launches independent scripts. `music_worker.py` performs work during import and points at another project's home-directory queue. |
| Decode and metadata | `core/ffmpeg_engine.py`, `core/audio_core.py`, `core/file_loader.py` | Depend on PATH tools (`ffmpeg`, `ffprobe`) without capability checks or declared installation requirements. |
| Main DNA assembly | `engines/dna_builder.py`, `engines/dna_store.py`, `engines/knowledge_engine.py` | Main assembly path. The knowledge write can fail on a clean machine because its parent directory is not created. |
| Rhythm and energy | `energy_pcm.py`, `bpm_engine.py`, `bpm_engine_v2.py`, `transient_stats.py`, `beat_strength.py`, `rhythm_analyzer.py`, `energy_pcm_v2.py` | Main builder calls `detect_transients`, not a BPM detector. V2 tempo detector is unused. `rhythm_analyzer.py` imports a missing `get_beats`. |
| Spectral and brightness | `spectrum_engine.py`, `centroid_engine.py`, `brightness_engine.py`, `brightness_timeline.py`, `spectrum_map.py`, `delta_spectrum_engine.py` | Main spectrum uses only the first five seconds. Centroid/brightness implementations overlap; some execute at import. |
| Pitch, melody, harmony | `pitch_engine.py`, `melody_tracker.py`, `melody_candidates.py`, `lead_engine.py`, `harmony_engine.py`, `chord_engine.py` | Pitch and melody use strongest FFT-bin heuristics. Harmony is raw chroma accumulation. `chord_engine.py` is empty. |
| Structure and arrangement | `structure_engine.py`, `arrangement_engine.py`, `layer_detector.py`, `layer_engine.py`, `density_engine.py`, `instrument_engine.py`, `orchestration_engine.py`, `transition_engine.py`, `timeline_engine.py` | Structure is energy-threshold labelling. Several related engines are not imported by the main path. |
| Production | `production_engine.py`, `vocal_engine.py`, `groove_engine.py`, `entropy_engine.py` | `production_engine.py` parses FFmpeg stderr but does not validate command success. Vocal and instrument labels are not source-separated measurements. |
| Emotion and narrative | `emotion_engine.py`, `emotion_journey_engine.py`, `emotion_curve_engine.py`, `narrative_engine.py`, `story_engine.py`, `dopamine_engine.py`, `reward_engine.py`, `surprise_engine.py`, `expectation_engine.py` | Main emotion/journey/curve results are direct transformations of heuristic inputs. `narrative_engine.py` invokes external `aubioonset`. |
| Rules, hypotheses, evidence | `rules_engine.py`, `hypothesis_engine.py`, `hypothesis_generator.py`, `evidence_engine_v2.py`, `counter_evidence_engine.py`, `falsification_engine.py`, `validation_engine.py`, `universal_law_engine.py`, `scientific_engine.py` | Rules and confidence labels are mostly authored thresholds or fixed values rather than measured statistical evidence. Several modules are script-style candidates not used by the main path. |
| Knowledge and comparison | `knowledge_engine.py`, `knowledge_graph_engine.py`, `cross_song_engine.py`, `correlation_engine.py`, `statistical_discovery_engine.py`, `discovery_engine.py`, `discovery_engine_v2.py`, `discovery/discovery_engine.py` | Uses multiple incompatible stores and overlapping discovery engines. The graph derives support from generated rules, not independent listener evidence. |
| Prompt and generation | `prompt_engine.py`, `prompt_engine_v6.py`, `prompt_engine_v7.py`, `prompt_engine_v8.py`, `prompt_compiler.py`, `golden_prompt_engine.py`, `generator_engine.py`, `composer_engine.py` | Current prompt module is used by `generate_prompt.py`; older versions remain. V8 expects a metric name that `production_engine.py` does not emit. |
| Brain and schema | `brain/pipeline.py`, `brain/pipeline_v2.py`, `brain/*.py`, `schema/dna_schema.json`, `schema_v1.json` | V2 reads a hard-coded DNA file at import. Three incompatible output contracts exist. |
| Collectors | `collectors/youtube_collector.py`, `youtube_search.py`, `registry.py` | Require `yt-dlp`/network but no dependency or failure contract is documented. |

This inventory distinguishes currently wired modules from candidate modules. Static lack of imports is not proof a script is never manually executed; candidate removals require an explicit owner decision and runtime usage evidence.

## 5. Critical bugs

### C1. The repository has no reproducible runtime contract

Evidence:

- No `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, or equivalent package/test configuration exists.
- `python main.py` fails immediately at `engines/energy_pcm.py:3` with `ModuleNotFoundError: No module named 'numpy'`.
- `core/ffmpeg_engine.py:7-25` invokes `ffmpeg`; `core/audio_core.py:7-18` invokes `ffprobe`; `collectors/youtube_collector.py:24-36` invokes `yt-dlp`; `engines/narrative_engine.py:4-14` invokes `aubioonset`.
- During the audit, `ffmpeg`, `ffprobe`, and `yt-dlp` were not available on PATH.

Impact: a clean developer, Windows, or Termux environment cannot reliably run the documented entry point. This is the first blocker.

### C2. The main pipeline cannot write its knowledge store on a clean machine

Evidence:

- `engines/knowledge_engine.py:4` uses `Path.home() / "music_dna" / "knowledge.json"`.
- `engines/knowledge_engine.py:11-14` conditionally reads the file, but `engines/knowledge_engine.py:25` writes it without `DB.parent.mkdir(...)`.
- `%USERPROFILE%\music_dna` did not exist during the audit.
- `engines/dna_builder.py:85-88` unconditionally calls `knowledge_analyze` near the end of every build.

Impact: after dependency issues are resolved, a first successful analysis can still fail during persistence.

### C3. The rhythm/BPM contract is incorrect

Evidence:

- `engines/dna_builder.py:2` imports `detect_transients`; `engines/dna_builder.py:42-48` writes transient timestamps into `dna["beats"]`.
- `engines/bpm_engine.py:11-56` detects energy-difference events and never calculates a BPM value.
- `engines/bpm_engine_v2.py:9-40` implements `detect_bpm`, but no main pipeline module imports it.
- `engines/rhythm_analyzer.py:2` imports `get_beats`; no `get_beats` definition exists in the repository.

Impact: labels and downstream reasoning can represent transient count/timestamps as beats even though no supported tempo estimate is made. This violates the central measurement objective in `VISION.md`.

### C4. DNA output has no single compatible schema or validation boundary

Evidence:

- `engines/dna_builder.py:17-31` emits `audio`, `energy`, `beats`, `spectrum`, `pitch`, `melody`, `structure`, `harmony`, `emotion`, `journey`, `curve`, `production`, and `rules`.
- `schema/dna_schema.json:1-14` expects a different set including `file`, `rhythm`, `mfcc`, `vocal`, and `summary`.
- `schema_v1.json:2-19` expects a third contract: `measurements`, `facts`, `features`, `hypotheses`, `evidence`, `laws`, and `prompt_rules`.
- No code validates builder output against either schema before persisting it.

Impact: downstream consumers can silently receive incomplete or differently named data. This is a data-integrity blocker.

### C5. Evidence and law confidence are not evidence-based

Evidence:

- `engines/emotion_engine.py:14-71` maps raw energy, event count, FFT-bin pitch, and a major/minor heuristic directly to emotion labels.
- `engines/structure_engine.py:11-77` labels sections from smoothed relative energy thresholds.
- `engines/emotion_journey_engine.py:18-57` and `engines/emotion_curve_engine.py:15-50` deterministically transform those labels into a journey and numeric curve.
- `engines/rules_engine.py:17-73` turns results into broad statements.
- `engines/knowledge_graph_engine.py:10-55` counts a generated rule as supported when the same generated rule is present, and calculates confidence as `support / tested` at line 37.
- `engines/hypothesis_engine.py:30-63` assigns fixed confidence numbers (for example 70, 75, 85, 90, 95) without a statistical estimator.

Impact: the repository may present internally generated heuristics as validated music knowledge. This conflicts with the evidence standard in `VISION.md` and `AGENTS.md`. The audit does not say these heuristics are useless; it says the output must be explicitly labelled as a hypothesis or heuristic until calibrated.

## 6. High-priority issues

| ID | Evidence | Risk |
|---|---|---|
| H1 | `brain/pipeline_v2.py:6-16`, `music_worker.py:19-79`, `brightness_engine.py:11-43`, `centroid_engine.py:13-36`, `smooth_energy.py:1-20`, and others run work at import. | Importing a module can read files, invoke commands, download/analyze, or fail unexpectedly. |
| H2 | `core/ffmpeg_engine.py:7-29` decodes whole audio files; at least 16 modules independently call `load_pcm`. | High CPU, memory use, and repeated decoding; especially poor on mobile/Termux. |
| H3 | `engines/bpm_engine_v2.py:25` uses full `np.correlate(..., "full")`. | O(N^2) tempo calculation can become impractical for long tracks. |
| H4 | `engines/spectrum_engine.py:10-43` analyses only the first five seconds; `pitch_engine.py:20-46` and `melody_tracker.py:16-50` use the strongest mixed-audio FFT bin. | Measurements can be non-representative and confuse harmonics with melody/fundamental frequency. |
| H5 | `engines/production_engine.py:8-46` parses stderr without checking process return status; output fields can be `None`. | Silent tool failure becomes apparently valid data. |
| H6 | `engines/vocal_engine.py:11-38` measures full-mix RMS, while `instrument_engine.py:12-40` uses bands as instrument labels. | Labels overstate what is actually measured. |
| H7 | `engines/dna_store.py:4-15`, `knowledge_engine.py:4-25`, `knowledge_graph_engine.py:10-55`, and `discovery_engine.py:5-6` use incompatible relative/root/home paths. | Data is split, overwritten, or invisible between platforms and runs. |
| H8 | `analyze_all.py` launches subprocesses without failure propagation; several script modules use bare sibling imports such as `engines/hypothesis_generator.py:3-4`. | Batch output can appear complete despite failed components; package imports are brittle. |
| H9 | `README.md` describes unrelated LUMIR OS onboarding rather than MusicDNA. Local display of several documents/messages showed mojibake; encoding cause was not byte-verified. | Users cannot reproduce the project; text may be unreadable in some environments. |
| H10 | No test files were found; `unittest` ran zero tests and `pytest` collected none. | Regression safety does not exist for measurement, schema, persistence, or error handling. |

## 7. Unreliable measurements and claims

### BPM, beats, transients

`bpm_engine.py` is a transient detector, not a BPM engine. `bpm_engine_v2.py` is not integrated and uses a raw autocorrelation heuristic without documented sampling, normalization, range selection, or fixture validation. The current builder's `beats` field is not a supported beat grid.

### Energy and loudness

`energy_pcm.py` uses raw decoded PCM magnitude. `core/ffmpeg_engine.py` converts `int16` to float without normalizing it, so fixed thresholds depend on mastering level and source format. `production_engine.py` can extract LUFS from FFmpeg output, but failures become `None` rather than a structured unavailable status.

### Centroid and spectrum

The centroid calculation itself is a conventional spectral descriptor in `brightness_timeline.py:11-45`, but its fixed label thresholds (900, 1800, 3500) are uncalibrated. `spectrum_engine.py` considers only the first five seconds and reports highest raw FFT magnitudes; it is not a song-wide spectral profile.

### Pitch, melody, harmony, and key

`pitch_engine.py`, `melody_tracker.py`, and `melody_candidates.py` choose dominant mixed-audio FFT bins. A dominant bin is not necessarily a vocal or melodic fundamental. `harmony_engine.py:22-69` accumulates pitch classes then compares a major/minor third; its `confidence` is concentration of energy, not validated key confidence. There is no verified chord detector in the active path.

### Structure, emotion, and emotion journey

Structure labels are energy bands, not verified form segmentation. Emotion, journey, and curve are direct deterministic transforms of those labels. They should not be called listener-measured emotion without a labelled validation set, versioned thresholds, error estimates, and counterexamples.

### Research conclusions

`knowledge_graph_engine.py` measures recurrence of rule text produced by the system. It does not independently test causal claims, listener response, or confounders. Existing counts should be treated as exploratory observations, not universal laws.

## 8. Duplicate, obsolete, dead, and unused candidates

No file was removed. The following are confirmed candidates or duplicate groups, not deletion instructions.

### Confirmed backup artifacts (five files)

- `engines/dna_builder.py.bak2`
- `engines/dna_builder.py.bak3`
- `engines/dna_builder.py.bak4`
- `engines/dna_builder.py.bak5`
- `engines/spectrum_engine.py.bak2`

They are historical copies, ignored by `.gitignore`, and have no import references. Preserve them outside the active engine namespace or retain them as an explicit archive only after an owner confirms no recovery need.

### Empty placeholder modules (four files)

- `database/vault.py`
- `engines/chord_engine.py`
- `engines/feedback_engine.py`
- `engines/music_dna.py`

Static inspection found no implementation body. `engines/generator_engine.py:1-12` describes itself as feedback-related and tells users to invoke `engines.feedback_engine`, while that destination is empty. This is a documentation/ownership defect, not proof these names can safely be deleted.

### Duplicate or superseded groups (seven groups)

1. `bpm_engine.py` versus unused `bpm_engine_v2.py`.
2. `energy_pcm.py` versus unused `energy_pcm_v2.py`.
3. `brightness_engine.py` versus `centroid_engine.py` / `brightness_timeline.py` overlapping centroid logic.
4. `prompt_engine.py`, `prompt_engine_v6.py`, `prompt_engine_v7.py`, and `prompt_engine_v8.py` with no version ownership policy.
5. `engines/discovery_engine.py`, `engines/discovery_engine_v2.py`, and `discovery/discovery_engine.py` with unrelated behaviours under similar names.
6. `brain/pipeline.py` and import-unsafe `brain/pipeline_v2.py`.
7. `generator_engine.py` and empty `feedback_engine.py` with mismatched stated invocation.

Static import analysis found many modules with no inbound Python import edge. Six research scripts are explicitly started by `analyze_all.py` through subprocess; all other no-inbound modules are candidates only. A manual owner/use-case review is required before archival or deletion.

## 9. Missing tests

No project test files exist. Required first tests, before algorithm changes:

1. Bootstrap tests: missing `numpy`, `ffmpeg`, `ffprobe`, `yt-dlp`, and unwritable data directories produce clear structured errors.
2. Persistence tests: clean home directory creates the knowledge parent and writes a valid record.
3. Schema tests: every `dna_builder.build()` result validates against one canonical, versioned schema.
4. Rhythm contract tests: known synthetic click tracks prove the meaning and units of transients, beat positions, and BPM.
5. Audio edge tests: empty, short, silent, stereo, unsupported, and malformed inputs.
6. Production tests: unavailable/failed FFmpeg returns a status, not silently populated `None` values.
7. Cross-platform path tests: Windows separators, Termux storage, and project-relative paths.
8. No-import-side-effect tests for library modules.
9. Regression fixtures for centroid, spectrum, key confidence, and structure outputs after calibration.

## 10. Performance risks

- Whole-file PCM is repeatedly decoded by many engines instead of being shared by one analysis context.
- `bpm_engine_v2.py` performs full autocorrelation, which is quadratic in input length.
- `knowledge_graph_engine.py` repeatedly opens each DNA file for each rule.
- `analyze_all.py` runs sequential subprocesses and does not expose a reliable completion/failure contract.
- Main and helper engines print intermediate samples, event details, and large result objects to the console. This adds noise and makes batch/mobile use harder to inspect.
- `knowledge.json` and `music_dna_prompt.txt` are multi-megabyte root artifacts; loading full knowledge repeatedly is a mobile/Termux risk as the data grows.

## 11. Mobile and Termux compatibility risks

- `smooth_energy.py`, `story_engine.py`, and `energy_plot.py` hard-code `/storage/emulated/0/...` paths.
- External executables are invoked by bare names without a portable installation or capability policy.
- `music_worker.py:8` points to `Path.home() / "lumir_air_v14" / "data" / "music_queue.json"`, which is outside this project and ties MusicDNA to another repository name.
- `knowledge_graph_engine.py` derives titles with `split('/')`, which is not Windows-path safe.
- Full-file repeated PCM decoding and O(N^2) autocorrelation are especially unsuitable for Termux memory and battery limits.

## 12. Data integrity and schema risks

- Three incompatible DNA contracts exist: the builder output, `schema/dna_schema.json`, and `schema_v1.json`.
- Root `knowledge.json` is not the same location used by `knowledge_engine.py`; the root file is not referenced by the active persistence path.
- `dna/` and `research/` are ignored, so generated evidence cannot be reproduced from git history by default.
- `None` production values are persisted without provenance, status, measurement unit, or error cause.
- `function_validator.py:13-52` executes at module import and divides by `len(songs)` at line 43 without an empty-data guard.
- `music_genome_engine.py:3-31` labels 100% coverage as core without a minimum sample-size rule.
- Derived labels and authored rule text are mixed with measured values without a shared evidence/status envelope.

## 13. Quick wins

These are recommendations for TASK-002, not changes made in this audit.

1. Define one dependency manifest and a documented environment check for Python modules and external binaries.
2. Add one canonical data-path configuration and create parent directories before every controlled write.
3. Choose one versioned DNA schema, validate at the builder boundary, and record unavailable/error status explicitly.
4. Correct the rhythm API contract before presenting BPM or beat claims.
5. Add a small synthetic-audio fixture suite and bootstrap/error-path tests.
6. Make analysis modules import-safe; keep executable scripts behind explicit `main()` entry guards.
7. Mark heuristic outputs as heuristic/hypothesis until validation data supports stronger language.
8. Reduce unstructured prints and use one controlled diagnostic mechanism.

## 14. Recommended repair order

### Package 1 - Reproducible and safe analysis baseline (recommended TASK-002)

1. Add a dependency/runtime declaration and capability checks for Python packages and required external binaries.
2. Establish one path policy and guarantee storage directory creation before writes.
3. Select one canonical, versioned DNA schema and validate main-builder output.
4. Repair the rhythm interface so transients, beat positions, and BPM have separate explicit fields and tested meanings.
5. Add automated tests for bootstrap, persistence, schema, and known synthetic rhythm fixtures.

### Package 2 - Measurement reliability

1. Share decoded PCM and metadata across engines.
2. Replace or constrain uncalibrated fixed thresholds using documented measurement units and fixture validation.
3. Make FFmpeg failure an explicit result status.
4. Separate measured observations from inferred labels and hypotheses.

### Package 3 - Research integrity and maintenance

1. Require provenance, sample size, confidence method, and counterevidence before a result is stored as a law.
2. Make import-time scripts explicit commands.
3. Assign ownership or archive policy to duplicate/backup/legacy modules only after usage verification.
4. Update README to describe the actual MusicDNA entry point, setup, data locations, and limits.

## 15. Proposed scope for TASK-002

TASK-002 should be limited to the first repair package. It should not add new music features, modify emotion models, or remove legacy engines. Its acceptance criteria should be:

- a clean supported environment has one documented installation path;
- missing capabilities yield actionable errors without traceback-like partial output;
- first run creates required data directories safely;
- one builder output validates against one versioned schema;
- BPM, transient, and beat outputs have distinct documented fields and tests;
- automated tests cover bootstrap, persistence, schema, and synthetic rhythm fixtures;
- no research claim becomes stronger than its evidence during the repair.

## 16. Final audit counts and uncertainties

| Item | Result |
|---|---|
| Files inspected | 169 repository files outside `.git`; 133 Python files AST-parsed |
| Critical issues | 5 |
| High-priority issues | 10 |
| Confirmed duplicate/obsolete artifacts or groups | 16 (five backups, four empty placeholders, seven duplicate/superseded groups) |
| Recommended first repair package | Reproducible and safe analysis baseline |
| Files created or modified by this audit | Created only `AUDIT_REPORT.md`; no production file modified |
| Tests/checks executed | Python version, PATH capability checks, primary-command smoke test, `unittest` discovery, `pytest` collection, AST syntax parse, JSON parse, static import/reference inspection, git status/history inspection |
| Remaining uncertainties | Actual intended user workflows for candidate orphan scripts; historical role of backup files; audio-fixture accuracy; source encoding cause of displayed mojibake; whether ignored local audio/data exists outside the tracked repository |

## 17. Exact check results

- Python runtime: `Python 3.14.6`.
- `python main.py`: failed before analysis because `numpy` is not installed.
- `python -m unittest discover -v`: ran 0 tests.
- `python -m pytest --collect-only -q`: no tests collected.
- Python AST parsing: 133/133 repository Python files parsed; no syntax parse errors.
- JSON parsing: all eight discovered JSON files parsed successfully.
- No `ffmpeg`, `ffprobe`, or `yt-dlp` command was available during the audit.

This report is an evidence-based audit, not an instruction to delete files. Uncertain classifications are intentionally marked as candidates until runtime ownership and user workflow evidence is available.
