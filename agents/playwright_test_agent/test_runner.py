"""Runs scaffolded test files via pytest subprocess and captures structured output."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from shared.logger import get_logger

logger = get_logger("test-runner")


class TestRunner:
    def __init__(self, test_file: str):
        self.test_file = Path(test_file)

    def run(self) -> dict:
        if not self.test_file.exists():
            raise FileNotFoundError(f"Test file not found: {self.test_file}")

        cmd = [sys.executable, "-m", "pytest", str(self.test_file), "-v", "--tb=short", "--no-header"]
        logger.info("Running tests", extra={"command": " ".join(cmd)})

        result = subprocess.run(cmd, capture_output=True, text=True)
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode

        passed, failed, errors = self._parse_output(stdout)

        summary = {
            "returncode": returncode,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "stdout": stdout,
            "stderr": stderr,
        }
        logger.info("Test run complete", extra={"passed": len(passed), "failed": len(failed)})
        return summary

    def _parse_output(self, stdout: str) -> tuple[list, list, list]:
        passed, failed, errors = [], [], []
        for line in stdout.splitlines():
            if " PASSED" in line:
                passed.append(line.strip())
            elif " FAILED" in line:
                failed.append(line.strip())
            elif " ERROR" in line:
                errors.append(line.strip())
        return passed, failed, errors
