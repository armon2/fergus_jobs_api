import pytest as pytest

from jobs import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": 'tests.sqlite',
    })

    # other setup can go here
    with app.app_context():
        from jobs import db
        db.init_db()

    yield app

    # clean up / reset resources here
    with app.app_context():
        db.close_db()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
