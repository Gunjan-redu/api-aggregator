import httpx


r = httpx.get("https://api.open-meteo.com/v1/forecast?latitude=28.83&longitude=47&current_weather=true")
news = httpx.get("https://newsapi.org/v2/everything?q=Apple&from=2026-09-17&sortBy=popularity&apiKey=2f7d298cf48047d5aa6dfe114c1acc9e")
print(r.status_code)
print(r.json())
print(r.json()["current_weather_units"])