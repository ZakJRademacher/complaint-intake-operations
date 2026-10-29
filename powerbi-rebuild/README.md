# Complaint Intake Review — Power BI guide

**Business question:** Where should intake routing be reviewed?

Open [the ready-to-use PBIX](../deliverables/Complaint%20Intake%20Review.pbix). Imported data is included. The editable [PBIP source](IntakeReview.pbip) is kept beside its Report and SemanticModel folders. Use Power BI Desktop's current project support. The PBIX is distributed through GitHub. No Power BI Service hosting or scheduled cloud refresh is configured.

## Reading the report

Page 1 pairs outcome magnitude with a comparison that changes the prioritization decision. Dropdown slicers update the headline metrics and charts. Chart tooltips provide population context. The interpretation distinguishes investigation leads from causal findings. Text explicitly marked as an unfiltered snapshot remains a historical reference when slicers change.

Page 2 documents populations, exclusions and limitations. Its evidence represents the complete historical population, not the selections on page 1. Restore every dropdown to All before saving the default view. Use the report's fit-to-page view for readability; Use channel counts alongside the percentile comparisons.

## Refresh and handoff

Keep this complete folder together. On a new machine, set DataFolder through Transform data > Edit parameters to the absolute path of the prepared input folder described below. Choose Home > Refresh. Read [data instructions](data/README.md) before replacing any input. Refresh the PBIP first, check both pages and filters, then save a new PBIX into deliverables; saving the source does not automatically update the exported PBIX.

The report is a historical portfolio demonstration, not a live backlog or operational alert system. Dates, exclusions and illustrative rules are visible. Source preparation, model definitions, measures, report definitions and source licenses remain inspectable. The original report/workbook is preserved.

## Your practice task

Select Email. Confirm 354 cases, 351 valid intervals, P90 19 days and 87 review cases. Explain why routing is not resolution time and why review share is not a legal compliance rate. Restore All.

Acceptance: show the denominator behind the rate or percentile, identify an excluded population, and describe one sensible follow-up that the report cannot answer. Change the chart sort in a practice copy, then confirm the totals still agree. Read the DAX measure for one headline metric and explain it in plain language.

Native Power BI Desktop refresh, both report pages and the filter example above were checked on October 29, 2026. See verification.json and the report previews for evidence.
