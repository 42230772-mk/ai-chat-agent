import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/current.json"


def get_current_weather(location: str) -> str:
    """
    Calls WeatherAPI.com Current Weather endpoint and returns a short, readable summary.
    """
    if not WEATHER_API_KEY:
        raise RuntimeError("Missing WEATHER_API_KEY in .env")

    location = (location or "").strip()
    if not location:
        return "Please provide a location (example: Beirut)."

    params = {"key": WEATHER_API_KEY, "q": location, "aqi": "no"}

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        loc = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        feelslike_c = data["current"]["feelslike_c"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]

        return (
            f"Weather in {loc}, {country}: {condition}, {temp_c}°C "
            f"(feels like {feelslike_c}°C). Humidity {humidity}%, wind {wind_kph} kph."
        )

    except requests.HTTPError:
        # WeatherAPI often returns helpful error messages in JSON
        try:
            err = resp.json()
            msg = err.get("error", {}).get("message", "Weather API request failed.")
            return f"Weather API error: {msg}"
        except Exception:
            return "Weather API error: request failed."

    except requests.RequestException:
        return "Network error while calling Weather API. Check your internet connection."
    except (KeyError, TypeError):
        return "Unexpected response format from Weather API."
