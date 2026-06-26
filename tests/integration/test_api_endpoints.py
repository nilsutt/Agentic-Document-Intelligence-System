from fastapi.testclient import TestClient

def test_health_check(api_client):
    r = api_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": "0.1.0"}

def test_ingest_endpoint(api_client):
    r = api_client.post("/api/v1/documents/ingest", json={"file_path": "doc.pdf"})
    assert r.status_code == 202
    assert "Successfully ingested" in r.json()["message"]

def test_ingest_empty_path_returns_422(api_client):
    r = api_client.post("/api/v1/documents/ingest", json={"file_path": ""})
    assert r.status_code == 422

def test_ask_endpoint(api_client):
    r = api_client.post("/api/v1/queries/ask", json={"question": "What is the interest rate?"})
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert "sources" in body
    assert body["answer"] == "The document discusses interest rates."

def test_ask_empty_question_returns_422(api_client):
    r = api_client.post("/api/v1/queries/ask", json={"question": ""})
    assert r.status_code == 422
