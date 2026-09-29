from flask import Flask, request, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__)

# CSV file path for machine learning data
CSV_FILE = "sound_ml_data.csv"

# Ensure CSV file exists with proper headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "sound", "decibels"])  # Headers

# Route to receive data and save it for ML
@app.route("/receive_data", methods=["POST"])
def receive_data():
    try:
        # Parse incoming JSON data
        data = request.get_json()
        if not data or "sound" not in data or "decibels" not in data:
            return jsonify({"error": "Invalid JSON keys"}), 400

        # Prepare the data row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sound = data["sound"]
        decibels = data["decibels"]

        # Append data to CSV
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, sound, decibels])

        print(f"Data saved: Timestamp={timestamp}, Sound={sound}, Decibels={decibels}")

        return jsonify({"message": "Data received and saved successfully"}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="192.168.0.3", port=5000, debug=True)
