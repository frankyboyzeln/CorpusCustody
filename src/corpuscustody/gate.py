"""The pass or refuse decision and the cleared manifest writer.

The gate takes a set of records and a purpose, evaluates compatibility, and
decides:

  PASS    no blocking findings. A cleared manifest may be emitted.
  REFUSE  at least one blocking finding. No cleared manifest is emitted.

