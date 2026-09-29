from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Data Sound storage
sound_data = []

# displaying data
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sound Data Monitor</title>
    <meta http-equiv="refresh" content="2"> <!-- Auto-refresh every 2 seconds -->
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 50%; border-collapse: collapse; }
        th, td { padding: 8px; border: 1px solid black; text-align: center; }
    </style>
</head>
<body>
    <h1>Sound Data Monitor</h1>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Sound and Decibels</th>
        </tr>
        {% for entry in data %}
        <tr>
            <td>{{ entry.timestamp }}</td>
            <td>{{ entry.value }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Route to receive data
@app.route("/receive_data", methods=["POST"])
def receive_data():
    data = request.get_json()
    # print("Received JSON:", data)  # Debugging print
    if "sound" in data and "decibels" in data:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "value": f"Sound: {data['sound']}, Decibels: {data['decibels']}"
        }
        sound_data.append(entry)
        print(f"Received Data: {entry}")
        return jsonify({"message": "Data received successfully"}), 200
    return jsonify({"error": "Invalid data"}), 400
print("Received JSON:", sound_data)
# Route to display data
@app.route("/")
def display_data():
    return render_template_string(HTML_TEMPLATE, data=sound_data[-20:])  # Show last 20 entries

if __name__ == "__main__":
    app.run(host="192.168.0.3", port=5000, debug=True)
