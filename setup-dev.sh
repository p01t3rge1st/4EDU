#!/bin/bash
# Quick start script for Geiger Monitor development

# Install dependencies
pip install -e ".[dev]"

# Optional: install pre-commit hooks
# pre-commit install

echo "✓ Development environment ready!"
echo ""
echo "To run the application:"
echo "  python -m geiger_monitor.main"
echo ""
echo "To build Flatpak:"
echo "  flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml --user --install-deps-from=flathub"
