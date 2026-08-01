# Changelog

All notable changes to CorpusCustody are documented in this file. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `gate` now accepts `--out` to write a cleared manifest on a pass.

## [0.7.0] - 2026-09-02

### Added
- Line-oriented dataset manifest parser (`corpuscustody.manifest`) with
  1-based line-number errors.
- Offline SPDX obligation table for common identifiers
  (`corpuscustody.spdx`), covering MIT, Apache-2.0, BSD-3-Clause, GPL-2.0,
  GPL-3.0, LGPL, MPL-2.0, CC-BY-*, and CC0.
- Pairwise and set-level compatibility resolution against a declared purpose
  (`internal`, `commercial`, `redistribute`) in `corpuscustody.compat`.
- Gate that refuses when any record's provenance is unknown and writes a
  cleared manifest only on pass (`corpuscustody.gate`).
- CLI subcommands: `resolve`, `gate`, `report`, `version`
  (`corpuscustody.cli`).
- Line oriented report rendering (`corpuscustody.report`).
- Sample manifests covering the permissive, share-alike, and unknown cases.

## [0.6.0] - 2025-11-18

### Added
- `report` subcommand printing the combined resolve + gate output with a
  per-record obligation list and a trailing summary.
- Notes collection: attribution, copyleft, and share-alike obligations are
  surfaced as notes next to each record.

## [0.5.0] - 2024-06-21

### Added
- Purpose-aware compatibility: a permissive pair can pass `internal` and
  `commercial` but refuse `redistribute` when a share-alike record joins the
  set.

## [0.4.0] - 2023-08-09

### Added
- Unknown-provenance rule: a record whose license identifier is not in the
  SPDX table makes the gate refuse with a distinct `UNKNOWN_LICENSE` finding.

## [0.3.0] - 2022-09-04

### Added
- Set-level resolution: the gate now evaluates the whole manifest, not
  record pairs, so three compatible records that pairwise pass but jointly
  conflict are caught.

## [0.2.0] - 2021-12-06

### Added
- Pairwise compatibility table for the initial identifier set.
- First `gate` prototype with `--purpose` and a pass/refuse decision.

## [0.1.0] - 2021-03-11

### Added
- The custody problem in prose: training corpora mix licenses, and nobody
  can say what the joint obligations are.
- Initial package skeleton, README, and the MIT licence.
- A single sample manifest and a hand-written resolve script.