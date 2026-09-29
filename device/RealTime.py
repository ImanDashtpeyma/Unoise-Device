from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import matplotlib.pyplot as plt
import io
import matplotlib

# Use the Agg backend for non-interactive rendering
matplotlib.use("Agg")

app = Flask(__name__)

# Data storage for sound
sound_data = []

# Route to receive data
@app.route("/receive_data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if "sound" in data and "decibels" in data:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "value": f"Sound: {data['sound']}, Decibels: {data['decibels']}",
            "sound": data["sound"],
            "decibels": float(data["decibels"])
        }
        sound_data.append(entry)
        return jsonify({"message": "Data received successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400

# Route to generate and serve the chart as an image
@app.route("/chart")
def chart():
    if not sound_data:
        return jsonify({"error": "No data available"}), 404

    # Extract data for the plot
    timestamps = [entry["timestamp"] for entry in sound_data[-20:]]
    decibels = [entry["decibels"] for entry in sound_data[-20:]]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, decibels, marker="o", linestyle="-", label="Sound Level (dB)")
    plt.axhline(80, color="red", linestyle="--", label="Threshold (80 dB)")
    plt.xticks(rotation=45, fontsize=8)
    plt.ylabel("Decibels (dB)")
    plt.xlabel("Timestamp")
    plt.title("Sound Levels Over Time")
    plt.legend()
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    # Serve the image
    return send_file(img, mimetype="image/png")

# Route to display the dashboard
@app.route("/")
def display_dashboard():
    return render_template("index.html", data=sound_data[-20:])  # Pass the last 20 data entries to the template

if __name__ == "__main__":
    app.run(host="192.168.137.1", port=5000, debug=True)
