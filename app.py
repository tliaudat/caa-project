from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(os.path.abspath(env_path))
from flask import Flask, request, jsonify, send_file
from google.cloud import bigquery
from datetime import datetime, timezone
from weather_service import WeatherService
from tts_service import TTSService


app = Flask(__name__)

# === CONFIG BIGQUERY ===
project_id = "data-science-443020"
dataset_id = "weather_monitor"
table_name = "sensor_readings"
table_ref = f"{project_id}.{dataset_id}.{table_name}"
client = bigquery.Client(project=project_id)
tts_service = TTSService()

# === INIT WEATHER SERVICE ===
weather_service = WeatherService()

# === ENDPOINT 1 : Upload sensor data ===
@app.route("/upload", methods=["POST"])
def upload_data():
    data = request.json or {}
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    

    row = {
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "humidity":    data.get("humidity"),
        "temperature": data.get("temperature"),
        "tvoc":        data.get("tvoc")
    }

    errors = client.insert_rows_json(table_ref, [row])
    if errors:
        return jsonify({"error": errors}), 500

    return jsonify({"status": "success"}), 200



# === ENDPOINT 2 : Get current weather ===
@app.route("/weather", methods=["GET"])
def get_current_weather():
    location = request.args.get("location", "Lausanne,CH")
    try:
        data = weather_service.get_current_weather(location)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === ENDPOINT 3 : Get weather forecast ===
@app.route("/forecast", methods=["GET"])
def get_forecast():
    location = request.args.get("location", "Lausanne,CH")
    try:
        data = weather_service.get_forecast(location)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/announce", methods=["GET"])
def generate_audio():
    try:
        
        weather_data = weather_service.get_current_weather("Lausanne,CH")

        sensor_data = {} 

        announcement = tts_service.generate_announcement(weather_data, sensor_data)

        if not announcement:
            return jsonify({"message": "No announcement generated"}), 200

        
        output_path = tts_service.text_to_speech(announcement, filename="static/announcement.wav")
        if not output_path:
            return jsonify({"error": "Failed to synthesize speech"}), 500

        return jsonify({
            "message": "Audio generated",
            "text": announcement,
            "audio_url": "/audio"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/audio", methods=["GET"])
def serve_audio():
    if not os.path.exists("static/announcement.wav"):
        return jsonify({"error": "Audio file not found"}), 404
    return send_file("static/announcement.wav", mimetype="audio/wav")



# === LANCEMENT SERVEUR ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
