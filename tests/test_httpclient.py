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

