"""Compatibility shim for setuptools.

Project metadata lives in pyproject.toml and is consumed by uv/build frontends.
"""

from setuptools import setup


if __name__ == "__main__":
    setup()
