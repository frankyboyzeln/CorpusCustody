"""Dataset manifest parsing, line oriented.

A manifest is a UTF-8 text file, one record per line. Blank lines and lines
whose first non-space character is `#` are ignored, so manifests can carry
comments and stay diffable.

Each record line has three tab-separated or pipe-separated fields:

    record_id  <sep>  spdx_id  <sep>  source

The separator is a single pipe `|`. Surrounding whitespace on each field is
stripped. `record_id` and `source` are free text. `spdx_id` is looked up in the
offline SPDX table at resolve time; it is not validated here beyond being read.
