import json
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service, gtm_agent
from gtm_agent.gtm_records import OFFERINGS, PROSPECTS


SENSITIVE_KEYS = {
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
}


def assert_no_sensitive_keys(value):
    if isinstance(value, dict):
        assert SENSITIVE_KEYS.isdisjoint(value)
        for nested in value.values():
            assert_no_sensitive_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_sensitive_keys(nested)


def test_prospect_tools_filter_sensitive_fields(monkeypatch):
    data_service._PROFILES.clear()
    captured_users = []

    class FakeScoringLLM:
        def invoke(self, messages):
            captured_users.append(messages[1]["content"])
            return gtm_agent.ProspectScore(
                score=50,
                justification="test",
                rubric_breakdown={
                    "revenue_fit": 10,
                    "tech_stack_match": 20,
                    "segment_fit": 20,
                },
            )

    monkeypatch.setattr(gtm_agent, "_scoring_llm", FakeScoringLLM())
    offering = next(iter(OFFERINGS.values()))

    for prospect_id in PROSPECTS:
        contact = gtm_agent.get_prospect.invoke({"prospect_id": prospect_id})
        profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})
        gtm_agent.score_prospect.invoke({
            "prospect_profile": {
                **profile["prospect_profile"],
                "billing_qualification": PROSPECTS[prospect_id]["billing_qualification"],
                "extra": "should be dropped",
            },
            "offering": offering,
        })

        assert_no_sensitive_keys(contact)
        assert_no_sensitive_keys(profile)

    for user in captured_users:
        assert_no_sensitive_keys(json.loads(user.split("\n\nProspect profile:\n", 1)[1]))


def test_build_profile_sanitizes_legacy_cached_profile():
    data_service._PROFILES.clear()
    prospect_id = next(iter(PROSPECTS))
    legacy_profile = {
        **PROSPECTS[prospect_id],
        "prospect_id": prospect_id,
        "billing_qualification": PROSPECTS[prospect_id]["billing_qualification"],
    }
    data_service._PROFILES[prospect_id] = legacy_profile

    result = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})

    assert_no_sensitive_keys(result)
    assert_no_sensitive_keys(data_service._PROFILES[prospect_id])
