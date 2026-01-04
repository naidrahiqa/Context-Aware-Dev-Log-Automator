# Minimal setup.py for DevPulse
from setuptools import setup, find_packages

setup(
    name="devpulse",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.7",
        "watchdog>=3.0.0",
        "groq>=0.4.0",
        "openai>=1.12.0",
        "litellm>=1.30.0",
    ],
    entry_points={
        "console_scripts": [
            "devpulse=devpulse.cli:main",
        ],
    },
    python_requires=">=3.9",
)
