"""Packaged data for the ``agentsec`` distribution.

This package exists so that the trace schema can be read from *package
resources* rather than from the repository checkout: the file below is shipped
inside the wheel, so validation works from an installed package that has no
repository around it.

Source of truth
---------------
The trace schema is generated from the pydantic models by
``scripts/export_trace_schema.py``, which writes the same bytes to two places:

* ``schemas/trace/trace_event.v1.schema.json`` - the repository/documentation
  copy, linked from the README; and
* ``agentsec/schemas/trace/trace_event.v1.schema.json`` - this packaged copy.

The two copies must stay byte-identical. ``tests/schema/test_schema_file.py``
and ``tests/schema/test_packaged_schema.py`` enforce that identity and the
agreement of both copies with the models, so neither can drift unnoticed.

Nothing here is imported at runtime: the JSON file is data, read through
``importlib.resources`` by :mod:`agentsec.trace.validate`.
"""
