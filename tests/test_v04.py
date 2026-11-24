"""Pruebas del editor v0.4; no requieren ejecutar ventanas de Qt."""
import shutil
import tempfile
import unittest
from pathlib import Path
from musicavatar.metadata import read_track
from musicavatar.metadata_edit import write_file_tags, safe_rename_audio
from musicavatar.database import MusicDatabase

DEMO = Path(__file__).resolve().parents[1] / 'demo' / 'Amanecer en píxeles.mp3'


class V04EditorTests(unittest.TestCase):
    def test_title_changed_in_original_without_renaming(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'nombre-original.mp3'
            shutil.copy2(DEMO, source)
            write_file_tags(source, 'Mi nuevo título', 'Autor', 'Álbum', 'Rock')
            result = read_track(source, Path(folder)/'covers')
            self.assertEqual(result['title'], 'Mi nuevo título')
            self.assertTrue(source.exists())

    def test_optional_rename_preserves_database_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'antes.mp3'
            shutil.copy2(DEMO, source)
            db = MusicDatabase(Path(folder)/'library.db')
            data = read_track(source, Path(folder)/'covers')
            sid, _ = db.add_track(data)
            db.create_playlist('Favorites')
            pid = db.playlists()[0][0]
            db.add_to_playlist(pid, sid)
            db.set_favorites([sid], True)
            write_file_tags(source, 'Nuevo nombre', 'Autor', 'Álbum', 'Rock')
            dest = safe_rename_audio(source, 'Nuevo nombre')
            db.update_track_path(sid, str(dest))
            db.update_track_metadata(sid, read_track(dest,Path(folder)/'covers'))
            track = db.get_track(sid)
            self.assertEqual(track.title, 'Nuevo nombre')
            self.assertTrue(track.favorite)
            self.assertEqual(track.path, str(dest))
            self.assertEqual(db.playlist_track_ids(pid)[0], sid)
            db.close()

    def test_rename_rejects_collision(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder)/'old.mp3'
            other = Path(folder)/'new.mp3'
            old.touch();other.touch()
            with self.assertRaises(FileExistsError):
                safe_rename_audio(old,'new')

    def test_rename_windows_invalid_chars(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder)/'original.mp3'
            old.touch()
            new = safe_rename_audio(old,'a:b?c')
            self.assertEqual(new.name, 'a_b_c.mp3')

    def test_persisted_settings_survive_reopen(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db.sqlite'
            db=MusicDatabase(path)
            for k,v in {'theme_color':'#395580','spectrum_enabled':'0','spectrum_count':'64','spectrum_color':'#fab455'}.items():
                db.set_setting(k,v)
            db.close()
            db=MusicDatabase(path)
            self.assertEqual(db.get_setting('spectrum_count'),'64')
            self.assertEqual(db.get_setting('theme_color'),'#395580')
            db.close()

if __name__=='__main__':
    unittest.main()
