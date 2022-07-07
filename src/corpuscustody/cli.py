"""Command line interface for corpuscustody.

Subcommands:
  resolve   parse a manifest and print each record's resolved license
  gate      run the pass or refuse decision for a declared purpose
  report    print the combined resolve and gate report
  version   print the version

Exit codes:
  0  clean, gate passed, or informational command succeeded
  1  gate refused (findings present)
  2  usage error or bad input
