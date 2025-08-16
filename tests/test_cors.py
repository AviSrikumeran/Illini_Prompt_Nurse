from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_cors_preflight_options():
    response = client.options(
        "/message",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    # When allow_credentials=True Starlette echoes back the origin rather than "*".
    assert (
        response.headers.get("access-control-allow-origin")
        == "http://example.com"
    )
