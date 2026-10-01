import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service, gtm_agent


class ProspectUpdateTest(unittest.TestCase):
    def setUp(self):
        self.prospect_id = "LEAD-39002"
        self.original_stack = list(data_service.PROSPECTS[self.prospect_id]["tech_stack"])
        self.original_profile = data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        data_service.PROSPECTS[self.prospect_id]["tech_stack"] = self.original_stack
        if self.original_profile is None:
            data_service._PROFILES.pop(self.prospect_id, None)
        else:
            data_service._PROFILES[self.prospect_id] = self.original_profile

    def test_update_then_score_uses_persisted_tech_stack(self):
        profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": self.prospect_id})["prospect_profile"]

        result = data_service.update_prospect_info(self.prospect_id, "Terraform")

        self.assertIn("Terraform", result["tech_stack"])
        self.assertIn("Terraform", data_service.fetch_tech_stack(self.prospect_id))
        self.assertIn("Terraform", data_service._PROFILES[self.prospect_id]["tech_stack"])

        scoring_llm = Mock()
        scoring_llm.invoke.return_value = gtm_agent.ProspectScore(
            score=80,
            justification="Terraform is present.",
            rubric_breakdown={
                "revenue_fit": 25,
                "tech_stack_match": 25,
                "segment_fit": 30,
            },
        )
        with patch.object(gtm_agent, "_scoring_llm", scoring_llm):
            gtm_agent.score_prospect.invoke({
                "prospect_profile": profile,
                "offering": data_service.get_offering("OFFER-10004"),
            })

        scoring_input = scoring_llm.invoke.call_args.args[0][1]["content"]
        self.assertIn("Terraform", scoring_input)


if __name__ == "__main__":
    unittest.main()
