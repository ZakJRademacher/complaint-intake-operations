"""Synthetic edge cases only; portfolio findings use the full real Kaggle CSV."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import FIELDS, build, parse_date, read_notes, write_csv
from update_notes import update


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        test_root=Path(__file__).resolve().parents[1]/'tmp/tests'
        test_root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=test_root)
        self.root=Path(self.tmp.name)
        self.source=self.root/'source.csv'
        self.notes=self.root/'notes.csv'
        write_csv(self.notes,[],['complaint_id','owner','review_status','notes'])

    def tearDown(self):
        self.tmp.cleanup()

    def row(self,key='1',received='01/01/2017',sent='01/01/2017',timely='Yes'):
        return dict(zip(FIELDS,[key,received,sent,'Mortgage','Service','Web','Closed',timely]))

    def run_rows(self,rows):
        write_csv(self.source,rows,FIELDS)
        return build(self.source,self.root/'results',self.notes)

    def test_date_parser(self):
        self.assertEqual(parse_date('2/29/2016'),'2016-02-29')
        self.assertIsNone(parse_date('2/29/2017'))

    def test_negative_retained_but_not_duration(self):
        result=self.run_rows([self.row(),self.row('2',sent='12/31/2016')])
        self.assertEqual(result['metrics']['cases'],2)
        self.assertEqual(result['metrics']['valid_intervals'],1)
        self.assertEqual(result['metrics']['negative_intervals'],1)
        self.assertEqual(result['metrics']['median_intake_days'],0)

    def test_threshold_strictly_greater_than_seven(self):
        result=self.run_rows([self.row(sent='01/08/2017'),self.row('2',sent='01/09/2017')])
        self.assertEqual(result['metrics']['over_review_days'],1)

    def test_unknown_timely_not_in_denominator(self):
        m=self.run_rows([self.row(),self.row('2',timely=''),self.row('3',timely='No')])['metrics']
        self.assertEqual((m['known_timely'],m['timely_unknown'],m['timely_rate']),(2,1,.5))

    def test_identical_duplicate_keeps_first(self):
        m=self.run_rows([self.row(),self.row()])['metrics']
        self.assertEqual((m['cases'],m['identical_duplicate_rows']),(1,1))

    def test_conflicting_id_quarantines_all_versions(self):
        m=self.run_rows([self.row(),self.row(sent='01/02/2017'),self.row('2')])['metrics']
        self.assertEqual((m['cases'],m['conflicting_id_rows']),(1,2))

    def test_invalid_id_quarantined(self):
        m=self.run_rows([self.row('bad'),self.row('2')])['metrics']
        self.assertEqual((m['cases'],m['invalid_ids']),(1,1))

    def test_bad_date_counts_and_flags(self):
        result=self.run_rows([self.row(received='not a date')])
        self.assertEqual(result['metrics']['invalid_dates'],1)
        self.assertEqual(result['reports']['monthly'][0]['month'],'Unknown')
        self.assertTrue(all(result['checks'].values()))

    def test_nearest_rank_p90(self):
        result=self.run_rows([self.row(str(i),sent=f'01/{i:02}/2017') for i in range(1,11)])
        self.assertEqual(result['reports']['channels'][0]['p90_days'],8)

    def test_notes_survive_report_rerun(self):
        write_csv(self.notes,[{'complaint_id':'1','owner':'Reviewer','review_status':'In progress','notes':'Check date'}])
        original=self.notes.read_bytes()
        for _ in range(2):
            result=self.run_rows([self.row(sent='01/20/2017')])
            self.assertEqual(result['reports']['review_queue'][0]['notes'],'Check date')
        self.assertEqual(original,self.notes.read_bytes())

    def test_unmatched_notes_preserved(self):
        write_csv(self.notes,[{'complaint_id':'999','owner':'Reviewer','review_status':'In progress','notes':'Older case'}])
        result=self.run_rows([self.row()])
        self.assertEqual(result['metrics']['unmatched_notes'],1)
        self.assertIn('999',read_notes(self.notes))

    def test_excel_preface_and_untouched_rows(self):
        write_csv(self.notes,[{'complaint_id':'2','owner':'Old','review_status':'In progress','notes':'Keep'}])
        exported=self.root/'excel.csv'
        exported.write_text('Review queue\nDemo subset\nComplaint ID,Owner,Review status,Notes\n1,Sam,Resolved,Verified source\n2,,Not started,\n',encoding='utf-8')
        self.assertEqual(update(exported,self.notes),2)
        self.assertEqual(read_notes(self.notes)['2'][2],'Keep')

    def test_invalid_resolved_import_does_not_write(self):
        original=self.notes.read_bytes()
        exported=self.root/'excel.csv'
        exported.write_text('complaint_id,owner,review_status,notes\n1,,Resolved,\n',encoding='utf-8')
        with self.assertRaises(ValueError):
            update(exported,self.notes)
        self.assertEqual(original,self.notes.read_bytes())

    def test_duplicate_note_ids_rejected(self):
        self.notes.write_text('complaint_id,owner,review_status,notes\n1,Sam,In progress,A\n1,Sam,In progress,B\n',encoding='utf-8')
        with self.assertRaises(ValueError):
            read_notes(self.notes)


if __name__=='__main__':
    unittest.main()
