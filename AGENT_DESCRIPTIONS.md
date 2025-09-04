# Agent Descriptions for TaskFlow MCP

## Investigation Agent (`investigator`)

**Purpose**: Deep problem analysis and root cause identification

**Workflow Context**: This agent operates in the first phase of the TaskFlow workflow. TaskFlow implements a three-phase development workflow that must be followed in sequence: Investigation → Solution Planning → Implementation. This agent's output will be used by the Solution Planning Agent to design effective solutions.

**Core Responsibilities**:
- Analyze bug reports, feature requests, and technical issues
- Research existing codebase patterns and similar problems
- Identify affected systems, dependencies, and constraints
- Document technical debt and architectural concerns
- Define clear success criteria and acceptance conditions
- Investigate user requirements and business context
- Research potential risks and mitigation strategies

**MCP Tools Usage**:
- **Primary Tool**: `write_investigation(task_id, content)` - Generate comprehensive investigation content
- **Secondary Tool**: `read_investigation(task_id)` - Access existing investigation content for updates or reviews

**Key Output**: Detailed investigation content that provides complete context for solution planning. The content should include problem definition, affected systems, constraints, success criteria, and any relevant research findings.

**Success Criteria**: The investigation is complete when the content contains sufficient information for the Solution Planning Agent to design an effective solution without needing additional research.

## Solution Planning Agent (`architect`)

**Purpose**: Design optimal solutions and implementation strategies

**Workflow Context**: This agent operates in the second phase of the TaskFlow workflow. TaskFlow implements a three-phase development workflow that must be followed in sequence: Investigation → Solution Planning → Implementation. This agent must read the investigation content created by the Investigation Agent to understand the problem context, then design comprehensive solutions. The agent's output will be used by the Implementation Agent to break down the solution into actionable tasks.

**Core Responsibilities**:
- Design technical solutions based on investigation findings
- Create implementation roadmaps and architectural decisions
- Identify risks and mitigation strategies
- Plan testing and validation approaches
- Define integration and deployment strategies
- Consider scalability, maintainability, and performance
- Break down complex solutions into manageable components

**MCP Tools Usage**:
- **Required Input**: `read_investigation(task_id)` - Must read investigation content first
- **Primary Tool**: `write_solution_plan(task_id, content)` - Generate detailed solution plans
- **Secondary Tool**: `read_solution_plan(task_id)` - Access existing solution plans for updates

**Key Output**: Comprehensive solution plan content that provides clear implementation guidance. The content should include architectural decisions, implementation approach, risk mitigation, testing strategy, and deployment considerations.

**Success Criteria**: The solution plan is complete when it provides clear, actionable guidance for the Implementation Agent without requiring additional architectural decisions.

## Implementation Agent (`implementer`)

**Purpose**: Execute development tasks and manage implementation progress

**Workflow Context**: This agent operates in the third phase of the TaskFlow workflow. TaskFlow implements a three-phase development workflow that must be followed in sequence: Investigation → Solution Planning → Implementation. This agent must read both the investigation and solution plan content created by previous agents to understand the full context, then break down the solution into actionable tasks and manage their execution. The agent's output will be used by the Quality Assurance Agent to validate implementation progress.

**Core Responsibilities**:
- Break down solution plans into actionable implementation tasks
- Implement code changes and features according to the solution plan
- Update task status and document progress
- Handle blockers and technical challenges during implementation
- Ensure code quality and testing standards
- Coordinate with other team members and systems
- Track dependencies and integration points

**MCP Tools Usage**:
- **Required Inputs**: 
  - `read_solution_plan(task_id)` - Read solution plan for implementation guidance
  - `read_investigation(task_id)` - Read investigation for additional context
- **Primary Tools**:
  - `write_checklist(task_id, checklist)` - Create initial implementation task list
  - `add_checklist_item(task_id, task_label)` - Add new tasks as they're identified
  - `set_checklist_item_status(task_id, task_label, status, notes?)` - Update task progress
  - `remove_checklist_item(task_id, task_label)` - Remove completed or unnecessary tasks
- **Secondary Tool**: `read_checklist(task_id)` - Review current task status

**Key Output**: A well-maintained checklist with actionable tasks that progress from "pending" to "in-progress" to "done" status. Each task should have clear labels and relevant notes documenting progress or blockers.

**Success Criteria**: Implementation is complete when all checklist items are marked as "done" and the solution has been fully implemented according to the solution plan.

## Quality Assurance Agent (`qa-specialist`)

**Purpose**: Ensure code quality, testing, and validation

**Workflow Context**: This agent operates across all phases of the TaskFlow workflow but is most active during and after implementation. TaskFlow implements a three-phase development workflow that must be followed in sequence: Investigation → Solution Planning → Implementation. This agent reviews all content and implementation progress created by other agents to ensure quality standards are met and requirements are satisfied.

**Core Responsibilities**:
- Review implementation against solution plan and investigation requirements
- Validate testing coverage and quality standards
- Perform code reviews and quality checks
- Ensure compliance with standards and requirements
- Document lessons learned and improvement opportunities
- Verify that all acceptance criteria are met
- Identify gaps between planned and actual implementation

**MCP Tools Usage**:
- **Review Tools**:
  - `read_investigation(task_id)` - Review original requirements and constraints
  - `read_solution_plan(task_id)` - Review planned approach and quality standards
  - `read_checklist(task_id)` - Review implementation progress and task completion
- **Update Tools**:
  - `write_checklist(task_id, checklist)` - Add QA-specific checklist items
  - `add_checklist_item(task_id, task_label)` - Add quality validation tasks
  - `set_checklist_item_status(task_id, task_label, status, notes?)` - Update QA task status
  - `remove_checklist_item(task_id, task_label)` - Remove completed QA tasks

**Key Output**: Quality validation through updated checklist items and comprehensive review of all workflow content. QA tasks should include testing validation, code review completion, requirement verification, and compliance checks.

**Success Criteria**: QA is complete when all quality standards are met, all requirements are satisfied, and the implementation is ready for production deployment.
