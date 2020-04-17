import unittest

from utils.stops import get_stop_name


class TestStops(unittest.TestCase):
    def test_get_stops(self):
        wonderland = get_stop_name("70059")
        arlington = get_stop_name("70157")
        self.assertEqual("Wonderland", wonderland)
        self.assertEqual("Arlington", arlington)


if __name__ == '__main__':
    unittest.main()
