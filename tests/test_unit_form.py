"""Unit tests for form-input handling.

These tests call helpers directly. They do not start Flask, open a socket,
touch the database, or render HTML. A plain dict stands in for request.form.
"""

import pytest

from src.app import submitted_text_from_form, user_name_from_form, user_role_from_form


@pytest.mark.parametrize(
    "method, form, expected",
    [
        ("GET", {}, None),
        ("POST", {"name": "Ada Lovelace"}, "Ada Lovelace"),
        ("POST", {"name": ""}, ""),
        ("POST", {}, ""),
    ],
)
def test_submitted_text_from_form(method, form, expected):
    assert submitted_text_from_form(method, form) == expected


@pytest.mark.parametrize(
    "form, expected",
    [
        ({"name": "  Ada Lovelace  "}, "Ada Lovelace"),
        ({"name": ""}, ""),
        ({}, ""),
    ],
)
def test_user_name_from_form(form, expected):
    assert user_name_from_form(form) == expected


def test_user_role_from_form_blank_becomes_none():
    assert user_role_from_form({"role": ""}) is None
    assert user_role_from_form({"role": "Geologist"}) == "Geologist"
