"""Pruebas opcionales del modelo Qt; no se ejecutan si PySide6 no está instalado."""
import importlib.util
import os
import unittest
from types import SimpleNamespace

HAS_QT = importlib.util.find_spec('PySide6') is not None
if HAS_QT:
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from musicavatar.track_table import TrackModel, TrackFilter


@unittest.skipUnless(HAS_QT, 'Requiere PySide6 instalado')
class QtFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.model = TrackModel()
        self.model.set_tracks([
            SimpleNamespace(id=1,title='Alba',artist='Ana',album='Uno',genre='Pop, Synthwave',duration=50,favorite=False,mood_override='',path='a',cover=''),
            SimpleNamespace(id=2,title='Noche',artist='Luis',album='Dos',genre='Lo-Fi, Jazz',duration=75,favorite=True,mood_override='',path='b',cover=''),
            SimpleNamespace(id=3,title='Lluvia',artist='Ana',album='Uno',genre='Sadcore',duration=90,favorite=False,mood_override='',path='c',cover=''),
        ])
        self.proxy = TrackFilter()
        self.proxy.setSourceModel(self.model)

    def visible(self):
        return {self.proxy.index(i,0).data(Qt.ItemDataRole.UserRole) for i in range(self.proxy.rowCount())}

    def test_multi_genre_filter(self):
        self.proxy.set_filters(genre='Synthwave')
        self.assertEqual(self.visible(),{1})

    def test_artist_and_album_filters(self):
        self.proxy.set_filters(artist='Ana',album='Uno')
        self.assertEqual(self.visible(),{1,3})

    def test_playlist_and_mood_filters(self):
        self.proxy.set_context('Listas',[3,2])
        self.proxy.set_filters(mood='sad')
        self.assertEqual(self.visible(),{3})

    def test_favorites(self):
        self.proxy.set_context('Favoritos')
        self.assertEqual(self.visible(),{2})

if __name__ == '__main__':
    unittest.main()
