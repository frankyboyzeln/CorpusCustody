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

