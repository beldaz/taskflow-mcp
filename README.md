# taskflow-mcp

An MCP server that manages per-activity task folders in a code repository.

Each activity lives under `.tasks/{id}/` with:
- `INVESTIGATION.md` (root cause analysis)
- `SOLUTION_PLAN.md` (architecture/design proposal)
- `CHECKLIST.json` (implementation tasks with status)

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
