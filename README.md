# <img src="docs/assets/logo.svg" alt="Three record blocks passing through a gate bar, the custody half of the wordmark in amber" width="40" align="top"> corpuscustody

<p align="right">
  <a href="#the-mixing-problem">Problem</a> &middot;
  <a href="#install">Install</a> &middot;
  <a href="#commands">Commands</a> &middot;
  <a href="#the-obligation-model">Obligations</a> &middot;
  <a href="#the-compatibility-rules">Rules</a> &middot;
  <a href="#a-worked-gate-run">Worked run</a> &middot;
  <a href="#manifest-format-field-by-field">Manifest</a> &middot;
  <a href="#exit-codes">Exit codes</a> &middot;
  <a href="#limitations-expanded">Limitations</a> &middot;
  <a href="#design-decisions">Design</a>
</p>

> This is a mechanical obligation check, not legal advice. It matches SPDX
> identifiers against a short hand-maintained table and applies fixed rules. A
> PASS means no conflict was found in that table, not that a lawyer cleared the
> set. Treat every result as input to a human decision, never as the decision.

corpuscustody is a training-data license and provenance gate. It walks a dataset
manifest, resolves the license of every record against an offline SPDX table,
and decides whether the combined set is usable for a declared purpose: internal
research, a commercial product, or redistribution. It flags incompatible
combinations, such as a share-alike corpus mixed into a commercial release, and
it refuses to emit a cleared manifest when any record's provenance is unknown
rather than assuming permissive.

Python 3.11, standard library only. No third-party dependencies and no network
access anywhere in the code.

## The mixing problem

A training set is rarely one license. It is a pile of records pulled from many
places: a permissive tokenizer here, a Wikipedia dump there, a scraped folder
nobody labelled, one corpus grabbed under a non-commercial term and never
flagged. Each record on its own is fine. The set is the problem.

The moment records are combined and put to a purpose, the obligations stack. A
single share-alike record can force the whole release to carry share-alike
terms. A single non-commercial record makes the set unsafe to sell. A single
unlabelled record means you cannot honestly say what you are allowed to do with
any of it. These conflicts are invisible in a per-record spreadsheet, because the
danger lives in the combination and the declared use, not in any one row.

corpuscustody makes that combination explicit. You declare what you intend to do
with the set. It resolves every record, applies the rules a careful reviewer
would apply, and either clears the set for that purpose or refuses and names the
records that blocked it, and why.

## Install

Install as an editable package:

```
pip install -e .
```

Or run without installing, from the project root:

```
set PYTHONPATH=src
python -m corpuscustody version
```

```
corpuscustody 0.1.0
```

The `set PYTHONPATH=src` form is the Windows shell. On a POSIX shell use
`PYTHONPATH=src python -m corpuscustody version`.

## Commands

Four subcommands. All read a manifest; `gate` and `report` also require a
declared `--purpose`.

| Command   | Purpose                                            | Requires `--purpose` |
| --------- | -------------------------------------------------- | -------------------- |
| `resolve` | parse a manifest, print each record's license      | no                   |
| `gate`    | run the pass or refuse decision for a purpose      | yes                  |
| `report`  | combined resolve view then gate view               | yes                  |
| `version` | print the version                                  | no                   |

Run with no subcommand and it prints help and exits 2:

```
python -m corpuscustody
```

```
usage: corpuscustody [-h] {resolve,gate,report,version} ...

Training-data license and provenance gate.

positional arguments:
  {resolve,gate,report,version}
    resolve             parse a manifest and resolve each record's license
    gate                run the pass or refuse decision for a declared purpose
    report              print the combined resolve and gate report
    version             print the version

options:
  -h, --help            show this help message and exit
```

`--purpose` accepts exactly `internal`, `commercial`, or `redistribute`. It is
case-insensitive: `Commercial` normalises to `commercial`. Pass `--out PATH` to
`gate` to write a cleared manifest on PASS.

## The obligation model

Every license in the offline table maps to a set of obligations. An obligation
is a mechanical yes or no fact about the license, not a judgement. These five
obligations are the entire vocabulary the tool reasons over.

| Obligation       | Key              | What it means                                                  |
| ---------------- | ---------------- | -------------------------------------------------------------- |
| Attribution      | `attribution`    | attribution or notices must be preserved                       |
| Share alike      | `share_alike`    | derivatives or the combined work must carry the same license   |
| Non commercial   | `non_commercial` | commercial use is not permitted                                |
| No derivatives   | `no_derivatives` | modified or derived works are not permitted                    |
| Unknown          | `unknown`        | provenance or license is not established                       |

The `unknown` obligation is special. It is never inferred as permissive. A
record whose license cannot be resolved is treated as carrying every restrictive
obligation at once, so it can never quietly pass a gate. That is defined once, in
`src/corpuscustody/spdx.py`, as the `UNKNOWN` sentinel with all five flags set.

## Purposes and why they differ

