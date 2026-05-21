import json
import unittest
from datetime import datetime, timezone

from dcim_ai.llm.rca_prompt_contract import (
    MAX_ACTIONS,
    SYSTEM_PROMPT,
    build_ollama_options,
    build_rca_chat_messages,
    build_rca_user_prompt,
    validate_rca_llm_response,
)
from dcim_ai.root_cause.rca_models import RootCauseResult, RCA_MODE_HYBRID


class TestRCAPromptContract(unittest.TestCase):
    def _sample_result(self):
        return RootCauseResult(
            incident_id="inc-001",
            timestamp=datetime(2026, 5, 20, 10, 30, tzinfo=timezone.utc),
            domain_probabilities={"power": 0.72, "cooling": 0.21, "compute": 0.07},
            root_domain="power",
            ranked_domains=[("power", 0.72), ("cooling", 0.21), ("compute", 0.07)],
            causal_chain=["power", "cooling", "compute"],
            impact_domains=["cooling", "compute"],
            confidence=0.72,
            explanation="PDU load spike followed by cooling temperature rise.",
            metadata={"source": "unit-test"},
            mode=RCA_MODE_HYBRID,
            forecast_horizon_h=24,
            forecast_confidence=0.66,
            asset_context={
                "asset_id": "srv-001",
                "role": "compute-node",
                "rack": "R1",
                "site": "DC-A",
                "criticality": "high",
            },
        )

    def test_build_prompt_contains_required_context(self):
        prompt = build_rca_user_prompt(self._sample_result())

        self.assertIn("Incident: inc-001", prompt)
        self.assertIn("Asset: compute-node di R1 (DC-A), criticality high", prompt)
        self.assertIn("Mode: hybrid", prompt)
        self.assertIn("Root domain: power (confidence=0.72", prompt)
        self.assertIn("Causal chain: power → cooling → compute", prompt)
        self.assertIn('"summary"', prompt)
        self.assertIn('"impact"', prompt)
        self.assertIn('"actions"', prompt)
        self.assertNotIn('"limitations"', prompt)

    def test_build_prompt_fallback_for_missing_asset(self):
        result = self._sample_result()
        result.asset_context = None

        prompt = build_rca_user_prompt(result)

        self.assertIn("Asset: unknown di unknown (unknown), criticality unknown", prompt)

    def test_build_chat_messages_and_options(self):
        messages = build_rca_chat_messages(self._sample_result())
        options = build_ollama_options()

        self.assertEqual(messages[0], {"role": "system", "content": SYSTEM_PROMPT})
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(options["temperature"], 0)
        self.assertIn("num_predict", options)

    def test_validate_mapping_response(self):
        response = {
            "summary": "Root cause berasal dari domain power dan berdampak ke cooling.",
            "impact": "Risiko thermal throttling pada node kritikal meningkat.",
            "actions": ["Cek PDU", "Validasi cooling", "Eskalasi ke NOC"],
        }

        result = validate_rca_llm_response(response)

        self.assertTrue(result.valid)
        self.assertEqual(result.narrative.to_dict(), response)

    def test_validate_json_string_response(self):
        payload = json.dumps(
            {
                "summary": "Power anomaly memicu RCA lintas domain.",
                "impact": "Layanan compute dapat turun performa.",
                "actions": ["Audit power feed"],
            }
        )

        result = validate_rca_llm_response(payload)

        self.assertTrue(result.valid)
        self.assertEqual(result.narrative.actions, ["Audit power feed"])

    def test_reject_missing_keys(self):
        result = validate_rca_llm_response({"summary": "ada"})

        self.assertFalse(result.valid)
        self.assertTrue(any("Missing required keys" in error for error in result.errors))

    def test_reject_extra_keys(self):
        result = validate_rca_llm_response(
            {
                "summary": "Root cause valid.",
                "impact": "Impact valid.",
                "actions": ["Action valid"],
                "limitations": [],
            }
        )

        self.assertFalse(result.valid)
        self.assertTrue(any("Unexpected keys" in error for error in result.errors))

    def test_reject_too_many_actions(self):
        result = validate_rca_llm_response(
            {
                "summary": "Root cause valid.",
                "impact": "Impact valid.",
                "actions": ["a", "b", "c", "d"],
            }
        )

        self.assertFalse(result.valid)
        self.assertTrue(any(f"1..{MAX_ACTIONS}" in error for error in result.errors))

    def test_reject_invalid_json(self):
        result = validate_rca_llm_response("not-json")

        self.assertFalse(result.valid)
        self.assertTrue(any("Invalid JSON" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
