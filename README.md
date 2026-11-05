# BG | Separating Incoming and Post-process Evidence

Public report: https://nameuser-byte.github.io/BG-analysis/

## Current entrypoint

`index.html` contains an English contribution summary followed by the detailed Korean validation record and inline figures. The report uses educational synthetic data. It does not claim actual Fab operation, causal identification, production optimization or independent programming.

## Publication update — 2026-11-05

Replaces the earlier public entrypoint with the existing frozen validation report. Model fitting and frozen metric files were not changed. Old scripts, charts and CSVs elsewhere in this repository are historical materials, not the performance reference for this entrypoint.

Personal contribution: Proposed separating incoming from post-grinding measurements, shared comparisons with teammates, and organized observations, possible causes and follow-up checks.

AI contribution: implementation, calculations, figures, report generation and this publication update. Later validation is distinguished from original team work.

## Local preview

Run `python -m http.server 8780` from this repository, then open `http://127.0.0.1:8780/`. GitHub Pages is static: no Python inference endpoint is provided. Interactive examples use stored predictions or explicitly limited research rules.

## Evidence and limitations

Educational synthetic data, 20,000 rows. The historical RF importance near 90% is not a causal defect contribution. TTV measures thickness variation; it is not a direct bow/warp measurement. No production recipe or yield improvement is claimed.

Primary copied evidence: `bg_evidence.csv`, `error_analysis.json`, `evaluation_predictions.csv`, `legacy_reproduction.json`, `results.json`, `selection.json`. Data beside the report: `bg_evidence.csv`. See `PUBLICATION_MANIFEST.json` for source hashes and publication checks. Original educational data and frozen analysis artifacts remain unchanged in the source workspace.
