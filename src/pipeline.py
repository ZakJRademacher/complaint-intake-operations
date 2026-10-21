"""Reproducible, local complaint intake reporting. Python 3.10+, standard library."""
import argparse
import csv
import hashlib
import json
import math
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from contextlib import closing
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from publication import current_output, publish
FIELDS = ['Complaint ID', 'Date received', 'Date sent to company', 'Product', 'Issue',
          'Submitted via', 'Company response to consumer', 'Timely response?']
STATUSES = {'Not started', 'In progress', 'Resolved'}


def parse_date(value):
    try:
        return datetime.strptime(value.strip(), '%m/%d/%Y').date().isoformat()
    except ValueError:
        return None


def read_notes(path):
    notes = {}
    if not Path(path).exists():
        return notes
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'complaint_id', 'owner', 'review_status', 'notes'} <= set(reader.fieldnames or []):
            raise ValueError('Review notes must have complaint_id, owner, review_status, notes headers')
        for row in reader:
            key = row['complaint_id'].strip()
            if not key or not key.isdecimal() or key in notes:
                raise ValueError('Invalid or duplicate review-note ID: ' + key)
            status = row['review_status'].strip() or 'Not started'
            owner, text = row['owner'].strip(), row['notes'].strip()
            if status not in STATUSES:
                raise ValueError('Unknown review status: ' + status)
            if status == 'Resolved' and (not owner or not text):
                raise ValueError('Resolved notes require an owner and a note')
            notes[key] = (owner, status, text)
    return notes


