# TASK-001 — Full Technical Audit of MusicDNA

## Objective

Perform a complete technical audit of the entire MusicDNA repository.

The purpose is to determine what works, what is unreliable, what is incomplete, and what should be fixed first.

## Scope

Inspect the entire repository, including:

- core/
- engines/
- brain/
- collectors/
- database/
- discovery/
- schema/
- main.py
- analyze_all.py
- generate_prompt.py
- music_worker.py
- project JSON files
- project documentation

## Restrictions

- Do not modify production code.
- Do not add new features.
- Do not redesign the architecture.
- Do not delete files.
- Do not rename files.
- Do not make assumptions without evidence.
- Mark uncertain conclusions explicitly.

## Required Analysis

For every meaningful module or engine, report:

- Purpose
- Current status
- Whether it is actually used
- Whether it works correctly
- Bugs
- Reliability risks
- Duplicate or obsolete implementations
- Missing tests
- Confidence level
- Priority

Pay special attention to:

- BPM detection
- Beat and transient detection
- Energy analysis
- LUFS and production metrics
- Spectral centroid and brightness
- Spectrum analysis
- Pitch and melody tracking
- Harmony and key detection
- Structure detection
- Emotion classification
- Emotion journey and curve
- Rules and hypotheses
- Knowledge storage
- Comparison and statistics
- Prompt generation
- Duplicate engine versions
- Console noise and oversized outputs
- Data schema consistency
- Error handling
- Mobile and Termux performance

## Deliverable

Create one file:

AUDIT_REPORT.md

## Report Structure

The report must contain:

1. Executive summary
2. Architecture overview
3. Engine inventory
4. Critical bugs
5. Unreliable measurements
6. Dead, duplicate, or unused code
7. Missing tests
8. Performance risks
9. Data integrity risks
10. Quick wins
11. Recommended repair order
12. Proposed TASK-002 scope

## Evidence

Every important conclusion must reference:

- exact file path
- function or class name
- relevant line or code behavior
- reason for the conclusion

## Final Summary

At the end include:

- Number of files inspected
- Number of critical issues
- Number of high-priority issues
- Number of duplicate or obsolete modules
- Recommended first repair package
