"""Generates JSON and Markdown reports from test run results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "reports"


class Reporter:
    def __init__(self, target_url: str, scenarios: list[dict], results: dict):
        self.target_url = target_url
        self.scenarios = scenarios
        self.results = results
        self.timestamp = datetime.now(timezone.utc).isoformat()
        REPORTS_DIR.mkdir(exist_ok=True)

    def generate(self) -> dict:
        report = self._build_report()
        self._write_json(report)
        self._write_markdown(report)
        return report

    def _build_report(self) -> dict:
        passed_names = {line.split("::")[1].split(" ")[0] for line in self.results.get("passed", [])}
        failed_names = {line.split("::")[1].split(" ")[0] for line in self.results.get("failed", [])}

        scenario_results = []
        for s in self.scenarios:
            fn = f"test_{s['name']}"
            if fn in passed_names:
                status = "PASS"
                error = None
            elif fn in failed_names:
                status = "FAIL"
                error = self._extract_error(fn)
            else:
                status = "SKIP"
                error = None
            scenario_results.append({**s, "status": status, "error": error})

        total = len(scenario_results)
        passed = sum(1 for r in scenario_results if r["status"] == "PASS")

        return {
            "timestamp": self.timestamp,
            "target": self.target_url,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": round(passed / total * 100, 1) if total else 0,
            },
            "scenarios": scenario_results,
        }

    def _extract_error(self, fn_name: str) -> str | None:
        stdout = self.results.get("stdout", "")
        lines = stdout.splitlines()
        capture = False
        error_lines = []
        for line in lines:
            if fn_name in line and "FAILED" in line:
                capture = True
            elif capture:
                if line.startswith("FAILED") or line.startswith("PASSED"):
                    break
                error_lines.append(line)
        return "\n".join(error_lines).strip() or None

    def _write_json(self, report: dict) -> None:
        path = REPORTS_DIR / "report.json"
        path.write_text(json.dumps(report, indent=2))

    def _write_markdown(self, report: dict) -> None:
        s = report["summary"]
        lines = [
            f"# QA Report — {report['target']}",
            f"Generated: {report['timestamp']}",
            "",
            "## Summary",
            f"| Total | Passed | Failed | Pass Rate |",
            f"|-------|--------|--------|-----------|",
            f"| {s['total']} | {s['passed']} | {s['failed']} | {s['pass_rate']}% |",
            "",
            "## Scenarios",
            "| Name | Status | Expected Status | Description |",
            "|------|--------|-----------------|-------------|",
        ]
        for sc in report["scenarios"]:
            icon = "✅" if sc["status"] == "PASS" else "❌" if sc["status"] == "FAIL" else "⏭️"
            lines.append(f"| {sc['name']} | {icon} {sc['status']} | {sc['expected_status']} | {sc['description']} |")

        failed = [sc for sc in report["scenarios"] if sc["status"] == "FAIL"]
        if failed:
            lines += ["", "## Failures"]
            for sc in failed:
                lines += [f"### {sc['name']}", f"```", sc.get("error") or "No details", "```", ""]

        path = REPORTS_DIR / "report.md"
        path.write_text("\n".join(lines))
