"""Pruebas de integración Qt (necesitan PySide6 y modo offscreen)."""
import importlib.util
import os
import unittest

HAS_QT = importlib.util.find_spec('PySide6') is not None
if HAS_QT:
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from musicavatar.avatar import AvatarCanvas


@unittest.skipUnless(HAS_QT,'Requiere PySide6 instalado')
class AvatarQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_modular_avatar_renders(self):
        av = AvatarCanvas()
        av.timer.stop()
        av.set_customization('#a65d3b','#4b6998','Moño',
                            hair_style='long',top_style='shirt',
                            pants='#395c85',shoes='red',
                            skin='#845846',presentation='feminine')
        av.resize(220,220)
        picture = av.grab()
        self.assertFalse(picture.isNull())
        self.assertEqual(av.look.hair_style,'long')
        av.close()

    def test_preview_renders_with_character_crop(self):
        av = AvatarCanvas(preview=True)
        av.resize(160,180)
        av.set_customization('#a65d3b','#4b6998','Auriculares')
        self.assertFalse(av.grab().isNull())
        av.close()

    def test_legacy_three_argument_api(self):
        av = AvatarCanvas()
        av.timer.stop()
        av.set_customization('#608dbb','#71549d','Gorra')
        self.assertEqual(av.look.hair,'#608dbb')
        av.close()


if __name__=='__main__':
    unittest.main()
