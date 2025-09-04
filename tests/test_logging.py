"""Tests for tool action logging functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from taskflow_mcp.server import call_tool


class TestToolActionLogging:
    """Test the tool action logging functionality."""

    @pytest.mark.asyncio
    async def test_log_file_creation(self) -> None:
        """Test that log file is created at .tasks/tool_actions.log."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Patch WORKING_DIR to use our temp directory
            with patch("taskflow_mcp.server.WORKING_DIR", str(temp_path)):
                # Call a tool to trigger logging
                await call_tool("write_investigation", {"task_id": "test-task", "content": "Test content"})

                # Check that log file was created
                log_file = temp_path / ".tasks" / "tool_actions.log"
                assert log_file.exists(), "Log file should be created at .tasks/tool_actions.log"

    @pytest.mark.asyncio
    async def test_log_entry_format(self) -> None:
        """Test that log entries contain required fields in JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch("taskflow_mcp.server.WORKING_DIR", str(temp_path)):
                # Call a tool to trigger logging
                await call_tool("write_investigation", {"task_id": "test-task", "content": "Test content"})

                # Read and parse log file
                log_file = temp_path / ".tasks" / "tool_actions.log"
                with open(log_file, "r") as f:
                    log_line = f.read().strip()

                # Parse the log entry (format: timestamp - json)
                parts = log_line.split(" - ", 1)
                assert len(parts) == 2, "Log entry should have timestamp and JSON parts"

                log_entry = json.loads(parts[1])

                # Check required fields
                assert "tool" in log_entry, "Log entry should contain 'tool' field"
                assert "task_id" in log_entry, "Log entry should contain 'task_id' field"
                assert "timestamp" in log_entry, "Log entry should contain 'timestamp' field"
                assert "arguments" in log_entry, "Log entry should contain 'arguments' field"
                assert "result" in log_entry, "Log entry should contain 'result' field"

                # Check specific values
                assert log_entry["tool"] == "write_investigation"
                assert log_entry["task_id"] == "test-task"
                assert log_entry["arguments"] == {"task_id": "test-task", "content": "Test content"}
                assert "Wrote" in log_entry["result"]

    @pytest.mark.asyncio
    async def test_all_tools_logged(self) -> None:
        """Test that all 9 MCP tools are logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch("taskflow_mcp.server.WORKING_DIR", str(temp_path)):
                # Create required files for dependent tools
                await call_tool("write_investigation", {"task_id": "test-task", "content": "Test"})
                await call_tool("write_solution_plan", {"task_id": "test-task", "content": "Test"})
                await call_tool("write_checklist", {"task_id": "test-task", "checklist": []})

                # Test all 9 tools
                tools_to_test = [
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

                # Call each tool
                for tool in tools_to_test:
                    if tool in ["add_checklist_item", "set_checklist_item_status", "remove_checklist_item"]:
                        # These need specific arguments
                        if tool == "add_checklist_item":
                            await call_tool(tool, {"task_id": "test-task", "task_label": "test-item"})
                        elif tool == "set_checklist_item_status":
                            await call_tool(
                                tool, {"task_id": "test-task", "task_label": "test-item", "status": "pending"}
                            )
                        elif tool == "remove_checklist_item":
                            await call_tool(tool, {"task_id": "test-task", "task_label": "test-item"})
                    else:
                        # These use the same arguments
                        await call_tool(tool, {"task_id": "test-task"})

                # Read log file and check all tools were logged
                log_file = temp_path / ".tasks" / "tool_actions.log"
                with open(log_file, "r") as f:
                    log_lines = f.readlines()

                # Should have at least 12 log entries (3 setup + 9 tool calls)
                assert len(log_lines) >= 12, f"Expected at least 12 log entries, got {len(log_lines)}"

                # Check that all tools appear in the log
                logged_tools = set()
                for line in log_lines:
                    if " - " in line:
                        json_part = line.split(" - ", 1)[1]
                        try:
                            log_entry = json.loads(json_part)
                            if "tool" in log_entry:
                                logged_tools.add(log_entry["tool"])
                        except json.JSONDecodeError:
                            continue

                for tool in tools_to_test:
                    assert tool in logged_tools, f"Tool {tool} should be logged"

    @pytest.mark.asyncio
    async def test_logging_timing(self) -> None:
        """Test that logging occurs after tool execution but before returning results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch("taskflow_mcp.server.WORKING_DIR", str(temp_path)):
                # Call a tool
                result = await call_tool("write_investigation", {"task_id": "test-task", "content": "Test"})

                # Check that log file exists and contains the result
                log_file = temp_path / ".tasks" / "tool_actions.log"
                assert log_file.exists(), "Log file should exist after tool call"

                with open(log_file, "r") as f:
                    log_content = f.read()

                # The log should contain the result that was returned
                assert result[0].text in log_content, "Log should contain the tool result"

                # The log should contain the tool name and task_id
                assert "write_investigation" in log_content
                assert "test-task" in log_content

    @pytest.mark.asyncio
    async def test_log_file_append_mode(self) -> None:
        """Test that log entries are appended to existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch("taskflow_mcp.server.WORKING_DIR", str(temp_path)):
                # First tool call
                await call_tool("write_investigation", {"task_id": "task1", "content": "Test1"})

                # Second tool call
                await call_tool("write_investigation", {"task_id": "task2", "content": "Test2"})

                # Check that both entries are in the log file
                log_file = temp_path / ".tasks" / "tool_actions.log"
                with open(log_file, "r") as f:
                    log_lines = f.readlines()

                assert len(log_lines) >= 2, "Should have at least 2 log entries"
                log_content = "".join(log_lines)
                assert "task1" in log_content, "First tool call should be logged"
                assert "task2" in log_content, "Second tool call should be logged"
