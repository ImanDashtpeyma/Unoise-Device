# Unoise: Urban Noise Monitoring and Control System

![CI](https://github.com/ImanDashtpeyma/Unoise-Device/actions/workflows/ci.yml/badge.svg)

Unoise is an IoT prototype that measures urban noise with a sound sensor, classifies the readings with a machine learning model and shows them on a web dashboard. It was built by Iman Dashtpeyma and Jady Pamella Barbacena da Silva for the course *Internet of Things Services* (autumn 2024) at the Department of Computer and Systems Sciences, Stockholm University.

This repository contains the **device side**: the Arduino code, the Raspberry Pi scripts and the Flask gateway that receives sensor data, classifies it and serves a simple dashboard.

## How it works

```
Sound sensor -> Arduino UNO R4 WiFi -> (Wi-Fi) -> Raspberry Pi -> Flask gateway -> dashboard
                                                                  \-> ML model (Random Forest)
```

1. The sound sensor is analog, so an Arduino reads it and sends the values over Wi-Fi (the Raspberry Pi cannot read analog input directly).
2. The Raspberry Pi collects and processes the data with Python scripts.
3. The Flask app receives each reading, classifies it with a trained model and keeps the latest values for the dashboard and a chart.

Noise limits used in the project: below 70 dB safe, from 70 dB caution, from 85 dB dangerous, from 120 dB very dangerous.

## Repository layout

| Path | What it is |
|---|---|
| `app.py` | Flask gateway: receives sensor data, classifies it, serves the chart and dashboard |
| `model.pkl` | Trained Random Forest classifier (scikit-learn 1.6.1) |
| `Arduino-R4/` | Arduino UNO R4 WiFi sketches (sound sensor, Wi-Fi, SSL connection) |
| `device/` | Raspberry Pi scripts and training code |
| `dashboard/` | Second Flask app with the ML experiments and the dashboard pages |
| `tests/` | Automated tests (pytest) |
| `Dockerfile`, `.github/workflows/ci.yml` | Container image and CI pipeline |

## API

| Method | Route | Description |
|---|---|---|
| POST | `/receive_data` | Body `{"sound": <value>, "decibels": <number>}`. Stores the reading and adds the model's prediction |
| POST | `/predict` | Body `{"decibels": <number>}`. Returns `Above Threshold` or `Below Threshold` |
| GET | `/chart` | PNG chart of the last 20 readings (404 if there is no data yet) |
| GET | `/` | Dashboard page |

Example:

```bash
curl -X POST http://localhost:10000/receive_data \
  -H "Content-Type: application/json" \
  -d '{"sound": 140, "decibels": 72.5}'
```

## Run it locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:10000
```

With Docker:

```bash
docker build -t unoise-device .
docker run -p 10000:10000 unoise-device
```

## Tests and CI

```bash
pip install pytest
python -m pytest -v
```

On every push and pull request, GitHub Actions installs the dependencies, runs the tests, builds the Docker image and does a smoke test of the running container.

## Results

We compared four models for noise prediction on the collected data. Random Forest gave the lowest error.

| Model | MAE | RMSE |
|---|---|---|
| Random Forest | 1.05 | 1.24 |
| SVM | 2.87 | 3.24 |
| XGBoost | 2.90 | 3.25 |
| ARIMA | 3.09 | 3.40 |

Random Forest showed some signs of overfitting, and the dataset is small, so these numbers describe the prototype, not a production system. The full numbers are in `dashboard/model/results/metrics.json`.

## Limitations

- This is a prototype tested in a controlled environment and a small urban area.
- Wind and distant sounds disturbed the sensor, and hotspot connections were unreliable, so we used a dedicated Wi-Fi network.
- The real-time value in the `dashboard/` app is still a placeholder (random numbers) and is marked as a TODO in the code.
- The Arduino sketches need your own Wi-Fi name, password and server address before they will work.

## Future work

GPS and heatmaps for spatial analysis, a mobile app, more sensors across a larger area, and better models and noise reduction.

## Authors

Iman Dashtpeyma and Jady Pamella Barbacena da Silva. Supervisor: Rahim Rahmani.
