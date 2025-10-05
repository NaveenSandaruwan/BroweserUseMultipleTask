import requests
import pytest

HEALTH_URL = "http://127.0.0.1:5000/health"

test_cases = [
    ("https://scratch.mit.edu", True),
    ("https://malicious.example.com", False),
    ("https://randomsite.org", False),
    ("http://localhost:3000", False),
    ("https://untrusted.com", False),
    ("http://youtube.com", False),
    ("https://google.com", False),
]

@pytest.mark.parametrize("origin,expected", test_cases)
def test_health_cors(origin, expected):
    headers = {"Origin": origin}
    response = requests.get(HEALTH_URL, headers=headers)
    assert response.status_code == 200
    cors_header = response.headers.get("access-control-allow-origin")
    if expected:
        assert cors_header == origin
        print(f"PASSED ALLOWED: {origin}")
    else:
        assert cors_header != origin
        print(f"PASSED BLOCKED: {origin}")

if __name__ == "__main__":
    # Run each test one by one and print result immediately
    for origin, expected in test_cases:
        try:
            test_health_cors(origin, expected)
        except AssertionError:
            if expected:
                print(f"FAILED ALLOWED: {origin}")
            else:
                print(f"FAILED BLOCKED: {origin}")