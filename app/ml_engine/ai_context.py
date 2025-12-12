class IoTContextAI:
    def __init__(self):
        self.project_knowledge = {
            'domain': 'IoT Sensor Monitoring Platform',
            'purpose': 'Real-time sensor data collection, analysis, and prediction',
            'capabilities': [
                'Read multiple sensor types',
                'Predict future values', 
                'Detect anomalies',
                'Generate historical reports',
                'Provide natural language insights',
                'Manage device connections'
            ],
            'sensor_types': ['temperature', 'humidity', 'pressure', 'voltage', 'current', 'heart_rate', 'vehicle', 'vibration', 'air_quality'],
            'time_ranges': ['last hour', 'today', 'yesterday', 'last week', 'last month', 'custom']
        }
        
    def understand_user_intent(self, query):
        """AI understands what user wants based on natural language"""
        query = query.lower()
        
        if 'temperature' in query:
            return {'intent': 'sensor_data', 'sensor': 'temperature', 'timeframe': self.extract_timeframe(query)}
        elif 'humidity' in query:
            return {'intent': 'sensor_data', 'sensor': 'humidity', 'timeframe': self.extract_timeframe(query)}
        elif 'heart' in query or 'pulse' in query:
            return {'intent': 'sensor_data', 'sensor': 'heart_rate', 'timeframe': self.extract_timeframe(query)}
        elif 'vehicle' in query or 'car' in query:
            return {'intent': 'sensor_data', 'sensor': 'vehicle', 'timeframe': self.extract_timeframe(query)}
        elif 'pressure' in query:
            return {'intent': 'sensor_data', 'sensor': 'pressure', 'timeframe': self.extract_timeframe(query)}
        elif 'connect' in query or 'port' in query or 'com' in query:
            return {'intent': 'device_connection'}
        elif 'prediction' in query or 'predict' in query or 'forecast' in query:
            return {'intent': 'prediction', 'timeframe': self.extract_timeframe(query)}
        elif 'anomaly' in query or 'error' in query or 'problem' in query:
            return {'intent': 'anomaly_detection'}
        elif 'report' in query or 'summary' in query:
            return {'intent': 'report', 'timeframe': self.extract_timeframe(query)}
        elif 'help' in query or 'what can you do' in query:
            return {'intent': 'help'}
        else:
            return {'intent': 'general_help'}
    
    def extract_timeframe(self, query):
        """Extract time period from natural language"""
        if 'last hour' in query: return 'last hour'
        elif 'today' in query: return 'today'
        elif 'yesterday' in query: return 'yesterday' 
        elif 'last week' in query: return 'last week'
        elif 'last month' in query: return 'last month'
        else: return 'recent'