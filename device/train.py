import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
try:
    data = pd.read_csv("sound_ml_data.csv")
except FileNotFoundError:
    raise FileNotFoundError("The dataset file 'sound_ml_data.csv' was not found. Ensure it's in the correct directory.")

# Inspect dataset structure
print("Dataset Columns:", data.columns)
print(data.info())
print(data.describe())
print(data.head())

# Add a label column based on a threshold
threshold = 50  # Set the noise level threshold
data['label'] = data['decibels'].apply(lambda x: "Above Threshold" if x > threshold else "Below Threshold")

# Ensure the data has the necessary columns
if "decibels" not in data.columns or "label" not in data.columns:
    raise ValueError("The dataset does not contain the required 'decibels' or 'label' columns.")

# Handle invalid or missing data
data['decibels'] = pd.to_numeric(data['decibels'], errors='coerce')  # Convert to numeric
data = data.dropna(subset=['decibels', 'label'])  # Drop missing rows

# Encode labels
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
data['label'] = label_encoder.fit_transform(data['label'])

# Split data into features and target
X = data[['decibels']]  # Feature
y = data['label']  # Target

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate the model
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")

# Save the model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved as model.pkl")
