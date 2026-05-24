"""Unit tests for PlaywrightTestAgent — mocks LLM and HTTP calls."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import responses as responses_lib

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.playwright_test_agent.agent import PlaywrightTestAgent

SAMPLE_SCENARIOS = [
    {
        "name": "valid_zipcode_returns_200",
        "description": "Valid zip returns 200 with address fields",
        "method": "GET",
        "input": {"zip": "13140770"},
        "expected_status": 200,
        "expected_behavior": "Response has logradouro and localidade",
    }
]

SAMPLE_RESPONSE = {
    "cep": "13140-770",
    "logradouro": "Rua Exemplo",
    "bairro": "Centro",
    "localidade": "Campinas",
    "uf": "SP",
}


@pytest.fixture
def agent():
    config = {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4o-mini"}
    return PlaywrightTestAgent(target_url="https://viacep.com.br/ws/13140770/json/", config=config)


@responses_lib.activate
def test_explore_returns_shape(agent):
    responses_lib.add(
        responses_lib.GET,
        "https://viacep.com.br/ws/13140770/json/",
        json=SAMPLE_RESPONSE,
        status=200,
    )
    result = agent.explore()
    assert result["status_code"] == 200
    assert "response_shape" in result
    assert "logradouro" in result["response_shape"]


@responses_lib.activate
def test_explore_stores_sample(agent):
    responses_lib.add(
        responses_lib.GET,
        "https://viacep.com.br/ws/13140770/json/",
        json=SAMPLE_RESPONSE,
        status=200,
    )
    result = agent.explore()
    assert result["sample"]["cep"] == "13140-770"


@responses_lib.activate
def test_generate_scenarios_calls_llm(agent):
    responses_lib.add(
        responses_lib.GET,
        "https://viacep.com.br/ws/13140770/json/",
        json=SAMPLE_RESPONSE,
        status=200,
    )

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(SAMPLE_SCENARIOS)
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    with patch.object(agent.client.chat.completions, "create", return_value=mock_completion):
        scenarios = agent.generate_scenarios()

    assert len(scenarios) == 1
    assert scenarios[0]["name"] == "valid_zipcode_returns_200"


@responses_lib.activate
def test_generate_scenarios_raises_on_invalid_json(agent):
    responses_lib.add(
        responses_lib.GET,
        "https://viacep.com.br/ws/13140770/json/",
        json=SAMPLE_RESPONSE,
        status=200,
    )

    mock_choice = MagicMock()
    mock_choice.message.content = "not valid json at all"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    with patch.object(agent.client.chat.completions, "create", return_value=mock_completion):
        with pytest.raises(ValueError, match="valid JSON"):
            agent.generate_scenarios()


def test_scaffold_tests_writes_file(agent, tmp_path, monkeypatch):
    import agents.playwright_test_agent.agent as agent_module
    monkeypatch.setattr(agent_module, "GENERATED_TESTS_PATH", tmp_path / "generated_tests.py")
    agent._exploration = {"url": agent.target_url, "status_code": 200, "response_shape": {}, "sample": {}}
    code = agent.scaffold_tests(SAMPLE_SCENARIOS)
    assert "def test_valid_zipcode_returns_200" in code
    assert "assert resp.status_code == 200" in code
