import pandas as pd
import numpy as np
import json
import re
import os
import glob

class UniversalDataReader:
    def __init__(self):
        self.sensor_profiles = {}
        self.data_patterns = {}
        
    def auto_detect_sensor_type(self, data_sample):
        """AI automatically detects what type of sensor data this is"""
        sample_str = str(data_sample).lower()
        
        if 'temperature' in sample_str or 'temp' in sample_str:
            return 'temperature', '°C', '🌡️ Temperature Sensor'
        elif 'humidity' in sample_str or 'humid' in sample_str:
            return 'humidity', '%', '💧 Humidity Sensor'
        elif 'pressure' in sample_str:
            return 'pressure', 'Pa', '📊 Pressure Sensor'
        elif 'voltage' in sample_str or 'volt' in sample_str:
            return 'voltage', 'V', '⚡ Voltage Sensor'
        elif 'current' in sample_str or 'amp' in sample_str:
            return 'current', 'A', '🔌 Current Sensor'
        elif 'heart' in sample_str or 'pulse' in sample_str:
            return 'heart_rate', 'bpm', '❤️ Heart Rate Monitor'
        elif 'speed' in sample_str or 'rpm' in sample_str:
            return 'vehicle', 'km/h', '🚗 Vehicle Sensor'
        elif 'vibration' in sample_str:
            return 'vibration', 'g', '🏭 Vibration Sensor'
        elif 'air' in sample_str or 'quality' in sample_str:
            return 'air_quality', 'AQI', '🌍 Air Quality Sensor'
        else:
            return 'generic', 'units', '📡 Generic Sensor'
    
    def read_any_data_format(self, file_path):
        """Reads CSV, JSON, TXT - any format"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                # Try to read as text and parse
                df = self.parse_text_data(file_path)
            
            # Auto-detect sensor type from first row or column names
            sensor_type, unit, sensor_name = self.auto_detect_sensor_type(df.columns.tolist() if len(df.columns) > 0 else df.iloc[0] if len(df) > 0 else '')
            
            return {
                'data': df,
                'sensor_type': sensor_type,
                'sensor_name': sensor_name,
                'unit': unit,
                'filename': os.path.basename(file_path),
                'columns': list(df.columns),
                'sample_size': len(df)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def parse_text_data(self, file_path):
        """Parse text files with various formats"""
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                # Try to extract numbers from text
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if numbers:
                    data.append([float(x) for x in numbers])
        
        return pd.DataFrame(data)
    
    def get_active_sensors(self):
        """Get all active sensor data blocks"""
        sensor_blocks = []
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(BASE_DIR, "data")
        
        # Find all data files
        data_files = glob.glob(os.path.join(data_dir, "*.*"))
        
        for file_path in data_files:
            if file_path.endswith(('.csv', '.json', '.txt')):
                result = self.read_any_data_format(file_path)
                
                if 'error' not in result:
                    sensor_blocks.append({
                        'filename': result['filename'],
                        'sensor_name': result['sensor_name'],
                        'sensor_type': result['sensor_type'],
                        'unit': result['unit'],
                        'data_sample': result['data'].head(3).to_dict('records'),
                        'total_readings': len(result['data'])
                    })
        
        # If no real data files, create demo sensors
        if not sensor_blocks:
            sensor_blocks = self.create_demo_sensors()
        
        return sensor_blocks
    
    def create_demo_sensors(self):
        """Create demo sensors for testing"""
        return [
            {
                'filename': 'temperature_data.csv',
                'sensor_name': '🌡️ Temperature Sensor',
                'sensor_type': 'temperature',
                'unit': '°C',
                'data_sample': [{'timestamp': '10:00', 'value': 25.3}, {'timestamp': '10:01', 'value': 25.5}, {'timestamp': '10:02', 'value': 25.2}],
                'total_readings': 150
            },
            {
                'filename': 'heart_rate.json',
                'sensor_name': '❤️ Heart Rate Monitor',
                'sensor_type': 'heart_rate',
                'unit': 'bpm',
                'data_sample': [{'timestamp': '10:00', 'bpm': 72}, {'timestamp': '10:01', 'bpm': 75}, {'timestamp': '10:02', 'bpm': 71}],
                'total_readings': 120
            },
            {
                'filename': 'vehicle_data.txt',
                'sensor_name': '🚗 Vehicle Diagnostics',
                'sensor_type': 'vehicle',
                'unit': 'km/h',
                'data_sample': [{'timestamp': '10:00', 'speed': 65}, {'timestamp': '10:01', 'speed': 67}, {'timestamp': '10:02', 'speed': 63}],
                'total_readings': 90
            }
        ]