"""Export the complaint reporting projection from a validated SQLite snapshot."""
from pathlib import Path
import argparse,csv,hashlib,json,sqlite3

def export(database, output):
    output.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(f'file:{database.resolve().as_posix()}?mode=ro',uri=True)
    path=output/'Cases.csv'
    total=review_total=date_issues=0
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['Complaint ID','Received','Year','Month','Channel','Product','Timely flag','Routing Days','Valid Duration','Over 7 Days','Needs Review','Date Issue'])
        for key,received,channel,product,timely,days in db.execute('SELECT complaint_id,received,channel,product,timely,intake_days FROM cases ORDER BY source_row'):
            valid=int(days is not None and days>=0)
            over=int(days is not None and days>7)
            issue=1-valid
            review=int(over or issue or timely!='Yes')
            writer.writerow([key,received,(received or 'Unknown')[:4],(received or 'Unknown')[:7],channel,product,timely,days,valid,over,review,issue])
            total+=1;review_total+=review;date_issues+=issue
    evidence={'cases':total,'review_cases':review_total,'date_issues':date_issues,'database_sha256':hashlib.sha256(database.read_bytes()).hexdigest(),'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (output/'export-verification.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return evidence

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'powerbi-rebuild/data')
    args=parser.parse_args()
    print(json.dumps(export(args.database,args.output),indent=2))
