# TaskFlow MCP Server - Functional Specification

*Based on comprehensive test analysis of the current implementation*

## Overview

TaskFlow is a Model Context Protocol (MCP) server that provides structured task management capabilities for AI-assisted development workflows. The system enforces a three-phase workflow for managing complex development tasks, ensuring thorough investigation, planning, and execution tracking.

## Core Workflow

### Three-Phase Task Management

TaskFlow implements a mandatory three-phase workflow that must be followed in sequence:

1. **Investigation Phase** - Research and understand the problem
2. **Solution Planning Phase** - Plan how to solve the problem (requires investigation)
3. **Implementation Phase** - Break down solution into actionable items (requires solution plan)

*Validated by: [`test_task_dependencies_enforced`](tests/test_integration.py) - confirms that solution plans cannot be created without investigations, and checklists cannot be created without solution plans.*

### File Organization

Each task is organized in its own directory structure under `.tasks/{task_id}/` with three specific files:

- `INVESTIGATION.md` - Markdown document for problem analysis
- `SOLUTION_PLAN.md` - Markdown document for solution planning  
- `CHECKLIST.json` - JSON document for actionable task tracking

*Validated by: [`test_complete_task_workflow`](tests/test_integration.py) - demonstrates the complete file structure and workflow progression.*

## Document Management

### Investigation Documents

**Creation and Writing:**
- Investigation documents can be created with custom content or default template (`# Investigation\n\n`)
- The system automatically creates the necessary directory structure when writing files
- Writing operations are idempotent - overwriting existing content is safe and expected
- All write operations return confirmation messages indicating the file path

*Validated by: [`test_create_investigation_basic`](tests/test_server.py), [`test_create_investigation_with_content`](tests/test_server.py), [`test_create_investigation_creates_directory`](tests/test_server.py)*

**Reading:**
- Investigation documents can be read back exactly as written
- Reading returns the complete file content as a string
- File persistence is guaranteed - content written can always be read back

*Validated by: [`test_read_investigation_and_solution_and_checklist`](tests/test_server.py), [`test_file_persistence`](tests/test_integration.py)*

**Error Handling:**
- Attempting to read non-existent investigation documents raises `FileNotFoundError` with the message "INVESTIGATION.md not found"
- Reading operations fail gracefully when files don't exist, providing clear error messages

*Validated by: [`test_read_investigation_file_not_found`](tests/test_server.py)*

### Solution Plan Documents

**Creation and Writing:**
- Solution plans can be created with custom content or default template (`# Solution Plan\n\n`)
- **Dependency Enforcement:** Solution plans cannot be created without an existing investigation document
- The system validates this dependency and raises a `ValueError` with the message "Cannot write SOLUTION_PLAN.md without INVESTIGATION.md" if attempted
- Writing operations are idempotent and return confirmation messages

*Validated by: [`test_create_solution_plan_basic`](tests/test_server.py), [`test_create_solution_plan_with_content`](tests/test_server.py), [`test_create_solution_plan_without_investigation`](tests/test_server.py)*

**Reading:**
- Solution plan documents can be read back exactly as written
- Reading returns the complete file content as a string

*Validated by: [`test_read_investigation_and_solution_and_checklist`](tests/test_server.py), [`test_file_persistence`](tests/test_integration.py)*

**Error Handling:**
- Attempting to read non-existent solution plan documents raises `FileNotFoundError` with the message "SOLUTION_PLAN.md not found"
- Reading operations fail gracefully when files don't exist, providing clear error messages

*Validated by: [`test_read_solution_plan_file_not_found`](tests/test_server.py)*

### Checklist Documents

**Creation and Writing:**
- Checklists are JSON documents containing an array of task items
- **Dependency Enforcement:** Checklists cannot be created without an existing solution plan document
- The system validates this dependency and raises a `ValueError` with the message "Cannot write CHECKLIST.json without SOLUTION_PLAN.md" if attempted
- Checklists can be created with an empty array or with predefined task items
- Writing operations are idempotent and return confirmation messages

*Validated by: [`test_create_checklist_basic`](tests/test_server.py), [`test_create_checklist_with_data`](tests/test_server.py), [`test_create_checklist_without_solution_plan`](tests/test_server.py)*

