import unittest
from musicavatar.genres import split_genres,normalize_genres
from musicavatar.moods import mood_from_genre


class GenreTests(unittest.TestCase):
    def test_multiple_genres(self):
        self.assertEqual(split_genres('Lo-Fi; Jazz | Jazz, Ambient'),['Lo-Fi','Jazz','Ambient'])
    def test_normalization(self):
        self.assertEqual(normalize_genres(['Rock','Pop','Rock']), 'Rock, Pop')
    def test_secondary_genre_can_define_mood(self):
        self.assertEqual(mood_from_genre('Indie, Sadcore'), 'sad')
    def test_empty(self):
        self.assertEqual(normalize_genres(''), '')

if __name__ == '__main__': unittest.main()
