"""Compatibility resolution against a declared purpose.

Three purposes are recognised:

    internal   internal research use, not distributed outside the org
    commercial a commercial product, distributed, possibly proprietary
    redistribute  redistributed as a dataset or corpus to third parties

Each obligation is checked against the purpose to decide whether it produces a
finding. The rules are mechanical and intentionally conservative:

  unknown         a finding for every purpose. Unknown provenance never passes.
  non_commercial  a finding for commercial. Internal and redistribute are
                  assumed non commercial here, so it is only reported as a note.
  share_alike     a finding for commercial, because a share-alike corpus mixed
