"""Counterexamples that otherwise pass downstream arithmetic checks."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pipeline import FIELDS, build, read_notes


class CsvContractTests(unittest.TestCase):
    def test_ambiguous_and_malformed_refresh_preserves_current_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / 'input.csv', root / 'output'
            row = ['123', '01/01/2017', '01/02/2017', 'Mortgage', 'Example', 'Web', 'Closed', 'No']
            def write(headers, cells):
                with source.open('w', encoding='utf-8', newline='') as stream:
                    writer = csv.writer(stream)
                    writer.writerow(headers)
                    writer.writerow(cells)
            write(FIELDS, row)
            result = build(source, output, root / 'absent.csv')
            self.assertEqual(result['metrics']['review_queue_cases'], 1)
            pointer = (output / 'latest.json').read_bytes()
            for headers, cells in [(FIELDS + ['Timely response?'], row + ['Yes']),
                                   (FIELDS, row + ['unlabelled']), (FIELDS, row[:-1])]:
                with self.subTest(headers=headers, width=len(cells)):
                    write(headers, cells)
                    with self.assertRaises(ValueError):
                        build(source, output, root / 'absent.csv')
                    self.assertEqual((output / 'latest.json').read_bytes(), pointer)
            # Named unused source columns are supported and do not redefine the selected grain.
            write(FIELDS + ['Unused source field'], row + ['permitted'])
            self.assertEqual(build(source, output, root / 'absent.csv')['metrics']['timely_no'], 1)

    def test_notes_reject_duplicate_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'notes.csv'
            path.write_text('complaint_id,owner,review_status,notes,review_status\n1,Sam,Resolved,Checked,Not started\n')
            with self.assertRaises(ValueError):
                read_notes(path)
