import pytest
from unittest.mock import patch, Mock
from fletx.core.http import HTTPClient, HTTPResponse

@pytest.fixture
def client():
    return HTTPClient(base_url="https://api.example.com", debug=True)

def test_httpclient_initialization_defaults():
    client = HTTPClient()
    assert client.base_url == ""
    assert client.timeout == 30
    assert client.max_retries == 3
    assert client.retry_delay == 1.0
    assert client.debug is False
    assert client.proxy is None
    assert client.pool_size == 100
    assert client.verify_ssl is True
    assert client.follow_redirects is True
    assert client.max_redirects == 10
    assert client.default_cookies == {}
    assert client.sync_mode is False
    assert isinstance(client.default_headers, dict)
    assert "User-Agent" in client.default_headers

def test_httpclient_custom_initialization():
    headers = {"X-Test": "yes"}
    cookies = {"session": "abc"}
    client = HTTPClient(
        base_url="https://api.example.com/",
        default_headers=headers,
        timeout=10,
        max_retries=5,
        retry_delay=2.0,
        debug=True,
        proxy="http://localhost:8080",
        pool_size=10,
        verify_ssl=False,
        follow_redirects=False,
        max_redirects=5,
        cookies=cookies,
        sync_mode=True
    )
    assert client.base_url == "https://api.example.com"
    assert client.default_headers["X-Test"] == "yes"
    assert client.timeout == 10
    assert client.max_retries == 5
    assert client.retry_delay == 2.0
    assert client.debug is True
    assert client.proxy == "http://localhost:8080"
    assert client.pool_size == 10
    assert client.verify_ssl is False
    assert client.follow_redirects is False
    assert client.max_redirects == 5
    assert client.default_cookies == cookies
    assert client.sync_mode is True

def test_add_middleware(client):
    middleware = Mock()
    client.add_middleware(middleware)
    assert middleware in client.middlewares

def test_set_auth(client):
    client.set_auth("token123", auth_type="Bearer")
    assert any(m.__class__.__name__ == "AuthMiddleware" for m in client.middlewares)

def test_set_rate_limit(client):
    client.set_rate_limit(5.0)
    assert client.rate_limit_per_second == 5.0

def test_set_progress_callbacks(client):
    upload_cb = Mock()
    download_cb = Mock()
    client.set_upload_progress_callback(upload_cb)
    client.set_download_progress_callback(download_cb)
    assert client.upload_progress_callback is upload_cb
    assert client.download_progress_callback is download_cb

def test_sync_request(monkeypatch, client):
    # Patch the _request_sync method to return a fake response
    fake_response = HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        data={"ok": True},
        elapsed=0.1,
        url="https://api.example.com/test"
    )
    monkeypatch.setattr(client, "_request_sync", lambda *a, **k: fake_response)
    resp = client.request("GET", "/test", sync=True)
    assert isinstance(resp, HTTPResponse)
    assert resp.status == 200
    assert resp.ok
    assert resp.is_json
    assert resp.json() == {"ok": True}

def test_get_post_patch_delete_methods(monkeypatch, client):
    fake_response = HTTPResponse(
        status=201,
        headers={},
        data="created",
        elapsed=0.05,
        url="https://api.example.com/resource"
    )
    monkeypatch.setattr(client, "_request_sync", lambda *a, **k: fake_response)
    assert client.get("/resource", sync=True).status == 201
    assert client.post("/resource", sync=True).status == 201
    assert client.patch("/resource", sync=True).status == 201
    assert client.delete("/resource", sync=True).status == 201
    assert client.put("/resource", sync=True).status == 201

