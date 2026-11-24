import unittest
from musicavatar.utils import format_time, safe_filename

class UtilTests(unittest.TestCase):
    def test_zero(self): self.assertEqual(format_time(0),'0:00')
    def test_seconds(self): self.assertEqual(format_time(59),'0:59')
    def test_minutes(self): self.assertEqual(format_time(125),'2:05')
    def test_hours(self): self.assertEqual(format_time(3603),'1:00:03')
    def test_negative(self): self.assertEqual(format_time(-8),'0:00')
    def test_file(self): self.assertEqual(safe_filename('prueba_alegre.mp3'),'prueba alegre')

if __name__=='__main__': unittest.main()
