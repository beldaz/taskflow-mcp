"""Tests for the main entry point functionality."""

from typing import Any
from unittest.mock import patch

import pytest

from taskflow_mcp.server import main


class TestMain:
    """Test the main entry point."""

    def test_main_calls_server_run(self) -> None:
        """Test that main() calls server.run()."""
        with patch("taskflow_mcp.server.server") as mock_server:
            main()
            mock_server.run.assert_called_once()

    def test_main_entry_point(self) -> None:
        """Test that main can be called as entry point."""
        with patch("taskflow_mcp.server.server") as mock_server:
            # Simulate calling main as if it were the entry point
            main()
            mock_server.run.assert_called_once()

    @patch("taskflow_mcp.server.server")
    def test_main_with_exception(self, mock_server: Any) -> None:
        """Test that main handles exceptions from server.run()."""
        mock_server.run.side_effect = Exception("Server error")

        with pytest.raises(Exception, match="Server error"):
            main()
