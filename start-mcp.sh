#!/bin/bash
# TaskFlow MCP Server startup script
# Usage: ./start-mcp.sh [project-directory]
# If no project directory is provided, uses current directory

cd "$(dirname "$0")"

# Check if a project directory was provided as an argument
if [ $# -eq 1 ]; then
    PROJECT_DIR="$1"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "Error: Directory '$PROJECT_DIR' does not exist"
        exit 1
    fi
    
    # Set the working directory for the MCP server
    export TASKFLOW_WORKING_DIR="$PROJECT_DIR"
    echo "Starting TaskFlow MCP server for project: $PROJECT_DIR"
else
    echo "Starting TaskFlow MCP server for current directory: $(pwd)"
    echo "Tip: Use '$0 /path/to/project' to specify a different project directory"
fi

uv run taskflow-mcp