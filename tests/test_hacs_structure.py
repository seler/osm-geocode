"""Validate HACS repository structure and manifest files."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_hacs_json_exists_and_valid():
    """hacs.json exists and has required fields."""
    hacs = json.loads((ROOT / "hacs.json").read_text())
    assert "name" in hacs


def test_manifest_json_exists_and_valid():
    """manifest.json exists and has required fields for HACS integration."""
    manifest = json.loads(
        (ROOT / "custom_components" / "osm_geocode" / "manifest.json").read_text()
    )
    assert manifest["domain"] == "osm_geocode"
    assert "name" in manifest
    assert "version" in manifest
    assert "documentation" in manifest
    assert "issue_tracker" in manifest
    assert manifest.get("config_flow") is True
    assert "iot_class" in manifest


def test_init_py_exists():
    """__init__.py exists in the component directory."""
    assert (ROOT / "custom_components" / "osm_geocode" / "__init__.py").exists()


def test_required_files_structure():
    """Component has the expected file structure."""
    component_dir = ROOT / "custom_components" / "osm_geocode"
    assert component_dir.is_dir()
    assert (component_dir / "sensor.py").exists()
    assert (component_dir / "manifest.json").exists()
    assert (component_dir / "__init__.py").exists()
