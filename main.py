import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class WeatherOut(BaseModel):
    city: str
    time: str
    temperature: float
    windspeed: float


def fetch_json(url:str, name: str)-> dict:
    try:
        res = httpx.get(url, timeout=5.0)
        res.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(status_code= 504, detail= f"{name} service timed out")

    except httpx.HTTPError:
        raise  HTTPException(status_code= 502, detail=f"{name} service not available")

    return res.json()


def get_coordinates(city:str) -> tuple[float, float, str]:
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    res = fetch_json(url, "coordinates")

    if not res.get("results"):
        raise HTTPException(status_code=404, detail="Unknown City")
    row = res["results"][0]
    return row["latitude"], row["longitude"], row["name"]

@app.get("/weather", response_model=WeatherOut)
def get_weather(city :str):
    city = city.title()
    lat, lon, name = get_coordinates(city)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = fetch_json(url, "weather")

    return {"city": name, **r["current_weather"]}
