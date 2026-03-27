# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Test Runner Service - Orchestrates automated test execution

Runs tests before task completion and stores results in task history.
"""

import logging
import subprocess
from typing import List, Tuple
from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select
from app.models.task import Task

logger = logging.getLogger(__name__)


class TestResult:
    """Container for test execution results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.coverage = 0.0
        self.duration = 0.0
        self.errors: List[str] = []

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "coverage": self.coverage,
            "duration": self.duration,
            "errors": self.errors,
            "total_tests": self.passed + self.failed + self.skipped,
            "success_rate": (
                (self.passed / (self.passed + self.failed)) * 100
                if (self.passed + self.failed) > 0
                else 0
            ),
        }


class TestRunner:
    """Run automated tests and check quality gates."""

    def __init__(self, db_session: Session, repo_path: str = "."):
        self.db_session = db_session
        self.repo_path = repo_path
        self.coverage_threshold = 80  # Minimum coverage percentage

    async def run_unit_tests(self, test_path: str = "tests/") -> TestResult:
        """
        Run unit tests using pytest.

        Args:
            test_path: Path to test directory

        Returns:
            TestResult with pass/fail counts
        """
        result = TestResult()

        try:
            # Run pytest with JSON output
            cmd = [
                "pytest",
                test_path,
                "--tb=short",
                "--quiet",
                "-v",
            ]

            logger.info(f"Running unit tests: {' '.join(cmd)}")
            process = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse output
            output = process.stdout + process.stderr

            # Extract test counts from pytest output
            if "passed" in output:
                # Simple parsing - count lines with result keywords
                for line in output.split("\n"):
                    if " passed" in line:
                        try:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "passed":
                                    result.passed = int(parts[i - 1])
                                elif part == "failed":
                                    result.failed = int(parts[i - 1])
                                elif part == "skipped":
                                    result.skipped = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

            if process.returncode != 0:
                result.errors.append(f"Tests failed with exit code {process.returncode}")
                logger.error(f"Test execution failed: {process.stderr}")

            logger.info(f"Unit tests: {result.passed} passed, {result.failed} failed")

        except subprocess.TimeoutExpired:
            result.errors.append("Test execution timed out (>5 minutes)")
            logger.error("Tests timed out")
        except FileNotFoundError:
            result.errors.append("pytest not found. Install with: pip install pytest")
            logger.error("pytest not available")
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error running tests: {e}")

        return result

    async def run_integration_tests(self, test_path: str = "tests/integration/") -> TestResult:
        """
        Run integration tests.

        Args:
            test_path: Path to integration tests

        Returns:
            TestResult
        """
        result = TestResult()

        try:
            cmd = [
                "pytest",
                test_path,
                "-v",
                "--tb=short",
            ]

            logger.info(f"Running integration tests: {' '.join(cmd)}")
            process = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            # Parse results (same as unit tests)
            output = process.stdout + process.stderr
            for line in output.split("\n"):
                if " passed" in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "passed":
                                result.passed += int(parts[i - 1])
                            elif part == "failed":
                                result.failed += int(parts[i - 1])
                    except (ValueError, IndexError):
                        pass

            if process.returncode != 0:
                result.errors.append("Integration tests failed")

            logger.info(f"Integration tests: {result.passed} passed, {result.failed} failed")

        except subprocess.TimeoutExpired:
            result.errors.append("Integration tests timed out (>10 minutes)")
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error running integration tests: {e}")

        return result

    async def check_code_coverage(self, test_path: str = "tests/") -> Tuple[float, str]:
        """
        Check test code coverage.

        Args:
            test_path: Path to tests

        Returns:
            (coverage_percentage, coverage_report)
        """
        try:
            cmd = [
                "pytest",
                test_path,
                "--cov=app",
                "--cov-report=term-only",
                "--quiet",
            ]

            logger.info("Checking code coverage...")
            process = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = process.stdout + process.stderr

            # Parse coverage percentage
            coverage = 0.0
            for line in output.split("\n"):
                if "TOTAL" in line:
                    try:
                        # Line format: "TOTAL ... 85%"
                        parts = line.split()
                        coverage_str = parts[-1].rstrip("%")
                        coverage = float(coverage_str)
                        break
                    except (ValueError, IndexError):
                        pass

            logger.info(f"Coverage: {coverage}%")
            return coverage, output

        except subprocess.TimeoutExpired:
            logger.error("Coverage check timed out")
            return 0.0, "Coverage check timed out"
        except FileNotFoundError:
            logger.error("pytest-cov not found")
            return 0.0, "pytest-cov not installed"
        except Exception as e:
            logger.error(f"Error checking coverage: {e}")
            return 0.0, str(e)

    async def run_linting(self) -> Tuple[bool, List[str]]:
        """
        Run code linting (ruff + black).

        Returns:
            (all_passed, list_of_errors)
        """
        errors = []

        try:
            # Run ruff
            cmd = ["ruff", "check", "app/", "--fix"]
            logger.info("Running linting (ruff)...")
            process = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if process.returncode != 0:
                errors.append("Ruff linting found issues")

            # Run black
            cmd = ["black", "app/", "--check", "--quiet"]
            logger.info("Checking code formatting (black)...")
            process = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if process.returncode != 0:
                errors.append("Code formatting issues found (run: black app/)")

        except FileNotFoundError:
            errors.append("Linting tools not installed (ruff, black)")
        except Exception as e:
            errors.append(str(e))

        return len(errors) == 0, errors

    async def inject_test_results_into_task(
        self,
        task_id: UUID,
        test_result: TestResult,
    ) -> None:
        """
        Store test results in task history.

        Args:
            task_id: Task to update
            test_result: Results from test execution
        """
        task = self.db_session.exec(select(Task).where(Task.id == task_id)).first()
        if not task:
            logger.warning(f"Task {task_id} not found")
            return

        # Store test results in task description/metadata
        # (In production, would use a separate test_results table)
        test_summary = (
            f"\n\n**Test Results:**\n"
            f"- Passed: {test_result.passed}\n"
            f"- Failed: {test_result.failed}\n"
            f"- Skipped: {test_result.skipped}\n"
            f"- Coverage: {test_result.coverage:.1f}%\n"
        )

        if test_result.errors:
            test_summary += f"- Errors: {', '.join(test_result.errors)}\n"

        # Append to description (don't overwrite)
        if task.description:
            task.description += test_summary
        else:
            task.description = test_summary

        task.updated_at = datetime.utcnow()
        self.db_session.add(task)
        self.db_session.commit()

        logger.info(f"Test results injected into task {task_id}")

    async def check_quality_gates(
        self,
        test_result: TestResult,
        coverage: float,
    ) -> Tuple[bool, List[str]]:
        """
        Check if quality gates are met.

        Args:
            test_result: Unit test results
            coverage: Code coverage percentage

        Returns:
            (all_gates_passed, list_of_violations)
        """
        violations = []

        # Check for test failures
        if test_result.failed > 0:
            violations.append(f"{test_result.failed} test(s) failed")

        # Check coverage threshold
        if coverage < self.coverage_threshold:
            violations.append(
                f"Coverage {coverage:.1f}% below threshold ({self.coverage_threshold}%)"
            )

        # Check for errors during execution
        if test_result.errors:
            violations.extend(test_result.errors)

        return len(violations) == 0, violations
