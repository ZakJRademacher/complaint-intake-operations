"""Import Excel review-sheet CSV without losing notes for other complaint IDs."""
import argparse
import csv
import os
from pathlib import Path
from pipeline import ROOT, STATUSES, read_notes, write_csv

ALIASES = {'Complaint ID':'complaint_id','Owner':'owner','Review status':'review_status','Notes':'notes'}


def update(source, destination):
    merged = read_notes(destination)
    seen = set()
    with Path(source).open(encoding='utf-8-sig',newline='') as stream:
        reader = csv.reader(stream)
        for row in reader:
            header = [ALIASES.get(value.strip(),value.strip()) for value in row]
            if set(ALIASES.values()) <= set(header):
                break
        else:
            raise ValueError('Required note columns not found')
        for row in reader:
            record = dict(zip(header,row))
            key = record.get('complaint_id','').strip()
            if not key:
                continue
            if not key.isdecimal() or key in seen:
                raise ValueError('Invalid or duplicate import ID: '+key)
            seen.add(key)
            owner = record.get('owner','').strip()
            status = record.get('review_status','').strip() or 'Not started'
            note = record.get('notes','').strip()
            if status not in STATUSES or (status=='Resolved' and (not owner or not note)):
                raise ValueError('Invalid review state for '+key)
            # Untouched template rows never erase existing work.
            if not owner and not note and status=='Not started':
                continue
            merged[key] = (owner,status,note)
    destination = Path(destination)
    temp = destination.with_suffix('.tmp')
    write_csv(temp,[dict(zip(['complaint_id','owner','review_status','notes'],(key,*value)))
                    for key,value in sorted(merged.items())],['complaint_id','owner','review_status','notes'])
    os.replace(temp,destination)
    return len(merged)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--notes',type=Path,default=ROOT/'data/review_notes.csv')
    args=parser.parse_args()
    print(f'{update(args.source,args.notes)} saved note records')
