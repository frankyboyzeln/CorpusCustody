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
