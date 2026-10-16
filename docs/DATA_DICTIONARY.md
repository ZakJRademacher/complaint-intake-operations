# Data dictionary

| Derived field | Type | Meaning |
|---|---|---|
| source_row | integer | Original CSV row number, first data record = 2 |
| complaint_id | text | Stable source Complaint ID; never a row counter |
| fingerprint | text | SHA-256 of eight selected source strings |
| received / sent | ISO date or null | Parsed Date received / Date sent to company |
| month | text | Received YYYY-MM, or Unknown for an invalid received date |
| product / issue | text | Source product / issue; blank becomes Unspecified |
| channel | text | Source Submitted via; blank becomes Unspecified |
| response | text | Source Company response to consumer; categorical, not a resolution date |
| timely | Yes/No/Unknown | Normalized source Timely response? label |
| intake_days | integer or null | sent minus received in calendar days; can be negative |
| valid_intervals | integer | Count with parsed dates and intake_days >=0 |
| over_review_days | integer | Count with intake_days > configured cutoff |
| p90_days | integer or null | Nearest-rank 90th percentile of valid intervals |
| review_reason | text | One or more review flags; not an adjudication |
| owner / notes | text | User-entered review annotations |
| review_status | enum | Not started, In progress, Resolved |

Source field reference: https://cfpb.github.io/api/ccdb/fields.html
The SQLite `selected` table contains staged text and row lineage; `cases` contains accepted, normalized cases; `review_notes` copies the persistent annotations. Six SQL reports expose the operations outputs. Count measures are whole records; day measures are calendar days; rates are fractions in JSON/XLSX and percentages only when formatted.
