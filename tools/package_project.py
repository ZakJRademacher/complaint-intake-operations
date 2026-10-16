"""Compact portfolio bundle, with hashes and no raw/narrative data."""
import csv
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sample=ROOT/'data/sample';sample.mkdir(exist_ok=True)
with (ROOT/'results/review_queue.csv').open(encoding='utf-8-sig',newline='') as source:
    reader=csv.reader(source)
    with (sample/'review_examples_100.csv').open('w',encoding='utf-8-sig',newline='') as dest:
        writer=csv.writer(dest);writer.writerow(next(reader))
        for i,row in enumerate(reader):
            if i==100:break
            writer.writerow(row)
(sample/'README.md').write_text('''# Selected review examples

These are the first 100 cases from the full flagged queue sorted by longest nonnegative routing interval, then source ID. They are selected historical examples, not a random or representative sample, and do not include all flag types. No review annotations have been invented. Regenerate the full queue from the original Kaggle CSV using the pipeline.
''',encoding='utf-8')
files=[]
for folder in ['src','sql','tests','tools','docs','deliverables','data/sample','.github']:
    files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.inspect.ndjson') and p.name!='package-manifest.json']
files += [p for p in ROOT.glob('*') if p.is_file()]
files.append(ROOT/'data/review_notes.csv')
files += [p for p in (ROOT/'results').glob('*') if p.suffix=='.json' or (p.suffix=='.csv' and p.name not in {'review_queue.csv','quality_issues.csv'})]
files=sorted(set(files))
manifest=ROOT/'docs/package-manifest.json'
manifest.write_text(json.dumps({'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    'omitted':['data/raw/*','results/complaints.sqlite','results/review_queue.csv','results/quality_issues.csv'],'rebuild':'See README.md'},indent=2),encoding='utf-8')
files.append(manifest)
target=ROOT.parent/'complaint-operations-portfolio.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in files:archive.write(p,'complaint-operations/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
print(json.dumps({'zip':str(target),'files':len(files),'bytes':target.stat().st_size}))
