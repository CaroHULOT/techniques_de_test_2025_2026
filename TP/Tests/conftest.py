"""Configuration pytest et fixtures globales."""
import pytest
import time


def pytest_configure(config):
    """Configuration pytest."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test (deselect with '-m \"not performance\"')"
    )
