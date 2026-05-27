"""
Integration-level fixtures.
The root conftest.py already provides: db, client, auth_headers, admin_headers.
Add integration-specific fixtures here — e.g. pre-seeded DB records.
"""

import pytest


# Example: seed a user record before an integration test
# @pytest.fixture()
# def seeded_user(db):
#     from app.entity.user import User
#     from app.util.security import get_password_hash
#     user = User(
#         full_name="Test User",
#         email="test@example.com",
#         password_hash=get_password_hash("password123"),
#     )
#     db.add(user)
#     db.flush()
#     return user
