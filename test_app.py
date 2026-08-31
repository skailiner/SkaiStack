import unittest

from app import build_rate_card, price_campaign


class SponsorStackTests(unittest.TestCase):
    def test_rights_increase_price(self):
        base = price_campaign(50000, 20000, 5, "Technology", "YouTube", ["Short-form video"], "Organic repost only", "None", "Standard", 5, 50, 0)
        licensed = price_campaign(50000, 20000, 5, "Technology", "YouTube", ["Short-form video"], "12-month paid usage", "None", "Standard", 5, 50, 0)
        self.assertGreater(licensed["suggested"], base["suggested"])

    def test_outputs(self):
        metrics, packages, pitch, rationale, path = build_rate_card("Alex", "Technology", "YouTube", 50000, 20000, 5, ["Short-form video"], "30-day paid usage", "30 days", "Standard", 10, 75, 100, "USD ($)", "Acme", "launch a useful product")
        self.assertIn("Quote to send", metrics)
        self.assertEqual(len(packages), 3)
        self.assertIn("Acme", pitch)
        self.assertIn("Why this rate", rationale)
        self.assertTrue(path.endswith(".md"))


if __name__ == "__main__":
    unittest.main()
