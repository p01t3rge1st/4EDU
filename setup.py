"""Setup configuration for Geiger Monitor."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geiger-monitor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Radiation detection monitoring application using Geiger counter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/geiger-monitor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Polish",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.0",
        "PyQt6-Charts>=6.0",
        "pyserial>=3.5",
    ],
    entry_points={
        "console_scripts": [
            "geiger-monitor=geiger_monitor.main:main",
        ],
    },
)
