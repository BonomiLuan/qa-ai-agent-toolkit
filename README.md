# qa-ai-agent-toolkit

**AI-augmented quality engineering agents for regulated environments.**

This toolkit contains two AI agents designed to reduce the manual overhead of quality engineering in high-stakes software domains — financial services and healthcare. Both agents are active implementations built from real-world QA practice, not prototypes.

---

## Agents

### 🤖 Agent 1: Playwright Test Automation Agent

An AI-driven agent that integrates with Playwright to automate test generation and execution for web and API layers. Designed for environments where test suites need to evolve continuously alongside fast-moving software systems.

**What it does:**
- Analyzes application endpoints and UI flows to suggest and scaffold test scenarios
- Executes tests and reports results in structured format
- Reduces manual effort in maintaining coverage for evolving systems

**Stack:** Python · Playwright · OpenAI/LLM integration · pytest

```
agents/
└── playwright-test-agent/
    ├── agent.py          # Core agent logic
    ├── test_runner.py    # Execution layer
    ├── reporter.py       # Structured output
    └── README.md
```

---

### 📊 Agent 2: Azure DevOps Metrics Agent

An automation agent that ingests Azure DevOps sprint and backlog data to generate quality intelligence reports for engineering teams — defect rates, test coverage trends, incident frequency, and team-level quality compliance.

**What it does:**
- Pulls work item and test run data from Azure DevOps API
- Computes quality KPIs per team and sprint
- Generates structured reports for engineering managers and QA leads

**Stack:** Python · Azure DevOps REST API · pandas · Jinja2 (report templates)

```
agents/
└── azure-devops-metrics-agent/
    ├── agent.py          # Core agent logic
    ├── ado_client.py     # Azure DevOps API wrapper
    ├── metrics.py        # KPI computation
    ├── reporter.py       # Report generation
    └── README.md
```

---

## Design principles

This toolkit was designed with regulated environments in mind:

- **Traceability first**: every test generated or executed is logged with full context
- **No magic black boxes**: agents explain what they're doing and why
- **Domain-agnostic core, domain-specific adapters**: the agent logic is reusable; the configuration adapts to the target system
- **Observable by default**: outputs are structured and integrable with existing dashboards

---

## Applied examples

See [`ai-qa-lab`](https://github.com/BonomiLuan/ai-qa-lab) for demonstrations of these agents applied to real-world public APIs.

---

## Status

🚧 Active development — agents are in production use at a healthcare institution in Brazil. Open-source release in progress.

---

## Author

**Luan Bonomi** · Senior Quality Engineer  
[linkedin.com/in/luanbonomi](https://www.linkedin.com/in/luanbonomi) · [github.com/BonomiLuan](https://github.com/BonomiLuan)
