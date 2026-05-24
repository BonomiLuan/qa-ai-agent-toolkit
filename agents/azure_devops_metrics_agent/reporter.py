"""Generates Markdown and JSON quality reports from ADO metrics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

REPORTS_DIR = Path(__file__).parent / "reports"

_MD_TEMPLATE = """\
# Quality Report — {{ project }}
**Sprint:** {{ sprint }}
**Generated:** {{ timestamp }}

---

## KPI Summary

| Metric | Value |
|--------|-------|
| Total Work Items | {{ summary.total_work_items }} |
| Total Bugs | {{ summary.total_bugs }} |
| Open Bugs | {{ summary.open_bugs }} |
| Closed Bugs | {{ summary.closed_bugs }} |
| Defect Rate | {{ summary.defect_rate_pct }}% |
| Test Pass Rate | {{ summary.test_pass_rate_pct }}% |
| Total Test Runs | {{ summary.total_test_runs }} |
| Tests Executed | {{ summary.total_tests_executed }} |

## Bug Aging

| Metric | Value |
|--------|-------|
| Open Bug Count | {{ summary.bug_aging.bug_count }} |
| Average Days Open | {{ summary.bug_aging.avg_days_open }} |
| Oldest Bug (days) | {{ summary.bug_aging.oldest_bug_days }} |

---

## Recommendations

{% if summary.defect_rate_pct > 20 %}
- ⚠️ **High defect rate ({{ summary.defect_rate_pct }}%)** — review development process and add regression tests.
{% endif %}
{% if summary.test_pass_rate_pct < 80 %}
- ⚠️ **Low test pass rate ({{ summary.test_pass_rate_pct }}%)** — investigate failing test runs and flaky tests.
{% endif %}
{% if summary.bug_aging.oldest_bug_days > 30 %}
- ⚠️ **Oldest open bug is {{ summary.bug_aging.oldest_bug_days }} days old** — prioritize backlog grooming.
{% endif %}
{% if summary.defect_rate_pct <= 20 and summary.test_pass_rate_pct >= 80 and summary.bug_aging.oldest_bug_days <= 30 %}
- ✅ All key quality indicators are within acceptable thresholds.
{% endif %}
"""


class Reporter:
    def __init__(self, org: str, project: str, sprint: str, summary: dict):
        self.org = org
        self.project = project
        self.sprint = sprint
        self.summary = summary
        self.timestamp = datetime.now(timezone.utc).isoformat()
        REPORTS_DIR.mkdir(exist_ok=True)

    def generate(self) -> dict:
        report = {
            "timestamp": self.timestamp,
            "organization": self.org,
            "project": self.project,
            "sprint": self.sprint,
            "summary": self.summary,
        }
        date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._write_json(report, date_tag)
        self._write_markdown(report, date_tag)
        return report

    def _write_json(self, report: dict, date_tag: str) -> None:
        path = REPORTS_DIR / f"quality_report_{date_tag}.json"
        path.write_text(json.dumps(report, indent=2))

    def _write_markdown(self, report: dict, date_tag: str) -> None:
        rendered = Template(_MD_TEMPLATE).render(
            project=self.project,
            sprint=self.sprint,
            timestamp=self.timestamp,
            summary=self.summary,
        )
        path = REPORTS_DIR / f"quality_report_{date_tag}.md"
        path.write_text(rendered)
