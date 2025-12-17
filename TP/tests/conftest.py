"""Configuration pytest et fixtures globales."""
import os
import sys

# Ajouter les répertoires au path pour les imports
tests_dir = os.path.dirname(os.path.abspath(__file__))
tp_dir = os.path.dirname(tests_dir)
triangulator_dir = os.path.join(tp_dir, 'Triangulator')

sys.path.insert(0, tests_dir)
sys.path.insert(0, tp_dir)
sys.path.insert(0, triangulator_dir)



def pytest_configure(config):
    """Configuration pytest."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test (deselect with '-m \"not performance\"')"
    )

from .mocks import *  # noqa: E402, F403