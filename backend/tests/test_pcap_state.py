"""Preparación del PCAP guardada en la cuenta: /api/pcap-state."""

from app.schemas import MAX_PCAP_STATE_BYTES


def test_requires_login(client):
    assert client.get("/api/v1/pcap-state").status_code == 401
    assert client.put("/api/v1/pcap-state", json={"data": {}}).status_code == 401


def test_empty_state_then_save_and_read(client, auth_headers):
    empty = client.get("/api/v1/pcap-state", headers=auth_headers).json()
    assert empty == {"data": {}, "updated_at": None}

    state = {"answers": {"oop-01": [False, True]}, "exams": [{"score": 80}], "bestCombo": 4}
    saved = client.put("/api/v1/pcap-state", json={"data": state}, headers=auth_headers)
    assert saved.status_code == 200 and saved.json()["updated_at"]
    state["bestCombo"] = 7
    client.put("/api/v1/pcap-state", json={"data": state}, headers=auth_headers)
    assert client.get("/api/v1/pcap-state", headers=auth_headers).json()["data"]["bestCombo"] == 7


def test_rejects_oversized_state(client, auth_headers):
    huge = {"answers": {"x": ["a" * MAX_PCAP_STATE_BYTES]}}
    assert (
        client.put("/api/v1/pcap-state", json={"data": huge}, headers=auth_headers).status_code
        == 422
    )


def test_export_and_delete_include_pcap_state(client, auth_headers):
    assert client.get("/api/v1/users/me/export", headers=auth_headers).json()["pcap"] is None
    client.put("/api/v1/pcap-state", json={"data": {"known": ["oop-f01"]}}, headers=auth_headers)
    assert client.get("/api/v1/users/me/export", headers=auth_headers).json()["pcap"] == {
        "known": ["oop-f01"]
    }


def test_rejects_deeply_nested_state_with_422(client, auth_headers):
    """Un JSON muy anidado daba un 500 (recursión): ahora es un 422 controlado."""
    nested = '{"data":' + '{"a":' * 400 + "1" + "}" * 400 + "}"
    headers = {**auth_headers, "Content-Type": "application/json"}
    assert client.put("/api/v1/pcap-state", content=nested, headers=headers).status_code == 422
    # La API sigue respondiendo con normalidad
    ok = client.put("/api/v1/pcap-state", json={"data": {"a": {"b": [1, 2]}}}, headers=auth_headers)
    assert ok.status_code == 200
