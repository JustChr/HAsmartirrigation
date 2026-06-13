"""Test the Smart Irrigation performance monitoring utilities."""

import asyncio
import time
from unittest.mock import patch

import pytest

from custom_components.smart_irrigation.performance import (
    _log_duration,
    async_timer,
    performance_timer,
)


class TestPerformanceTimer:
    """Test performance timer decorator."""

    def test_performance_timer_sync_function_fast(self, caplog):
        """Test performance timer with fast sync function."""

        @performance_timer()
        def fast_function():
            return "result"

        result = fast_function()

        assert result == "result"
        # Should not log anything for fast functions
        assert "took" not in caplog.text

    def test_performance_timer_sync_function_slow(self, caplog):
        """Test performance timer with slow sync function."""

        @performance_timer()
        def slow_function():
            time.sleep(0.11)  # Sleep longer than threshold
            return "result"

        with patch(
            "custom_components.smart_irrigation.performance.time.perf_counter",
            side_effect=[0, 0.15],
        ):
            result = slow_function()

        assert result == "result"
        assert "took 0.150 seconds" in caplog.text

    async def test_performance_timer_async_function_fast(self, caplog):
        """Test performance timer with fast async function."""

        @performance_timer()
        async def fast_async_function():
            return "async_result"

        result = await fast_async_function()

        assert result == "async_result"
        # Should not log anything for fast functions
        assert "took" not in caplog.text

    async def test_performance_timer_async_function_slow(self, caplog):
        """Test performance timer with slow async function."""

        @performance_timer()
        async def slow_async_function():
            await asyncio.sleep(0.01)  # Small sleep
            return "async_result"

        with patch(
            "custom_components.smart_irrigation.performance.time.perf_counter",
            side_effect=[0, 0.15],
        ):
            result = await slow_async_function()

        assert result == "async_result"
        assert "took 0.150 seconds" in caplog.text

    def test_performance_timer_with_custom_name(self, caplog):
        """Test performance timer with custom function name."""

        @performance_timer("custom_function_name")
        def function_with_custom_name():
            return "result"

        with patch(
            "custom_components.smart_irrigation.performance.time.perf_counter",
            side_effect=[0, 0.15],
        ):
            result = function_with_custom_name()

        assert result == "result"
        assert "custom_function_name took 0.150 seconds" in caplog.text

    def test_performance_timer_exception_handling(self, caplog):
        """Test performance timer with function that raises exception."""

        @performance_timer()
        def failing_function():
            raise ValueError("Test error")

        with (
            patch(
                "custom_components.smart_irrigation.performance.time.perf_counter",
                side_effect=[0, 0.15],
            ),
            pytest.raises(ValueError, match="Test error"),
        ):
            failing_function()

        # Should still log the duration despite the exception
        assert "took 0.150 seconds" in caplog.text

    async def test_performance_timer_async_exception_handling(self, caplog):
        """Test performance timer with async function that raises exception."""

        @performance_timer()
        async def failing_async_function():
            raise ValueError("Async test error")

        with (
            patch(
                "custom_components.smart_irrigation.performance.time.perf_counter",
                side_effect=[0, 0.15],
            ),
            pytest.raises(ValueError, match="Async test error"),
        ):
            await failing_async_function()

        # Should still log the duration despite the exception
        assert "took 0.150 seconds" in caplog.text

    def test_async_timer_alias(self):
        """Test that async_timer is an alias for performance_timer."""
        assert async_timer is performance_timer


class TestLogDuration:
    """Test _log_duration function."""

    def test_log_duration_warning_threshold(self, caplog):
        """Test logging at warning level for slow operations."""
        _log_duration("test_function", 0.15)

        assert "WARNING" in caplog.text
        assert "test_function took 0.150 seconds (threshold: 0.1s)" in caplog.text

    def test_log_duration_debug_threshold(self, caplog):
        """Test logging at debug level for medium operations."""
        with caplog.at_level("DEBUG"):
            _log_duration("test_function", 0.06)

        assert "DEBUG" in caplog.text
        assert "test_function took 0.060 seconds" in caplog.text

    def test_log_duration_no_logging(self, caplog):
        """Test no logging for fast operations."""
        _log_duration("test_function", 0.01)

        assert "took" not in caplog.text
