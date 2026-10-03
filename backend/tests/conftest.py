import os
import tempfile

import pytest

import config

config.DATABASE_PATH = os.path.join(tempfile.gettempdir(), "studypilot-test.db")

from database import init_db  # noqa: E402
from seed import seed_demo  # noqa: E402


@pytest.fixture
def demo_db():
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
    init_db()
    seed_demo()
    yield
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
