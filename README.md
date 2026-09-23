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

<!-- REPLACE EACH LINE WITH 1-2 SENTENCES IN YOUR OWN WORDS.
     These bullets are also the outline of the blog post. -->

- **Chaining API calls:** [the two-hop geocoding chain — one API's output
  feeding the next one's input]
- **Whose failure is it:** [500 vs 502 vs 504 — translating upstream
  failures into honest status codes instead of blaming my own server]
- **Graceful degradation:** [the /aggregate design decision — bad input
  kills the request, upstream failures degrade; what the keyboard-mash
  city taught me]
- **Caching:** [the TTL cache — what it saves, and its honest limits:
  dies with the process, not shared across workers]
- **Testing with mocks:** [replacing httpx with a fake so tests can stage
  disasters — testing the fire drill without burning the building]