The same set can be safe for one use and unsafe for another. The purpose you
declare changes which obligations block and which are only noted.

| Purpose        | Intent                                                        | Distribution      |
| -------------- | ------------------------------------------------------------- | ----------------- |
| `internal`     | internal research use, not distributed outside the org        | none              |
| `commercial`   | a commercial product, distributed, possibly proprietary       | yes, and for sale |
| `redistribute` | redistributed as a dataset or corpus to third parties         | yes               |

Internal use is the most permissive purpose here, because nothing leaves the
organisation. Share-alike and non-commercial obligations do not block internal
research: you are not distributing, and you are not selling. Commercial use is
the strictest, because it both distributes and sells. Redistribution sits
between the two: it distributes, so no-derivatives blocks it, but it is assumed
non-commercial, so a share-alike record is a note rather than a hard block.

## The compatibility rules

These are the actual rules the code applies, transcribed from the `_RULES` table
in `src/corpuscustody/compat.py`. A blank cell means the obligation raises no
issue for that purpose. `finding` blocks the gate. `note` is informational and
does not block.

| Obligation       | `internal` | `commercial` | `redistribute` |
| ---------------- | ---------- | ------------ | -------------- |
| `unknown`        | finding    | finding      | finding        |
| `share_alike`    | (none)     | finding      | note           |
| `non_commercial` | (none)     | finding      | (none)         |
| `no_derivatives` | note       | finding      | finding        |
| `attribution`    | note       | note         | note           |

Reading the table as prose, so the intent is unambiguous:

- `unknown` is a finding for every purpose. Unknown provenance never passes.
- `share_alike` is a finding for commercial, because a share-alike corpus mixed
  into a proprietary release forces that release to share alike. For
  redistribute it is a note: the combined set must then carry the terms.
- `non_commercial` is a finding for commercial only. Internal and redistribute
  are assumed non-commercial here, so it is not reported at all for internal and
  raises nothing for redistribute.
- `no_derivatives` is a finding for commercial and redistribute, because both
  typically transform or repackage the data, and a note for internal.
- `attribution` is never a blocking finding. It is always a note: attribution
  must be preserved.

Issues are emitted in record order, then in the obligation order declared in
`spdx.py` (`attribution`, `share_alike`, `non_commercial`, `no_derivatives`,
`unknown`), so identical input yields byte-identical output.

## Unknown provenance is a refusal, not a warning

The single most consequential design choice is that an unresolvable license does
not degrade to permissive and does not become a soft warning. It becomes a
blocking finding for every purpose, and it makes the gate refuse.

Two things resolve to `UNKNOWN`: an empty license field, and the explicit token
`UNKNOWN`. The resolver in `spdx.py` returns the `UNKNOWN` sentinel for both, and
for any identifier not in the table. That sentinel carries all five obligations,
so it trips the `unknown` finding no matter the purpose.

This default matters because the opposite choice fails silently and expensively.
If unknown resolved to permissive, a scraped folder nobody labelled would sail
through and land in a shipped product, and the first sign of trouble would be a
takedown or a lawsuit. A refusal is loud and cheap: it stops the pipeline now,
names the records, and asks a person to establish provenance before proceeding.
That conservatism is deliberate and not adjustable by a flag.

## A worked gate run

Below are the real decisions for each of the three sample manifests, captured by
running the CLI in this repository. The manifests are described in
[samples/README.md](samples/README.md); they are hand-authored test vectors, not
scraped data.

### permissive.manifest, commercial: PASS, 0 findings

Five permissive records, attribution at most. It clears for commercial with four
attribution notes and no findings.

```
python -m corpuscustody gate samples/permissive.manifest --purpose commercial
```

```
purpose: commercial
records: 5
decision: PASS
findings: 0
notes: 4
  rec-0001 | MIT | attribution: attribution must be preserved
  rec-0002 | Apache-2.0 | attribution: attribution must be preserved
  rec-0004 | BSD-3-Clause | attribution: attribution must be preserved
  rec-0005 | CC-BY-4.0 | attribution: attribution must be preserved
```

Note that `rec-0003` (CC0-1.0) produces no note at all: CC0 carries no
obligations, so it is silent.

### sharealike.manifest, commercial: REFUSE, 3 findings

The same set that is fine internally mixes share-alike and non-commercial
records into a commercial release. Three findings, and the process exits 1.

```
python -m corpuscustody gate samples/sharealike.manifest --purpose commercial
```

```
purpose: commercial
records: 5
decision: REFUSE
findings: 3
  rec-1002 | CC-BY-SA-4.0 | share_alike: share-alike terms attach to the combined set
  rec-1004 | CC-BY-NC-4.0 | non_commercial: non-commercial license, commercial use blocked
  rec-1005 | GPL-3.0-only | share_alike: share-alike terms attach to the combined set
notes: 5
  rec-1001 | MIT | attribution: attribution must be preserved
  rec-1002 | CC-BY-SA-4.0 | attribution: attribution must be preserved
  rec-1003 | Apache-2.0 | attribution: attribution must be preserved
  rec-1004 | CC-BY-NC-4.0 | attribution: attribution must be preserved
  rec-1005 | GPL-3.0-only | attribution: attribution must be preserved
```

