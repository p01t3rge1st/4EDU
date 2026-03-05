#!/usr/bin/env python3
"""
Quick verification script for Geiger Monitor Python migration.
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and print status."""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description:50} {path}")
    return exists

def check_dir_exists(path, description):
    """Check if a directory exists and print status."""
    exists = Path(path).is_dir()
    status = "✓" if exists else "✗"
    print(f"{status} {description:50} {path}/")
    return exists

def main():
    """Run verification checks."""
    print("=" * 80)
    print("GEIGER MONITOR PYTHON MIGRATION - VERIFICATION CHECKLIST")
    print("=" * 80)
    print()

    base = Path(__file__).parent
    all_good = True

    print("📦 Python Package Files:")
    print("-" * 80)
    all_good &= check_dir_exists(base / "src/geiger_monitor", "Package directory")
    all_good &= check_file_exists(base / "src/geiger_monitor/__init__.py", "Package init")
    all_good &= check_file_exists(base / "src/geiger_monitor/main.py", "Entry point")
    all_good &= check_file_exists(base / "src/geiger_monitor/main_window.py", "Main window UI")
    all_good &= check_file_exists(base / "src/geiger_monitor/analog_gauge.py", "Analog gauge widget")
    print()

    print("🔧 Package Configuration:")
    print("-" * 80)
    all_good &= check_file_exists(base / "setup.py", "Setup script (setuptools)")
    all_good &= check_file_exists(base / "pyproject.toml", "Project metadata (PEP 518)")
    all_good &= check_file_exists(base / "MANIFEST.in", "Package manifest")
    all_good &= check_file_exists(base / "requirements.txt", "Dependencies")
    print()

    print("📚 Documentation:")
    print("-" * 80)
    all_good &= check_file_exists(base / "README.md", "Main documentation")
    all_good &= check_file_exists(base / "MIGRATION.md", "Migration guide")
    all_good &= check_file_exists(base / "LICENSE", "MIT License")
    print()

    print("📦 Flatpak Distribution:")
    print("-" * 80)
    all_good &= check_dir_exists(base / "flatpak", "Flatpak manifest directory")
    all_good &= check_file_exists(base / "flatpak/org.example.GeigerMonitor.yml", "Flatpak manifest")
    print()

    print("🗑️  Cleanup Verification (C++ files removed):")
    print("-" * 80)
    removed_files = [
        "CMakeLists.txt",
        "src/MainWindow.h",
        "src/MainWindow.cpp",
        "src/AnalogGauge.h",
        "src/AnalogGauge.cpp",
        "src/main.cpp",
    ]
    for file in removed_files:
        path = base / file
        removed = not path.exists()
        status = "✓ REMOVED" if removed else "✗ STILL EXISTS"
        print(f"{status:30} {path}")
        all_good &= removed

    print()
    print("=" * 80)
    if all_good:
        print("✅ ALL CHECKS PASSED! Migration appears complete.")
        print()
        print("Next steps:")
        print("  1. Install dev environment: python -m pip install -e '.[dev]'")
        print("  2. Run application: python -m geiger_monitor.main")
        print("  3. Build Flatpak: flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml --user --install-deps-from=flathub")
        print("  4. Check MIGRATION.md for detailed information")
    else:
        print("❌ SOME CHECKS FAILED! Please review the output above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
