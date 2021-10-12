"""Dataset manifest parsing, line oriented.

A manifest is a UTF-8 text file, one record per line. Blank lines and lines
whose first non-space character is `#` are ignored, so manifests can carry
comments and stay diffable.

Each record line has three tab-separated or pipe-separated fields:
