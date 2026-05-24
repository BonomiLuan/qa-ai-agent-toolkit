"""Unit tests for ADO Metrics Agent — mocks API responses, validates KPI computations."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.azure_devops_metrics_agent.metrics import (
    compute_bug_aging,
    compute_defect_rate,
    compute_team_summary,
    compute_test_pass_rate,
)


def _make_item(work_type: str, state: str = "Active", created: str = "2026-04-01T00:00:00Z") -> dict:
    return {
        "fields": {
            "System.WorkItemType": work_type,
            "System.State": state,
            "System.CreatedDate": created,
        }
    }


def _make_run(total: int, passed: int) -> dict:
    return {"totalTests": total, "passedTests": passed}


class TestComputeDefectRate:
    def test_no_items_returns_zero(self):
        assert compute_defect_rate([]) == 0.0

    def test_all_bugs(self):
        items = [_make_item("Bug")] * 3
        assert compute_defect_rate(items) == 100.0

    def test_mixed_items(self):
        items = [_make_item("Bug"), _make_item("Task"), _make_item("Task"), _make_item("Bug")]
        assert compute_defect_rate(items) == 50.0

    def test_no_bugs(self):
        items = [_make_item("Task"), _make_item("User Story")]
        assert compute_defect_rate(items) == 0.0


class TestComputeTestPassRate:
    def test_no_runs_returns_zero(self):
        assert compute_test_pass_rate([]) == 0.0

    def test_all_passed(self):
        runs = [_make_run(10, 10), _make_run(5, 5)]
        assert compute_test_pass_rate(runs) == 100.0

    def test_partial_pass(self):
        runs = [_make_run(10, 8), _make_run(10, 6)]
        assert compute_test_pass_rate(runs) == 70.0

    def test_zero_total_tests(self):
        runs = [_make_run(0, 0)]
        assert compute_test_pass_rate(runs) == 0.0


class TestComputeBugAging:
    def test_no_bugs_returns_zeros(self):
        result = compute_bug_aging([])
        assert result["bug_count"] == 0
        assert result["avg_days_open"] == 0
        assert result["oldest_bug_days"] == 0

    def test_single_bug_aging(self):
        bugs = [_make_item("Bug", created="2026-04-24T00:00:00Z")]
        result = compute_bug_aging(bugs)
        assert result["bug_count"] == 1
        assert result["avg_days_open"] == result["oldest_bug_days"]
        assert result["oldest_bug_days"] > 0

    def test_multiple_bugs(self):
        bugs = [
            _make_item("Bug", created="2026-01-01T00:00:00Z"),
            _make_item("Bug", created="2026-05-01T00:00:00Z"),
        ]
        result = compute_bug_aging(bugs)
        assert result["bug_count"] == 2
        assert result["oldest_bug_days"] > result["avg_days_open"]


class TestComputeTeamSummary:
    def test_full_summary(self):
        items = [
            _make_item("Bug", state="Active"),
            _make_item("Bug", state="Closed"),
            _make_item("Task", state="Active"),
            _make_item("User Story", state="Done"),
        ]
        runs = [_make_run(20, 18)]
        result = compute_team_summary(items, runs)

        assert result["total_work_items"] == 4
        assert result["total_bugs"] == 2
        assert result["open_bugs"] == 1
        assert result["closed_bugs"] == 1
        assert result["defect_rate_pct"] == 50.0
        assert result["test_pass_rate_pct"] == 90.0
        assert result["total_test_runs"] == 1
        assert result["total_tests_executed"] == 20

    def test_empty_inputs(self):
        result = compute_team_summary([], [])
        assert result["total_work_items"] == 0
        assert result["defect_rate_pct"] == 0.0
        assert result["test_pass_rate_pct"] == 0.0