def write_csv(path, rows, headers=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = list(rows[0]) if rows else []
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _build(source, output, notes_path, review_days=7):
    if review_days < 0:
        raise ValueError('review_days must be nonnegative')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    notes = read_notes(notes_path)  # Validate before touching the existing database.
    database = output / 'complaints.sqlite'
    with closing(sqlite3.connect(database)) as conn:
        conn.row_factory = sqlite3.Row
        conn.executescript('''DROP TABLE IF EXISTS selected;
        DROP TABLE IF EXISTS cases;
        DROP TABLE IF EXISTS review_notes;
        CREATE TABLE selected(source_row INTEGER PRIMARY KEY, complaint_id TEXT, fingerprint TEXT,
          received TEXT, sent TEXT, product TEXT, issue TEXT, channel TEXT, response TEXT, timely TEXT);
        CREATE TABLE review_notes(complaint_id TEXT PRIMARY KEY, owner TEXT, review_status TEXT, notes TEXT);
        ''')
        conn.executemany('INSERT INTO review_notes VALUES (?,?,?,?)', [(key, *value) for key, value in notes.items()])
        rows, invalid_ids, batch = 0, 0, []
        with Path(source).open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if not set(FIELDS) <= set(reader.fieldnames or []):
                raise ValueError('Source is missing required fields')
            for line, record in enumerate(reader, start=2):
                rows += 1
                values = [record[field].strip() for field in FIELDS]
                key = values[0]
                if not key.isdecimal():
                    invalid_ids += 1
                    key = None
                fingerprint = hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()
                batch.append((line, key, fingerprint, *values[1:]))
                if len(batch) == 10000:
                    conn.executemany('INSERT INTO selected VALUES (?,?,?,?,?,?,?,?,?,?)', batch)
                    batch.clear()
            conn.executemany('INSERT INTO selected VALUES (?,?,?,?,?,?,?,?,?,?)', batch)
        conn.execute('CREATE INDEX selected_id ON selected(complaint_id)')
        conflicts = conn.execute('''SELECT COUNT(*) FROM selected WHERE complaint_id IN
           (SELECT complaint_id FROM selected WHERE complaint_id IS NOT NULL
            GROUP BY complaint_id HAVING COUNT(DISTINCT fingerprint)>1)''').fetchone()[0]
        conn.create_function('iso_date', 1, parse_date)
        conn.executescript('''CREATE TABLE cases AS
          WITH unique_rows AS (
            SELECT MIN(source_row) first_row FROM selected WHERE complaint_id IS NOT NULL
            GROUP BY complaint_id HAVING COUNT(DISTINCT fingerprint)=1
          ), parsed AS (
            SELECT s.source_row,s.complaint_id,iso_date(s.received) received,
              iso_date(s.sent) sent,COALESCE(NULLIF(s.product,''),'Unspecified') product,
              COALESCE(NULLIF(s.issue,''),'Unspecified') issue,
              COALESCE(NULLIF(s.channel,''),'Unspecified') channel,
              COALESCE(NULLIF(s.response,''),'Unspecified') response,
              CASE WHEN lower(s.timely)='yes' THEN 'Yes' WHEN lower(s.timely)='no' THEN 'No' ELSE 'Unknown' END timely
            FROM selected s JOIN unique_rows u ON s.source_row=u.first_row
          ) SELECT *,COALESCE(substr(received,1,7),'Unknown') month,
            CASE WHEN received IS NOT NULL AND sent IS NOT NULL THEN CAST(julianday(sent)-julianday(received) AS INTEGER) END intake_days
          FROM parsed;
          CREATE UNIQUE INDEX cases_id ON cases(complaint_id);
          CREATE INDEX cases_channel ON cases(channel);
        ''')
        count = conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
        duplicate_rows = rows - invalid_ids - conflicts - count
        metrics = dict(conn.execute('''SELECT COUNT(*) cases,
          SUM(timely='Yes') timely_yes,SUM(timely='No') timely_no,SUM(timely='Unknown') timely_unknown,
          SUM(intake_days<0) negative_intervals,SUM(intake_days IS NULL) invalid_dates,
          SUM(intake_days>=0) valid_intervals,SUM(intake_days>?) over_review_days,
          MIN(received) first_received,MAX(received) last_received FROM cases''', (review_days,)).fetchone())
        metrics = {key: (value if value is not None else 0) for key,value in metrics.items()}
        metrics.update(input_rows=rows, invalid_ids=invalid_ids, conflicting_id_rows=conflicts,
                       identical_duplicate_rows=duplicate_rows, review_days=review_days)
        metrics['known_timely'] = metrics['timely_yes'] + metrics['timely_no']
        metrics['timely_rate'] = metrics['timely_yes']/metrics['known_timely'] if metrics['known_timely'] else None
        valid_days = [r[0] for r in conn.execute('SELECT intake_days FROM cases WHERE intake_days>=0 ORDER BY intake_days')]
        middle = len(valid_days)//2
        metrics['median_intake_days'] = ((valid_days[middle-1]+valid_days[middle])/2 if len(valid_days)%2==0 else valid_days[middle]) if valid_days else None
        metrics['p90_intake_days'] = valid_days[math.ceil(.9*len(valid_days))-1] if valid_days else None
        reports = {}
        for name in ['channels', 'monthly', 'products', 'review_queue', 'quality_issues', 'unmatched_notes']:
            query = (ROOT/'sql'/f'{name}.sql').read_text(encoding='utf-8')
            cursor = conn.execute(query, {'review_days': review_days})
            headers = [column[0] for column in cursor.description]
            report = [dict(row) for row in cursor]
            write_csv(output/f'{name}.csv', report, headers)
            reports[name] = report[:100] if name in {'review_queue','quality_issues'} else report
            if name == 'review_queue':
                metrics['review_queue_cases'] = len(report)
        metrics['unmatched_notes'] = len(reports['unmatched_notes'])
        checks = {
            'source_partition': rows == count+invalid_ids+conflicts+duplicate_rows,
            'response_partition': count == metrics['timely_yes']+metrics['timely_no']+metrics['timely_unknown'],
            'date_partition': count == metrics['valid_intervals']+metrics['negative_intervals']+metrics['invalid_dates'],
            'channel_reconciliation': count == sum(r['cases'] for r in reports['channels']),
            'monthly_reconciliation': count == sum(r['cases'] for r in reports['monthly']),
            'product_reconciliation': count == sum(r['cases'] for r in reports['products']),
            'database_integrity': conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok',
        }
        source_hash = hashlib.sha256()
        with Path(source).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                source_hash.update(chunk)
        analysis = {'source': {'file':Path(source).name,'sha256':source_hash.hexdigest()},
                    'metrics':metrics, 'checks':checks, 'reports':reports}
        (output/'analysis.json').write_text(json.dumps(analysis, indent=2), encoding='utf-8')
        conn.commit()
        if not all(checks.values()):
            raise AssertionError(checks)
        return analysis

def build(source, output, notes_path, review_days=7):
    return publish(output, lambda stage: _build(source, stage, notes_path, review_days))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'data/raw/Consumer_Complaints.csv')
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    parser.add_argument('--notes', type=Path, default=ROOT/'data/review_notes.csv')
    parser.add_argument('--review-days', type=int, default=7)
    args = parser.parse_args()
    result = build(args.source,args.output,args.notes,args.review_days)
    print(json.dumps({'metrics':result['metrics'],'checks':result['checks']}, indent=2))
