import unittest
from musicavatar.contrib.credits_info import (
    PROJECT_NAME, PROJECT_DESCRIPTION, TEAM_MEMBERS,
    TECHNOLOGIES, members_text,
)


class TestCredits(unittest.TestCase):
    def test_three_exact_members(self):
        self.assertEqual(TEAM_MEMBERS, (
            'Christofer Alberto Rodríguez Ocaña',
            'Ángel Mario Presenda Alpuche',
            'Rafael Gabriel Jiménez Espinosa',
        ))

    def test_members_not_repeated(self):
        self.assertEqual(len(TEAM_MEMBERS), len(set(TEAM_MEMBERS)))
        self.assertEqual(len(members_text().splitlines()), 3)

    def test_about_content(self):
        self.assertEqual(PROJECT_NAME, 'Musicavatar')
        self.assertIn('avatar pixel art', PROJECT_DESCRIPTION)
        self.assertIn('PySide6', TECHNOLOGIES)


if __name__ == '__main__':
    unittest.main()
