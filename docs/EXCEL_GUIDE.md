# Excel and reviewer-note guide

## Sheets
**Operations review** reconciles totals to its six-channel table and charts the last 12 received months. Blue imported values come from SQL. Headline formulas calculate count and response rate; changing the displayed review-day number does not rerun SQL. Regenerate the report and rebuild the workbook to change that rule.

**Monthly** holds all observed months, imported counts and formula rates. The known-timely denominator is Yes+No; the routing-review denominator is valid intervals. K:L contain a 12-month chart helper linked by formulas. The final month is marked partial. Changing source periods requires rebuilding, rather than pasting arbitrary rows into fixed ranges.

**Review queue** contains 100 longest valid routing-delay examples, sorted descending. It is not the complete 105,969-case review population and omits negative-interval examples from this selected display. The full CSV and quality-issue extract are generated locally. All displayed IDs are source IDs. Sort whole rows only.

## Enter review work
Edit only Owner, Review status and Notes on the Review queue sheet. The status dropdown offers Not started, In progress and Resolved. Next action is a formula: a Resolved status needs both owner and note before it reads Complete. This is a workflow prompt, not protection or evidence that a review happened. The workbook is intentionally not password-protected.

## Save notes across runs
1. Export just the Review queue sheet as **CSV UTF-8**. Excel may warn that only the active sheet is saved; keep the XLSX master separately.
2. Run `python src/update_notes.py exported-review-queue.csv` from the project root.
3. Run `python src/pipeline.py`. Existing note IDs absent from the import remain saved. Completely untouched template rows do not erase old notes. `unmatched_notes.csv` surfaces notes absent from the current accepted source.
4. Rebuild the workbook to display refreshed merged notes. For a different set of examples, adjust the documented queue selection before authoring a new sheet.

The importer finds the required headers even below the sheet's title rows. It validates all rows before writing, rejects duplicate import IDs and bad statuses, and requires owner plus note for Resolved. It does not currently support deleting a saved note through a blank import; edit the notes CSV deliberately and keep a backup. Treat notes as local work data: do not upload real client notes to a public repository.

## Validation
The workbook builder recalculates formulas, checks total records and timely rate against Python, changes an input and restores it, and exercises the resolution guard. It scans formula errors and renders all three sheets for visual review. Native desktop Excel was not available for a second recalculation test. The pipeline and CSV handoff remain independent of the workbook authoring package.
