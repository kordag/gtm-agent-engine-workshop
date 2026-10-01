import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    def test_disqualified_prospect_is_blocked(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "email": "priya.nair@brightwaveapps.com",
            },
            "Demo invitation",
            "Please book a demo.",
            runtime=None,
            from_rep={},
        )

        self.assertEqual(result["status"], "blocked")
        self.assertIn("disqualified", result["error"])

    def test_qualified_prospect_is_sent(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-39002",
                "email": "chloe.rodriguez@westwindcloud.com",
            },
            "Demo invitation",
            "Please book a demo.",
            runtime=None,
            from_rep={},
        )

        self.assertEqual(result["status"], "sent")


if __name__ == "__main__":
    unittest.main()
