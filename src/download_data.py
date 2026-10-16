"""Download the public Kaggle snapshot; no credentials required at publication."""
import urllib.request
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'data/raw'
target.mkdir(parents=True,exist_ok=True)
archive=target/'kaggle-complaints.zip'
urllib.request.urlretrieve('https://www.kaggle.com/api/v1/datasets/download/sebastienverpile/consumercomplaintsdata',archive)
with zipfile.ZipFile(archive) as z:
    member=next(n for n in z.namelist() if Path(n).name=='Consumer_Complaints.csv')
    with z.open(member) as source, (target/'Consumer_Complaints.csv').open('wb') as output:
        import shutil
        shutil.copyfileobj(source,output)
print(target/'Consumer_Complaints.csv')
