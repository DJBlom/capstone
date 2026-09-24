import pytest

from src.app import create_app, db


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
