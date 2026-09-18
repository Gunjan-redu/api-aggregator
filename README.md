# API-Aggregator

A FastAPI service that returns current weather for any city in the world.
My first project consuming external APIs. **Work in progress.**
---
## Stack
- FastAPI
- httpx
- Pydantic
- External APIs: Open-Meteo (geocoding + weather)

## Endpoints
- `GET /weather?city={name}` — current temperature, windspeed and time for
  any city, geocoded by name. Returns 404 for unknown cities; 502/504 when
  the upstream service fails or times out.

## Planned
- Currency conversion (Frankfurter)
- News headlines (NewsAPI)
- Combined `/aggregate` endpoint
- Tests (pytest)

