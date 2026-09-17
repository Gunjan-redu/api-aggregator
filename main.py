import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class WeatherOut(BaseModel):
    city: str
    time: str
    temperature: float
    windspeed: float



CITIES = {
    "Modinagar":   (28.83, 77.58) ,
    "Delhi":      (28.61, 77.21)  ,
    "London":    (51.50, 0.12)
}


@app.get("/weather", response_model= WeatherOut)
def get_weather(city :str):
    city = city.title()
    if  city not in CITIES:
        raise HTTPException(status_code=404, detail=f"Unknown city. Supported: {', '.join(CITIES)}")
    lat = CITIES[city][0]
    long = CITIES[city][1]
    r = httpx.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current_weather=true")
    return {"city": city, **r.json()["current_weather"]}
