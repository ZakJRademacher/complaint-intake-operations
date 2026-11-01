"""Build a two-page briefing and presentation images from executed results."""
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
import sys
sys.path.insert(0, str(ROOT/'src'))
from publication import current_output
RESULTS=current_output(ROOT/'results')
OUT=ROOT/'deliverables'; DOCS=ROOT/'docs'
OUT.mkdir(exist_ok=True);DOCS.mkdir(exist_ok=True)
a=json.loads((RESULTS/'analysis.json').read_text())
m=a['metrics']; r=a['reports']
navy='#172B4B'; teal='#285CD2'; muted='#5C6C87'; amber='#AD512C'
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
story += [t,p('What the review should focus on','Heading2'),p('Postal mail has a 21-day P90 routing interval, compared with 5 days for Web. These are descriptive channel observations, with nonnegative intervals only. They do not establish a cause or compare company quality.'),p('The 7,052 negative intervals remain in volume counts and are excluded from duration statistics. Very long positive intervals are also retained and flagged for source verification; an interval alone does not establish how an individual case was handled.'),Image(str(OUT/'routing-by-channel.png'),width=6.8*inch,height=2.04*inch),PageBreak(),p('Delivery, controls &amp; repeatability','BriefTitle'),p('A practical handoff for remote reporting and data-cleaning work','Deck'),p('Run and review','Heading2'),p('1. Download the documented Kaggle snapshot and run the standard-library Python pipeline. It creates SQLite tables, six SQL extracts, a metrics JSON file and reconciliation results.'),p('2. Open the Excel workbook. The overview reconciles to the channel table; monthly rates use explicit denominators. The review sheet contains 100 longest valid routing-delay examples, with Owner, Review status and Notes entry cells.'),p('3. Export the Review queue sheet as CSV and import its notes by Complaint ID. Untouched template rows do not erase saved notes. Invalid status values and resolved items without an owner and note are rejected before writing.'),p('4. Rerun the report. Saved notes rejoin by stable ID. Notes whose cases are absent from the new source appear in a separate unmatched-notes extract.'),p('Evidence a client can inspect','Heading2'),p('27 automated tests cover date boundaries, negative intervals, unknown response flags, duplicate/conflicting IDs, note preservation and safe import. Seven full-data controls reconcile row partitions and channel, monthly and product counts. The workbook checks headline values, formula propagation and the resolution-note guard.'),p('Example SQL: duration denominator','Heading2'),Preformatted('SELECT channel, COUNT(*) AS valid_intervals,\n       AVG(intake_days) AS mean_days\nFROM cases\nWHERE intake_days >= 0\nGROUP BY channel;',ParagraphStyle(name='Code',fontName='Courier',fontSize=9,leading=12,backColor=colors.HexColor('#F1F5F7'),borderPadding=8)),p('Scope and limitations','Heading2'),p('This is a historical portfolio demonstration, not a live backlog. November 2017 is partial. The illustrative seven-day routing review rule is configurable in Python and is not a legal or regulatory SLA. The source timely-response flag is a separate categorical measure. There is no resolution date, market-share denominator or representative sample of all consumers.'),p('Source and privacy','Heading2'),p('Kaggle: sebastienverpile/consumercomplaintsdata, CC0 Public Domain, originally the CFPB Consumer Complaint Database. Derived exports omit narratives, company names, ZIP codes, state, tags and consent fields. Code is MIT licensed; provenance and a source-file SHA-256 are supplied. Native desktop Excel recalculation was not tested.'),p('<link href="https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata" color="#285CD2">Kaggle dataset</link> | <link href="https://www.consumerfinance.gov/data-research/consumer-complaints/" color="#285CD2">CFPB database</link> | <link href="https://cfpb.github.io/api/ccdb/fields.html" color="#285CD2">Official field definitions</link>')]
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor(muted));canvas.drawString(42,27,'Zak Rademacher | Complaint intake operations | Personal portfolio project');canvas.drawRightString(570,27,str(doc.page))
SimpleDocTemplate(str(OUT/'case-study.pdf'),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=42,title='Complaint intake and response operations',author='Zak Rademacher').build(story,onFirstPage=footer,onLaterPages=footer)

print(json.dumps({'pdf':str(OUT/'case-study.pdf'),'cover':str(OUT/'portfolio-cover.png'),'documentation':'preserved'}))
