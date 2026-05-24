"""Quality KPI computation functions for Azure DevOps data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _field(item: dict, key: str) -> Any:
    return item.get("fields", {}).get(key)


def compute_defect_rate(work_items: list[dict]) -> float:
    total = len(work_items)
    if not total:
        return 0.0
    bugs = sum(1 for i in work_items if _field(i, "System.WorkItemType") == "Bug")
    return round(bugs / total * 100, 2)


def compute_test_pass_rate(test_runs: list[dict]) -> float:
    total_tests = sum(r.get("totalTests", 0) for r in test_runs)
    if not total_tests:
        return 0.0
    passed = sum(r.get("passedTests", 0) for r in test_runs)
    return round(passed / total_tests * 100, 2)


def compute_bug_aging(bugs: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    ages = []
    for bug in bugs:
        created_raw = _field(bug, "System.CreatedDate")
        if not created_raw:
            continue
        created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        ages.append((now - created).days)

    if not ages:
        return {"avg_days_open": 0, "oldest_bug_days": 0, "bug_count": 0}

    return {
        "avg_days_open": round(sum(ages) / len(ages), 1),
        "oldest_bug_days": max(ages),
        "bug_count": len(ages),
    }


def compute_team_summary(work_items: list[dict], test_runs: list[dict]) -> dict:
    bugs = [i for i in work_items if _field(i, "System.WorkItemType") == "Bug"]
    open_bugs = [b for b in bugs if _field(b, "System.State") not in ("Closed", "Resolved", "Done")]
    closed_bugs = [b for b in bugs if _field(b, "System.State") in ("Closed", "Resolved", "Done")]

    return {
        "total_work_items": len(work_items),
        "total_bugs": len(bugs),
        "open_bugs": len(open_bugs),
        "closed_bugs": len(closed_bugs),
        "defect_rate_pct": compute_defect_rate(work_items),
        "test_pass_rate_pct": compute_test_pass_rate(test_runs),
        "bug_aging": compute_bug_aging(open_bugs),
        "total_test_runs": len(test_runs),
        "total_tests_executed": sum(r.get("totalTests", 0) for r in test_runs),
    }
