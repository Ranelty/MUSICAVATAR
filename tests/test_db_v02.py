import tempfile
import sqlite3
import unittest
from pathlib import Path
from musicavatar.database import MusicDatabase


class DatabaseV02Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'musicavatar.db'
        self.db = MusicDatabase(self.path)
        self.tids=[]
        for i in range(3):
            tid,_=self.db.add_track(dict(path=f'C:/Canciones/{i}.mp3',title=f'Pista {i}',artist='Prueba',album='Mi álbum',genre='Rock, Pop',duration=30,cover=''))
            self.tids.append(tid)
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()
    def test_bulk_genres_and_mood(self):
        self.db.set_genres(self.tids,'Lo-Fi, Chill')
        self.db.set_moods(self.tids,'calm')
        self.assertTrue(all(t.genre == 'Lo-Fi, Chill' and t.mood_override == 'calm' for t in self.db.all_tracks()))
    def test_bulk_favorites(self):
        self.db.set_favorites(self.tids,True)
        self.assertTrue(all(t.favorite for t in self.db.all_tracks()))
    def test_bulk_playlist_preserves_order_no_duplicates(self):
        self.db.create_playlist('Trabajo')
        pid=self.db.playlists()[0][0]
        self.assertEqual(self.db.add_many_to_playlist(pid,[self.tids[2],self.tids[0],self.tids[2],self.tids[1]]),3)
        self.assertEqual(self.db.playlist_track_ids(pid),[self.tids[2],self.tids[0],self.tids[1]])
        self.assertEqual(self.db.add_many_to_playlist(pid,[self.tids[0]]),0)
    def test_top_stats(self):
        self.db.increment_track_play(self.tids[1])
        self.db.increment_track_play(self.tids[1])
        self.db.increment_track_play(self.tids[0])
        self.assertEqual([t.id for t in self.db.top_tracks()],[self.tids[1],self.tids[0]])
        self.db.create_playlist('Uno')
        self.db.create_playlist('Dos')
        ids=[pid for pid,_ in self.db.playlists()]
        self.db.increment_playlist_play(ids[0])
        self.assertEqual(self.db.top_playlists()[0][0],ids[0])
    def test_v01_schema_migrates_existing_content(self):
        self.db.close()
        with sqlite3.connect(self.path) as conn:
            conn.execute('CREATE TABLE oldplay AS SELECT id,name FROM playlists')
            conn.execute('DROP TABLE oldplay')
            # Simula una base antigua sin columnas v0.2, conservando las canciones.
            conn.execute('ALTER TABLE tracks DROP COLUMN play_count')
            conn.execute('ALTER TABLE playlists DROP COLUMN play_count')
        self.db=MusicDatabase(self.path)
        self.assertEqual(len(self.db.all_tracks()),3)
        self.assertEqual(self.db.get_track(self.tids[0]).play_count,0)
        self.db.increment_track_play(self.tids[0])
        self.assertEqual(self.db.get_track(self.tids[0]).play_count,1)

if __name__ == '__main__': unittest.main()
