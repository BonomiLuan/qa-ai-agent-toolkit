# qa-ai-agent-toolkit

**AI-augmented quality engineering for regulated systems.**

> **Status: design stage.** This repository currently contains architecture and design
> documentation. Implementation is published incrementally — see the [Roadmap](#roadmap)
> for what exists and what is coming.

---

## The problem

In regulated domains — payments, healthcare billing, financial services — the cost of
adequate test coverage is high enough that it routinely loses to schedule pressure. The
consequences are documented at national scale: CMS reported approximately **$94 billion in
improper payments** across federal healthcare programs in FY2025, and **77% of Medicaid
improper payments** trace to insufficient documentation — failures of process and system
correctness rather than clinical judgment.

Testing these systems properly is expensive. That expense is why it often doesn't happen.
This project exists to lower that cost.

---

## Scope

Two agents, aimed at the two places where quality work in regulated systems consumes the
most human effort: producing and maintaining test coverage, and turning engineering activity
into decision-grade quality signal.

### Agent 1 — Test generation and execution

An agent that works alongside Playwright to scaffold, execute and maintain test coverage for
web and API layers in systems that change continuously.

**Intended capability**
- Analyze application endpoints and UI flows and propose test scenarios
- Scaffold executable tests from those proposals
- Execute and report results in a structured, machine-readable format
- Flag coverage drift as the system under test evolves

**Planned stack:** Python · Playwright · pytest · LLM integration

### Agent 2 — Quality metrics

An agent that ingests work-item and test-execution data and produces quality intelligence
for engineering teams: defect density, coverage trends, escaped-defect rates and
team-level quality signal.

**Intended capability**
- Pull work item and test run data from Azure DevOps
- Compute quality KPIs per team and per iteration
- Generate structured reports for engineering leads

**Planned stack:** Python · Azure DevOps REST API · pandas

---

## Design principles

These constraints come from building quality practice inside regulated environments, where
"the tool decided" is not an acceptable answer to an auditor.

- **Traceability first.** Every generated or executed test is logged with full context —
  what was tested, why it was proposed, what the result was.
- **No black boxes.** The agent states what it is doing and on what basis. A suggestion you
  cannot interrogate is a suggestion you cannot defend.
- **Domain-agnostic core, domain-specific adapters.** Agent logic stays reusable;
  configuration carries the domain.
- **Observable by default.** Output is structured and integrable with existing dashboards,
  not trapped in the tool.
- **Human decides.** These agents reduce the cost of coverage. They do not decide what
  adequate coverage is.

---

## Roadmap

| Milestone | Target | Status |
|---|---|---|
| Architecture and design documentation | Aug 2026 | 🟡 In progress |
| Agent 1 — core generation loop | Oct 2026 | ⬜ Planned |
| Agent 1 — first usable release | Dec 2026 | ⬜ Planned |
| Applied examples against public APIs | Dec 2026 | ⬜ Planned |
| Agent 2 — metrics ingestion and reporting | Feb 2027 | ⬜ Planned |

Progress is published as it lands. Nothing is described here as working before it works.

---

## Provenance and scope

This repository is written independently. It contains **no client code, data, configuration,
or proprietary material of any employer or client**.

The design draws on the author's professional practice in quality engineering for financial
services and healthcare systems, but everything published here is original and written for
public use. That separation is deliberate and non-negotiable.

---

## Contributing

Early stage — issues and design discussion welcome. If you work on quality engineering in
regulated systems and something here is wrong or naive, say so.

---

## Author

**Luan Bonomi** · Software Quality Engineer
[linkedin.com/in/luanbonomi](https://www.linkedin.com/in/luanbonomi) ·
[github.com/BonomiLuan](https://github.com/BonomiLuan)
