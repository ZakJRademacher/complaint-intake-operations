# Complaint intake walkthrough

Start with the [Power BI report](../deliverables/Complaint%20Intake%20Review.pbix). It compares routing delays with review workload, so a channel with a long interval can be read alongside the number of cases behind it.

1. Explain the source: 903,983 historical Kaggle/CFPB records, with narratives and company/location fields omitted from the reporting data.
2. Read the definition of routing: sent date minus received date. Contrast it with the source timely-response flag; neither should be called complaint resolution time.
3. Open `src/pipeline.py` to trace ID handling, then `sql/channels.sql` for channel counts and nearest-rank P90 over valid nonnegative intervals.
4. Open the Excel workbook. The Review queue contains 100 selected examples; the full generated queue has 105,969 cases. The final source month is partial.
5. In a copy, enter an owner, status, and note. Export that sheet to UTF-8 CSV, import it, rerun the pipeline, and inspect the merged notes. Keep actual annotations private.
6. Run the 27 tests and inspect the reconciliation controls. The recorded workbook checks use the authoring engine; native Excel recalculation is a separate, untested boundary.

For another intake workflow, agree on date definitions, review thresholds, record keys, update frequency, and note ownership first. The seven-day example here is a review rule, rather than a statutory deadline.
