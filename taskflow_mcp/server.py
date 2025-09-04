"""TaskFlow MCP Server - Structured Task Management System

This module implements a Model Context Protocol (MCP) server that provides structured
task management capabilities. It enforces a logical workflow for complex tasks:

1. INVESTIGATION.md - Research and understand the problem
2. SOLUTION_PLAN.md - Plan how to solve the problem (requires investigation)
3. CHECKLIST.json - Break down solution into actionable items (requires solution plan)

Each task is organized in its own folder under .tasks/ with a unique task ID.
The server provides tools for creating and managing these documents, with built-in
validation to ensure data consistency and workflow compliance.

Key Features:
- Enforced workflow progression (investigation → solution → checklist)
- JSON schema validation for checklist items
- Resource management for AI assistant integration
- Structured status tracking (pending, in-progress, done)
"""

import json
import os
import sys
from typing import Any

from jsonschema import validate
from jsonschema.validators import Draft202012Validator
from mcp.server import Server
from mcp.types import TextContent, Tool

# Get working directory from environment variable, default to current directory
WORKING_DIR = os.environ.get("TASKFLOW_WORKING_DIR", os.getcwd())
BASE_DIR = ".tasks"

CHECKLIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "label": {"type": "string"},
            "status": {"enum": ["pending", "in-progress", "done"]},
            "notes": {"type": ["string", "null"]},
        },
        "required": ["label", "status"],
        "additionalProperties": False,
    },
}

server = Server(name="taskflow-mcp")


def task_path(task_id: str, filename: str) -> str:
    """Generate the file path for a task document.

    Args:
        task_id: Unique identifier for the task
        filename: Name of the file (e.g., 'INVESTIGATION.md', 'CHECKLIST.json')

    Returns:
        Full file path: {WORKING_DIR}/.tasks/{task_id}/{filename}
    """
    return os.path.join(WORKING_DIR, BASE_DIR, task_id, filename)


# ---------------- Checklist helpers ----------------


def _load_checklist(task_id: str) -> list[dict[str, Any]]:
    path = task_path(task_id, "CHECKLIST.json")
    if not os.path.exists(path):
        raise FileNotFoundError("CHECKLIST.json not found")
    with open(path) as f:
        return json.load(f)


def _save_checklist(task_id: str, checklist: list[dict[str, Any]]) -> None:
    validate(instance=checklist, schema=CHECKLIST_SCHEMA, cls=Draft202012Validator)
    path = task_path(task_id, "CHECKLIST.json")
    with open(path, "w") as f:
        json.dump(checklist, f, indent=2)


# ---------------- Creation Methods ----------------


# ---------------- Tool Definitions ----------------


def write_investigation(task_id: str, content: str = "# Investigation\n\n") -> str:
    """Write the investigation document for a task (create or overwrite).

    This is the first step in the task workflow. Creates INVESTIGATION.md
    where you research and understand the problem before planning solutions.

    Args:
        task_id: Unique identifier for the task
        content: Markdown content for the investigation (defaults to basic template)

    Returns:
        Success message with file path
    """
    print(f"TaskFlow MCP Server: write_investigation called with task_id='{task_id}'", file=sys.stderr)
    path = task_path(task_id, "INVESTIGATION.md")
    print(f"TaskFlow MCP Server: Creating file at path: {path}", file=sys.stderr)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    result = f"Wrote {path}"
    print(f"TaskFlow MCP Server: {result}", file=sys.stderr)
    return result


def write_solution_plan(task_id: str, content: str = "# Solution Plan\n\n") -> str:
    """Write a solution plan document for a task (create or overwrite).

    Second step in the workflow. Creates SOLUTION_PLAN.md where you plan
    how to solve the problem identified in the investigation.

    Args:
        task_id: Unique identifier for the task
        content: Markdown content for the solution plan (defaults to basic template)

    Returns:
        Success message with file path

    Raises:
        ValueError: If INVESTIGATION.md doesn't exist (enforces workflow order)
    """
    inv_path = task_path(task_id, "INVESTIGATION.md")
    if not os.path.exists(inv_path):
        raise ValueError("Cannot write SOLUTION_PLAN.md without INVESTIGATION.md")
    path = task_path(task_id, "SOLUTION_PLAN.md")
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote {path}"


