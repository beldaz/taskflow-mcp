#!/usr/bin/env python3
"""Simple test runner script for taskflow-mcp."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the test suite."""
    print("Running taskflow-mcp tests...")
    print("=" * 50)

    # Run pytest with coverage using uv
    cmd = [
        "uv",
        "run",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=taskflow_mcp",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
    ]

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Tests failed!")
        return e.returncode


if __name__ == "__main__":
    sys.exit(main())