### sharealike.manifest, internal and redistribute: PASS

The exact same records pass for `internal` (share-alike and non-commercial do
not block internal use, leaving the five attribution notes) and for
`redistribute` (a PASS with seven notes, where the two share-alike obligations
become notes rather than the commercial findings above). Only the declared
purpose changed; the records did not.

### unknown.manifest, internal: REFUSE, 2 findings

Two records resolve to `UNKNOWN`, one from an empty license field (`rec-2003`)
and one from the explicit token (`rec-2005`). Even for the most permissive
purpose, the gate refuses.

```
python -m corpuscustody gate samples/unknown.manifest --purpose internal
```

```
purpose: internal
records: 5
decision: REFUSE
findings: 2
  rec-2003 | UNKNOWN | unknown: provenance unknown, cannot clear
  rec-2005 | UNKNOWN | unknown: provenance unknown, cannot clear
notes: 7
  rec-2001 | MIT | attribution: attribution must be preserved
  rec-2002 | CC-BY-4.0 | attribution: attribution must be preserved
  rec-2003 | UNKNOWN | attribution: attribution must be preserved
  rec-2003 | UNKNOWN | no_derivatives: no-derivatives license, transformation blocked
  rec-2004 | Apache-2.0 | attribution: attribution must be preserved
  rec-2005 | UNKNOWN | attribution: attribution must be preserved
  rec-2005 | UNKNOWN | no_derivatives: no-derivatives license, transformation blocked
```

The `UNKNOWN` records also emit `no_derivatives` notes for internal, because the
sentinel carries every obligation and `no_derivatives` is a note under internal.

## Manifest format field by field

A manifest is a UTF-8 text file, one record per line. Blank lines and lines whose
first non-space character is `#` are ignored, so manifests carry comments and
stay diffable. Each record line has exactly three pipe-separated fields.

```
record_id | spdx_id | source
```

| Field       | Position | Required | Meaning                                                              |
| ----------- | -------- | -------- | -------------------------------------------------------------------- |
| `record_id` | 1        | yes      | free text identifier for the record; an empty value is a parse error |
| `spdx_id`   | 2        | no       | SPDX identifier; empty or unrecognised resolves to `UNKNOWN`         |
| `source`    | 3        | no       | free text provenance note; not validated                            |

Surrounding whitespace on each field is stripped. Parsing is deliberately dumb:
`spdx_id` is read but not validated at parse time, so parsing and license policy
stay in separate modules. Validation happens later, at resolve time. A line with
anything other than three fields raises a `ManifestError` and the process exits
2. A real sample manifest, comment lines and all:

```
# permissive.manifest
rec-0001 | MIT | github.com/example/tokenizer
rec-0002 | Apache-2.0 | github.com/example/corpus-tools
rec-0003 | CC0-1.0 | zenodo.org/record/000001
rec-0004 | BSD-3-Clause | github.com/example/textnorm
rec-0005 | CC-BY-4.0 | data.example.org/news-2020
```

## Output format and the cleared manifest

The `resolve` view lists every record with its resolved license and its active
obligations (or `none`), then a license count summary sorted by SPDX identifier.

```
python -m corpuscustody resolve samples/sharealike.manifest
```

```
records: 5
  rec-1001 | MIT | attribution
  rec-1002 | CC-BY-SA-4.0 | attribution,share_alike
  rec-1003 | Apache-2.0 | attribution
  rec-1004 | CC-BY-NC-4.0 | attribution,non_commercial
  rec-1005 | GPL-3.0-only | attribution,share_alike
license counts:
  Apache-2.0: 1
  CC-BY-NC-4.0: 1
  CC-BY-SA-4.0: 1
  GPL-3.0-only: 1
  MIT: 1
```

The `gate` view is fixed and diffable: a `purpose` line, a `records` count, a
`decision` of `PASS` or `REFUSE`, a `findings` count with one line per finding,
then a `notes` count with one line per note. Each issue line is
`record_id | spdx_id | obligation: message`.

On PASS, passing `--out PATH` writes a cleared manifest. It is written with LF
line endings regardless of platform, so identical input produces byte-identical
output. The file lists every checked record, its resolved identifier, and the
purpose it was cleared for, under a three-line comment header.

```
python -m corpuscustody gate samples/permissive.manifest --purpose commercial --out cleared.manifest
```

```
# corpuscustody cleared manifest
# purpose: commercial
# record_id | spdx_id | cleared_for
rec-0001 | MIT | commercial
rec-0002 | Apache-2.0 | commercial
rec-0003 | CC0-1.0 | commercial
rec-0004 | BSD-3-Clause | commercial
rec-0005 | CC-BY-4.0 | commercial
```
