import unittest
from types import SimpleNamespace
from musicavatar.moods import mood_from_genre, get_track_mood, MoodSession

class MoodTests(unittest.TestCase):
    def test_happy_pop(self):
        self.assertEqual(mood_from_genre('Dance Pop'), 'happy')
    def test_melancholic(self):
        self.assertEqual(mood_from_genre('Sadcore'), 'sad')
    def test_unknown(self):
        self.assertEqual(mood_from_genre(''), 'neutral')
    def test_manual_override(self):
        t = SimpleNamespace(genre='Metal', mood_override='calm')
        self.assertEqual(get_track_mood(t), 'calm')
    def test_session_paused_does_not_count(self):
        s=MoodSession()
        s.update('sad',5,False)
        self.assertEqual(s.seconds,0)
    def test_stage_thresholds(self):
        s=MoodSession(mood='sad',seconds=899)
        self.assertEqual(s.stage,0)
        s.update('sad',1,True)
        self.assertEqual(s.stage,1)
        s.seconds=1799
        s.update('sad',1,True)
        self.assertEqual(s.stage,2)
    def test_switch_mood_resets_time(self):
        s=MoodSession('sad',1600)
        s.update('happy',1,True)
        self.assertEqual(s.seconds,1)
        self.assertEqual(s.stage,0)

if __name__=='__main__': unittest.main()
