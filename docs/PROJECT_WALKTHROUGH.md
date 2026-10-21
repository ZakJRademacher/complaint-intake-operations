# Five-minute project walkthrough

1. **Problem:** A recurring CSV arrives, operations needs counts, date anomalies and a traceable review list, and someone needs to annotate cases without losing their work next refresh.
2. **Source:** Show the real Kaggle/CFPB snapshot and provenance fingerprint. Explain why narratives and identifying company/location fields are omitted.
3. **Code:** Show `src/pipeline.py` staging and ID rules. Open `sql/channels.sql` for CTEs, window functions and a valid P90 denominator. Distinguish the source response flag from routing days.
4. **Deliverable:** Open Excel overview, then Monthly and Review queue. Explain why the partial month is labeled and why a 100-case selection cannot represent all flagged complaints.
5. **Handoff:** Enter an owner, status and note on a copy of the workbook. Export that sheet, import its CSV, rerun, and inspect merged notes. Never publish real annotations to the public repository.
6. **Evidence:** Run 25 tests, inspect seven full-data reconciliation controls and the independent output verification. Explain the native-Excel limitation plainly.

## Relevant paid work
CSV cleanup and validation; SQL report preparation; recurring spreadsheet refreshes; exception-list handoffs; documentation of repeatable admin workflows. Ask a prospective client about column definitions, review thresholds, refresh frequency and note ownership before adapting the project.

## Honest limits
This is a personal portfolio project. It does not establish a prior client relationship, production deployment, earned savings, certification or a completed degree. The dataset is historical and the example queue is intentionally small. Automated controls support a review; they do not adjudicate complaints.
