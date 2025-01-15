from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import matplotlib.pyplot as plt
import io
import matplotlib
import pickle

# Use the Agg backend for non-interactive rendering
matplotlib.use("Agg")

app = Flask("app")

# Load the trained ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

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
    plt.axhline(50, color="red", linestyle="--", label="Threshold (85 dB)")
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

# Route to predict noise levels using the ML model
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if "decibels" in data:
        # Prepare data for prediction
        decibel_value = [[float(data["decibels"])]]
        prediction = model.predict(decibel_value)
        # Decode prediction result
        label_map = {0: " Above Threshold", 1: "Below Threshold"}  # Adjust based on label encoding
        return jsonify({
            "decibels": data["decibels"],
            "prediction": label_map[prediction[0]]
        }), 200
    return jsonify({"error": "Invalid input"}), 400

# Default route for the dashboard
@app.route("/")
def display_dashboard():
    return render_template("index.html", data=sound_data[-20:])  # Pass the last 20 data entries to the template

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)