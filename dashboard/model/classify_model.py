import pandas as pd

# Classification Function
def classify_noise_level(decibels):
    """
    Classifies noise levels into categories based on decibels.
    """
    if decibels > 120:
        return "Very Dangerous"
    elif decibels >= 85:
        return "Dangerous"
    elif decibels >= 70:
        return "Caution"
    else:
        return "Safe"

# Function to classify a dataset
def classify_dataset(data):
    """
    Classifies a dataset containing decibel values.
    """
    if 'decibels' not in data.columns:
        raise ValueError('The dataset must contain a "decibels" column.')
    
    # Apply classification
    data['classification'] = data['sound'].apply(classify_noise_level)
    return data

# Function to generate summary
def generate_summary(data):
    """
    Generates a summary of the classification counts.
    """
    summary = data['classification'].value_counts().reindex(
        ["Safe", "Caution", "Dangerous", "Very Dangerous"], fill_value=0
    ).to_dict()
    return summary
