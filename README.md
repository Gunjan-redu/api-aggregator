# API-Aggregator

A FastAPI service that fetches and combines data from multiple external
APIs, current weather for any city, live currency conversion, and top
news headlines. My first project consuming external APIs. **Work in progress.**
---
## Stack
- FastAPI
- httpx
- Pydantic
- External APIs: Open-Meteo (geocoding + weather), Frankfurter (currency), NewsAPI (headlines)

## Endpoints
- `GET /weather?city={name}` — current temperature, windspeed and time for
  any city, geocoded by name. Returns 404 for unknown cities; 502/504 when
  the upstream service fails or times out.

- `GET /currency?from={code}&to={code}&amount={n}` — converts an amount
  between currencies using live rates.

- `GET /news?country={code}` — top 5 news headlines for a country
  (two-letter code, e.g. `in`, `us`), reshaped to title, source and URL.
  502/504 when the upstream service fails or times out.

## Planned
- Currency conversion (Frankfurter)
- News headlines (NewsAPI)
- Combined `/aggregate` endpoint
- Tests (pytest)

