from pathlib import Path
from setuptools import setup


REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
REQUIREMENTS_DEV_FILE = Path(__file__).parent / "requirements-dev.txt"


def read_file(filepath: Path) -> list[str]:
    """ Read given `filepath` and return contents as list of strings.

    Args:
        filepath (obj: Path): Path to file.

    Returns:
        list[str]: File contents as list of strings.
    """

    contents: list[str] = []
    with filepath.open("r") as f:
        contents = f.readlines()
    return contents


setup(
    install_requires=read_file(REQUIREMENTS_FILE),
    extras_require={
        "test": read_file(REQUIREMENTS_DEV_FILE),
    },
)

