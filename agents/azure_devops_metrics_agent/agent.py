"""Azure DevOps Metrics Agent — fetches work items and test runs, computes KPIs, generates report."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.config import load_config
from shared.logger import get_logger
from agents.azure_devops_metrics_agent.ado_client import ADOClient
from agents.azure_devops_metrics_agent.metrics import compute_team_summary
from agents.azure_devops_metrics_agent.reporter import Reporter

logger = get_logger("ado-metrics-agent")
console = Console()

_REQUIRED_KEYS = ["ADO_ORGANIZATION", "ADO_PROJECT", "ADO_PAT"]


class ADOMetricsAgent:
    def __init__(self, sprint: str, config: dict):
        self.sprint = sprint
        self.config = config
        self.client = ADOClient(
            org=config["ADO_ORGANIZATION"],
            project=config["ADO_PROJECT"],
            pat=config["ADO_PAT"],
        )

    def _build_wiql(self) -> str:
        return (
            f"SELECT [System.Id] FROM WorkItems "
            f"WHERE [System.TeamProject] = '{self.config['ADO_PROJECT']}' "
            f"AND [System.IterationPath] CONTAINS '{self.sprint}' "
            f"ORDER BY [System.CreatedDate] DESC"
        )

    def run(self) -> dict:
        console.print(f"[bold cyan]Fetching[/] work items for sprint: [yellow]{self.sprint}[/]")
        work_items = self.client.get_work_items(self._build_wiql())

        to_date = datetime.now(timezone.utc)
        from_date = to_date - timedelta(days=30)
        console.print(f"[bold cyan]Fetching[/] test runs (last 30 days)…")
        test_runs = self.client.get_test_runs(
            from_date=from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            to_date=to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        console.print("[bold cyan]Computing[/] KPIs…")
        summary = compute_team_summary(work_items, test_runs)
        self._print_summary(summary)

        reporter = Reporter(
            org=self.config["ADO_ORGANIZATION"],
            project=self.config["ADO_PROJECT"],
            sprint=self.sprint,
            summary=summary,
        )
        report = reporter.generate()
        console.print("[bold green]Done.[/] Reports written to reports/")
        return report

    def _print_summary(self, summary: dict) -> None:
        table = Table(title="Quality KPIs", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")
        for key, val in summary.items():
            if isinstance(val, dict):
                for k, v in val.items():
                    table.add_row(f"  {k}", str(v))
            else:
                table.add_row(key, str(val))
        console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Azure DevOps Metrics Agent")
    parser.add_argument("--sprint", required=True, help="Sprint name or path (e.g. 'Sprint 42')")
    args = parser.parse_args()

    cfg = load_config(required_keys=_REQUIRED_KEYS)
    agent = ADOMetricsAgent(sprint=args.sprint, config=cfg)
    agent.run()
