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
    return os.path.join(BASE_DIR, task_id, filename)


# ---------------- Resource Providers ----------------


def list_task_resources_sync() -> list[Resource]:
    """Synchronous version of list_task_resources for testing."""
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
    """List all tasks and their artifacts."""
    return list_task_resources_sync()


@server.read_resource()
async def read_task_resource(uri: AnyUrl) -> str:
    """Read the content of a task resource."""
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
    path = task_path(task_id, "INVESTIGATION.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


def create_solution_plan(task_id: str, content: str = "# Solution Plan\n\n") -> str:
    inv_path = task_path(task_id, "INVESTIGATION.md")
    if not os.path.exists(inv_path):
        raise ValueError("Cannot create SOLUTION_PLAN.md without INVESTIGATION.md")
    path = task_path(task_id, "SOLUTION_PLAN.md")
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


def create_checklist(task_id: str, checklist: list[dict[str, Any]] | None = None) -> str:
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
    """List available tools."""

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
    """Handle tool calls."""

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
