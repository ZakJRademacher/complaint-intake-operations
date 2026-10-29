# Method and operating assumptions

## Ingestion and lineage
The CSV is read as UTF-8 with an optional BOM. Only eight documented fields enter the SQLite staging table: Complaint ID, received date, sent date, product, issue, submitted-via channel, categorical company response and timely-response flag. `source_row` is the CSV line number starting at 2. A SHA-256 of the selected raw strings supports deduplication; the entire source file has a separate SHA-256. Narrative and identifying location/company fields never enter derived tables.

## IDs and records
IDs remain text. Empty/nondecimal IDs are quarantined. For repeated IDs with identical selected values, keep the earliest source row; for conflicting selected values, quarantine every occurrence of that ID. Differences solely in omitted source fields do not count as selected-field conflicts. The delivered snapshot has no duplicate or invalid IDs. The `selected` table preserves retained staging lineage. Source rows reconcile to accepted cases plus invalid-ID, conflicting-ID and redundant identical rows.

## Dates, rates and flags
Parse dates as US month/day/year, convert to ISO and subtract calendar dates. Parsed intervals >=0 enter mean, median, P90 and routing-review denominators. Negative and unparseable intervals stay in complaint counts and enter the review queue. Do not impute dates or cap extreme positive intervals. P90 uses nearest rank: sorted position ceil(0.9*n), with 1-based indexing. Median averages the middle two for even samples.

Timely Yes / (Yes + No) is a source categorical measure. Other or blank labels become Unknown, excluded from that denominator and flagged. Blank product/issue/channel/response labels become Unspecified. No semantic remapping of product categories is attempted; historical category changes limit longitudinal comparisons.

Default review rule: interval >7 calendar days, negative/unparseable dates, or source timely flag No/Unknown. Reasons can overlap, but a case enters the review queue once. Seven is an illustrative operational review assumption, not a statutory requirement or evidence of a missed company-response deadline. `--review-days N` changes the SQL cutoff; refresh/rebuild the workbook after changing it.

## Notes and safe reruns
`data/review_notes.csv` is a persistent input, never overwritten by the reporting pipeline. Notes join by Complaint ID. Imports merge by key, retain previously saved IDs not in the import and skip untouched blank Not started rows. Invalid statuses, duplicate import IDs, and Resolved records without owner and note fail before a notes-file write. A successful import writes a temporary file then atomically replaces the notes CSV. There is no erase-via-blank shortcut; edit the notes input deliberately to clear saved annotations. Unmatched note IDs are reported separately, not discarded.

The reporting database and exports are built in a staging directory and checked before a complete snapshot is published. A refresh lock rejects simultaneous builds. Readers resolve `results/latest.json` once per operation; a failed refresh leaves the prior pointer unchanged. Back up edited review notes and inspect failed staging output before retrying. Checked-in root-level results are historical reference files, not automatically the newest refresh.

Source and notes CSVs reject blank or duplicate headers and malformed row widths before selecting fields. Additional explicitly named source columns remain permitted; only the eight documented fields enter the analysis.

## Scope
Historical public snapshot; partial final month; no live backlog, no resolution-time field and no financial advice or lender-quality comparison. Public complaints are not a representative consumer sample. Very long intervals require source verification, not automatic attribution of fault. Excel's 100 examples are the longest nonnegative flagged intervals, not random cases and not the full review population.
