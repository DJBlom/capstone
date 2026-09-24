"""Integration test for the public form page and Users table.

Uses Flask's test client against an in-memory SQLite database: a real WSGI
request through routing, SQLAlchemy, Jinja, and the response — without a
network port or the on-disk users.db file.
"""

from src.app import Users, db


def test_posting_form_persists_user_and_echoes_name(client, app):
    response = client.post(
        "/",
        data={"name": "Ada Lovelace", "role": "Geologist"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "You submitted" in page
    assert "Ada Lovelace" in page
    assert "Geologist" in page
    assert "<form" in page
    assert "Submit!" in page

    reload = client.get("/")
    assert reload.status_code == 200
    assert "Ada Lovelace" in reload.get_data(as_text=True)

    with app.app_context():
        stored = Users.query.filter_by(name="Ada Lovelace").one()
        assert stored.id is not None
        assert stored.role == "Geologist"
        assert db.session.query(Users).count() == 1