**Schema Validation:**
- All checklist items must conform to a strict JSON schema
- Each item must have:
  - `label` (string, required) - The task description
  - `status` (string, required) - Must be one of: "pending", "in-progress", "done"
  - `notes` (string or null, optional) - Additional notes about the task
- Invalid items (missing required fields, invalid status values, extra fields) are rejected with `ValidationError`
- Schema validation applies to both initial creation and overwrite operations

*Validated by: [`test_valid_checklist_items`](tests/test_server.py), [`test_invalid_checklist_items`](tests/test_server.py), [`test_valid_status_values`](tests/test_server.py), [`test_invalid_status_values`](tests/test_server.py), [`test_create_checklist_invalid_schema`](tests/test_server.py), [`test_write_checklist_invalid_schema`](tests/test_server.py)*

**Reading:**
- Checklist documents can be read back as JSON strings
- Reading returns the complete file content that can be parsed as JSON

*Validated by: [`test_read_investigation_and_solution_and_checklist`](tests/test_server.py), [`test_file_persistence`](tests/test_integration.py)*

**Error Handling:**
- Attempting to read non-existent checklist documents raises `FileNotFoundError` with the message "CHECKLIST.json not found"
- Reading operations fail gracefully when files don't exist, providing clear error messages

*Validated by: [`test_read_checklist_file_not_found`](tests/test_server.py)*

## Granular Checklist Operations

### Individual Item Management

The system provides granular operations for managing individual checklist items without overwriting the entire checklist:

**Adding Items:**
- New items can be added to existing checklists using the item's label as the identifier
- Added items default to "pending" status with no notes
- Duplicate labels are not allowed - the system raises a `ValueError` if attempting to add an item with an existing label
- Adding items requires an existing checklist file

*Validated by: [`test_update_checklist_basic`](tests/test_server.py) (add item section), [`test_granular_ops_require_existing_checklist`](tests/test_server.py)*

**Error Handling:**
- Attempting to add a checklist item with a label that already exists raises `ValueError` with the message "Checklist item already exists with this label"
- Duplicate label detection prevents conflicting task identifiers within the same checklist

*Validated by: [`test_add_checklist_item_duplicate_label`](tests/test_server.py)*

**Updating Item Status:**
- Individual items can have their status and notes updated by label
- Valid status values are strictly enforced: "pending", "in-progress", "done"
- Notes can be updated or set to null
- Status updates require an existing checklist file and valid item label

*Validated by: [`test_update_checklist_basic`](tests/test_server.py) (set status section), [`test_granular_ops_require_existing_checklist`](tests/test_server.py)*

**Error Handling:**
- Attempting to set status to invalid values (not "pending", "in-progress", or "done") raises `ValueError` with the message "Invalid status; must be one of: pending, in-progress, done"
- Attempting to update status for a non-existent item label raises `FileNotFoundError` with the message "Checklist item not found"
- Status validation ensures data integrity and prevents invalid state transitions

*Validated by: [`test_set_checklist_item_status_invalid_status`](tests/test_server.py), [`test_set_checklist_item_status_nonexistent_item`](tests/test_server.py)*

**Removing Items:**
- Individual items can be removed by their label
- Removing non-existent items raises a `FileNotFoundError`
- Item removal requires an existing checklist file

*Validated by: [`test_update_checklist_basic`](tests/test_server.py) (remove item section), [`test_granular_ops_require_existing_checklist`](tests/test_server.py)*

**Error Handling:**
- Attempting to remove a non-existent item label raises `FileNotFoundError` with the message "Checklist item not found"
- Item removal operations fail gracefully when the specified label doesn't exist in the checklist

*Validated by: [`test_remove_checklist_item_nonexistent_item`](tests/test_server.py)*

### Checklist Overwriting

- Entire checklists can be overwritten using the write operation
- Overwriting replaces all existing items with the new list
- Schema validation applies to overwrite operations
- Overwriting is idempotent and safe

*Validated by: [`test_update_checklist_basic`](tests/test_server.py) (overwrite section)*

