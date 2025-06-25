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


