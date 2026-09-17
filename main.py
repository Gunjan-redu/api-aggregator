import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class WeatherOut(BaseModel):
    city: str
    time: str
    temperature: float
    windspeed: float


def get_coordinates(city:str) -> tuple[float, float, str]:
    res = httpx.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
    if not res.get("results"):
        raise HTTPException(status_code=404, detail="Unknown City")

    lat = res["results"][0]["latitude"]
    lon = res["results"][0]["longitude"]
    name= res ["results"] [0] ["name"]
    return lat, lon, name

@app.get("/weather", response_model= WeatherOut)
def get_weather(city :str):
    city = city.title()
    lat, lon, name = get_coordinates(city)
    r = httpx.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
    return {"city": name, **r.json()["current_weather"]}