## Multi-Task Management

### Concurrent Task Support

The system supports managing multiple tasks simultaneously:

- Each task maintains its own isolated directory structure
- Tasks can have nested directory structures (e.g., "nested/task")
- All three document types (investigation, solution plan, checklist) are created for each task
- File persistence is guaranteed across all tasks

*Validated by: [`test_multiple_tasks_workflow`](tests/test_integration.py)*

### File Persistence

- All written content is persistently stored and can be read back exactly as written
- File system operations are reliable and consistent
- Content integrity is maintained across read/write cycles

*Validated by: [`test_file_persistence`](tests/test_integration.py)*

## MCP Server Interface

### Tool Availability

The MCP server exposes exactly 9 tools for AI assistant integration:

1. `write_investigation` - Write investigation documents
2. `write_solution_plan` - Write solution plan documents
3. `write_checklist` - Write checklist documents
4. `read_investigation` - Read investigation documents
5. `read_solution_plan` - Read solution plan documents
6. `read_checklist` - Read checklist documents
7. `add_checklist_item` - Add individual checklist items
8. `set_checklist_item_status` - Update individual item status/notes
9. `remove_checklist_item` - Remove individual checklist items

*Validated by: [`test_list_tools`](tests/test_server.py)*

### Tool Execution

- All tools return structured text content responses
- Tool calls are processed asynchronously
- Unknown tool names raise `ValueError` with "Unknown tool" message
- Tool execution maintains the same validation and dependency rules as direct function calls

*Validated by: [`test_call_tool_write_investigation`](tests/test_server.py), [`test_call_tool_write_solution_plan`](tests/test_server.py), [`test_call_tool_write_checklist`](tests/test_server.py), [`test_call_tool_granular_checklist`](tests/test_server.py), [`test_call_tool_unknown_tool`](tests/test_server.py)*

**Error Handling:**
- MCP tool calls for read operations (read_investigation, read_solution_plan, read_checklist) can raise `FileNotFoundError` when attempting to read non-existent files
- Tool execution maintains the same error handling behavior as direct function calls
- Error responses are properly formatted and returned through the MCP interface

*Validated by: [`test_call_tool_read_investigation_file_not_found`](tests/test_server.py), [`test_call_tool_read_solution_plan_file_not_found`](tests/test_server.py), [`test_call_tool_read_checklist_file_not_found`](tests/test_server.py)*

## Tool Action Logging

### Automatic Logging

All tool actions are automatically logged to a structured log file for audit and debugging purposes:

**Log File Location:**
- Log file is created at `.tasks/tool_actions.log`
- Log file is created automatically when the first tool action occurs
- Log entries are appended to the existing file (no rotation by default)

*Validated by: [`test_log_file_creation`](tests/test_logging.py) - confirms that log file is created at the correct location when tools are called.*

**Log Entry Format:**
Each tool action is logged as a JSON entry containing:
- `tool`: Name of the tool that was called
- `task_id`: The task ID associated with the tool call
- `timestamp`: ISO 8601 formatted timestamp of when the tool was called
- `arguments`: Complete dictionary of arguments passed to the tool
- `result`: Result message returned by the tool (if any)

*Validated by: [`test_log_entry_format`](tests/test_logging.py) - confirms that log entries contain all required fields in proper JSON format.*

**Logging Scope:**
- All 9 MCP tools are logged (write_investigation, write_solution_plan, write_checklist, read_investigation, read_solution_plan, read_checklist, add_checklist_item, set_checklist_item_status, remove_checklist_item)
- Both successful and failed tool calls are logged
- Logging occurs after tool execution but before returning results to the client

*Validated by: [`test_all_tools_logged`](tests/test_logging.py) - confirms that all 9 MCP tools are logged when called.*

**Logging Behavior:**
- Log entries are appended to the existing file in append mode
- Each tool call generates exactly one log entry
- Log file is created automatically when the first tool action occurs
- Directory structure is created as needed for the log file

*Validated by: [`test_log_file_append_mode`](tests/test_logging.py) - confirms that multiple tool calls append to the same log file.*

