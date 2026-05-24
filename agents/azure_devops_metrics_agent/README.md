# Azure DevOps Metrics Agent

Connects to Azure DevOps REST API, fetches work items and test run data for a sprint, computes quality KPIs, and generates a Markdown + JSON report.

## Usage

```bash
python -m agents.azure_devops_metrics_agent.agent --sprint "Sprint 42"
```

## Pipeline

1. **Fetch** — Query work items via WIQL for the given sprint
2. **Fetch** — Retrieve test runs from the last 30 days
3. **Compute** — Calculate defect rate, test pass rate, bug aging
4. **Report** — Write `reports/quality_report_{date}.md` and `.json`

## Configuration

Set in `.env` at the project root:

| Variable | Description |
|---|---|
| `ADO_ORGANIZATION` | Azure DevOps organization name |
| `ADO_PROJECT` | Project name |
| `ADO_PAT` | Personal Access Token (needs Read permissions on Work Items and Test) |
