from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import matplotlib.pyplot as plt
import io
import matplotlib
import pickle
import csv  # For saving data to CSV

# Use the Agg backend for non-interactive rendering
matplotlib.use("Agg")

app = Flask("app")

# Load the trained ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Data storage for sound
sound_data = []

# Labels used by the trained model (adjust based on label encoding)
LABEL_MAP = {0: "Above Threshold", 1: "Below Threshold"}


def predict_label(decibels):
    """Predict the noise class for one decibel value with the local model."""
    # scikit-learn expects a 2D array: one row, one feature
    prediction = model.predict([[float(decibels)]])
    return LABEL_MAP[int(prediction[0])]


def save_to_csv(entry):
    file_name = "static/sound_ml_data.csv"

    # Read existing data if the file exists
    try:
        with open(file_name, mode="r", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            existing_data = list(reader)
    except FileNotFoundError:
        existing_data = []

    # Prepend the new entry
    updated_data = [entry] + existing_data

    # Write all data back to the file, with the new entry at the top
    with open(file_name, mode="w", newline="") as csv_file:
        fieldnames = ["timestamp", "sound", "decibels", "prediction"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write all rows
        writer.writerows(updated_data)


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
        
        # Classify the reading with the local ML model
        try:
            entry["prediction"] = predict_label(entry["decibels"])
        except Exception as e:
            entry["prediction"] = f"Error: {str(e)}"

        # Save to sound_data and CSV
        sound_data.append(entry)
        save_to_csv(entry)

        return jsonify({"message": "Data received and processed successfully", "entry": entry}), 200
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
    plt.axhline(85, color="red", linestyle="--", label="Threshold (85 dB)")
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

# Route to predict noise levels using the local ML model
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if "decibels" in data:
        return jsonify({
            "decibels": data["decibels"],
            "prediction": predict_label(data["decibels"])
        }), 200
    return jsonify({"error": "Invalid input"}), 400

# Default route for the dashboard
@app.route("/")
def display_dashboard():
    return render_template("index.html", data=sound_data[-20:])  # Pass the last 20 data entries to the template

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