**Logging Timing:**
- Logging occurs after tool execution completes but before returning results to the client
- The log entry contains the actual result that was returned to the client
- Timestamp reflects when the logging occurred, not when the tool was called

*Validated by: [`test_logging_timing`](tests/test_logging.py) - confirms that logging occurs at the correct time in the tool execution flow.*

**Example Log Entry:**
```json
{"tool": "write_investigation", "task_id": "example-task", "timestamp": "2024-01-15T10:30:45.123456", "arguments": {"task_id": "example-task", "content": "# Investigation\n\n"}, "result": "Wrote .tasks/example-task/INVESTIGATION.md"}
```

## Server Execution

### Main Entry Point

- The server can be executed as a main module
- The main function initializes and runs the MCP server using asyncio
- Server execution handles exceptions appropriately
- The entry point is callable and properly structured

*Validated by: [`test_main_calls_asyncio_run`](tests/test_main.py), [`test_main_entry_point`](tests/test_main.py), [`test_main_with_exception`](tests/test_main.py), [`test_main_module_execution`](tests/test_main.py)*

**Runtime Execution:**
- The server initializes and runs using asyncio with stdio communication streams
- Server startup establishes communication channels for MCP protocol interaction
- The main function can be executed directly as a module entry point
- Server runtime handles the complete MCP protocol lifecycle including initialization and tool registration

*Validated by: [`test_main_server_runtime_execution`](tests/test_main.py), [`test_main_server_initialization_options`](tests/test_main.py)*

## Error Handling

### Dependency Violations

- Attempting to create solution plans without investigations raises `ValueError`
- Attempting to create checklists without solution plans raises `ValueError`
- Error messages are descriptive and indicate the specific dependency requirement

*Validated by: [`test_create_solution_plan_without_investigation`](tests/test_server.py), [`test_create_checklist_without_solution_plan`](tests/test_server.py), [`test_task_dependencies_enforced`](tests/test_integration.py)*

### File System Errors

- Operations on non-existent files raise `FileNotFoundError` with descriptive messages
- Granular checklist operations require existing checklist files
- Error messages indicate the specific missing file

*Validated by: [`test_granular_ops_require_existing_checklist`](tests/test_server.py)*

### Schema Validation Errors

- Invalid checklist items raise `ValidationError` from the JSON schema validator
- Validation applies to both individual items and complete checklists
- Invalid status values, missing required fields, and extra fields are all rejected

*Validated by: [`test_invalid_checklist_items`](tests/test_server.py), [`test_invalid_status_values`](tests/test_server.py), [`test_create_checklist_invalid_schema`](tests/test_server.py)*

## Path Management

### Directory Structure

- Task paths are constructed using the pattern `.tasks/{task_id}/{filename}`
- Nested task directories are supported (e.g., "nested/task" creates `.tasks/nested/task/`)
- Directory creation is automatic when writing files
- Path construction is consistent and predictable

*Validated by: [`test_task_path_construction`](tests/test_server.py), [`test_task_path_with_subdirs`](tests/test_server.py), [`test_create_investigation_creates_directory`](tests/test_server.py)*

---

## Specification Status

### Verified Functionality (98% Coverage)
The vast majority of this specification is based on comprehensive test coverage of 46 test cases. All statements marked with "Validated by:" links are confirmed through automated testing and represent reliable, tested behavior.

### Minimal Unverified Functionality (2% Coverage)
Only a small amount of runtime execution code remains uncovered by automated tests. These represent:

- **Runtime Execution**: The actual asyncio server execution code and stdio communication stream handling (lines 417-418, 428)

These uncovered lines are part of the server startup sequence that is difficult to test without complex integration testing, but the core functionality is validated through mocking and interface testing.

### Coverage Summary
- **Total Lines**: 123
- **Covered Lines**: 120 (97.56%)
- **Uncovered Lines**: 3 (2.44%)
- **Test Cases**: 46

*This specification is derived from comprehensive analysis of 46 test cases covering all aspects of the TaskFlow MCP server functionality. Each verified statement is validated by specific test cases that demonstrate the behavior in practice. The minimal uncovered functionality represents only the deepest runtime execution code that is difficult to test in isolation.*
