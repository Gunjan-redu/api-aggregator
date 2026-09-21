import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import Query
from pydantic_settings import BaseSettings, SettingsConfigDict
from  pydantic import ConfigDict, Field

app = FastAPI()

class Settings(BaseSettings):
    news_api_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

class WeatherOut(BaseModel):
    city: str
    time: str
    temperature: float
    windspeed: float


class CurrencyOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_currency: str = Field(alias="from")
    to: str
    rate: float
    converted: float




class Article(BaseModel):
    title: str
    source: str
    url: str

class NewsOut(BaseModel):
    country: str
    articles : list[Article]

class AggregateOut(BaseModel):
    city: str
    weather: WeatherOut | None
    usd_to_inr: float | None        # or a small CurrencyOut slice
    news: NewsOut | None
    errors: list[str] = []

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


def get_weather_data(city:str) -> dict:
    lat, lon, name = get_coordinates(city)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = fetch_json(url, "weather")

    return {"city": name, **r["current_weather"]}


@app.get("/weather", response_model=WeatherOut)
def get_weather(city :str):
    return get_weather_data(city.title())

def currency_conversion_data(from_currency:str,to:str,  amount:float) ->dict :
    url = f"https://api.frankfurter.dev/v1/latest?base={from_currency}&symbols={to}"
    res = fetch_json(url, "currency conversion")
    rate = res["rates"][to]
    return {"from": from_currency, "to": to, "rate": rate, "converted": amount * rate}


@app.get("/currency", response_model= CurrencyOut)
def currency_conversion(from_currency: str = Query(alias="from"), to: str = Query(...) , amount : float = 1.0):
    return currency_conversion_data(from_currency.upper(), to.upper(), amount)

def get_news_data(country: str):
    country = country.lower()
    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={settings.news_api_key}&pageSize=5"
    res_articles = fetch_json(url, "NewsAPI")["articles"]

    articles = [{"title": a["title"], "source": a["source"]["name"], "url": a["url"]} for a in res_articles[: 5]]

    return {"country": country, "articles": articles}


@app.get("/news", response_model= NewsOut)
def get_news(country: str):
    return get_news_data(country)
