import pandas as pd
import numpy as np
import os

def predict_next_value(csv_file):
    try:
        if not os.path.exists(csv_file):
            return 0
            
        df = pd.read_csv(csv_file)
        
        if len(df) < 2:
            return 0

        # Handle different column names
        if 'sensor_value' in df.columns:
            values_column = 'sensor_value'
        elif 'value' in df.columns:
            values_column = 'value'
        else:
            # Use first numeric column
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                values_column = numeric_columns[0]
            else:
                return 0

        last_two = df[values_column].tail(2)
        diff = last_two.iloc[-1] - last_two.iloc[-2]
        predicted = last_two.iloc[-1] + diff

        return round(predicted, 2)
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0