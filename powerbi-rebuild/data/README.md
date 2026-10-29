# Complaint Intake Review refresh inputs

The PBIX in deliverables already contains the complete imported reporting projection. Narratives, names and location identifiers are omitted. The compact source repository does not duplicate the full Cases.csv here.

To rebuild, run the original pipeline following the repository README and locate the published complaints.sqlite using src/publication.py. From the repository root run:

```sh
python tools/export_powerbi_data.py --database "ABSOLUTE_PATH_TO_VALIDATED_DATABASE"
```

The command writes powerbi-rebuild/data/Cases.csv and export-verification.json. Set Power Query's DataFolder to that absolute data directory, then refresh. Expected baseline: 903,983 cases, 105,969 review cases, 7,052 date issues and 896,931 valid intervals. Email: 354 cases, 351 valid intervals, P90 19 days and 87 review cases.

P90 uses nearest rank over nonnegative routing intervals. Review combines routing over 7 days, date issues and timely No/Unknown, counting each record once. Seven days is illustrative, not a legal SLA. This is a historical routing review, not company resolution time or a live backlog. Update the fixed period and unfiltered interpretation when changing source populations.

Read [source attribution and scope](../../docs/SOURCES.md).
