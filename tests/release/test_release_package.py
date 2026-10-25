import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('release_builder',ROOT/'tools/release/build_release.py')
BUILDER=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BUILDER)


class ReleasePackage(unittest.TestCase):
    def test_reproducible_runtime_allowlist(self):
        with tempfile.TemporaryDirectory() as td:
            first=BUILDER.build(Path(td)/'one');second=BUILDER.build(Path(td)/'two')
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with zipfile.ZipFile(first) as z:
                members=z.namelist()
                self.assertTrue(all(n.startswith('rca-scoring/') for n in members))
                self.assertFalse(any(set(Path(n).parts)&{'tests','tools','docs','data','legacy','__pycache__'} for n in members))
                manifest=json.loads(z.read('rca-scoring/PACKAGE_MANIFEST.json'))
                self.assertEqual(manifest['channel'],'prerelease')
                self.assertEqual(len(members),len(manifest['files'])+2)

    def test_unpacked_package_runs_without_repository(self):
        with tempfile.TemporaryDirectory() as td:
            archive=BUILDER.build(Path(td)/'assets')
            with zipfile.ZipFile(archive) as z:z.extractall(Path(td)/'installation')
            installed=Path(td)/'installation/rca-scoring'
            output=Path(td)/'review.json'
            result=subprocess.run([sys.executable,str(installed/'scripts/assess_v2.py'),
                str(installed/'examples/result.example.json'),'--output',str(output)],
                cwd=Path(td),capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            review=json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(review['decision'],'needs_evidence')
            self.assertIsNone(review['overall'])


if __name__=='__main__':unittest.main()
