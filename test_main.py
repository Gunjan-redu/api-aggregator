import httpx
from fastapi.testclient import TestClient
from main import  app

client = TestClient(app)

class FakeResponse:
    def __init__(self, data, status_code = 200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >=400:
            raise httpx.HTTPStatusError("boom", request=None, response= None)


def test_unknown_city_returns_404():
    response = client.get("/weather?city=asdfghjkl")
    assert response.status_code == 404

def test_city_returns_200():
    response = client.get("/weather?city=Delhi")
    assert response.status_code == 200

def test_currency_returns_200():
    response = client.get("/currency?from=usd&to=inr")
    assert response.status_code == 200
    assert "rate" in response.json()

def test_get_new_returns_200():
    response = client.get("/news?country=US")
    assert response.status_code == 200
    assert len(response.json()["articles"]) <= 5

def test_aggregate_unknown_city_404():
    response = client.get("/aggregate?city=asdfghjkl")
    assert response.status_code == 404


def test_weather_with_mocked_upstream(monkeypatch):
    monkeypatch.setattr("main._cache", {})

    def fake_get(url, timeout = None):
        if "geocoding" in url:
            return FakeResponse({"results" : [ {"latitude": 28.6, "longitude": 77.2, "name": "Delhi"}       ]})
        return FakeResponse({"current_weather": {"time": "2026-09-22T10:00", "temperature": 30.0, "windspeed": 5.0}})

    monkeypatch.setattr("main.httpx.get", fake_get)
    response = client.get("/weather?city=delhi")
    assert  response.status_code == 200
    assert  response.json()["temperature"] == 30.0

def test_upstream_down_returns_502(monkeypatch):
    monkeypatch.setattr("main._cache", {})

    def fake_get(url, timeout=None):
        return FakeResponse({}, status_code=500)   # every upstream: "I'm broken"

    monkeypatch.setattr("main.httpx.get", fake_get)

    response = client.get("/weather?city=delhi")
    assert response.status_code == 502


def test_upstream_timeout_returns_504(monkeypatch):
    monkeypatch.setattr("main._cache", {})

    def fake_get(url, timeout=None):
        raise httpx.TimeoutException("too slow")   # the actor doesn't answer at all

    monkeypatch.setattr("main.httpx.get", fake_get)

    response = client.get("/weather?city=delhi")
    assert response.status_code == 504


def test_aggregate_with_news_failure(monkeypatch):
    monkeypatch.setattr("main._cache", {})

    def fake_get(url, timeout=None):
        if "geocoding" in url:
            return FakeResponse({
                "results": [
                    {
                        "latitude": 28.6,
                        "longitude": 77.2,
                        "name": "Delhi"
                    }
                ]
            })

        if "api.open-meteo.com/v1/forecast" in url:
            return FakeResponse({
                "current_weather": {
                    "time": "2026-09-22T10:00",
                    "temperature": 30.0,
                    "windspeed": 5.0
                }
            })

        if "frankfurter" in url:

                return FakeResponse({"rates": {"INR": 88.0}})


        return FakeResponse({}, status_code=500)

    monkeypatch.setattr("main.httpx.get", fake_get)

    response = client.get("/aggregate?city=delhi")

    assert response.status_code == 200
    assert response.json()["news"] is None
    assert "news" in response.json()["errors"][0]

