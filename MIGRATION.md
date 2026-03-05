# Migration from C++ to Python

## What Changed

The Geiger Monitor application has been completely migrated from C++ (Qt/CMake) to Python (PyQt6).

### Old Stack (Removed)
- **Language**: C++17
- **Framework**: Qt 5/6 C++ API
- **Build System**: CMake
- **Distribution**: Native binaries, AppImage
- **Files**: 
  - `CMakeLists.txt`
  - `src/MainWindow.{h,cpp}`
  - `src/AnalogGauge.{h,cpp}`
  - `src/main.cpp`

### New Stack (Added)
- **Language**: Python 3.8+
- **Framework**: PyQt6
- **Build System**: setuptools/pyproject.toml
- **Distribution**: Python package + Flatpak
- **Files**:
  - `src/geiger_monitor/main.py` - Entry point
  - `src/geiger_monitor/main_window.py` - Main UI & logic
  - `src/geiger_monitor/analog_gauge.py` - Custom gauge widget
  - `setup.py` / `pyproject.toml` - Package configuration
  - `requirements.txt` - Dependencies
  - `flatpak/org.example.GeigerMonitor.yml` - Flatpak manifest

## Key Improvements

1. **Cross-platform Support**: Python runs on Linux, macOS, Windows
2. **Easier Distribution**: Flatpak, pip, direct source installation
3. **Faster Development**: No compilation needed
4. **Better Accessibility**: Python is more readable than C++
5. **Dependency Management**: Clear requirements.txt
6. **Version Control**: Easy semantic versioning

## Installation

### Quick Start (Development)

```bash
cd geiger-monitor
./setup-dev.sh
python -m geiger_monitor.main
```

### Production Installation

```bash
pip install .
geiger-monitor
```

### Flatpak Installation

```bash
flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml --user --install-deps-from=flathub
```

## File Renames/Migrations

| Old (C++) | New (Python) |
|-----------|--------------|
| `src/MainWindow.h/.cpp` | `src/geiger_monitor/main_window.py` |
| `src/AnalogGauge.h/.cpp` | `src/geiger_monitor/analog_gauge.py` |
| `src/main.cpp` | `src/geiger_monitor/main.py` |
| `CMakeLists.txt` | `pyproject.toml` + `setup.py` |
| N/A | `src/geiger_monitor/__init__.py` |

## API Compatibility

The core logic remains the same:

```python
# Old C++
MainWindow w;
w.show();

# New Python
window = MainWindow()
window.show()
```

Class names and methods are preserved, just with Python naming conventions:
- `QSerialPort` → `QSerialPort` (same)
- `m_serial` → `self.m_serial` (same)
- `MainWindow::toggleConnection()` → `MainWindow.toggle_connection()` (snake_case)

## Breaking Changes

None in terms of functionality. Users may notice:
- Slightly faster startup (Python bytecode vs compiled binary)
- Different error messages from PyQt6 vs Qt C++
- Window styling might differ slightly between Qt5 and Qt6

## Development Workflow

### Install dev dependencies

```bash
pip install -e ".[dev]"
```

### Run code quality checks

```bash
black src/
flake8 src/
mypy src/
```

### Run tests

```bash
pytest
```

## Debugging

### Enable Python debugging

```bash
python -m pdb -m geiger_monitor.main
```

### Check imports

```bash
python -c "import geiger_monitor; print(geiger_monitor.__version__)"
```

### Run with verbose output

```bash
PYTHONVERBOSE=2 python -m geiger_monitor.main
```

## Flatpak Publishing

### For Your Own Flatpak Hub

1. Update `app-id` in `flatpak/org.example.GeigerMonitor.yml`
2. Build and create bundle:
   ```bash
   flatpak-builder build-dir flatpak/org.example.GeigerMonitor.yml
   flatpak build-bundle build-dir geiger-monitor.flatpak org.example.GeigerMonitor
   ```
3. Distribute `geiger-monitor.flatpak` to users
4. Users install with:
   ```bash
   flatpak install geiger-monitor.flatpak
   ```

### For Flathub (Community Repository)

1. Fork https://github.com/flathub/org.example.GeigerMonitor
2. Update manifest with your details
3. Submit PR to Flathub maintainers
4. Once approved, automatically available in Flatpak store

## Version Management

Version is controlled in one place: `VERSION` file

Current version structure: `MAJOR.MINOR.PATCH`

```bash
# View current version
cat VERSION

# Update version (manually)
echo "1.1.0" > VERSION

# Or use release script
./release.sh --minor
```

## PyQt6 vs PyQt5

This project uses **PyQt6** because:
- Active maintenance
- Native Wayland support
- Better Linux integration
- Type hints support

To use PyQt5 instead:

```bash
# Modify requirements.txt and setup.py
pip install PyQt5 PyQtChart pyserial
```

## Troubleshooting Migration Issues

### ImportError: No module named 'PyQt6'

```bash
pip install PyQt6 PyQt6-Charts
```

### Serial port permission denied

```bash
sudo usermod -aG dialout $USER
# Log out and back in
```

### Flatpak build fails

Ensure you have latest Flatpak runtimes:

```bash
flatpak update
flatpak install org.freedesktop.Sdk//22.08 org.freedesktop.Sdk.Extension.python3//22.08
```

## Future Roadmap

- [ ] Unit tests with pytest
- [ ] GitHub Actions CI/CD
- [ ] Flathub integration
- [ ] AppImage distribution
- [ ] macOS app bundle
- [ ] Windows standalone exe

## Support

For issues with the new Python version:
1. Check [README.md](README.md) troubleshooting section
2. Create GitHub issue with:
   - Python version (`python --version`)
   - PyQt6 version (`pip show PyQt6`)
   - System info (`uname -a`)
   - Error message and stack trace
