"""Derechos de acceso comerciales: por defecto toda cuenta empieza en Free."""


def test_account_has_no_paid_entitlements_by_default(client, auth_headers):
    response = client.get("/api/v1/users/me/entitlements", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_entitlements_endpoint_returns_only_active_rights(client, auth_headers):
    with client.engine.begin() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO entitlements (user_id, feature_key, source, source_ref, starts_at, ends_at)
            VALUES
              (1, 'pcap_advanced', 'manual', 'grant-1',
               datetime('now', '-1 day'), datetime('now', '+1 day')),
              (1, 'expired_feature', 'manual', 'grant-2',
               datetime('now', '-3 day'), datetime('now', '-1 day')),
              (1, 'future_feature', 'manual', 'grant-3',
               datetime('now', '+1 day'), NULL)
            """
        )

    response = client.get("/api/v1/users/me/entitlements", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == [
        {
            "feature_key": "pcap_advanced",
            "starts_at": response.json()[0]["starts_at"],
            "ends_at": response.json()[0]["ends_at"],
        }
    ]
    assert "source_ref" not in response.text
    assert "manual" not in response.text


def test_entitlements_endpoint_requires_authentication(client):
    response = client.get("/api/v1/users/me/entitlements")
    assert response.status_code == 401


def test_require_entitlement_protects_an_endpoint(client, auth_headers):
    """La dependencia consulta los derechos en la base de datos, nunca el plan del navegador."""
    from fastapi import APIRouter

    from app.entitlements import require_entitlement
    from app.main import app

    probe = APIRouter()

    @probe.get("/_probe/pro", dependencies=[require_entitlement("pcap_advanced")])
    def pro_only() -> dict[str, bool]:
        return {"ok": True}

    before = list(app.router.routes)
    app.include_router(probe)
    try:
        denied = client.get("/_probe/pro", headers={**auth_headers, "X-PLD-Plan": "pro"})
        assert denied.status_code == 403
        assert denied.json()["detail"]["code"] == "entitlement_required"
        with client.engine.begin() as conn:
            conn.exec_driver_sql(
                "INSERT INTO entitlements (user_id, feature_key, source, source_ref, starts_at) "
                "VALUES (1, 'pcap_advanced', 'manual', 'grant-1', datetime('now', '-1 day'))"
            )
        assert client.get("/_probe/pro", headers=auth_headers).json() == {"ok": True}
    finally:
        app.router.routes[:] = before
