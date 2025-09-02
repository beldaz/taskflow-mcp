"""Tests for the taskflow-mcp server functionality."""

import json
import os
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest
from jsonschema import ValidationError

from taskflow_mcp.server import (
    BASE_DIR,
    CHECKLIST_SCHEMA,
    create_checklist,
    create_investigation,
    create_solution_plan,
    list_task_resources_sync,
    task_path,
    update_checklist,
)


class TestTaskPath:
    """Test the task_path utility function."""

    def test_task_path_construction(self) -> None:
        """Test that task_path constructs correct paths."""
        result = task_path("test-task", "INVESTIGATION.md")
        expected = os.path.join(BASE_DIR, "test-task", "INVESTIGATION.md")
        assert result == expected

    def test_task_path_with_subdirs(self) -> None:
        """Test task_path with nested directories."""
        result = task_path("nested/task", "CHECKLIST.json")
        expected = os.path.join(BASE_DIR, "nested/task", "CHECKLIST.json")
        assert result == expected


class TestCreateInvestigation:
    """Test the create_investigation method."""

    def test_create_investigation_basic(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test creating an investigation file with default content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            result = create_investigation(task_id)

            expected_path = task_path(task_id, "INVESTIGATION.md")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == "# Investigation\n\n"

    def test_create_investigation_with_content(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test creating an investigation file with custom content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            result = create_investigation(task_id, sample_investigation_content)

            expected_path = task_path(task_id, "INVESTIGATION.md")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == sample_investigation_content

    def test_create_investigation_creates_directory(self, temp_dir: Path) -> None:
        """Test that create_investigation creates the task directory."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "nested/task"
            create_investigation(task_id)

            task_dir = os.path.dirname(task_path(task_id, "INVESTIGATION.md"))
            assert os.path.exists(task_dir)
            assert os.path.isdir(task_dir)


class TestCreateSolutionPlan:
    """Test the create_solution_plan method."""

    def test_create_solution_plan_basic(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a solution plan file with default content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # First create investigation (required)
            create_investigation(task_id, sample_investigation_content)

            result = create_solution_plan(task_id)

            expected_path = task_path(task_id, "SOLUTION_PLAN.md")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == "# Solution Plan\n\n"

    def test_create_solution_plan_with_content(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a solution plan file with custom content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # First create investigation (required)
            create_investigation(task_id, sample_investigation_content)

            result = create_solution_plan(task_id, sample_solution_plan_content)

            expected_path = task_path(task_id, "SOLUTION_PLAN.md")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == sample_solution_plan_content

    def test_create_solution_plan_without_investigation(self, temp_dir: Path) -> None:
        """Test that create_solution_plan fails without investigation."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            with pytest.raises(
                ValueError,
                match="Cannot create SOLUTION_PLAN.md without INVESTIGATION.md",
            ):
                create_solution_plan(task_id)


class TestCreateChecklist:
    """Test the create_checklist method."""

    def test_create_checklist_basic(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a checklist file with empty list."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)

            result = create_checklist(task_id)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = json.load(f)
            assert content == []

    def test_create_checklist_with_data(
        self,
        temp_dir: Path,
        sample_investigation_content: str,
        sample_solution_plan_content: str,
        sample_checklist: list[dict[str, Any]],
    ) -> None:
        """Test creating a checklist file with data."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)

            result = create_checklist(task_id, sample_checklist)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert os.path.exists(expected_path)
            assert result == f"Created {expected_path}"

            with open(expected_path) as f:
                content = json.load(f)
            assert content == sample_checklist

    def test_create_checklist_without_solution_plan(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test that create_checklist fails without solution plan."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create only investigation
            create_investigation(task_id, sample_investigation_content)

            with pytest.raises(
                ValueError,
                match="Cannot create CHECKLIST.json without SOLUTION_PLAN.md",
            ):
                create_checklist(task_id)

    def test_create_checklist_invalid_schema(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that create_checklist validates schema."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)

            # Invalid checklist (missing required fields)
            invalid_checklist = [{"label": "test"}]  # missing status

            with pytest.raises(ValidationError):
                create_checklist(task_id, cast(list[dict[str, Any]], invalid_checklist))


class TestUpdateChecklist:
    """Test the update_checklist method."""

    def test_update_checklist_basic(
        self,
        temp_dir: Path,
        sample_investigation_content: str,
        sample_solution_plan_content: str,
        sample_checklist: list[dict[str, Any]],
    ) -> None:
        """Test updating an existing checklist."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)
            create_checklist(task_id, sample_checklist)

            # Update checklist
            updated_checklist = [{"label": "Updated task", "status": "done", "notes": "Completed"}]

            result = update_checklist(task_id, updated_checklist)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert result == f"Updated {expected_path}"

            with open(expected_path) as f:
                content = json.load(f)
            assert content == updated_checklist

    def test_update_checklist_file_not_found(self, temp_dir: Path) -> None:
        """Test that update_checklist fails when file doesn't exist."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            checklist = [{"label": "test", "status": "pending"}]

            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                update_checklist(task_id, checklist)

    def test_update_checklist_invalid_schema(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that update_checklist validates schema."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)
            create_checklist(task_id, [])

            # Invalid checklist
            invalid_checklist = [{"label": "test"}]  # missing status

            with pytest.raises(ValidationError):
                update_checklist(task_id, cast(list[dict[str, Any]], invalid_checklist))


class TestListTaskResources:
    """Test the list_task_resources method."""

    def test_list_task_resources_empty(self, temp_dir: Path) -> None:
        """Test listing resources when no tasks exist."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            resources = list_task_resources_sync()
            assert resources == []

    def test_list_task_resources_nonexistent_base_dir(self, temp_dir: Path) -> None:
        """Test listing resources when base directory doesn't exist."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / "nonexistent")):
            resources = list_task_resources_sync()
            assert resources == []

    def test_list_task_resources_with_tasks(
        self,
        temp_dir: Path,
        sample_investigation_content: str,
        sample_solution_plan_content: str,
        sample_checklist: list[dict[str, Any]],
    ) -> None:
        """Test listing resources with existing tasks."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create all task files
            create_investigation(task_id, sample_investigation_content)
            create_solution_plan(task_id, sample_solution_plan_content)
            create_checklist(task_id, sample_checklist)

            resources = list_task_resources_sync()

            # Should have 3 resources
            assert len(resources) == 3

            # Check URIs
            uris = [str(resource.uri) for resource in resources]
            expected_uris = [
                f"task://{task_id}/INVESTIGATION.md",
                f"task://{task_id}/SOLUTION_PLAN.md",
                f"task://{task_id}/CHECKLIST.json",
            ]
            for expected_uri in expected_uris:
                assert expected_uri in uris

            # Check resource properties
            for resource in resources:
                assert resource.uri is not None
                assert resource.name is not None
                assert resource.mimeType is not None

    def test_list_task_resources_partial_files(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test listing resources when only some files exist."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create only investigation
            create_investigation(task_id, sample_investigation_content)

            resources = list_task_resources_sync()

            # Should have only 1 resource
            assert len(resources) == 1
            assert str(resources[0].uri) == f"task://{task_id}/INVESTIGATION.md"

    def test_list_task_resources_ignores_non_directories(self, temp_dir: Path) -> None:
        """Test that list_task_resources ignores non-directory files in base dir."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            base_dir = Path(temp_dir / ".tasks")
            base_dir.mkdir()

            # Create a file (not directory) in base dir
            (base_dir / "not-a-task").write_text("not a task")

            resources = list_task_resources_sync()
            assert resources == []


class TestChecklistSchema:
    """Test the CHECKLIST_SCHEMA validation."""

    def test_valid_checklist_items(self):
        """Test that valid checklist items pass validation."""
        valid_items = [
            {"label": "Task 1", "status": "pending"},
            {"label": "Task 2", "status": "in-progress", "notes": "Working on it"},
            {"label": "Task 3", "status": "done", "notes": None},
        ]

        for item in valid_items:
            # Should not raise ValidationError
            from jsonschema import validate

            validate(instance=item, schema=cast(dict[str, Any], CHECKLIST_SCHEMA["items"]))

    def test_invalid_checklist_items(self):
        """Test that invalid checklist items fail validation."""
        from jsonschema import validate

        invalid_items = [
            {"label": "Task 1"},  # missing status
            {"status": "pending"},  # missing label
            {"label": "Task 1", "status": "invalid"},  # invalid status
            {"label": "Task 1", "status": "pending", "extra": "field"},  # extra field
        ]

        for item in invalid_items:
            with pytest.raises(ValidationError):
                validate(instance=item, schema=cast(dict[str, Any], CHECKLIST_SCHEMA["items"]))

    def test_valid_status_values(self):
        """Test that only valid status values are accepted."""
        from jsonschema import validate

        valid_statuses = ["pending", "in-progress", "done"]
        for status in valid_statuses:
            item = {"label": "Test", "status": status}
            # Should not raise ValidationError
            validate(instance=item, schema=cast(dict[str, Any], CHECKLIST_SCHEMA["items"]))

    def test_invalid_status_values(self):
        """Test that invalid status values are rejected."""
        from jsonschema import validate

        invalid_statuses = ["completed", "started", "finished", "todo"]
        for status in invalid_statuses:
            item = {"label": "Test", "status": status}
            with pytest.raises(ValidationError):
                validate(instance=item, schema=cast(dict[str, Any], CHECKLIST_SCHEMA["items"]))
