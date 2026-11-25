import tempfile
import unittest
from pathlib import Path
from musicavatar.contrib.background_rules import (
    validate_image_path, normalize_fit, clamp_dim, stored_background_path,
)


class TestBackgroundRules(unittest.TestCase):
    def test_file_extensions_accept_uppercase(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'MI_FONDO.PNG'
            p.write_bytes(b'not_an_image_yet')
            self.assertEqual(validate_image_path(p), p)

    def test_reject_invalid_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'virus.exe'
            p.write_bytes(b'x')
            with self.assertRaises(ValueError):
                validate_image_path(p)

    def test_reject_missing_file(self):
        with self.assertRaises(ValueError):
            validate_image_path('/archivo_que_no_existe.jpg')

    def test_adjustments(self):
        self.assertEqual(normalize_fit('contain'), 'contain')
        self.assertEqual(normalize_fit('desconocido'), 'cover')
        self.assertEqual(clamp_dim(150), 80)
        self.assertEqual(clamp_dim(-4), 0)
        self.assertEqual(clamp_dim('xyz'), 0)

    def test_local_storage_location(self):
        p = stored_background_path(Path('/proyecto'))
        self.assertEqual(p, Path('/proyecto/data/avatar_backgrounds/scene.png'))


if __name__ == '__main__':
    unittest.main()
