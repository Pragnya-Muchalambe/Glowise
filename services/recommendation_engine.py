
"""
Glowise 3.0 Recommendation Engine
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(name):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


PRODUCTS = load_json("products.json")
REMEDIES = load_json("remedies.json")
CONCERNS = load_json("concerns.json")


def normalize(text):
    return str(text).strip().lower()


def get_products(skin_type, concerns, limit=6):
    skin = normalize(skin_type)
    concern_names = [normalize(c["name"] if isinstance(c, dict) else c) for c in concerns]

    ranked = []

    for product in PRODUCTS:
        score = 0

        product_skin = [normalize(x) for x in product.get("skin_types", [])]
        product_concerns = [normalize(x) for x in product.get("concerns", [])]

        if "all" in product_skin or skin in product_skin:
            score += 3

        for c in concern_names:
            if c in product_concerns:
                score += 2

        if score:
            item = dict(product)
            item["score"] = score
            ranked.append(item)

    ranked.sort(key=lambda x: (x["score"], x.get("rating", 0)), reverse=True)
    return ranked[:limit]


def get_remedies(concerns, limit=5):
    concern_names = [normalize(c["name"] if isinstance(c, dict) else c) for c in concerns]

    remedies = []

    for remedy in REMEDIES:
        rc = normalize(remedy.get("concern"))

        if rc in concern_names:
            remedies.append(remedy)
            continue

        for c in concern_names:
            if rc in c or c in rc:
                remedies.append(remedy)
                break

    return remedies[:limit]


def build_routine(skin_type, concerns, weather):
    morning = [
        "Gentle Cleanser",
        "Moisturizer",
        "SPF 50 Sunscreen"
    ]

    night = [
        "Gentle Cleanser",
        "Moisturizer"
    ]

    use = set()
    avoid = set()
    lifestyle = []

    for concern in concerns:
        key = normalize(concern["name"] if isinstance(concern, dict) else concern)

        if key not in CONCERNS:
            continue

        data = CONCERNS[key]

        for i in data.get("ingredients_to_use", []):
            use.add(i)

        for i in data.get("ingredients_to_avoid", []):
            avoid.add(i)

        routine = data.get("routine", {})

        if routine.get("morning"):
            morning = routine["morning"]

        if routine.get("night"):
            night = routine["night"]

    temp = weather.get("temperature", 28)
    humidity = weather.get("humidity", 60)

    if temp >= 34:
        morning.append("Reapply sunscreen every 2-3 hours")
        lifestyle.append("Stay hydrated throughout the day.")

    if humidity < 40:
        night.append("Apply a hydrating sleeping mask.")

    return {
        "morning": morning,
        "night": night,
        "ingredients_to_use": sorted(use),
        "ingredients_to_avoid": sorted(avoid),
        "lifestyle": lifestyle
    }


def generate_recommendations(ai_result, weather):
    skin_type = ai_result.get("skin_type", "Combination")
    concerns = ai_result.get("concerns", [])

    return {
        "products": get_products(skin_type, concerns),
        "remedies": get_remedies(concerns),
        "routine": build_routine(skin_type, concerns, weather)
    }
