# TaskFlow MCP Server

A Model Context Protocol (MCP) server that provides structured task management capabilities for AI-assisted development workflows. TaskFlow enforces a logical progression through complex development tasks, ensuring thorough investigation, planning, and execution tracking.

## Overview

TaskFlow implements a three-phase workflow for managing development tasks:

1. **INVESTIGATION.md** - Research and understand the problem
2. **SOLUTION_PLAN.md** - Plan how to solve the problem (requires investigation)
3. **CHECKLIST.json** - Break down solution into actionable items (requires solution plan)

Each task is organized in its own folder under `.tasks/{task_id}/` with a unique identifier, providing clear separation and organization of work.

### Checklist Schema

While `INVESTIGATION.md` and `SOLUTION_PLAN.md` can be markdown documents with any structure, `CHECKLIST.json` is strictly a list of items with a completion status.

```json
[
  {
    "label": "string (required)",
    "status": "pending|in-progress|done (required)",
    "notes": "string|null (optional)"
  }
]
```

## Key Features

- **Enforced Workflow Progression**: Tasks must follow the investigation → solution → checklist sequence
- **JSON Schema Validation**: Checklist items are validated against a strict schema
- **Status Tracking**: Structured status tracking (pending, in-progress, done) for checklist items
- **MCP Integration**: Full Model Context Protocol support for seamless AI assistant integration

> **📋 For detailed technical specifications, error handling, and complete API behavior, see [SPECIFICATION.md](SPECIFICATION.md)**

## Installation

Install with [uv](https://github.com/astral-sh/uv):

```bash
uv add git+https://github.com/yourname/taskflow-mcp.git
```

## Usage

### Basic Usage

Run the MCP server in the root of your code repository:
```bash
taskflow-mcp
```

### Working Directory Configuration

By default, TaskFlow creates the `.tasks` directory in the current working directory. To specify a different project directory, you have several options:

**Option 1: Using the start script (recommended)**
```bash
# For current directory
./start-mcp.sh

# For a specific project directory
./start-mcp.sh /path/to/your/project
```

**Option 2: Using environment variable**
```bash
# For a specific project directory
TASKFLOW_WORKING_DIR=/path/to/your/project taskflow-mcp
```

### Claude Desktop Integration

Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "taskflow": {
      "command": "taskflow-mcp",
      "args": [],
      "env": {
        "TASKFLOW_WORKING_DIR": "/path/to/your/project"
      }
    }
  }
}
```

Configure Claude Code (VS Code / JetBrains) to connect:
```json
{
  "mcpServers": {
    "taskflow": {
      "command": "taskflow-mcp",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Alternative Installation

```bash
claude mcp add taskflow '<path to taskflow-mcp local folder>/start-mcp.sh' -s user
```

## Available Tools

The TaskFlow server provides a clean, consistent API for AI agents:

### Write Tools (Create or Update)
- `write_investigation(task_id, content)` - Write investigation document
- `write_solution_plan(task_id, content)` - Write solution plan document  
- `write_checklist(task_id, checklist)` - Write checklist document

### Read Tools
- `read_investigation(task_id)` - Read investigation document
- `read_solution_plan(task_id)` - Read solution plan document
- `read_checklist(task_id)` - Read checklist document

### Checklist Operations (granular)
- `add_checklist_item(task_id, task_label)` - Append one item (item_id is the item's label)
- `set_checklist_item_status(task_id, task_label, status, notes?)` - Update one item's status/notes
- `remove_checklist_item(task_id, task_label)` - Remove one item

### Benefits of This Design
- **Consistency**: All operations follow the same `write_*`/`read_*` pattern
- **Simplicity**: No distinction between create vs. update operations
- **Idempotency**: Writing the same content multiple times is safe
- **Clean Logic**: Agents don't need to check if documents exist first

## API Reference

### Tool Parameters

**Write Tools**:
- `write_investigation(task_id, content)` - Write investigation document
- `write_solution_plan(task_id, content)` - Write solution plan (requires investigation)
- `write_checklist(task_id, checklist)` - Write checklist (requires solution plan)

**Read Tools**:
- `read_investigation(task_id)` - Read investigation document
- `read_solution_plan(task_id)` - Read solution plan document
- `read_checklist(task_id)` - Read checklist document

**Checklist Operations**:
- `add_checklist_item(task_id, task_label)` - Append one item (item_id is item's label)
- `set_checklist_item_status(task_id, task_label, status, notes?)` - Update one item's status/notes
- `remove_checklist_item(task_id, task_label)` - Remove one item


## AI Agent Architecture

TaskFlow is designed to work with specialized AI agents, each optimized for a specific phase of the development workflow. This approach ensures thoroughness and prevents agents from skipping critical steps. See [AGENT_DESCRIPTIONS.md] for suggested specifications to provide to a agent generation wizard such as Claude Code.


## Development

Run tests:
```bash
uv run pytest
```

Run linting:
```bash
uv run ruff check .
uv run pyright
```