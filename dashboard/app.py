import os
# Suppress TensorFlow logs and disable oneDNN custom operations
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from flask import Flask, jsonify, render_template, send_file
from model.classify_model import classify_dataset, generate_summary, classify_noise_level
from model.predict_model import generate_predictions
import pandas as pd
import json
import random # TODO: Replace this with actual real-time model predictions

app = Flask(__name__)

# Model training results folder
RESULTS_DIR = 'model/results'

# Load the dataset
data = pd.read_csv('data/noise_data.csv')

# Global variable to store the last measurement
last_measurement = None

@app.route('/')
def home():
    """
    Route to render the index page.
    """
    return render_template('index.html')

def get_realtime_measurement():
    """
    Simulates fetching real-time noise levels.
    Replace this with actual logic to fetch real-time data from the model.
    """
    # Example: Random value between 50 and 130 dB
    return random.uniform(50, 130)

@app.route('/realtime_value', methods=['GET'])
def realtime_value():
    """
    Endpoint to fetch the real-time noise measurement.
    """
    global last_measurement
    last_measurement = get_realtime_measurement()
    return jsonify({'current_measurement': last_measurement})

@app.route('/realtime_status', methods=['GET'])
def realtime_status():
    """
    Endpoint to fetch the current noise classification status based on the last measurement.
    """
    global last_measurement
    if last_measurement is None:
        return jsonify({'error': 'No measurement available'}), 400
    classification = classify_noise_level(last_measurement)
    return jsonify({'classification': classification})


@app.route('/model_classify', methods=['GET'])
def model_classify():
    """
    Endpoint to classify the dataset and return a summary.
    """
    try:
        # Classify the dataset
        classified_data = classify_dataset(data)
        # Generate the summary
        summary = generate_summary(classified_data)
        return jsonify({'summary': summary})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/dashboard_classify')
def dashboard_classify():
    """
    Route to render the classification dashboard.
    """
    return render_template('classify.html')


@app.route('/model_predict', methods=['GET'])
def model_predict():
    """
    Loads pre-computed predictions and metrics, and returns them.
    """
    # Load predictions
    predictions_path = os.path.join(RESULTS_DIR, 'predictions.csv')
    predictions_df = pd.read_csv(predictions_path)

    # Load metrics
    metrics_path = os.path.join(RESULTS_DIR, 'metrics.json')
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    # Return predictions, metrics, and chart URL
    return jsonify({
        "predictions": predictions_df.to_dict(orient="list"),
        "metrics": metrics,
        "chart_url": "/results_chart"
    })

@app.route('/results_chart', methods=['GET'])
def results_chart():
    """
    Endpoint to serve the prediction chart.
    """
    chart_path = os.path.join(RESULTS_DIR, 'comparison_chart.png')
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype='image/png')
    else:
        return jsonify({'error': 'Chart not found'}), 404
    
@app.route('/dashboard_predict')
def dashboard_predict():
    """
    Renders the prediction dashboard.
    """
    return render_template('predict.html')

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=10000, debug=True)
