import pathlib

import pytest


RESOURCES = pathlib.Path(__file__).parent / "resources"


@pytest.fixture(scope="session")
def resources():
    return RESOURCES
