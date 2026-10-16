"""Build a two-page briefing, cover and handoff documentation from executed results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted

rl_config.useA85=False
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'; DOCS=ROOT/'docs'
OUT.mkdir(exist_ok=True);DOCS.mkdir(exist_ok=True)
a=json.loads((ROOT/'results/analysis.json').read_text())
m=a['metrics']; r=a['reports']
navy='#18283F'; teal='#087F73'; muted='#65758A'; amber='#BA6A13'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':navy,'axes.labelcolor':muted,'xtick.color':muted,'ytick.color':muted,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
def chart(ax):
    rows=r['channels'][::-1]
    ax.barh([x['channel'] for x in rows],[x['p90_days'] for x in rows],color=teal,height=.58)
    ax.set_xlim(0,25);ax.set_xlabel('90th percentile: calendar days from receipt to sending')
    ax.grid(axis='x',color='#E4EAF0');ax.set_axisbelow(True)
    for i,x in enumerate(rows):ax.text(x['p90_days']+.5,i,str(x['p90_days']),va='center',fontsize=11)
fig,ax=plt.subplots(figsize=(10,3));chart(ax);fig.tight_layout();fig.savefig(OUT/'routing-by-channel.png',dpi=160,facecolor='white');plt.close(fig)
fig=plt.figure(figsize=(15,10),facecolor='#F4F7F8')
fig.text(.06,.93,'COMPLAINT INTAKE & RESPONSE OPERATIONS',fontsize=22,weight='bold')
fig.text(.06,.89,'A repeatable reporting and review workflow | Kaggle / CFPB | 2011–November 15, 2017',fontsize=12,color=muted)
for x,label,value in [(.06,'HISTORICAL COMPLAINTS',f"{m['cases']:,}"),(.39,'SOURCE TIMELY RESPONSE',f"{m['timely_rate']:.1%}"),(.72,'DATE-ORDER ANOMALIES',f"{m['negative_intervals']:,}")]:
    fig.text(x,.81,label,fontsize=10,weight='bold',color=muted);fig.text(x,.755,value,fontsize=28,weight='bold')
ax=fig.add_axes([.15,.35,.75,.30]);chart(ax)
ax.set_title('Routing intervals vary by intake channel',loc='left',fontweight='bold',pad=14)
fig.text(.06,.235,'FROM RAW CSV TO AN ACTIONABLE HANDOFF',fontsize=13,weight='bold')
fig.text(.06,.19,'Python validation → SQLite reporting → Excel review queue → saved reviewer notes',fontsize=14,color=teal)
fig.text(.06,.13,f"{m['review_queue_cases']:,} flagged records | 100 examples in Excel | No narrative or company data in exports",fontsize=11,color=muted)
fig.text(.06,.065,'Historical portfolio demonstration. Routing intervals are not company resolution times or regulatory SLA measurements.',fontsize=10,color=muted)
fig.savefig(OUT/'portfolio-cover.png',dpi=120,facecolor=fig.get_facecolor());plt.close(fig)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BriefTitle',fontName='Helvetica-Bold',fontSize=22,leading=25,textColor=colors.HexColor(navy),spaceAfter=12))
styles.add(ParagraphStyle(name='Deck',fontSize=10,leading=14,textColor=colors.HexColor(muted),spaceAfter=14))
styles['BodyText'].fontSize=10;styles['BodyText'].leading=14;styles['BodyText'].spaceAfter=8
styles['Heading2'].fontName='Helvetica-Bold';styles['Heading2'].fontSize=13;styles['Heading2'].leading=17;styles['Heading2'].spaceBefore=12;styles['Heading2'].textColor=colors.HexColor(navy)
def p(text,style='BodyText'):return Paragraph(text,styles[style])
story=[p('Complaint intake &amp; response operations','BriefTitle'),p('Management briefing | Personal portfolio project | Historical snapshot: Dec 2011–Nov 15, 2017','Deck'),
       p('The business task','Heading2'),p('Turn a large complaint intake export into a repeatable operations report, a traceable review queue and an Excel handoff. Preserve reviewer notes across runs and distinguish source response flags from intake routing intervals.')]
table=[['CONTROL / RESULT','OBSERVED VALUE'],['Source complaint records',f"{m['cases']:,}"],['Source timely flag = Yes',f"{m['timely_yes']:,} / {m['known_timely']:,} ({m['timely_rate']:.2%})"],['Valid routing-date intervals',f"{m['valid_intervals']:,}"],['Median / P90 valid routing interval',f"{m['median_intake_days']:g} / {m['p90_intake_days']} calendar days"],['Negative date intervals',f"{m['negative_intervals']:,}"],['Intervals above 7-day review threshold',f"{m['over_review_days']:,} ({m['over_review_days']/m['valid_intervals']:.2%} of valid intervals)"],['Flagged cases, all review reasons',f"{m['review_queue_cases']:,}"]]
t=Table(table,colWidths=[3.25*inch,3.55*inch]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(navy)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F1F5F7'),colors.white])]))
story += [t,p('What the review should focus on','Heading2'),p('Postal mail has a 21-day P90 routing interval, compared with 5 days for Web. These are descriptive channel observations, with nonnegative intervals only. They do not establish a cause or compare company quality.'),p('The 7,052 negative intervals remain in volume counts and are excluded from duration statistics. Very long positive intervals are also retained and flagged for source verification; an interval alone does not establish how an individual case was handled.'),Image(str(OUT/'routing-by-channel.png'),width=6.8*inch,height=2.04*inch),PageBreak(),p('Delivery, controls &amp; repeatability','BriefTitle'),p('A practical handoff for remote reporting and data-cleaning work','Deck'),p('Run and review','Heading2'),p('1. Download the documented Kaggle snapshot and run the standard-library Python pipeline. It creates SQLite tables, six SQL extracts, a metrics JSON file and reconciliation results.'),p('2. Open the Excel workbook. The overview reconciles to the channel table; monthly rates use explicit denominators. The review sheet contains 100 longest valid routing-delay examples, with Owner, Review status and Notes entry cells.'),p('3. Export the Review queue sheet as CSV and import its notes by Complaint ID. Untouched template rows do not erase saved notes. Invalid status values and resolved items without an owner and note are rejected before writing.'),p('4. Rerun the report. Saved notes rejoin by stable ID. Notes whose cases are absent from the new source appear in a separate unmatched-notes extract.'),p('Evidence a client can inspect','Heading2'),p('Fourteen automated tests cover date boundaries, negative intervals, unknown response flags, duplicate/conflicting IDs, note preservation and safe import. Seven full-data controls reconcile row partitions and channel, monthly and product counts. The workbook checks headline values, formula propagation and the resolution-note guard.'),p('Example SQL: duration denominator','Heading2'),Preformatted('SELECT channel, COUNT(*) AS valid_intervals,\n       AVG(intake_days) AS mean_days\nFROM cases\nWHERE intake_days >= 0\nGROUP BY channel;',ParagraphStyle(name='Code',fontName='Courier',fontSize=9,leading=12,backColor=colors.HexColor('#F1F5F7'),borderPadding=8)),p('Scope and limitations','Heading2'),p('This is a historical portfolio demonstration, not a live backlog. November 2017 is partial. The illustrative seven-day routing review rule is configurable in Python and is not a legal or regulatory SLA. The source timely-response flag is a separate categorical measure. There is no resolution date, market-share denominator or representative sample of all consumers.'),p('Source and privacy','Heading2'),p('Kaggle: sebastienverpile/consumercomplaintsdata, CC0 Public Domain, originally the CFPB Consumer Complaint Database. Derived exports omit narratives, company names, ZIP codes, state, tags and consent fields. Code is MIT licensed; provenance and a source-file SHA-256 are supplied. Native desktop Excel recalculation was not tested.'),p('<link href="https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata" color="#087F73">Kaggle dataset</link> | <link href="https://www.consumerfinance.gov/data-research/consumer-complaints/" color="#087F73">CFPB database</link> | <link href="https://cfpb.github.io/api/ccdb/fields.html" color="#087F73">Official field definitions</link>')]
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor(muted));canvas.drawString(42,27,'Zak Rademacher | Complaint intake operations | Personal portfolio project');canvas.drawRightString(570,27,str(doc.page))
SimpleDocTemplate(str(OUT/'case-study.pdf'),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=42,title='Complaint intake and response operations',author='Zak Rademacher').build(story,onFirstPage=footer,onLaterPages=footer)

readme=f'''# Complaint Intake & Response Operations

**Python · SQLite · Excel · recurring operations reporting**

An operations reporting project using **{m['cases']:,} real complaint records** from a historical Kaggle mirror of the CFPB database. It converts a large CSV into validated SQL reports and an Excel review queue, and preserves reviewer notes between runs.

![Portfolio overview](deliverables/portfolio-cover.png)

## Inspect the work

- [Two-page management briefing](deliverables/case-study.pdf)
- [Excel workbook](deliverables/complaint-operations-review.xlsx) — overview, monthly report and 100 editable review examples
- [Python pipeline](src/pipeline.py), [six SQL reports](sql), [14 automated tests](tests/test_workflow.py)
- [Method](docs/METHOD.md), [data dictionary](docs/DATA_DICTIONARY.md), [Excel / notes guide](docs/EXCEL_GUIDE.md), [verification](docs/QA_REPORT.md)
- [Five-minute walkthrough](docs/PROJECT_WALKTHROUGH.md), [source and license](docs/SOURCES.md)

## Why this work is useful

The deliverables demonstrate CSV cleanup, recurring report preparation, SQL aggregation, spreadsheet formulas, exception handling and documented handoff. The project includes stable-ID review-note persistence, a practical requirement when another person reviews an export and the source is refreshed later. This is a personal portfolio demonstration; no client or employer engagement is claimed.

## Results from the complete snapshot

| Measure | Result |
|---|---:|
| Complaint records | {m['cases']:,} |
| Source timely flag: Yes | {m['timely_yes']:,} ({m['timely_rate']:.2%} of known flags) |
| Nonnegative routing intervals | {m['valid_intervals']:,} |
| Median / P90 interval | {m['median_intake_days']:g} / {m['p90_intake_days']} calendar days |
| Negative intervals, flagged separately | {m['negative_intervals']:,} |
| Routing interval above 7 days | {m['over_review_days']:,} |
| Review queue across all flag reasons | {m['review_queue_cases']:,} |

**Interpretation:** routing is the recorded sent date minus received date, not company resolution time. The seven-day cutoff is a demonstration review rule, not a legal SLA. The source's timely-response flag measures something different. November 2017 ends on Nov 15. Do not interpret these historical records as a current backlog or compare lender quality from complaint volumes.

## Reproduce the core project

Python 3.10+; the pipeline and tests use only the standard library. Download size is about 112 MB, extracted CSV about 413 MB. Allow approximately 1 GB free space and several minutes for the full run.

```sh
python src/download_data.py
python src/pipeline.py
python -m unittest discover -s tests -v
```

The downloader uses the public Kaggle dataset endpoint. If its access policy changes, download `Consumer_Complaints.csv` manually from the linked Kaggle page into `data/raw/`. The delivered source fingerprint is recorded in `results/analysis.json`; upstream snapshots may change.

Generated locally: `results/complaints.sqlite`, the complete `results/review_queue.csv`, `quality_issues.csv`, and all aggregate reports. Raw data, database and full row-level exports are excluded from the compact repository. The delivered workbook shows only 100 selected review examples. They are not a representative sample.

### Carry notes into the next run

Export the **Review queue** Excel sheet as UTF-8 CSV (one sheet), then:

```sh
python src/update_notes.py exported-review-queue.csv
python src/pipeline.py
```

See the [Excel guide](docs/EXCEL_GUIDE.md) for statuses, validation, refresh and limits. No fictitious completed reviews are supplied.

### Optional presentation rebuild

```sh
pip install -r requirements-visuals.txt
python tools/build_presentation.py
node tools/build_workbook.mjs /absolute/path/to/complaint-operations
```

The workbook builder requires `@oai/artifact-tool`, supplied by a compatible Codex runtime. Set `RETAIL_ARTIFACT_ROOT` to that runtime's Node dependency root when necessary. The checked-in XLSX is ready to inspect; the Python/SQL workflow and tests do not require that optional authoring package. Artifact-tool recalculation was tested; native Excel was not available.

```sh
pip install -r requirements-qa.txt
python tools/verify_outputs.py
python tools/package_project.py
```

## Repository layout

`src/` ingestion and note import · `sql/` readable reports · `tests/` edge cases · `data/review_notes.csv` persistent annotation input · `results/` aggregates and evidence · `deliverables/` client-facing files · `docs/` handoff · `tools/` presentation, verification and packaging.

## Data and license

[Kaggle dataset](https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata), labeled CC0 Public Domain, originally the [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/). The snapshot covers Dec 1, 2011–Nov 15, 2017. Code: MIT. Derived exports omit narratives, company names, ZIP, state and tags. Public complaints are not a statistical sample of all consumer experiences.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
(DOCS/'METHOD.md').write_text('''# Method and operating assumptions

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

The reporting database is rebuilt in place. Do not run two builds simultaneously or consume its reports while a build is running. Back up edited review notes. A failed run should be corrected and rerun before using its output; the report directory is not an atomic multi-file transaction.

## Scope
Historical public snapshot; partial final month; no live backlog, no resolution-time field and no financial advice or lender-quality comparison. Public complaints are not a representative consumer sample. Very long intervals require source verification, not automatic attribution of fault. Excel's 100 examples are the longest nonnegative flagged intervals, not random cases and not the full review population.
''',encoding='utf-8')
(DOCS/'DATA_DICTIONARY.md').write_text('''# Data dictionary

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
''',encoding='utf-8')
(DOCS/'EXCEL_GUIDE.md').write_text('''# Excel and reviewer-note guide

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
''',encoding='utf-8')
(DOCS/'SOURCES.md').write_text(f'''# Source, provenance and licensing

- Dataset: [Consumer Complaints Database](https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata), uploaded by Sebastien Verpile. Kaggle labels it **CC0 Public Domain**; mirror last updated January 2018.
- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/sebastienverpile/consumercomplaintsdata
- Original: [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/).
- Official [field definitions](https://cfpb.github.io/api/ccdb/fields.html) and [Data.gov listing](https://catalog.data.gov/dataset/consumer-complaint-database).
- Downloaded for this project: October 15, 2026. Actual snapshot receipt dates: {m['first_received']} through {m['last_received']}. Historical mirror, not the current CFPB export.
- Exact source CSV: {a['source']['file']}; SHA-256 `{a['source']['sha256']}`.
- Code and original documentation: MIT, see LICENSE. Data licensing is separate from code licensing.

The source has 18 fields. Only eight selected fields are used. Full narratives, company names, ZIP codes, state, tags, consent and public company-response narrative are not included in derived reports or the public project. Raw data is downloaded locally and excluded from Git. If working with a client's private data later, keep source files and notes outside public repositories.

The CFPB explains that these public complaints are not a statistical sample and need context. This project consequently avoids company rankings and claims about current service performance. Source dates are interpreted according to their field definitions, not treated as resolution timestamps.
''',encoding='utf-8')
(DOCS/'PROJECT_WALKTHROUGH.md').write_text('''# Five-minute project walkthrough

1. **Problem:** A recurring CSV arrives, operations needs counts, date anomalies and a traceable review list, and someone needs to annotate cases without losing their work next refresh.
2. **Source:** Show the real Kaggle/CFPB snapshot and provenance fingerprint. Explain why narratives and identifying company/location fields are omitted.
3. **Code:** Show `src/pipeline.py` staging and ID rules. Open `sql/channels.sql` for CTEs, window functions and a valid P90 denominator. Distinguish the source response flag from routing days.
4. **Deliverable:** Open Excel overview, then Monthly and Review queue. Explain why the partial month is labeled and why a 100-case selection cannot represent all flagged complaints.
5. **Handoff:** Enter an owner, status and note on a copy of the workbook. Export that sheet, import its CSV, rerun, and inspect merged notes. Never publish real annotations to the public repository.
6. **Evidence:** Run 14 tests, inspect seven full-data reconciliation controls and the independent output verification. Explain the native-Excel limitation plainly.

## Relevant paid work
CSV cleanup and validation; SQL report preparation; recurring spreadsheet refreshes; exception-list handoffs; documentation of repeatable admin workflows. Ask a prospective client about column definitions, review thresholds, refresh frequency and note ownership before adapting the project.

## Honest limits
This is a personal portfolio project. It does not establish a prior client relationship, production deployment, earned savings, certification or a completed degree. The dataset is historical and the example queue is intentionally small. Automated controls support a review; they do not adjudicate complaints.
''',encoding='utf-8')
(DOCS/'UPWORK_LISTING.md').write_text('''# Portfolio listing

Title: Complaint Intake Review | Python, SQL & Excel

Role: Portfolio project owner | Data cleaning, SQL reporting and Excel workflow

Description: Personal portfolio project using 903,983 real Kaggle/CFPB complaint records. Python validates IDs and dates, and SQLite creates channel, monthly and review-queue reports. The Excel workbook includes formulas, a chart and 100 review examples. A CSV import preserves reviewer notes across runs. Includes a two-page briefing, full documentation and 14 automated tests. Historical public data; seven-day routing review is a demo rule, not a regulatory SLA.

Skills: Python; SQL; Microsoft Excel; Data Cleaning; Data Analysis.

Cover caption: Complaint intake reporting: 903,983 Kaggle/CFPB records, SQL controls and an Excel review workflow.

PDF caption: Two-page briefing: findings, review-note handoff, tests, source definitions and reporting limitations.
''',encoding='utf-8')
(OUT/'README.md').write_text('''# Client-facing deliverables

- `complaint-operations-review.xlsx`: editable three-sheet review workbook; macros are not used.
- `case-study.pdf`: two-page management briefing.
- `portfolio-cover.png`: project overview.
- `routing-by-channel.png`: sourced descriptive chart.
- `excel-*-preview.png`: visual reviews of each workbook sheet.

Read the project README and docs before adapting to a new source. The 100 review examples are selected historical cases, not a live work queue. No completed review is fabricated.
''',encoding='utf-8')
print(json.dumps({'pdf':str(OUT/'case-study.pdf'),'cover':str(OUT/'portfolio-cover.png'),'documentation':'written'}))
