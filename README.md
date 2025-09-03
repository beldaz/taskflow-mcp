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

## Installation

Install with [uv](https://github.com/astral-sh/uv):

```bash
uv add git+https://github.com/yourname/taskflow-mcp.git
```

## Usage

Run the MCP server in the root of your code repository:
```bash
taskflow-mcp
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

### Specialized Phase-Based Agents

TaskFlow is designed to work with specialized AI agents, each optimized for a specific phase of the development workflow. This approach ensures thoroughness and prevents agents from skipping critical steps.

#### 1. Investigation Agent (`investigator`)

**Purpose**: Deep problem analysis and root cause identification

**Responsibilities**:
- Analyze bug reports, feature requests, and technical issues
- Research existing codebase patterns and similar problems
- Identify affected systems, dependencies, and constraints
- Document technical debt and architectural concerns
- Define clear success criteria and acceptance conditions

**MCP Tools Used**:
- `write_investigation(task_id, content)` - To generate or update key output
- `read_investigation(task_id)` - To access content to be updated

#### 2. Solution Planning Agent (`architect`)

**Purpose**: Design optimal solutions and implementation strategies

**Responsibilities**:
- Design technical solutions based on investigation findings
- Create implementation roadmaps and architectural decisions
- Identify risks and mitigation strategies
- Plan testing and validation approaches
- Define integration and deployment strategies

**MCP Tools Used**:
- `read_investigation(task_id)` - Retrieve context for solution
- `write_solution_plan(task_id, content)` - To generate or update key output
- `read_solution_plan(task_id)` - To access content to be updated

#### 3. Implementation Agent (`implementer`)

**Purpose**: Execute development tasks and manage implementation progress

**Responsibilities**:
- Break down solution plans into actionable tasks
- Implement code changes and features
- Update task status and document progress
- Handle blockers and technical challenges
- Ensure code quality and testing

**MCP Tools Used**:
- `read_solution_plan(task_id)` - Read solution plan
- `read_investigation(task_id)` - Read investigation for context
- `write_checklist(task_id, checklist)` - Create and update implementation tasks
- `add_checklist_item(task_id, task_label)` - Add a single checklist item
- `set_checklist_item_status(task_id, task_label, status, notes?)` - Update status/notes for item of specified label
- `remove_checklist_item(task_id, task_label)` - Remove a specific item 

#### 4. Quality Assurance Agent (`qa-specialist`)

**Purpose**: Ensure code quality, testing, and validation

**Responsibilities**:
- Review implementation against solution plan
- Validate testing coverage and quality
- Perform code reviews and quality checks
- Ensure compliance with standards and requirements
- Document lessons learned and improvements

**MCP Tools Used**:
- `read_investigation(task_id)` - Review investigation document
- `read_solution_plan(task_id)` - Review solution plan
- `read_checklist(task_id)` - Review implementation checklist
- `write_checklist(task_id, checklist)` - Add QA-specific checklist items
- `add_checklist_item(task_id, task_label)`
- `set_checklist_item_status(task_id, task_label, status, notes?)`
- `remove_checklist_item(task_id, task_label)`



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