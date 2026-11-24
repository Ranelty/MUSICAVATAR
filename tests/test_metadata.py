import unittest
import tempfile
from pathlib import Path
from musicavatar.metadata import read_track, scan_paths

ROOT = Path(__file__).resolve().parents[1]

class MetadataTests(unittest.TestCase):
    def test_sample_metadata_and_art(self):
        path = ROOT/'demo'/'Amanecer en píxeles.mp3'
        with tempfile.TemporaryDirectory() as folder:
            data = read_track(path,Path(folder))
            self.assertEqual(data['title'],'Amanecer en píxeles')
            self.assertEqual(data['artist'],'Musicavatar Demo')
            self.assertEqual(data['genre'],'Happy Pop')
            self.assertGreater(data['duration'],1)
            self.assertTrue(Path(data['cover']).is_file())
    def test_melancholic_sample(self):
        path=ROOT/'demo'/'Lluvia en la ventana.mp3'
        with tempfile.TemporaryDirectory() as folder:
            data=read_track(path,Path(folder))
            self.assertEqual(data['genre'],'Sadcore')
    def test_scan_paths(self):
        files = scan_paths([ROOT/'demo',ROOT/'demo'/'Amanecer en píxeles.mp3'])
        self.assertEqual(len(files),2)
    def test_reject_unsupported(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'nota.txt';p.write_text('hola')
            with self.assertRaises(ValueError):
                read_track(p,Path(folder)/'covers')

if __name__ == '__main__': unittest.main()
