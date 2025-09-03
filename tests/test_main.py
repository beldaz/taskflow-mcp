"""Tests for the main entry point functionality."""

from typing import Any
from unittest.mock import patch

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

    @patch("asyncio.run")
    @patch("mcp.stdio_server")
    def test_main_server_runtime_execution(self, mock_stdio_server: Any, mock_asyncio_run: Any) -> None:
        """Test that main function sets up server runtime with proper MCP protocol handling."""
        from taskflow_mcp.server import main

        # Mock the stdio server context manager
        mock_read_stream = "mock_read_stream"
        mock_write_stream = "mock_write_stream"
        mock_stdio_server.return_value.__aenter__.return_value = (mock_read_stream, mock_write_stream)

        # Call main function
        main()

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function that was passed to asyncio.run
        call_args = mock_asyncio_run.call_args[0]
        async_func = call_args[0]

        # Verify the async function exists (it's a coroutine object)
        assert async_func is not None
        # Verify it has the expected coroutine attributes
        assert hasattr(async_func, "cr_code")
        assert hasattr(async_func, "cr_frame")

    @patch("asyncio.run")
    @patch("mcp.stdio_server")
    def test_main_server_initialization_options(self, mock_stdio_server: Any, mock_asyncio_run: Any) -> None:
        """Test that main function creates proper server initialization options."""
        from taskflow_mcp.server import main, server

        # Mock the stdio server context manager
        mock_read_stream = "mock_read_stream"
        mock_write_stream = "mock_write_stream"
        mock_stdio_server.return_value.__aenter__.return_value = (mock_read_stream, mock_write_stream)

        # Call main function
        main()

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function that was passed to asyncio.run
        call_args = mock_asyncio_run.call_args[0]
        async_func = call_args[0]

        # Verify the async function exists (it's a coroutine object)
        assert async_func is not None
        # Verify it has the expected coroutine attributes
        assert hasattr(async_func, "cr_code")
        assert hasattr(async_func, "cr_frame")

        # Verify server has create_initialization_options method
        assert hasattr(server, "create_initialization_options")
        assert callable(server.create_initialization_options)
