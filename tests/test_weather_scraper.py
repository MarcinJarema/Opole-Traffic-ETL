import unittest
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("TOMTOM_API_KEY", "test-key")

from weather_scraper import parse_float


class TestParseFloat(unittest.TestCase):

    def test_plain_number(self):
        self.assertEqual(parse_float("14.5"), 14.5)

    def test_comma_decimal(self):
        """Europejski format przecinkowy."""
        self.assertEqual(parse_float("14,5"), 14.5)

    def test_value_with_unit(self):
        """Jednostka po spacji powinna być obcięta."""
        self.assertEqual(parse_float("14,5 °C"), 14.5)

    def test_negative_value(self):
        self.assertEqual(parse_float("-3,2 °C"), -3.2)

    def test_integer_string(self):
        self.assertEqual(parse_float("20"), 20.0)

    def test_empty_string(self):
        self.assertIsNone(parse_float(""))

    def test_whitespace_only(self):
        self.assertIsNone(parse_float("   "))

    def test_non_numeric(self):
        self.assertIsNone(parse_float("brak danych"))

    def test_wind_format(self):
        """Format prędkości wiatru: '12 km/h'."""
        self.assertEqual(parse_float("12 km/h"), 12.0)

    def test_humidity_percent(self):
        """Format wilgotności: '75 %'."""
        self.assertEqual(parse_float("75 %"), 75.0)


if __name__ == "__main__":
    unittest.main()
