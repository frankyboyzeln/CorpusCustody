# Sample manifests

These three manifests are test vectors that I authored by hand for this project.
They are not scraped from a real dataset and are not production data. The record
ids and sources are illustrative placeholders. The SPDX identifiers are real and
resolve against the offline table in `src/corpuscustody/spdx.py`.

- `permissive.manifest`: five records under permissive licenses (MIT, Apache-2.0,
  CC0-1.0, BSD-3-Clause, CC-BY-4.0). Passes every purpose. The only obligations
  are attribution notes.

- `sharealike.manifest`: five records that pass internal use but conflict with a
  commercial purpose. It mixes a share-alike corpus (CC-BY-SA-4.0, GPL-3.0-only)
  and a non-commercial corpus (CC-BY-NC-4.0) into the set.

- `unknown.manifest`: five records where two have unknown provenance, one via an
  empty license field and one via an explicit UNKNOWN. The gate refuses these
  for every purpose rather than assuming permissive.

## Extending the fixtures

Each manifest here is a real gate fixture: permissive records only, a 
share-alike record that flips the commercial decision, and an unknown 
identifier that must refuse. To add a case, keep the format stable (one 
record per line, SPDX identifiers exactly as in the table in `spdx.py`) 
and add a matching assertion in `tests/` so the gate behaviour is pinned 
for the new case. The `unknown.manifest` file is the one to extend when 
testing a newly added SPDX identifier.
