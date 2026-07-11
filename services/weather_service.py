"""
Glowise 3.0
Weather Service
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):

    if not API_KEY:

        return {
            "city": city,
            "temperature": 28,
            "humidity": 65,
            "description": "Weather unavailable",
            "uv_index": 5,
            "skincare_tip": "Add your OpenWeather API key."
        }

    try:

        response = requests.get(

            BASE_URL,

            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },

            timeout=5

        )

        data = response.json()

        temperature = round(data["main"]["temp"])

        humidity = data["main"]["humidity"]

        description = data["weather"][0]["description"].title()

        advice = generate_skincare_tip(
            temperature,
            humidity
        )

        return {

            "city": city,

            "temperature": temperature,

            "humidity": humidity,

            "description": description,

            "uv_index": estimate_uv(temperature),

            "skincare_tip": advice

        }

    except Exception:

        return {

            "city": city,

            "temperature": 27,

            "humidity": 60,

            "description": "Unavailable",

            "uv_index": 5,

            "skincare_tip": "Weather service unavailable."

        }


def estimate_uv(temp):

    if temp >= 38:
        return 11

    elif temp >= 35:
        return 9

    elif temp >= 30:
        return 7

    elif temp >= 25:
        return 5

    else:
        return 3


def generate_skincare_tip(temp, humidity):

    tips = []

    if temp >= 35:

        tips.append(
            "Use a lightweight gel moisturizer."
        )

        tips.append(
            "Avoid heavy creams."
        )

    if humidity >= 80:

        tips.append(
            "Cleanse twice daily to reduce excess oil."
        )

    if humidity <= 35:

        tips.append(
            "Use a hydrating moisturizer with hyaluronic acid."
        )

    if temp >= 30:

        tips.append(
            "Wear SPF 50+ sunscreen."
        )

        tips.append(
            "Reapply sunscreen every 2 hours."
        )

    if temp <= 18:

        tips.append(
            "Protect your skin barrier with ceramides."
        )

    if not tips:

        tips.append(
            "Maintain your regular skincare routine."
        )

    return tips


if __name__ == "__main__":

    print(

        get_weather(

            "Bangalore"

        )

    )