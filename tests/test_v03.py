"""Pruebas v0.3 de datos, géneros, edición real de MP3 y migración."""
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from musicavatar.database import MusicDatabase
from musicavatar.genres import normalize_genres, genre_suggestions, infer_genre_from_words
from musicavatar.metadata import read_track
from musicavatar.metadata_edit import write_file_tags, cover_mime
from musicavatar.moods import mood_from_genre

ROOT = Path(__file__).resolve().parents[1]


class V03GenreTests(unittest.TestCase):
    def test_case_normalization(self):
        self.assertEqual(normalize_genres('rock, Rock, POP, pop'), 'Rock, Pop')

    def test_typo_suggests_but_does_not_silently_overwrite(self):
        self.assertIn('Rock', genre_suggestions('roc'))
        self.assertEqual(normalize_genres('roc'), 'roc')

    def test_conservative_inference(self):
        self.assertEqual(infer_genre_from_words('Lo-Fi Sunset'), 'Lo-Fi')
        self.assertEqual(infer_genre_from_words('A random song'), '')

    def test_auto_rock_mood(self):
        self.assertEqual(mood_from_genre('Rock'), 'energy')
        self.assertEqual(mood_from_genre('OST'), 'neutral')


class V03DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = MusicDatabase(Path(self.tmp.name)/'musicavatar.db')
        self.song_id,_ = self.db.add_track(dict(path='/fake/song.mp3',title='Old',artist='X',album='Y',genre='',duration=120,cover=''))
        self.db.create_playlist('Mis canciones')
        self.pid = self.db.playlists()[0][0]

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_playlist_cover_and_count(self):
        self.db.add_to_playlist(self.pid,self.song_id)
        self.db.set_playlist_cover(self.pid,'C:/covers/one.png')
        self.assertEqual(self.db.get_playlist_cover(self.pid),'C:/covers/one.png')
        self.assertEqual(self.db.playlist_details()[0][-1],1)

    def test_metadata_changes_preserve_user_stats(self):
        self.db.set_mood(self.song_id,'sad')
        self.db.set_favorites([self.song_id],True)
        self.db.increment_track_play(self.song_id)
        self.db.update_track_metadata(self.song_id,dict(title='New',artist='A',album='B',genre='Rock',duration=130,cover='abc.jpg'))
        track=self.db.get_track(self.song_id)
        self.assertEqual(track.title,'New')
        self.assertTrue(track.favorite)
        self.assertEqual(track.mood_override,'sad')
        self.assertEqual(track.play_count,1)

    def test_mood_totals_accumulate(self):
        self.db.add_mood_seconds('happy',20)
        self.db.add_mood_seconds('happy',40)
        self.db.add_mood_seconds('sad',5)
        self.assertEqual(self.db.mood_totals(),{'happy':60,'sad':5})

    def test_v02_playlist_migration(self):
        location=Path(self.tmp.name)/'legacy.db'
        cn=sqlite3.connect(location)
        cn.executescript('''CREATE TABLE playlists (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, play_count INTEGER NOT NULL DEFAULT 0);
         INSERT INTO playlists VALUES (1,'Anterior',4);''')
        cn.close()
        # MusicDatabase crea tablas faltantes y agrega playlists.cover sin borrar datos.
        legacy=MusicDatabase(location)
        self.assertEqual(legacy.playlist_details()[0][1:4],('Anterior','',4))
        legacy.close()


class V03MetadataTests(unittest.TestCase):
    def test_bad_cover(self):
        with self.assertRaises(ValueError):
            cover_mime(b'not an image')

    def test_real_mp3_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'test.mp3'
            shutil.copy2(ROOT/'demo'/'Amanecer en píxeles.mp3',target)
            write_file_tags(target,'Nuevo título','Artista nuevo','Un álbum','Rock, OST')
            values=read_track(target,Path(tmp)/'covers')
            self.assertEqual(values['title'],'Nuevo título')
            self.assertEqual(values['artist'],'Artista nuevo')
            self.assertEqual(values['genre'],'Rock, OST')

    def test_real_mp3_cover(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'test.mp3'
            shutil.copy2(ROOT/'demo'/'Amanecer en píxeles.mp3',target)
            # Pixel PNG mínimo válido, usado solo como carga APIC de etiquetas.
            png=bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000b49444154789c636000020000050001a5f645400000000049454e44ae426082')
            write_file_tags(target,'Portada','Autor','Disco','Pop',png)
            values=read_track(target,Path(tmp)/'covers')
            self.assertTrue(values['cover'])
            self.assertTrue(Path(values['cover']).is_file())


if __name__=='__main__':
    unittest.main()
