"""Integration tests for the complete taskflow workflow."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from taskflow_mcp.server import (
    write_checklist,
    write_investigation,
    write_solution_plan,
)


class TestCompleteWorkflow:
    """Test the complete taskflow workflow from start to finish."""

    def test_complete_task_workflow(self, temp_dir: Path) -> None:
        """Test creating a complete task with all artifacts."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "feature-123"

            # Step 1: Create investigation
            investigation_content = """# Investigation

## Problem
Users are reporting slow page load times.

## Root Cause Analysis
After profiling, we found that the database queries are not optimized.

## Impact
- 40% of users experience >3s load times
- High bounce rate on slow pages
"""

            result1 = write_investigation(task_id, investigation_content)
            assert "Wrote" in result1
            assert "INVESTIGATION.md" in result1

            # Step 2: Create solution plan
            solution_content = """# Solution Plan

## Approach
Implement database query optimization and caching.

## Implementation Steps
1. Add database indexes for frequently queried fields
2. Implement Redis caching for expensive queries
3. Optimize N+1 query problems
4. Add query monitoring

## Timeline
- Week 1: Database optimization
- Week 2: Caching implementation
- Week 3: Monitoring and testing
"""

            result2 = write_solution_plan(task_id, solution_content)
            assert "Wrote" in result2
            assert "SOLUTION_PLAN.md" in result2

            # Step 3: Create initial checklist
            initial_checklist = [
                {
                    "label": "Analyze slow queries",
                    "status": "done",
                    "notes": "Identified 5 problematic queries",
                },
                {
                    "label": "Add database indexes",
                    "status": "in-progress",
                    "notes": "Working on user table indexes",
                },
                {
                    "label": "Implement Redis caching",
                    "status": "pending",
                    "notes": None,
                },
                {"label": "Add query monitoring", "status": "pending", "notes": None},
            ]

            result3 = write_checklist(task_id, initial_checklist)
            assert "Wrote" in result3
            assert "CHECKLIST.json" in result3

            # Step 4: Update checklist as work progresses
            updated_checklist = [
                {
                    "label": "Analyze slow queries",
                    "status": "done",
                    "notes": "Identified 5 problematic queries",
                },
                {
                    "label": "Add database indexes",
                    "status": "done",
                    "notes": "Added indexes for user, order, and product tables",
                },
                {
                    "label": "Implement Redis caching",
                    "status": "in-progress",
                    "notes": "Setting up Redis instance",
                },
                {"label": "Add query monitoring", "status": "pending", "notes": None},
            ]

            result4 = write_checklist(task_id, updated_checklist)
            assert "Wrote" in result4
            assert "CHECKLIST.json" in result4

            # Step 5: Verify all files exist
            # (Resource listing functionality not available in current API)

            # Check that all files exist and have correct content
            investigation_path = Path(temp_dir / ".tasks" / task_id / "INVESTIGATION.md")
            solution_path = Path(temp_dir / ".tasks" / task_id / "SOLUTION_PLAN.md")
            checklist_path = Path(temp_dir / ".tasks" / task_id / "CHECKLIST.json")

            assert investigation_path.exists()
            assert solution_path.exists()
            assert checklist_path.exists()

            # Verify content
            assert investigation_content in investigation_path.read_text()
            assert solution_content in solution_path.read_text()

            with open(checklist_path) as f:
                saved_checklist = json.load(f)
            assert saved_checklist == updated_checklist

    def test_multiple_tasks_workflow(self, temp_dir: Path) -> None:
        """Test managing multiple tasks simultaneously."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            # Create multiple tasks
            tasks = ["bug-456", "feature-789", "refactor-101"]

            for task_id in tasks:
                # Create investigation for each task
                write_investigation(task_id, f"# Investigation for {task_id}\n\nTask-specific content.")

                # Create solution plan for each task
                write_solution_plan(task_id, f"# Solution Plan for {task_id}\n\nTask-specific solution.")

                # Create checklist for each task
                checklist = [
                    {
                        "label": f"Task {task_id} - Step 1",
                        "status": "pending",
                        "notes": None,
                    },
                    {
                        "label": f"Task {task_id} - Step 2",
                        "status": "pending",
                        "notes": None,
                    },
                ]
                write_checklist(task_id, checklist)

            # Verify all files exist for each task
            for task_id in tasks:
                investigation_path = Path(temp_dir / ".tasks" / task_id / "INVESTIGATION.md")
                solution_path = Path(temp_dir / ".tasks" / task_id / "SOLUTION_PLAN.md")
                checklist_path = Path(temp_dir / ".tasks" / task_id / "CHECKLIST.json")

                assert investigation_path.exists()
                assert solution_path.exists()
                assert checklist_path.exists()

    def test_task_dependencies_enforced(self, temp_dir: Path) -> None:
        """Test that task dependencies are properly enforced."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-dependencies"

            # Try to create solution plan without investigation - should fail
            with pytest.raises(
                ValueError,
                match="Cannot write SOLUTION_PLAN.md without INVESTIGATION.md",
            ):
                write_solution_plan(task_id)

            # Create investigation
            write_investigation(task_id, "# Investigation\n\nContent.")

            # Try to create checklist without solution plan - should fail
            with pytest.raises(
                ValueError,
                match="Cannot write CHECKLIST.json without SOLUTION_PLAN.md",
            ):
                write_checklist(task_id)

            # Create solution plan
            write_solution_plan(task_id, "# Solution Plan\n\nContent.")

            # Now checklist should work
            result = write_checklist(task_id, [])
            assert "Wrote" in result

    def test_file_persistence(self, temp_dir: Path) -> None:
        """Test that files persist correctly and can be read back."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "persistence-test"

            # Create all files
            investigation_content = "# Investigation\n\nThis is a test investigation."
            solution_content = "# Solution Plan\n\nThis is a test solution."
            checklist_content = [{"label": "Test task", "status": "done", "notes": "Completed"}]

            write_investigation(task_id, investigation_content)
            write_solution_plan(task_id, solution_content)
            write_checklist(task_id, checklist_content)

            # Read files back directly from filesystem
            investigation_path = Path(temp_dir / ".tasks" / task_id / "INVESTIGATION.md")
            solution_path = Path(temp_dir / ".tasks" / task_id / "SOLUTION_PLAN.md")
            checklist_path = Path(temp_dir / ".tasks" / task_id / "CHECKLIST.json")

            # Verify content
            assert investigation_path.read_text() == investigation_content
            assert solution_path.read_text() == solution_content

            with open(checklist_path) as f:
                saved_checklist = json.load(f)
            assert saved_checklist == checklist_content

            # Verify files exist (MCP resource listing not available in current API)
            assert investigation_path.exists()
            assert solution_path.exists()
            assert checklist_path.exists()