def write_checklist(task_id: str, checklist: list[dict[str, Any]] | None = None) -> str:
    """Write the structured checklist for task implementation (create or overwrite).

    Final step in the workflow. Creates CHECKLIST.json with actionable items
    derived from the solution plan. Each item has a label, status, and optional notes.

    Args:
        task_id: Unique identifier for the task
        checklist: List of checklist items (defaults to empty list)
                  Each item must have: {'label': str, 'status': str, 'notes': str|None}
                  Valid statuses: 'pending', 'in-progress', 'done'

    Returns:
        Success message with file path

    Raises:
        ValueError: If SOLUTION_PLAN.md doesn't exist (enforces workflow order)
        ValidationError: If checklist items don't match required schema
    """
    sol_path = task_path(task_id, "SOLUTION_PLAN.md")
    if not os.path.exists(sol_path):
        raise ValueError("Cannot write CHECKLIST.json without SOLUTION_PLAN.md")
    if checklist is None:
        checklist = []
    _save_checklist(task_id, checklist)
    return f"Wrote {task_path(task_id, 'CHECKLIST.json')}"


def read_investigation(task_id: str) -> str:
    """Read the investigation document for a task."""
    path = task_path(task_id, "INVESTIGATION.md")
    if not os.path.exists(path):
        raise FileNotFoundError("INVESTIGATION.md not found")
    with open(path) as f:
        return f.read()


def read_solution_plan(task_id: str) -> str:
    """Read the solution plan document for a task."""
    path = task_path(task_id, "SOLUTION_PLAN.md")
    if not os.path.exists(path):
        raise FileNotFoundError("SOLUTION_PLAN.md not found")
    with open(path) as f:
        return f.read()


def read_checklist(task_id: str) -> str:
    """Read the checklist document for a task as a JSON string."""
    path = task_path(task_id, "CHECKLIST.json")
    if not os.path.exists(path):
        raise FileNotFoundError("CHECKLIST.json not found")
    with open(path) as f:
        return f.read()


def add_checklist_item(task_id: str, task_label: str) -> str:
    """Append a single checklist item identified by its label."""
    items = _load_checklist(task_id)
    if any(item.get("label") == task_label for item in items):
        raise ValueError("Checklist item already exists with this label")
    items.append({"label": task_label, "status": "pending", "notes": None})
    _save_checklist(task_id, items)
    return f"Added item '{task_label}' to {task_path(task_id, 'CHECKLIST.json')}"


def set_checklist_item_status(task_id: str, task_label: str, status: str, notes: str | None = None) -> str:
    """Update status (and optional notes) for a single checklist item by label."""
    if status not in {"pending", "in-progress", "done"}:
        raise ValueError("Invalid status; must be one of: pending, in-progress, done")
    items = _load_checklist(task_id)
    for item in items:
        if item.get("label") == task_label:
            item["status"] = status
            if notes is not None:
                item["notes"] = notes
            _save_checklist(task_id, items)
            return f"Updated item '{task_label}' in {task_path(task_id, 'CHECKLIST.json')}"
    raise FileNotFoundError("Checklist item not found")


def remove_checklist_item(task_id: str, task_label: str) -> str:
    """Remove a single checklist item by label."""
    items = _load_checklist(task_id)
    new_items = [it for it in items if it.get("label") != task_label]
    if len(new_items) == len(items):
        raise FileNotFoundError("Checklist item not found")
    _save_checklist(task_id, new_items)
    return f"Removed item '{task_label}' from {task_path(task_id, 'CHECKLIST.json')}"


