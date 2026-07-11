"""
==========================================================
Glowise 3.0
Gemini AI Service
==========================================================
"""

import json
import os
import time

from dotenv import load_dotenv
from PIL import Image
from google import genai


# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()


# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(

    api_key=os.getenv("GEMINI_API_KEY")

)

MODEL = "gemini-2.5-flash"


# ==========================================================
# FACE ANALYSIS PROMPT
# ==========================================================

FACE_ANALYSIS_PROMPT = """
You are Glowise AI.

You are an intelligent skincare analysis assistant.

Your task is to analyze ONLY the visible facial skin.

IMPORTANT RULES

• Never diagnose diseases.

• Never guess age.

• Never guess gender.

• Never guess ethnicity.

• Never invent skin concerns.

• Mention ONLY what is visible.

• If lighting is poor,
say confidence is low.

• If the skin looks healthy,
say so.

Return ONLY valid JSON.

Schema:

{
    "skin_score":85,

    "skin_type":"Combination",

    "summary":"",

    "confidence":"High",

    "concerns":[

        {
            "name":"Oiliness",
            "severity":"Low",
            "description":"Visible shine around the forehead."
        }

    ]
}

Allowed Skin Types

Oily

Dry

Combination

Normal

Sensitive


Allowed Concerns

Acne

Oiliness

Pigmentation

Dark Circles

Dryness

Redness

Sensitivity


Allowed Severity

Low

Medium

High


Allowed Confidence

High

Medium

Low


Summary Rules

Write 4-6 natural sentences.

Describe ONLY what is visible.

Mention:

• Overall appearance

• Texture

• Shine

• Oiliness

• Dryness

• Acne

• Pigmentation

• Redness

• Dark circles

If no concern is visible,
say the skin appears healthy.

Do not repeat yourself.

Return ONLY JSON.

No markdown.

No explanation.

No code blocks.
"""


# ==========================================================
# FACE ANALYSIS
# ==========================================================

def analyze_face(image_path: str):

    image = Image.open(image_path)

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(

                model=MODEL,

                contents=[

                    FACE_ANALYSIS_PROMPT,

                    image

                ]

            )

            text = response.text.strip()

            print("\n========== GEMINI RAW RESPONSE ==========")
            print(text)
            print("=========================================\n")

            text = (

                text
                .replace("```json", "")
                .replace("```", "")
                .strip()

            )

            try:

                result = json.loads(text)

            except Exception:

                result = {

                    "skin_score": 75,

                    "skin_type": "Combination",

                    "summary": text,

                    "confidence": "Low",

                    "concerns": []

                }

            result.setdefault(

                "skin_score",

                75

            )

            result.setdefault(

                "skin_type",

                "Combination"

            )

            result.setdefault(

                "summary",

                "Skin analysis completed."

            )

            result.setdefault(

                "confidence",

                "Medium"

            )

            result.setdefault(

                "concerns",

                []

            )
            allowed_concerns = {

                "Acne",

                "Oiliness",

                "Pigmentation",

                "Dark Circles",

                "Dryness",

                "Redness",

                "Sensitivity"

            }

            cleaned = []

            for item in result["concerns"]:

                if not isinstance(item, dict):

                    continue

                name = item.get(

                    "name",

                    ""

                ).strip()

                severity = item.get(

                    "severity",

                    "Low"

                ).strip()

                description = item.get(

                    "description",

                    ""

                ).strip()

                if name not in allowed_concerns:

                    continue

                if severity not in [

                    "Low",

                    "Medium",

                    "High"

                ]:

                    severity = "Low"

                if not description:

                    description = (

                        "Visible characteristics detected in the uploaded image."

                    )

                cleaned.append({

                    "name": name,

                    "severity": severity,

                    "description": description

                })

            result["concerns"] = cleaned

            # -----------------------------
            # Clamp Skin Score
            # -----------------------------

            try:

                score = int(result["skin_score"])

            except Exception:

                score = 75

            score = max(

                40,

                min(

                    98,

                    score

                )

            )

            result["skin_score"] = score

            return result

        except Exception as e:

            last_error = e

            time.sleep(2)

    raise Exception(

        f"Gemini Error: {last_error}"

    )
    # ==========================================================
# GLOWISE AI CHATBOT
# ==========================================================

CHATBOT_PROMPT = """
You are Glowise AI.

You are a friendly AI skincare assistant.

You ONLY answer questions related to:

• Skincare
• Skin Types
• Acne
• Pigmentation
• Dark Circles
• Dryness
• Oiliness
• Cleansers
• Moisturizers
• Sunscreen
• Serums
• Ingredients
• Home Remedies
• Lifestyle
• Sun Protection

Rules:

1. Keep answers concise.

2. Use simple English.

3. Give practical advice.

4. Never diagnose diseases.

5. If someone asks about a medical condition,
recommend consulting a dermatologist.

6. If the question is unrelated to skincare,
politely explain that you only answer skincare-related questions.

Avoid long paragraphs.
"""


def ask_glowise(question: str):

    """
    Glowise AI Chatbot
    """

    if not question.strip():

        return "Please enter a skincare question."

    prompt = f"""

{CHATBOT_PROMPT}

User Question:

{question}

"""

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(

                model=MODEL,

                contents=prompt

            )

            if response.text:

                return response.text.strip()

            return "Sorry, I couldn't generate a response."

        except Exception as e:

            last_error = e

            time.sleep(2)

    return f"AI Error: {last_error}"
# ==========================================================
# INGREDIENT ANALYZER
# ==========================================================

INGREDIENT_PROMPT = """
You are Glowise AI.

Analyze the uploaded skincare product ingredient label.

Your task is to explain the ingredients in simple language.

Include:

1. Safe ingredients
2. Ingredients that may cause irritation
3. Suitable skin types
4. Possible side effects (if any)
5. Overall verdict

Rules:

- Keep the response under 250 words.
- Use beginner-friendly English.
- Never diagnose diseases.
- Mention only ingredients that are visible on the label.
"""


def analyze_ingredients(image_path: str):

    """
    Analyze a skincare ingredient label using Gemini Vision.
    """

    image = Image.open(image_path)

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(

                model=MODEL,

                contents=[

                    INGREDIENT_PROMPT,

                    image

                ]

            )

            if response.text:

                return response.text.strip()

            return "Unable to analyze ingredients."

        except Exception as e:

            last_error = e

            time.sleep(2)

    return f"Ingredient Analysis Error: {last_error}"


# ==========================================================
# END OF FILE
# ==========================================================