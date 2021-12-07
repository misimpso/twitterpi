from pathlib import Path
from setuptools import setup


REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
REQUIREMENTS_DEV_FILE = Path(__file__).parent / "requirements-dev.txt"

def read_file(filepath: Path) -> list[str]:
    contents = []
    with filepath.open("r") as f:
        contents = f.readlines()
    return contents


setup(
    extras_requires=read_file(REQUIREMENTS_DEV_FILE),
    install_requires=read_file(REQUIREMENTS_FILE),
)