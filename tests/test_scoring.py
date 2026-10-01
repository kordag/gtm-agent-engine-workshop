import unittest
import os
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import SegmentScore, score_prospect


class ScoreProspectTests(unittest.TestCase):
    def setUp(self):
        self.prospect = {
            "annual_revenue": 50_000_000,
            "tech_stack": ["Snowflake", "Databricks", "Kubernetes"],
        }
        self.offering = {
            "required_tech_stack": ["Snowflake", "Databricks", "Kubernetes", "AWS"],
            "min_annual_revenue": 50_000_000,
            "description": "Test offering",
        }

    @patch("gtm_agent.gtm_agent._scoring_llm")
    def test_identical_inputs_return_identical_scores(self, scoring_llm):
        scoring_llm.invoke.return_value = SegmentScore(
            segment_fit=75,
            justification="Computed fit values are consistent.",
        )

        first = score_prospect.func(self.prospect, self.offering)
        second = score_prospect.func(self.prospect, self.offering)

        self.assertEqual(first, second)

    @patch("gtm_agent.gtm_agent._scoring_llm")
    def test_tech_stack_match_is_based_on_present_required_technologies(self, scoring_llm):
        scoring_llm.invoke.return_value = SegmentScore(
            segment_fit=75,
            justification="Three of four required technologies are present.",
        )

        result = score_prospect.func(self.prospect, self.offering)

        self.assertEqual(result["rubric_breakdown"]["tech_stack_match"], 75)


if __name__ == "__main__":
    unittest.main()
