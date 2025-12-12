import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class TimeSeriesAI:
    def generate_historical_data(self, sensor_type, timeframe):
        """Generate data for any time period user requests"""
        if timeframe == 'yesterday':
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()
            freq = '1H'
        elif timeframe == 'last week':
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            freq = '6H'
        elif timeframe == 'last month':
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            freq = '1D'
        else:  # recent / last hour
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now()
            freq = '1T'  # 1 minute
        
        # Generate synthetic data
        return self.create_time_series_data(sensor_type, start_date, end_date, freq)
    
    def create_time_series_data(self, sensor_type, start, end, freq):
        """Create realistic sensor data for given period"""
        time_range = pd.date_range(start=start, end=end, freq=freq)
        
        if sensor_type == 'temperature':
            base_temp = 22
            data = [base_temp + np.sin(i/24 * 2*np.pi) * 5 + random.uniform(-1, 1) for i in range(len(time_range))]
        elif sensor_type == 'humidity':
            data = [50 + np.sin(i/24 * 2*np.pi) * 20 + random.uniform(-5, 5) for i in range(len(time_range))]
        elif sensor_type == 'heart_rate':
            data = [72 + random.uniform(-3, 3) for _ in range(len(time_range))]
        elif sensor_type == 'vehicle':
            data = [65 + random.uniform(-10, 10) for _ in range(len(time_range))]
        elif sensor_type == 'pressure':
            data = [1013 + random.uniform(-10, 10) for _ in range(len(time_range))]
        else:
            data = [random.uniform(0, 100) for _ in range(len(time_range))]
        
        return pd.DataFrame({
            'timestamp': time_range,
            'value': data
        })