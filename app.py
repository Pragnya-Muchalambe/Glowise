
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

from config import Config, allowed_file
from database import (
    initialize_database,
    save_analysis,
    get_history,
    delete_analysis,
)

from services.gemini_service import (
    analyze_face,
    ask_glowise,
)

from services.weather_service import get_weather
from services.recommendation_engine import generate_recommendations

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/chat")
def chat_page():
    return render_template("chatbot.html")


@app.route("/api/status")
def status():
    return jsonify({
        "status": "running",
        "version": "Glowise 3.0"
    })


@app.route("/api/history")
def api_history():
    return jsonify(get_history())


@app.route("/api/delete/<int:analysis_id>", methods=["DELETE"])
def delete_record(analysis_id):
    delete_analysis(analysis_id)
    return jsonify({"success": True})


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "Bangalore")
    return jsonify(get_weather(city))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    question = data.get("question", "")
    answer = ask_glowise(question)
    return jsonify({"answer": answer})


@app.route("/api/face-analysis", methods=["POST"])
def face_analysis():

    if "photo" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image uploaded."
        }), 400

    photo = request.files["photo"]

    if photo.filename == "":
        return jsonify({
            "success": False,
            "message": "Empty filename."
        }), 400

    if not allowed_file(photo.filename):
        return jsonify({
            "success": False,
            "message": "Only JPG, JPEG, PNG and WEBP files are allowed."
        }), 400

    filename = f"{uuid.uuid4()}_{secure_filename(photo.filename)}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    photo.save(filepath)

    try:

        ai_result = analyze_face(filepath)

        city = request.form.get("city", "Bangalore")
        weather = get_weather(city)

        recommendations = generate_recommendations(
            ai_result,
            weather
        )

        response = {
            "success": True,
            "skin_score": ai_result.get("skin_score", 75),
            "skin_type": ai_result.get("skin_type", "Unknown"),
            "summary": ai_result.get("summary", ""),
            "concerns": ai_result.get("concerns", []),
            "morning": recommendations["routine"]["morning"],
            "night": recommendations["routine"]["night"],
            "ingredients_to_use": recommendations["routine"]["ingredients_to_use"],
            "ingredients_to_avoid": recommendations["routine"]["ingredients_to_avoid"],
            "lifestyle": recommendations["routine"]["lifestyle"],
            "products": recommendations["products"],
            "remedies": recommendations["remedies"],
            "weather": weather
        }

        save_analysis(
            filepath,
            response["skin_score"],
            response["skin_type"],
            response["concerns"],
            response["products"],
            response["remedies"],
            response["weather"]
        )

        return jsonify(response)

    except Exception as e:

        import traceback

        traceback.print_exc()

        print("=" * 50)
        print("FULL ERROR:")
        print(repr(e))
        print("=" * 50)

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


if __name__ == "__main__":
    app.run(debug=True)
