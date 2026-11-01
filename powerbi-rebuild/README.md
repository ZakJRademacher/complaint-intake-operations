# Complaint Intake Review — Power BI guide

**Business question:** Where should intake routing be reviewed?

Open [the ready-to-use PBIX](../deliverables/Complaint%20Intake%20Review.pbix). Imported data is included. The editable [PBIP source](IntakeReview.pbip) is kept beside its Report and SemanticModel folders. Use Power BI Desktop's current project support. The PBIX is distributed through GitHub. No Power BI Service hosting or scheduled cloud refresh is configured.

## Reading the report

On page 1, compare channel routing percentiles with case and review counts. Dropdowns update the metrics and charts, and tooltips show the eligible population. Routing measures receipt-to-sending time; the timely-response flag measures something different.

Page 2 documents populations, exclusions and limitations. Its evidence represents the complete historical population, not the selections on page 1. Restore every dropdown to All before saving the default view. Use the report's fit-to-page view for readability; Use channel counts alongside the percentile comparisons.

## Refresh and handoff

Keep this complete folder together. On a new machine, set DataFolder through Transform data > Edit parameters to the absolute path of the prepared input folder described below. Choose Home > Refresh. Read [data instructions](data/README.md) before replacing any input. Refresh the PBIP first, check both pages and filters, then save a new PBIX into deliverables; saving the source does not automatically update the exported PBIX.

The report uses a historical snapshot. Check the period and exclusions when interpreting it; it is not a live backlog. The original workbook and reporting files remain available.

## Your practice task

Select Email. Confirm 354 cases, 351 valid intervals, P90 19 days and 87 review cases. Explain why routing is not resolution time and why review share is not a legal compliance rate. Restore All.

Acceptance: explain the denominator, identify an excluded population, and describe the additional data needed for a follow-up. Change the chart sort in a practice copy, then confirm the totals still agree. Read the DAX measure for one headline metric and explain it in plain language.

Native Power BI Desktop refresh, both report pages and the filter example above were checked on October 29, 2026. See verification.json and the report previews for evidence.
