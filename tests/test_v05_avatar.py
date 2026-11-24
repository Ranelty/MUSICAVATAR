"""Pruebas de la nueva personalización sin instalar PySide6."""
import tempfile
import unittest
from pathlib import Path
from musicavatar.avatar_parts import (
    AvatarLook, HAIR_STYLES, TOP_STYLES, SKIN_TONES,
    PANTS, SHOES, PRESENTATIONS, HAIR_COLORS, OUTFIT_COLORS,
)
from musicavatar.database import MusicDatabase


class AvatarPartsTests(unittest.TestCase):
    def test_three_hair_shapes(self):
        self.assertEqual(len(HAIR_STYLES),3)
        self.assertEqual(len({v for _,v in HAIR_STYLES}),3)

    def test_three_top_styles_and_pants_and_shoes(self):
        self.assertEqual(len(TOP_STYLES),3)
        self.assertEqual(len(PANTS),3)
        self.assertEqual(len(SHOES),3)

    def test_three_skin_tones(self):
        self.assertEqual(len(SKIN_TONES),3)

    def test_three_presentations(self):
        self.assertEqual(len(PRESENTATIONS),3)

    def test_color_options_are_unique(self):
        self.assertEqual(len({v for _,v in HAIR_COLORS}),len(HAIR_COLORS))
        self.assertEqual(len({v for _,v in OUTFIT_COLORS}),len(OUTFIT_COLORS))

    def test_valid_values_are_preserved(self):
        look = AvatarLook(hair='#a65d3b',outfit='#4b6998',accessory='Gorra',
                          hair_style='messy',top_style='shirt',pants='#395c85',
                          shoes='red',skin='#845846',presentation='feminine')
        self.assertEqual(look.validated(),look)

    def test_bad_options_fallback_without_crashing(self):
        look = AvatarLook(hair_style='?', top_style='?', pants='?', shoes='?',
                          skin='?', presentation='?', accessory='???')
        self.assertEqual(look.validated(), AvatarLook())

    def test_old_hair_color_from_v04_kept(self):
        self.assertEqual(AvatarLook(hair='#608dbb').validated().hair,'#608dbb')

    def test_new_preferences_persist_and_preserve_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'musicavatar.db'
            db = MusicDatabase(path)
            db.set_setting('hair','#8d72bf')
            for k,v in {'skin_tone':'#845846','hair_style':'long','top_style':'shirt',
                        'pants_style':'#395c85','shoes_style':'boots',
                        'presentation':'feminine'}.items():
                db.set_setting(k,v)
            db.close()
            reopened = MusicDatabase(path)
            self.assertEqual(reopened.get_setting('hair'),'#8d72bf')
            self.assertEqual(reopened.get_setting('skin_tone'),'#845846')
            self.assertEqual(reopened.get_setting('hair_style'),'long')
            self.assertEqual(reopened.get_setting('presentation'),'feminine')
            reopened.close()


if __name__=='__main__':
    unittest.main()
