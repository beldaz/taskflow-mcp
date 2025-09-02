import os
import json
from jsonschema import validate, ValidationError
from mcp.server import Server, Resource

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


def task_path(task_id, filename):
    return os.path.join(BASE_DIR, task_id, filename)


# ---------------- Resource Providers ----------------


@server.resource("task")
def list_task_resources() -> list[Resource]:
    """List all tasks and their artifacts."""
    resources = []
    if not os.path.exists(BASE_DIR):
        return resources
    for task_id in os.listdir(BASE_DIR):
        folder = os.path.join(BASE_DIR, task_id)
        if not os.path.isdir(folder):
            continue
        for fname in ["INVESTIGATION.md", "SOLUTION_PLAN.md", "CHECKLIST.json"]:
            path = os.path.join(folder, fname)
            if os.path.exists(path):
                resources.append(
                    Resource(uri=f"task://{task_id}/{fname}", text=open(path).read())
                )
    return resources


# ---------------- Creation Methods ----------------


@server.method
def create_investigation(task_id: str, content: str = "# Investigation\n\n") -> str:
    path = task_path(task_id, "INVESTIGATION.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


@server.method
def create_solution_plan(task_id: str, content: str = "# Solution Plan\n\n") -> str:
    inv_path = task_path(task_id, "INVESTIGATION.md")
    if not os.path.exists(inv_path):
        raise ValueError("Cannot create SOLUTION_PLAN.md without INVESTIGATION.md")
    path = task_path(task_id, "SOLUTION_PLAN.md")
    with open(path, "w") as f:
        f.write(content)
    return f"Created {path}"


@server.method
def create_checklist(task_id: str, checklist=None) -> str:
    sol_path = task_path(task_id, "SOLUTION_PLAN.md")
    if not os.path.exists(sol_path):
        raise ValueError("Cannot create CHECKLIST.json without SOLUTION_PLAN.md")
    if checklist is None:
        checklist = []
    validate(instance=checklist, schema=CHECKLIST_SCHEMA)
    path = task_path(task_id, "CHECKLIST.json")
    with open(path, "w") as f:
        json.dump(checklist, f, indent=2)
    return f"Created {path}"


@server.method
def update_checklist(task_id: str, checklist) -> str:
    validate(instance=checklist, schema=CHECKLIST_SCHEMA)
    path = task_path(task_id, "CHECKLIST.json")
    if not os.path.exists(path):
        raise FileNotFoundError("CHECKLIST.json not found")
    with open(path, "w") as f:
        json.dump(checklist, f, indent=2)
    return f"Updated {path}"


# ---------------- Entrypoint ----------------


def main():
    server.run()


if __name__ == "__main__":
    main()
