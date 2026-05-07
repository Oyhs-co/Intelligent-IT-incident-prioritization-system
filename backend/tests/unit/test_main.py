"""Tests para el entrypoint main.py."""

from src.presentation.api.app import app


def test_main_imports_app():
    """main.py debe importar la instancia app correctamente."""
    import importlib
    import sys

    # Ensure clean import
    if "src.main" in sys.modules:
        del sys.modules["src.main"]

    main_module = importlib.import_module("src.main")
    assert main_module.app is app
    assert main_module.app.title == "Incident Prioritization System"