# Register tools with the server
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools for task management.

    Returns the tools that AI assistants can use to manage the structured
    task workflow using a minimal read/write API with granular checklist edits.

    Returns:
        List of Tool objects with their schemas and descriptions
    """

    return [
        Tool(
            name="write_investigation",
            description="Write the investigation document for a task (create or overwrite)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "content": {
                        "type": "string",
                        "description": "The investigation content",
                        "default": "# Investigation\n\n",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="write_solution_plan",
            description="Write the solution plan document for a task (requires investigation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "content": {
                        "type": "string",
                        "description": "The solution plan content",
                        "default": "# Solution Plan\n\n",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="write_checklist",
            description="Write the checklist document for a task (requires solution plan)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "checklist": {
                        "type": "array",
                        "description": "The checklist items",
                        "default": [],
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="read_investigation",
            description="Read the investigation document for a task",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "The task ID"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="read_solution_plan",
            description="Read the solution plan document for a task",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "The task ID"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="read_checklist",
            description="Read the checklist document for a task",
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "The task ID"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="add_checklist_item",
            description="Add a single checklist item (label acts as item id)",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "task_label": {"type": "string", "description": "Checklist item label (acts as id)"},
                },
                "required": ["task_id", "task_label"],
            },
        ),
        Tool(
            name="set_checklist_item_status",
            description="Update status/notes for one checklist item by label",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "task_label": {"type": "string", "description": "Checklist item label (acts as id)"},
                    "status": {"type": "string", "enum": ["pending", "in-progress", "done"]},
                    "notes": {"type": ["string", "null"], "description": "Optional notes"},
                },
                "required": ["task_id", "task_label", "status"],
            },
        ),
        Tool(
            name="remove_checklist_item",
            description="Remove a single checklist item by label",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "task_label": {"type": "string", "description": "Checklist item label (acts as id)"},
                },
                "required": ["task_id", "task_label"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle incoming tool calls from MCP clients.

    Routes tool calls to the appropriate task management function
    and returns the result as text content for the AI assistant.

    Args:
        name: Name of the tool to call
        arguments: Dictionary of arguments for the tool

    Returns:
        List containing a single TextContent with the operation result

    Raises:
        ValueError: If the tool name is not recognized
    """
    print(f"TaskFlow MCP Server: Tool call received - name='{name}', arguments={arguments}", file=sys.stderr)

    if name == "write_investigation":
        result = write_investigation(
            task_id=arguments["task_id"],
            content=arguments.get("content", "# Investigation\n\n"),
        )
    elif name == "write_solution_plan":
        result = write_solution_plan(
            task_id=arguments["task_id"],
            content=arguments.get("content", "# Solution Plan\n\n"),
        )
    elif name == "write_checklist":
        result = write_checklist(task_id=arguments["task_id"], checklist=arguments.get("checklist", []))
    elif name == "read_investigation":
        result = read_investigation(task_id=arguments["task_id"])  # returns string
    elif name == "read_solution_plan":
        result = read_solution_plan(task_id=arguments["task_id"])  # returns string
    elif name == "read_checklist":
        result = read_checklist(task_id=arguments["task_id"])  # returns JSON string
    elif name == "add_checklist_item":
        result = add_checklist_item(task_id=arguments["task_id"], task_label=arguments["task_label"])
    elif name == "set_checklist_item_status":
        result = set_checklist_item_status(
            task_id=arguments["task_id"],
            task_label=arguments["task_label"],
            status=arguments["status"],
            notes=arguments.get("notes"),
        )
    elif name == "remove_checklist_item":
        result = remove_checklist_item(task_id=arguments["task_id"], task_label=arguments["task_label"])
    else:
        raise ValueError(f"Unknown tool: {name}")

    return [TextContent(type="text", text=result)]


# ---------------- Entrypoint ----------------


def main() -> None:
    """Start the TaskFlow MCP server.

    Initializes and runs the MCP server using stdio communication,
    making it available to AI assistants that support the MCP protocol.
    """
    import asyncio

    from mcp import stdio_server

    # Create .tasks directory and print debug information
    try:
        tasks_path = os.path.join(WORKING_DIR, BASE_DIR)
        os.makedirs(tasks_path, exist_ok=True)
        print(f"TaskFlow MCP Server: Created .tasks directory at {tasks_path}", file=sys.stderr)
        print(f"TaskFlow MCP Server: Working directory: {WORKING_DIR}", file=sys.stderr)
        print(f"TaskFlow MCP Server: Files will be created in: {tasks_path}/{{task_id}}/", file=sys.stderr)
        if WORKING_DIR != os.getcwd():
            print(
                f"TaskFlow MCP Server: Note: Working directory differs from server location ({os.getcwd()})",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"TaskFlow MCP Server: Error creating .tasks directory: {e}", file=sys.stderr)

    async def run_server():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=server.create_initialization_options(),
            )

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
