"""Azure DevOps REST API v7.0 client."""

from __future__ import annotations

import base64
from datetime import datetime

import requests

from shared.logger import get_logger

logger = get_logger("ado-client")

ADO_BASE = "https://dev.azure.com"
VSTEST_BASE = "https://vstmr.dev.azure.com"


class ADOClient:
    def __init__(self, org: str, project: str, pat: str):
        self.org = org
        self.project = project
        token = base64.b64encode(f":{pat}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        resp = requests.get(url, headers=self._headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _post(self, url: str, body: dict) -> dict | list:
        resp = requests.post(url, headers=self._headers, json=body, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_work_items(self, query: str) -> list[dict]:
        wiql_url = f"{ADO_BASE}/{self.org}/{self.project}/_apis/wit/wiql?api-version=7.0"
        result = self._post(wiql_url, {"query": query})
        ids = [item["id"] for item in result.get("workItems", [])]

        if not ids:
            return []

        ids_param = ",".join(str(i) for i in ids[:200])
        fields = "System.Id,System.Title,System.WorkItemType,System.State,System.CreatedDate,System.AssignedTo,Microsoft.VSTS.Common.Priority"
        items_url = f"{ADO_BASE}/{self.org}/{self.project}/_apis/wit/workitems?ids={ids_param}&fields={fields}&api-version=7.0"
        data = self._get(items_url)
        logger.info("Fetched work items", extra={"count": len(data.get("value", []))})
        return data.get("value", [])

    def get_test_runs(self, from_date: str, to_date: str) -> list[dict]:
        url = f"{ADO_BASE}/{self.org}/{self.project}/_apis/test/runs?api-version=7.0&minLastUpdatedDate={from_date}&maxLastUpdatedDate={to_date}"
        data = self._get(url)
        runs = data.get("value", [])
        logger.info("Fetched test runs", extra={"count": len(runs)})
        return runs

    def get_team_members(self) -> list[dict]:
        url = f"{ADO_BASE}/{self.org}/_apis/projects/{self.project}/teams?api-version=7.0"
        teams_data = self._get(url)
        members = []
        for team in teams_data.get("value", []):
            team_id = team["id"]
            members_url = f"{ADO_BASE}/{self.org}/_apis/projects/{self.project}/teams/{team_id}/members?api-version=7.0"
            m_data = self._get(members_url)
            members.extend(m_data.get("value", []))
        return members
