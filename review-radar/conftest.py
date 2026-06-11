import pytest


@pytest.fixture(autouse=True)
def _hermetic_dotenv(monkeypatch):
    """Keep tests hermetic: a developer's real .env must not bleed into config
    tests. config.py calls dotenv.load_dotenv() at import; neutralize it so
    tests see only the environment they set explicitly via monkeypatch."""
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None, raising=False)
    monkeypatch.setattr("dotenv.main.load_dotenv", lambda *a, **k: None, raising=False)
