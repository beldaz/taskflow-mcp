"""Tests for the main entry point functionality."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from taskflow_mcp.server import main


class TestMain:
    """Test the main entry point."""

    @patch("asyncio.run")
    def test_main_calls_asyncio_run(self, mock_asyncio_run: Any) -> None:
        """Test that main() calls asyncio.run()."""
        main()
        mock_asyncio_run.assert_called_once()

    @patch("asyncio.run")
    def test_main_entry_point(self, mock_asyncio_run: Any) -> None:
        """Test that main can be called as entry point."""
        # Simulate calling main as if it were the entry point
        main()
        mock_asyncio_run.assert_called_once()

    @patch("asyncio.run")
    def test_main_with_exception(self, mock_asyncio_run: Any) -> None:
        """Test that main handles exceptions from asyncio.run()."""
        mock_asyncio_run.side_effect = Exception("Server error")

        with pytest.raises(Exception, match="Server error"):
            main()

    def test_main_module_execution(self) -> None:
        """Test that main can be executed as a module."""
        # This tests the `if __name__ == "__main__"` block
        # We can't easily test the actual execution, but we can verify
        # that the main function exists and is callable
        from taskflow_mcp.server import main

        assert callable(main)
