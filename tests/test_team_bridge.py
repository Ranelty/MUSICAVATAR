import unittest
from unittest.mock import patch
from musicavatar import team_bridge


class TestTeamBridge(unittest.TestCase):
    def test_missing_modules_are_optional(self):
        with patch.object(team_bridge, 'MODULES', ('musicavatar.contrib.not_installed',)):
            self.assertEqual(team_bridge.install_team_modules(object()), [])

    def test_module_names_are_independent(self):
        self.assertEqual(len(team_bridge.MODULES), 2)
        self.assertEqual(len(set(team_bridge.MODULES)), 2)
        self.assertIn('musicavatar.contrib.credits', team_bridge.MODULES)
        self.assertIn('musicavatar.contrib.avatar_backgrounds', team_bridge.MODULES)


if __name__ == '__main__':
    unittest.main()
