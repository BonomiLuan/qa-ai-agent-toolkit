# Playwright Test Agent

Explores an API endpoint, uses an LLM to generate test scenarios, scaffolds and runs Playwright-compatible pytest tests, and produces a structured report.

## Usage

```bash
python -m agents.playwright_test_agent.agent --url https://viacep.com.br/ws/13140770/json/
```

## Pipeline

1. **Explore** — GET the target URL, infer response shape
2. **Generate** — Send shape to LLM, receive JSON test scenarios
3. **Scaffold** — Write `generated_tests.py` from scenarios
4. **Run** — Execute via pytest subprocess
5. **Report** — Output `reports/report.json` and `reports/report.md`

## Configuration

Set in `.env` at the project root:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | Model to use (default: `gpt-4o-mini`) |
