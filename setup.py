#!/usr/bin/env python3
# G3r4ki - Setup script for Python package

from setuptools import setup, find_packages

setup(
    name="g3r4ki",
    version="0.1.0",
    description="AI-powered Linux system for cybersecurity operations",
    author="RafalW3bCraft",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "numpy>=1.22.0",
        "torch>=2.0.0; sys_platform != 'darwin' or platform_machine != 'arm64'",
        "transformers>=4.30.0",
        "huggingface_hub>=0.16.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "gpu": [
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "g3r4ki=g3r4ki:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
