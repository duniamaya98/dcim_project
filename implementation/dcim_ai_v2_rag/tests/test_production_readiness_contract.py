import json
import unittest

try:
    from dcim_ai.llm.production_readiness_contract import (
        SCHEMA_VERSION,
        action_requires_approval,
        build_dcim_operations_messages,
        validate_dcim_agent_response,
    )
except ModuleNotFoundError:
    from implementation.dcim_ai_v2_rag.llm.production_readiness_contract import (
        SCHEMA_VERSION,
        action_requires_approval,
        build_dcim_operations_messages,
        validate_dcim_agent_response,
    )


class TestProductionReadinessContract(unittest.TestCase):
    def _valid_response(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "incident_id": "inc-thermal-001",
            "status": "needs_more_data",
            "summary": "Thermal alert exists, but fresh metrics are missing.",
            "evidence": [
                {
                    "id": "ev-001",
                    "source": "incident_state",
                    "timestamp": "2026-06-11T09:12:00Z",
                    "asset_id": "srv-app-05",
                    "kind": "fact",
                    "summary": "Critical thermal alarm for srv-app-05.",
                    "confidence": 1.0,
                    "value": {"severity": "critical"},
                    "metadata": {},
                }
            ],
            "risk": "high",
            "recommended_action": "Query fresh temperature and cooling logs before remediation.",
            "tool_calls": [
                {
                    "id": "tc-001",
                    "action_type": "read_metrics",
                    "tool_name": "prometheus_query",
                    "arguments": {
                        "query": 'dcim_temperature_celsius{asset_id="srv-app-05"}',
                        "start": "2026-06-11T08:57:00Z",
                        "end": "2026-06-11T09:12:00Z",
                        "step": "60s",
                    },
                    "risk": "low",
                    "requires_approval": False,
                    "reason": "Fresh metric is required before remediation.",
                    "timeout_seconds": 30,
                }
            ],
            "requires_human_approval": False,
            "approval_request": None,
            "missing_evidence": ["fresh temperature metric", "cooling zone event log"],
            "confidence": 0.45,
        }

    def test_build_messages_include_context_and_contract(self):
        context = {"incident_state": {"incident_id": "inc-1", "asset_id": "srv-1"}}

        messages = build_dcim_operations_messages(context)

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Jangan mengarang hostname", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn(SCHEMA_VERSION, messages[1]["content"])
        self.assertIn('"incident_id": "inc-1"', messages[1]["content"])

    def test_validate_valid_response_mapping(self):
        result = validate_dcim_agent_response(self._valid_response())

        self.assertTrue(result.valid, result.errors)

    def test_validate_valid_response_json_string(self):
        result = validate_dcim_agent_response(json.dumps(self._valid_response()))

        self.assertTrue(result.valid, result.errors)

    def test_reject_invalid_json(self):
        result = validate_dcim_agent_response("not-json")

        self.assertFalse(result.valid)
        self.assertTrue(any("Invalid JSON" in error for error in result.errors))

    def test_reject_extra_top_level_keys(self):
        response = self._valid_response()
        response["fabricated_cpu"] = "15 percent"

        result = validate_dcim_agent_response(response)

        self.assertFalse(result.valid)
        self.assertTrue(any("unexpected keys" in error for error in result.errors))

    def test_destructive_action_requires_approval(self):
        response = self._valid_response()
        response["tool_calls"][0]["action_type"] = "restart_service"
        response["tool_calls"][0]["tool_name"] = "runbook_automation"
        response["tool_calls"][0]["risk"] = "high"
        response["tool_calls"][0]["requires_approval"] = False

        result = validate_dcim_agent_response(response)

        self.assertFalse(result.valid)
        self.assertTrue(any("requires human approval" in error for error in result.errors))
        self.assertTrue(action_requires_approval("restart_service"))

    def test_top_level_approval_requires_payload(self):
        response = self._valid_response()
        response["requires_human_approval"] = True

        result = validate_dcim_agent_response(response)

        self.assertFalse(result.valid)
        self.assertTrue(any("approval_request" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
