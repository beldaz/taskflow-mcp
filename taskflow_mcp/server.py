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
from typing import Any

from jsonschema import validate
from jsonschema.validators import Draft202012Validator
from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

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
        Full file path: .tasks/{task_id}/{filename}
    """
    return os.path.join(BASE_DIR, task_id, filename)


# ---------------- Resource Providers ----------------


def list_task_resources_sync() -> list[Resource]:
    """Synchronously discover and list all available task resources.

    Scans the .tasks directory for all task folders and their documents.
    Only includes files that exist: INVESTIGATION.md, SOLUTION_PLAN.md, CHECKLIST.json.

    Returns:
        List of Resource objects that can be read by AI assistants
    """
    resources: list[Resource] = []
    if not os.path.exists(BASE_DIR):
        return resources
    for task_id in os.listdir(BASE_DIR):
        folder = os.path.join(BASE_DIR, task_id)
        if not os.path.isdir(folder):
            continue
        for fname in ["INVESTIGATION.md", "SOLUTION_PLAN.md", "CHECKLIST.json"]:
            path = os.path.join(folder, fname)
            if os.path.exists(path):
                # Determine MIME type based on file extension
                if fname.endswith(".md"):
                    mime_type = "text/markdown"
                elif fname.endswith(".json"):
                    mime_type = "application/json"
                else:
                    mime_type = "text/plain"

                resources.append(
                    Resource(
                        uri=AnyUrl(f"task://{task_id}/{fname}"),
                        name=fname,
                        mimeType=mime_type,
                        description=f"Task {task_id} - {fname}",
                    )
                )
    return resources


@server.list_resources()
async def list_task_resources() -> list[Resource]:
    """List all available task resources for MCP clients.

    This is the async MCP endpoint that AI assistants use to discover
    what task documents are available to read.

    Returns:
        List of Resource objects representing available task documents
    """
    return list_task_resources_sync()


@server.read_resource()
async def read_task_resource(uri: AnyUrl) -> str:
    """Read the content of a task resource by URI.

    Parses task:// URIs to locate and read task documents.
    URI format: task://{task_id}/{filename}

    Args:
        uri: Resource URI in format 'task://task_id/filename'

    Returns:
        File content as string

    Raises:
        ValueError: If URI format is invalid
        FileNotFoundError: If the requested resource doesn't exist
    """
    uri_str = str(uri)
    if not uri_str.startswith("task://"):
        raise ValueError(f"Invalid resource URI: {uri_str}")

    # Extract task_id and filename from URI
    path_part = uri_str[6:]  # Remove "task://" prefix
    parts = path_part.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid resource URI format: {uri_str}")

    task_id, filename = parts
    path = task_path(task_id, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Resource not found: {uri_str}")

    with open(path) as f:
        return f.read()


# ---------------- Creation Methods ----------------


# ---------------- Tool Definitions ----------------


def create_investigation(task_id: str, content: str = "# Investigation\n\n") -> str:
    """Create the initial investigation document for a task.

    This is the first step in the task workflow. Creates INVESTIGATION.md
    where you research and understand the problem before planning solutions.

    Args:
        task_id: Unique identifier for the task
        content: Markdown content for the investigation (defaults to basic template)

    Returns:
        Success message with file path
    """
    path = task_path(task_id, "INVESTIGATION.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


def create_solution_plan(task_id: str, content: str = "# Solution Plan\n\n") -> str:
    """Create a solution plan document for a task.

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
        raise ValueError("Cannot create SOLUTION_PLAN.md without INVESTIGATION.md")
    path = task_path(task_id, "SOLUTION_PLAN.md")
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


def create_checklist(task_id: str, checklist: list[dict[str, Any]] | None = None) -> str:
    """Create a structured checklist for task implementation.

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
        raise ValueError("Cannot create CHECKLIST.json without SOLUTION_PLAN.md")
    if checklist is None:
        checklist = []
    validate(instance=checklist, schema=CHECKLIST_SCHEMA, cls=Draft202012Validator)
    path = task_path(task_id, "CHECKLIST.json")
    with open(path, "w") as f:
        json.dump(checklist, f, indent=2)
    return f"Created {path}"


def update_checklist(task_id: str, checklist: list[dict[str, Any]]) -> str:
    """Update an existing checklist with new items or status changes.

    Allows modification of checklist items, typically to update status
    from 'pending' → 'in-progress' → 'done' as work progresses.

    Args:
        task_id: Unique identifier for the task
        checklist: Complete updated list of checklist items
                  Must follow the same schema as create_checklist

    Returns:
        Success message with file path

    Raises:
        FileNotFoundError: If CHECKLIST.json doesn't exist
        ValidationError: If checklist items don't match required schema
    """
    validate(instance=checklist, schema=CHECKLIST_SCHEMA, cls=Draft202012Validator)
    path = task_path(task_id, "CHECKLIST.json")
    if not os.path.exists(path):
        raise FileNotFoundError("CHECKLIST.json not found")
    with open(path, "w") as f:
        json.dump(checklist, f, indent=2)
    return f"Updated {path}"


# Register tools with the server
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools for task management.

    Returns the four main tools that AI assistants can use to manage
    the structured task workflow: create_investigation, create_solution_plan,
    create_checklist, and update_checklist.

    Returns:
        List of Tool objects with their schemas and descriptions
    """

    return [
        Tool(
            name="create_investigation",
            description="Create an investigation document for a task",
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
            name="create_solution_plan",
            description="Create a solution plan document for a task",
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
            name="create_checklist",
            description="Create a checklist for a task",
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
            name="update_checklist",
            description="Update an existing checklist for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The task ID"},
                    "checklist": {
                        "type": "array",
                        "description": "The updated checklist items",
                    },
                },
                "required": ["task_id", "checklist"],
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

    if name == "create_investigation":
        result = create_investigation(
            task_id=arguments["task_id"],
            content=arguments.get("content", "# Investigation\n\n"),
        )
    elif name == "create_solution_plan":
        result = create_solution_plan(
            task_id=arguments["task_id"],
            content=arguments.get("content", "# Solution Plan\n\n"),
        )
    elif name == "create_checklist":
        result = create_checklist(task_id=arguments["task_id"], checklist=arguments.get("checklist", []))
    elif name == "update_checklist":
        result = update_checklist(task_id=arguments["task_id"], checklist=arguments["checklist"])
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
