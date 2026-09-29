import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, median_absolute_error, mean_squared_error, mean_absolute_percentage_error
from statsmodels.tsa.arima.model import ARIMA
from keras.models import Sequential
from keras.layers import Input, Dense, LSTM, Conv1D, MaxPooling1D, Flatten
from datetime import timedelta
import json

def load_noise_data(file_path='../data/noise_data.csv'):
    """
    Load noise data from a CSV file and prepare it for analysis.
    """
    data = pd.read_csv(file_path, parse_dates=['timestamp'])
    data = data.sort_values(by='timestamp')
    data['time_index'] = np.arange(len(data))
    return data

def save_results(predictions, metrics, comparison_chart_path, output_dir='results'):
    """
    Save predictions, metrics, and chart to disk.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save predictions
    predictions_df = pd.DataFrame(predictions)
    predictions_df.to_csv(os.path.join(output_dir, 'predictions.csv'), index=False)

    # Save metrics
    with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

    # Save chart
    plt.savefig(comparison_chart_path)

def generate_predictions(file_path='../data/noise_data.csv', output_dir='results'):
    """
    Generate predictions using multiple models and save results.
    """
    data = load_noise_data(file_path)
    X = data[['time_index']]
    y = data['decibels']
    timestamps = data['timestamp']

    # Define training
    train_X = X
    train_y = y

    # Predictions for the last 30 actual and next 20 forecasted
    last_30_indices = np.arange(len(y) - 30, len(y))
    future_indices = np.arange(len(y), len(y) + 20)

    predictions = {}
    metrics = {}

    # ARIMA
    arima_model = ARIMA(train_y, order=(5, 1, 0)).fit()
    arima_preds_30 = arima_model.forecast(steps=30).tolist()
    arima_preds_20 = arima_model.forecast(steps=20).tolist()
    predictions['ARIMA'] = arima_preds_30 + arima_preds_20
    metrics['ARIMA'] = {
        'MAE': mean_absolute_error(y.iloc[-30:], arima_preds_30),
        'MedAE': median_absolute_error(y.iloc[-30:], arima_preds_30),
        'MSE': mean_squared_error(y.iloc[-30:], arima_preds_30),
        'RMSE': np.sqrt(mean_squared_error(y.iloc[-30:], arima_preds_30)),
        'MAPE': mean_absolute_percentage_error(y.iloc[-30:], arima_preds_30)
    }

    # Random Forest
    rf_model = RandomForestRegressor(random_state=42, n_jobs=-1)
    rf_model.fit(train_X, train_y)
    rf_preds_30 = rf_model.predict(X.iloc[last_30_indices]).tolist()
    rf_preds_20 = rf_model.predict(pd.DataFrame({'time_index': future_indices})).tolist()
    predictions['Random Forest'] = rf_preds_30 + rf_preds_20
    metrics['Random Forest'] = {
        'MAE': mean_absolute_error(y.iloc[-30:], rf_preds_30),
        'MedAE': median_absolute_error(y.iloc[-30:], rf_preds_30),
        'MSE': mean_squared_error(y.iloc[-30:], rf_preds_30),
        'RMSE': np.sqrt(mean_squared_error(y.iloc[-30:], rf_preds_30)),
        'MAPE': mean_absolute_percentage_error(y.iloc[-30:], rf_preds_30)
    }

    # XGBoost
    xgb_model = XGBRegressor(random_state=42, n_jobs=-1)
    xgb_model.fit(train_X, train_y)
    xgb_preds_30 = xgb_model.predict(X.iloc[last_30_indices]).tolist()
    xgb_preds_20 = xgb_model.predict(pd.DataFrame({'time_index': future_indices})).tolist()
    predictions['XGBoost'] = xgb_preds_30 + xgb_preds_20
    metrics['XGBoost'] = {
        'MAE': mean_absolute_error(y.iloc[-30:], xgb_preds_30),
        'MedAE': median_absolute_error(y.iloc[-30:], xgb_preds_30),
        'MSE': mean_squared_error(y.iloc[-30:], xgb_preds_30),
        'RMSE': np.sqrt(mean_squared_error(y.iloc[-30:], xgb_preds_30)),
        'MAPE': mean_absolute_percentage_error(y.iloc[-30:], xgb_preds_30)
    }

    # SVM
    svm_model = SVR()
    svm_model.fit(train_X, train_y)
    svm_preds_30 = svm_model.predict(X.iloc[last_30_indices]).tolist()
    svm_preds_20 = svm_model.predict(pd.DataFrame({'time_index': future_indices})).tolist()
    predictions['SVM'] = svm_preds_30 + svm_preds_20
    metrics['SVM'] = {
        'MAE': mean_absolute_error(y.iloc[-30:], svm_preds_30),
        'MedAE': median_absolute_error(y.iloc[-30:], svm_preds_30),
        'MSE': mean_squared_error(y.iloc[-30:], svm_preds_30),
        'RMSE': np.sqrt(mean_squared_error(y.iloc[-30:], svm_preds_30)),
        'MAPE': mean_absolute_percentage_error(y.iloc[-30:], svm_preds_30)
    }

    # Generate timestamps
    prediction_timestamps = pd.concat([timestamps.iloc[-30:], pd.Series([timestamps.iloc[-1] + timedelta(seconds=i) for i in range(1, 21)])], ignore_index=True)

    # Plot
    plt.figure(figsize=(12, 8))
    plt.plot(timestamps.iloc[-30:], y.iloc[-30:], label='Actual', linestyle='dashed', color='black')
    for model, preds in predictions.items():
        plt.plot(prediction_timestamps, preds, label=model)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%d/%m %H:%M'))
    plt.xticks(rotation=45)
    plt.legend()
    plt.title('Prediction Comparison')
    plt.xlabel('Timestamp')
    plt.ylabel('Decibels')
    plt.grid()

    # Save results
    comparison_chart_path = os.path.join(output_dir, 'comparison_chart.png')
    save_results(predictions, metrics, comparison_chart_path)

if __name__ == '__main__':
    generate_predictions()
