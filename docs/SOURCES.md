# Source, provenance and licensing

- Dataset: [Consumer Complaints Database](https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata), uploaded by Sebastien Verpile. Kaggle labels it **CC0 Public Domain**; mirror last updated January 2018.
- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/sebastienverpile/consumercomplaintsdata
- Original: [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/).
- Official [field definitions](https://cfpb.github.io/api/ccdb/fields.html) and [Data.gov listing](https://catalog.data.gov/dataset/consumer-complaint-database).
- Downloaded for this project: October 15, 2026. Actual snapshot receipt dates: 2011-12-01 through 2017-11-15. Historical mirror, not the current CFPB export.
- Exact source CSV: Consumer_Complaints.csv; SHA-256 `038210fab477fd01d526b87872610cb8f2266814aaf716979f51c04b55c81587`.
- Code and original documentation: MIT, see LICENSE. Data licensing is separate from code licensing.

The source has 18 fields. Only eight selected fields are used. Full narratives, company names, ZIP codes, state, tags, consent and public company-response narrative are not included in derived reports or the public project. Raw data is downloaded locally and excluded from Git. If working with a client's private data later, keep source files and notes outside public repositories.

The CFPB explains that these public complaints are not a statistical sample and need context. This project consequently avoids company rankings and claims about current service performance. Source dates are interpreted according to their field definitions, not treated as resolution timestamps.
