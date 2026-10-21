# Reliability update October 21 2026

The annotation importer rejects malformed CSV structure and duplicate mapped headers before replacing saved notes. Temporary filenames are unique, and the complete merge is validated. The pipeline builds an isolated complete result version and switches latest.json only after database closure, exports and checks. Updated readers and builders select one version per operation. Failures preserve the previous complete result. The portable bundle includes current docs, an exact-byte manifest and an empty example note input, with older ZIPs and private annotations excluded.

## Validation

The updated local suite passes 25 tests on Python 3.12.14. Regression tests exercise the affected failure scenarios and package freshness, repeated builds and archived-byte hashes. Full historical input was reprocessed with unchanged headline figures. Native Excel/Power BI refresh and optional presentation regeneration were not repeated.

## Release provenance

This release is based on the GitHub commit recorded in release.json. The October 21 regression and full-data checks verify the reliability changes described above. Native desktop verification remains limited to the earlier observations documented in this project.
