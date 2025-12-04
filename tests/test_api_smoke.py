def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("message")
