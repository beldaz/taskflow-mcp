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
    add_checklist_item,
    read_checklist,
    read_investigation,
    read_solution_plan,
    remove_checklist_item,
    set_checklist_item_status,
    task_path,
    write_checklist,
    write_investigation,
    write_solution_plan,
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


class TestWriteInvestigation:
    """Test the write_investigation method."""

    def test_create_investigation_basic(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test creating an investigation file with default content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            result = write_investigation(task_id)

            expected_path = task_path(task_id, "INVESTIGATION.md")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == "# Investigation\n\n"

    def test_create_investigation_with_content(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test creating an investigation file with custom content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            result = write_investigation(task_id, sample_investigation_content)

            expected_path = task_path(task_id, "INVESTIGATION.md")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == sample_investigation_content

    def test_create_investigation_creates_directory(self, temp_dir: Path) -> None:
        """Test that create_investigation creates the task directory."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "nested/task"
            write_investigation(task_id)

            task_dir = os.path.dirname(task_path(task_id, "INVESTIGATION.md"))
            assert os.path.exists(task_dir)
            assert os.path.isdir(task_dir)


class TestWriteSolutionPlan:
    """Test the write_solution_plan method."""

    def test_create_solution_plan_basic(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a solution plan file with default content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # First write investigation (required)
            write_investigation(task_id, sample_investigation_content)

            result = write_solution_plan(task_id)

            expected_path = task_path(task_id, "SOLUTION_PLAN.md")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == "# Solution Plan\n\n"

    def test_create_solution_plan_with_content(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a solution plan file with custom content."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # First write investigation (required)
            write_investigation(task_id, sample_investigation_content)

            result = write_solution_plan(task_id, sample_solution_plan_content)

            expected_path = task_path(task_id, "SOLUTION_PLAN.md")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = f.read()
            assert content == sample_solution_plan_content

    def test_create_solution_plan_without_investigation(self, temp_dir: Path) -> None:
        """Test that write_solution_plan fails without investigation."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            with pytest.raises(ValueError, match="Cannot write SOLUTION_PLAN.md without INVESTIGATION.md"):
                write_solution_plan(task_id)


class TestWriteChecklist:
    """Test the write_checklist method."""

    def test_create_checklist_basic(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test creating a checklist file with empty list."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)

            result = write_checklist(task_id)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

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
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)

            result = write_checklist(task_id, sample_checklist)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert os.path.exists(expected_path)
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = json.load(f)
            assert content == sample_checklist

    def test_create_checklist_without_solution_plan(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test that write_checklist fails without solution plan."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create only investigation
            write_investigation(task_id, sample_investigation_content)

            with pytest.raises(ValueError, match="Cannot write CHECKLIST.json without SOLUTION_PLAN.md"):
                write_checklist(task_id)

    def test_create_checklist_invalid_schema(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that write_checklist validates schema."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)

            # Invalid checklist (missing required fields)
            invalid_checklist = [{"label": "test"}]  # missing status

            with pytest.raises(ValidationError):
                write_checklist(task_id, cast(list[dict[str, Any]], invalid_checklist))


class TestChecklistOperations:
    """Test granular checklist operations and overwrites."""

    def test_update_checklist_basic(
        self,
        temp_dir: Path,
        sample_investigation_content: str,
        sample_solution_plan_content: str,
        sample_checklist: list[dict[str, Any]],
    ) -> None:
        """Test overwriting checklist and then granular ops."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, sample_checklist)

            # Overwrite checklist
            updated_checklist = [{"label": "Updated task", "status": "done", "notes": "Completed"}]

            result = write_checklist(task_id, updated_checklist)

            expected_path = task_path(task_id, "CHECKLIST.json")
            assert result == f"Wrote {expected_path}"

            with open(expected_path) as f:
                content = json.load(f)
            assert content == updated_checklist

            # Granular: add item
            add_checklist_item(task_id, "New Task")
            data = json.loads(read_checklist(task_id))
            assert any(i["label"] == "New Task" and i["status"] == "pending" for i in data)

            # Granular: set status and notes
            set_checklist_item_status(task_id, "New Task", "in-progress", "Working")
            data = json.loads(read_checklist(task_id))
            target = next(i for i in data if i["label"] == "New Task")
            assert target["status"] == "in-progress"
            assert target.get("notes") == "Working"

            # Granular: remove item
            remove_checklist_item(task_id, "New Task")
            data = json.loads(read_checklist(task_id))
            assert all(i["label"] != "New Task" for i in data)

    def test_granular_ops_require_existing_checklist(self, temp_dir: Path) -> None:
        """Granular ops should fail if checklist is missing."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"
            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                add_checklist_item(task_id, "X")
            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                set_checklist_item_status(task_id, "X", "pending")
            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                remove_checklist_item(task_id, "X")

    def test_add_checklist_item_duplicate_label(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that adding duplicate checklist item labels raises ValueError."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [{"label": "Existing Task", "status": "pending"}])

            # Try to add item with duplicate label
            with pytest.raises(ValueError, match="Checklist item already exists with this label"):
                add_checklist_item(task_id, "Existing Task")

    def test_set_checklist_item_status_invalid_status(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that setting invalid status values raises ValueError."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [{"label": "Test Task", "status": "pending"}])

            # Try to set invalid status
            with pytest.raises(ValueError, match="Invalid status; must be one of: pending, in-progress, done"):
                set_checklist_item_status(task_id, "Test Task", "invalid-status")

    def test_set_checklist_item_status_nonexistent_item(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that updating status for non-existent item raises FileNotFoundError."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [{"label": "Existing Task", "status": "pending"}])

            # Try to update non-existent item
            with pytest.raises(FileNotFoundError, match="Checklist item not found"):
                set_checklist_item_status(task_id, "Non-existent Task", "in-progress")

    def test_remove_checklist_item_nonexistent_item(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that removing non-existent item raises FileNotFoundError."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [{"label": "Existing Task", "status": "pending"}])

            # Try to remove non-existent item
            with pytest.raises(FileNotFoundError, match="Checklist item not found"):
                remove_checklist_item(task_id, "Non-existent Task")

    def test_write_checklist_invalid_schema(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test that write_checklist validates schema on overwrite."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "test-task"

            # Create required files and initial checklist
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [])

            # Invalid checklist
            invalid_checklist = [{"label": "test"}]  # missing status

            with pytest.raises(ValidationError):
                write_checklist(task_id, cast(list[dict[str, Any]], invalid_checklist))


class TestReadingHelpers:
    """Test read_* helpers."""

    def test_read_investigation_and_solution_and_checklist(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "task-1"
            write_investigation(task_id, sample_investigation_content)
            write_solution_plan(task_id, sample_solution_plan_content)
            write_checklist(task_id, [])

            assert read_investigation(task_id) == sample_investigation_content
            assert read_solution_plan(task_id) == sample_solution_plan_content
            assert json.loads(read_checklist(task_id)) == []

    def test_read_investigation_file_not_found(self, temp_dir: Path) -> None:
        """Test that read_investigation raises FileNotFoundError for non-existent files."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "non-existent-task"

            with pytest.raises(FileNotFoundError, match="INVESTIGATION.md not found"):
                read_investigation(task_id)

    def test_read_solution_plan_file_not_found(self, temp_dir: Path) -> None:
        """Test that read_solution_plan raises FileNotFoundError for non-existent files."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "non-existent-task"

            with pytest.raises(FileNotFoundError, match="SOLUTION_PLAN.md not found"):
                read_solution_plan(task_id)

    def test_read_checklist_file_not_found(self, temp_dir: Path) -> None:
        """Test that read_checklist raises FileNotFoundError for non-existent files."""
        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            task_id = "non-existent-task"

            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                read_checklist(task_id)


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


class TestAsyncFunctions:
    """Test the async server functions."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """Test the async list_tools function."""
        from taskflow_mcp.server import list_tools

        tools = await list_tools()

        # Should have 9 tools
        assert len(tools) == 9

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "write_investigation",
            "write_solution_plan",
            "write_checklist",
            "read_investigation",
            "read_solution_plan",
            "read_checklist",
            "add_checklist_item",
            "set_checklist_item_status",
            "remove_checklist_item",
        ]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_call_tool_write_investigation(self, temp_dir: Path) -> None:
        """Test calling the write_investigation tool."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            arguments = {"task_id": "test-task", "content": "Custom investigation content"}

            result = await call_tool("write_investigation", arguments)  # type: ignore

            assert len(result) == 1  # type: ignore
            assert result[0].type == "text"  # type: ignore
            assert "Wrote" in result[0].text  # type: ignore
            assert "test-task" in result[0].text  # type: ignore

    @pytest.mark.asyncio
    async def test_call_tool_write_solution_plan(self, temp_dir: Path, sample_investigation_content: str) -> None:
        """Test calling the write_solution_plan tool."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            # First write investigation (required)
            write_investigation("test-task", sample_investigation_content)

            arguments = {"task_id": "test-task", "content": "Custom solution plan content"}

            result = await call_tool("write_solution_plan", arguments)  # type: ignore

            assert len(result) == 1  # type: ignore
            assert result[0].type == "text"  # type: ignore
            assert "Wrote" in result[0].text  # type: ignore

    @pytest.mark.asyncio
    async def test_call_tool_write_checklist(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test calling the write_checklist tool."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            # Create required files
            write_investigation("test-task", sample_investigation_content)
            write_solution_plan("test-task", sample_solution_plan_content)

            arguments = {"task_id": "test-task", "checklist": [{"label": "Test task", "status": "pending"}]}

            result = await call_tool("write_checklist", arguments)  # type: ignore

            assert len(result) == 1  # type: ignore
            assert result[0].type == "text"  # type: ignore
            assert "Wrote" in result[0].text  # type: ignore

    @pytest.mark.asyncio
    async def test_call_tool_granular_checklist(
        self, temp_dir: Path, sample_investigation_content: str, sample_solution_plan_content: str
    ) -> None:
        """Test calling granular checklist tools."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            # Create required files and initial checklist
            write_investigation("test-task", sample_investigation_content)
            write_solution_plan("test-task", sample_solution_plan_content)
            write_checklist("test-task", [])

            # add
            result = await call_tool("add_checklist_item", {"task_id": "test-task", "task_label": "X"})  # type: ignore
            assert result[0].type == "text"  # type: ignore
            # set
            result = await call_tool(
                "set_checklist_item_status",
                {"task_id": "test-task", "task_label": "X", "status": "in-progress", "notes": "n"},
            )  # type: ignore
            assert result[0].type == "text"  # type: ignore
            # remove
            result = await call_tool("remove_checklist_item", {"task_id": "test-task", "task_label": "X"})  # type: ignore
            assert result[0].type == "text"  # type: ignore

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self) -> None:
        """Test calling an unknown tool."""
        from taskflow_mcp.server import call_tool

        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_read_investigation_file_not_found(self, temp_dir: Path) -> None:
        """Test that MCP tool call for read_investigation raises FileNotFoundError."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            arguments = {"task_id": "non-existent-task"}

            with pytest.raises(FileNotFoundError, match="INVESTIGATION.md not found"):
                await call_tool("read_investigation", arguments)

    @pytest.mark.asyncio
    async def test_call_tool_read_solution_plan_file_not_found(self, temp_dir: Path) -> None:
        """Test that MCP tool call for read_solution_plan raises FileNotFoundError."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            arguments = {"task_id": "non-existent-task"}

            with pytest.raises(FileNotFoundError, match="SOLUTION_PLAN.md not found"):
                await call_tool("read_solution_plan", arguments)

    @pytest.mark.asyncio
    async def test_call_tool_read_checklist_file_not_found(self, temp_dir: Path) -> None:
        """Test that MCP tool call for read_checklist raises FileNotFoundError."""
        from taskflow_mcp.server import call_tool

        with patch("taskflow_mcp.server.BASE_DIR", str(temp_dir / ".tasks")):
            arguments = {"task_id": "non-existent-task"}

            with pytest.raises(FileNotFoundError, match="CHECKLIST.json not found"):
                await call_tool("read_checklist", arguments)

    # Resource-based endpoints removed; no tests needed for them.
