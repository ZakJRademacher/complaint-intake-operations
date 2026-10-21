# Quality report

Validated against the complete 903,983-row Kaggle snapshot on October 15, 2026.

- **25 automated tests pass.** Synthetic test fixtures exercise date parsing, strict >7-day boundary, negative intervals, unknown response denominator, identical/conflicting IDs, invalid IDs, bad dates, nearest-rank P90, rerun note preservation, unmatched annotations, Excel-preface import, invalid resolved notes and duplicate note IDs.
- **Seven full-data controls pass:** source partition; response partition; date partition; channel, monthly and product reconciliation; SQLite integrity. Exact results are in `results/analysis.json`.
- **Independent verification** recomputes source metrics using pandas and inspects SQLite, XLSX and PDF. See `independent-verification.json` for each assertion.
- **Workbook engine checks:** matching case count and response rate, a temporary count change and restore, resolution guard with missing then present owner/note, restored example cells, no formula error matches. See `workbook-verification.json`.
- **Visual review:** all three sheet previews and both PDF pages inspected for clipped text, legibility and consistency. The workbook includes a native chart, dropdown and live formulas; it has no macros.
- **Compact bundle:** ZIP integrity test and per-file SHA-256 manifest. Raw CSV, local database and full row-level review/quality exports are omitted; refresh commands reproduce them.

Native desktop Excel recalculation was not available. Source data is historical, with a partial final month. Controls do not determine whether complaints were resolved, whether a company met a regulatory deadline or why source date anomalies occurred. Real client review notes must remain private; the delivered note input is empty.

## October 21 reliability update

The current local suite has 25 passing tests. Regression coverage includes the affected failure paths and portable bundle verification. Native Excel and Power BI checks were not repeated for this code update. See docs/RELIABILITY_UPDATE.md for the change and validation record.
