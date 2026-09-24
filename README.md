# API Aggregator

A FastAPI service that fetches and combines data from multiple external APIs —
current weather for any city on Earth, live currency conversion, and top news
headlines — with a combined `/aggregate` endpoint, upstream failure handling,
an in-process TTL cache, and a pytest suite that includes mocked upstream
failures.

## Stack

- FastAPI, httpx, Pydantic, pydantic-settings
- External APIs: Open-Meteo (geocoding + weather), Frankfurter (currency), NewsAPI (headlines)
- In-process TTL cache for upstream calls
- pytest (integration tests + mocked upstream-failure tests)

## Endpoints

- `GET /aggregate?city={name}` — the headline endpoint: combines current
  weather, USD→INR rate, and top headlines in one response. Unknown city
  returns 404 (the city is the subject of the request). If an individual
  upstream service fails, the rest still return — the failed section comes
  back as `null` with a note in `errors` (graceful degradation).
- `GET /weather?city={name}` — current temperature, windspeed and time for
  any city, geocoded by name (no hardcoded city list). 404 for unknown
  cities.
- `GET /currency?from={code}&to={code}&amount={n}` — converts an amount
  between currencies using live rates; case-insensitive codes.
- `GET /news?country={code}` — top 5 headlines for a country (two-letter
  code), reshaped to title, source and URL.

All endpoints return **502** when an upstream service answers with an error
and **504** when it times out — the status code says whose failure it was.

## Run it locally

**Prerequisites:** Python 3.10+

1. Clone the repo and create a virtual environment:

```
git clone https://github.com/Gunjan-redu/api-aggregator.git
cd api-aggregator
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

2. Configure environment: copy `.env.example` to `.env` and add your NewsAPI
   key (free at https://newsapi.org).

3. Run:

```
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs and try the endpoints.

4. Run the tests:

```
pytest -v
```

The suite includes integration tests (real upstream calls) and mocked tests
that simulate upstream failures — no network needed for those.

## What I learned building this

- **Chaining API calls:** Connected the 2 API's in a chain, latitudes and longitudes of a city are extracted from the geocoding-api, which are then given to weather API to get the weather of the city. So, the output of one API is the input for another one.
- **Whose failure is it:** Set up a system to handle API failure in a transparent way. If a request fails we get a 502 if the external API answered with an error, 504 if it timed out, and 500 only if it's genuinely my server's own bug.
- **Graceful degradation:** In the /aggregate endpoint if an unknown city is the input, it will kill the request. Also, if any of the other API's aren't responding then we get the responses from the ones that do respond. In the response we show all the successful responses of the API, and the names of those which failed.
- **Caching:** Used a TTL cache, responses are remembered for 5 minutes, so repeated identical calls are served from memory instead of re-asking the upstream. But, it has limits- it will reset if the app is stopped. Can't be used by other services since it lives in the process.
- **Testing with mocks:** Replaced httpx with a fake during tests, so I can stage upstream disasters — timeouts, 500s — on command and verify my error handling, without any real service being down.