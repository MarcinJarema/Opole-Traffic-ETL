import unittest
from unittest.mock import patch, MagicMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Musimy załadować środowisko przed importem modułów korzystających z config
os.environ.setdefault("TOMTOM_API_KEY", "test-key")

from traffic_api import fetch_current_traffic


def _mock_flow(speed, free_flow_speed, confidence=1.0):
    """Buduje odpowiedź API TomTom z podanymi wartościami."""
    return {
        "flowSegmentData": {
            "currentSpeed": speed,
            "freeFlowSpeed": free_flow_speed,
            "confidence": confidence,
        }
    }


class TestJamFactor(unittest.TestCase):

    def _fetch(self, speed, ffs, confidence=1.0):
        mock_resp = MagicMock()
        mock_resp.json.return_value = _mock_flow(speed, ffs, confidence)
        mock_resp.raise_for_status = MagicMock()

        with patch("traffic_api.requests.get", return_value=mock_resp):
            records = fetch_current_traffic()

        self.assertEqual(len(records), 1)
        return records[0]["jam_factor"]

    def test_free_flow_zero_jam(self):
        """Prędkość równa free flow → jam_factor = 0."""
        jam = self._fetch(speed=50, ffs=50)
        self.assertAlmostEqual(jam, 0.0, places=5)

    def test_half_speed_five_jam(self):
        """Prędkość 50% free flow → jam_factor = 5.0."""
        jam = self._fetch(speed=25, ffs=50)
        self.assertAlmostEqual(jam, 5.0, places=5)

    def test_full_stop_ten_jam(self):
        """Stanie w miejscu → jam_factor bliski 10."""
        jam = self._fetch(speed=0, ffs=50)
        self.assertGreater(jam, 9.9)

    def test_jam_capped_at_ten(self):
        """jam_factor nie przekracza 10."""
        jam = self._fetch(speed=0, ffs=100)
        self.assertLessEqual(jam, 10.0)

    def test_no_free_flow_data(self):
        """Brak freeFlowSpeed → jam_factor = 0 (bezpieczne domyślne)."""
        jam = self._fetch(speed=30, ffs=0)
        self.assertEqual(jam, 0.0)

    def test_record_contains_lat_lon(self):
        """Rekord zawiera współrzędne przekazane do funkcji."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = _mock_flow(50, 50)
        mock_resp.raise_for_status = MagicMock()

        with patch("traffic_api.requests.get", return_value=mock_resp):
            records = fetch_current_traffic(lat=51.0, lon=18.0)

        self.assertEqual(records[0]["lat"], 51.0)
        self.assertEqual(records[0]["lon"], 18.0)

    def test_api_error_returns_empty(self):
        """Błąd sieci → pusta lista (nie wyjątek)."""
        import requests as req
        with patch("traffic_api.requests.get", side_effect=req.exceptions.ConnectionError):
            records = fetch_current_traffic()
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
