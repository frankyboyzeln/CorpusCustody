# Sample manifests

These three manifests are test vectors that I authored by hand for this project.
They are not scraped from a real dataset and are not production data. The record
ids and sources are illustrative placeholders. The SPDX identifiers are real and
resolve against the offline table in `src/corpuscustody/spdx.py`.

- `permissive.manifest`: five records under permissive licenses (MIT, Apache-2.0,
  CC0-1.0, BSD-3-Clause, CC-BY-4.0). Passes every purpose. The only obligations
  are attribution notes.

- `sharealike.manifest`: five records that pass internal use but conflict with a
