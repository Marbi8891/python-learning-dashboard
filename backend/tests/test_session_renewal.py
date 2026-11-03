"""AUTH-01: la sesión de la web se renueva mientras se usa, con una caducidad absoluta."""

from datetime import UTC, datetime, timedelta

import jwt

from app.config import get_settings
from app.security import ALGORITHM, decode_access_token, get_jwt_secret, renewal_auth_time
from tests.conftest import register
from tests.test_session_cookie import WEB, session_cookie, with_cookie


def token(user_id=1, *, minutes_left=30, started_hours_ago=0.0, with_auth=True, version=0):
    now = datetime.now(UTC)
    started = now - timedelta(hours=started_hours_ago)
    payload = {
        "sub": str(user_id),
        "ver": version,
        "iat": now - timedelta(minutes=30 - minutes_left),
        "exp": now + timedelta(minutes=minutes_left),
    }
    if with_auth:
        payload["auth"] = int(started.timestamp())
    return jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)


def me(client, value, headers=WEB):
    return client.get("/api/v1/users/me", headers=with_cookie(value, headers))


def test_a_fresh_session_is_not_renewed(client):
    register(client)
    response = me(client, token(minutes_left=29))
    assert response.status_code == 200
    assert "set-cookie" not in response.headers


def test_a_session_past_half_its_life_gets_a_new_cookie_with_the_same_start(client):
    register(client)
    old = token(minutes_left=10, started_hours_ago=2)
    response = me(client, old)
    assert response.status_code == 200
    renewed = session_cookie(response)
    assert "Max-Age=1800" in response.headers["set-cookie"]
    old_claims = jwt.decode(old, get_jwt_secret(), algorithms=[ALGORITHM])
    new_claims = jwt.decode(renewed, get_jwt_secret(), algorithms=[ALGORITHM])
    assert new_claims["auth"] == old_claims["auth"], "la renovación no alarga la caducidad absoluta"
    assert new_claims["exp"] > old_claims["exp"]
    assert me(client, renewed).status_code == 200


def test_bearer_clients_are_not_renewed(client):
    register(client)
    bearer = {"Authorization": f"Bearer {token(minutes_left=5)}"}
    response = client.get("/api/v1/users/me", headers=bearer)
    assert response.status_code == 200
    assert "set-cookie" not in response.headers


def test_no_session_lasts_longer_than_the_absolute_limit(client):
    register(client)
    limit = get_settings().session_max_hours
    assert me(client, token(started_hours_ago=limit - 0.1)).status_code == 200
    assert me(client, token(started_hours_ago=limit + 0.1)).status_code == 401
    assert decode_access_token(token(started_hours_ago=limit + 0.1)) is None


def test_tokens_issued_before_this_change_use_their_issue_time(client):
    register(client)
    assert me(client, token(minutes_left=20, with_auth=False)).status_code == 200
    assert renewal_auth_time(token(minutes_left=10, with_auth=False)) is not None


def test_a_revoked_session_is_not_renewed(client):
    register(client)
    response = me(client, token(minutes_left=5, version=99))  # versión anterior a cerrar sesiones
    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_invalid_tokens_are_never_renewed():
    assert renewal_auth_time("no-es-un-token") is None


def test_a_signed_token_with_a_bad_subject_is_rejected():
    now = datetime.now(UTC)
    bad = jwt.encode(
        {"sub": "no-numero", "iat": now, "exp": now + timedelta(minutes=5)},
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )
    assert decode_access_token(bad) is None
