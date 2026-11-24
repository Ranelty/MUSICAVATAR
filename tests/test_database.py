import unittest
import tempfile
from pathlib import Path
from musicavatar.database import MusicDatabase

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=MusicDatabase(Path(self.temp.name)/'musicavatar.db')
        self.data=dict(path=str(Path(self.temp.name)/'a.mp3'),title='Hola',artist='Prueba',album='Ejemplo',genre='Pop',duration=32,cover='')
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()
    def test_add_and_no_duplicates(self):
        tid,created=self.db.add_track(self.data)
        self.assertTrue(created)
        again,created=self.db.add_track(self.data)
        self.assertFalse(created)
        self.assertEqual(tid,again)
        self.assertEqual(len(self.db.all_tracks()),1)
    def test_custom_mood_and_favorite(self):
        tid,_=self.db.add_track(self.data)
        self.db.set_mood(tid,'sad')
        self.assertEqual(self.db.get_track(tid).mood_override,'sad')
        self.assertTrue(self.db.toggle_favorite(tid))
        self.assertFalse(self.db.toggle_favorite(tid))
    def test_playlist_without_duplicate(self):
        tid,_=self.db.add_track(self.data)
        self.assertTrue(self.db.create_playlist('Viaje'))
        self.assertFalse(self.db.create_playlist('Viaje'))
        pid=self.db.playlists()[0][0]
        self.db.add_to_playlist(pid,tid)
        self.db.add_to_playlist(pid,tid)
        self.assertEqual(self.db.playlist_track_ids(pid),[tid])
    def test_settings(self):
        self.db.set_setting('outfit','purple')
        self.assertEqual(self.db.get_setting('outfit'),'purple')

if __name__=='__main__': unittest.main()
