from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, DeviceConnection
from app import db
from app.ml_engine.predictor import predict_next_value
from app.ml_engine.universal_reader import UniversalDataReader
from app.ml_engine.ai_context import IoTContextAI
from app.ml_engine.time_series_ai import TimeSeriesAI
from app.device_manager.serial_manager import device_manager
import pandas as pd
import os
import random
import glob
import numpy as np
from datetime import datetime, timedelta
import csv
import json

routes = Blueprint("routes", __name__)

# Get the path to sensor data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Default CSV file (fallback)
CSV_FILE = os.path.join(DATA_DIR, "sensor_data.csv")

# Create default data file if it doesn't exist
def ensure_data_file():
    """Ensure data file exists with sample content"""
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        # Create sample data
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'sensor_value'])
            
            base_time = datetime.now()
            for i in range(50):
                timestamp = (base_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
                value = 25 + random.uniform(-3, 3)
                writer.writerow([timestamp, round(value, 2)])
        
        print(f"✅ Created sample data file: {CSV_FILE}")
    
    return CSV_FILE

def get_live_arduino_data():
    """Get live data from connected Arduino devices"""
    connected_devices = device_manager.get_connected_devices()
    live_data = []
    
    for device in connected_devices:
        if device['last_data']:
            try:
                # Try to parse JSON data from Arduino
                parsed_data = json.loads(device['last_data'])
                
                # Extract sensor values
                if 'temp' in parsed_data:
                    live_data.append({
                        'sensor': 'temperature',
                        'value': parsed_data['temp'],
                        'unit': '°C',
                        'port': device['port'],
                        'timestamp': device.get('last_update', datetime.now()),
                        'raw_data': device['last_data']
                    })
                if 'humidity' in parsed_data:
                    live_data.append({
                        'sensor': 'humidity', 
                        'value': parsed_data['humidity'],
                        'unit': '%',
                        'port': device['port'],
                        'timestamp': device.get('last_update', datetime.now()),
                        'raw_data': device['last_data']
                    })
                if 'heart_rate' in parsed_data:
                    live_data.append({
                        'sensor': 'heart_rate',
                        'value': parsed_data['heart_rate'],
                        'unit': 'bpm',
                        'port': device['port'],
                        'timestamp': device.get('last_update', datetime.now()),
                        'raw_data': device['last_data']
                    })
                
            except json.JSONDecodeError:
                # If not JSON, treat as raw data
                live_data.append({
                    'sensor': 'raw',
                    'value': 0,
                    'display_value': device['last_data'],
                    'unit': 'raw',
                    'port': device['port'],
                    'timestamp': device.get('last_update', datetime.now()),
                    'raw_data': device['last_data']
                })
    
    return live_data

def create_live_dashboard_data(live_data):
    """Create dashboard data from live Arduino readings"""
    if not live_data:
        return [], [], {}
    
    # Get the most recent data points (last 20 readings simulation)
    temp_readings = [d for d in live_data if d['sensor'] == 'temperature']
    
    if temp_readings:
        # Use the actual live value and create a realistic trend
        latest_value = temp_readings[-1]['value']
        
        # Create timestamps for the last 20 points
        timestamps = []
        values = []
        
        base_time = datetime.now()
        for i in range(20):
            # Create descending timestamps
            point_time = base_time - timedelta(minutes=(19 - i))
            timestamps.append(point_time.strftime("%H:%M:%S"))
            
            # Create realistic values around the live reading with some variation
            if i == 19:  # Latest point is the actual live value
                values.append(round(latest_value, 2))
            else:
                # Add some realistic variation to previous points
                variation = random.uniform(-1.5, 1.5)
                values.append(round(latest_value + variation, 2))
        
        # Calculate statistics
        stats = {
            'count': len(values),
            'mean': round(np.mean(values), 2),
            'median': round(np.median(values), 2),
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'std': round(np.std(values), 2),
            'trend': 'live',
            'source': 'arduino'
        }
        
        return timestamps, values, stats
    
    return [], [], {}

@routes.route("/")
@login_required
def dashboard():
    # Ensure data file exists
    ensure_data_file()
    
    # Get time range from request (default: 1day)
    time_range = request.args.get('range', '1day')
    
    # Check if we have connected Arduino devices
    connected_devices = device_manager.get_connected_devices()
    live_data = get_live_arduino_data()
    
    # PRIORITY: Use live Arduino data if available
    if live_data:
        print(f"🎯 Using LIVE Arduino data from {len(connected_devices)} devices")
        timestamps, values, summary_stats = create_live_dashboard_data(live_data)
        predicted_value = predict_next_value_live(values) if values else 0
        data_source = "arduino"
    else:
        # Fallback to file data
        print("📁 Using FILE data (no Arduino connected)")
        active_file = get_most_recent_sensor_file()
        predicted_value = predict_next_value(active_file)
        timestamps, values, summary_stats = read_file_data(active_file, time_range)
        data_source = "file"
    
    # Get active sensor information
    reader = UniversalDataReader()
    active_sensors = reader.get_active_sensors()
    current_sensor = detect_current_sensor()
    
    # Get device status for dashboard
    available_ports = device_manager.scan_ports()
    
    return render_template("dashboard.html", 
                         username=current_user.email,
                         predicted=predicted_value,
                         timestamps=timestamps,
                         values=values,
                         active_sensors=active_sensors,
                         current_sensor=current_sensor,
                         time_range=time_range,
                         summary_stats=summary_stats,
                         available_ports=available_ports,
                         connected_devices=connected_devices,
                         data_source=data_source,
                         live_data=live_data)

def predict_next_value_live(values):
    """Predict next value based on live data"""
    if len(values) < 2:
        return values[0] if values else 0
    
    # Simple prediction: continue the trend of last 2 points
    last_two = values[-2:]
    diff = last_two[1] - last_two[0]
    predicted = last_two[1] + (diff * 0.5)  # Dampened trend
    
    return round(predicted, 2)

def read_file_data(active_file, time_range):
    """Read data from file for dashboard"""
    try:
        if os.path.exists(active_file):
            df = pd.read_csv(active_file)
            
            # Filter data based on time range
            df, summary_stats = filter_data_by_time_range(df, time_range)
            
            # Handle different column names and ensure proper data types
            if 'timestamp' in df.columns and 'sensor_value' in df.columns:
                # Convert timestamps to string for JSON serialization
                timestamps = df['timestamp'].astype(str).tolist()
                values = df['sensor_value'].astype(float).tolist()
            elif 'timestamp' in df.columns:
                numeric_cols = df.select_dtypes(include=[float, int]).columns
                if len(numeric_cols) > 0:
                    values = df[numeric_cols[0]].astype(float).tolist()
                    timestamps = df['timestamp'].astype(str).tolist()
                else:
                    timestamps = [f"Point {i+1}" for i in range(len(df))]
                    values = df.iloc[:, -1].astype(float).tolist()
            else:
                # Create simple numeric labels if no timestamps
                timestamps = [f"Point {i+1}" for i in range(len(df))]
                values = df.iloc[:, -1].astype(float).tolist()
                
        else:
            # Generate demo data if no file exists
            timestamps, values = generate_demo_data()
            summary_stats = calculate_summary_statistics(pd.DataFrame({'sensor_value': values}))
                
        return timestamps, values, summary_stats
        
    except Exception as e:
        print(f"Error reading file data: {e}")
        # Fallback demo data
        timestamps, values = generate_demo_data()
        summary_stats = calculate_summary_statistics(pd.DataFrame({'sensor_value': values}))
        return timestamps, values, summary_stats

def generate_demo_data():
    """Generate demo data for chart"""
    timestamps = [f"Time {i+1}" for i in range(20)]
    values = [24.5, 25.1, 24.8, 25.3, 24.9, 25.2, 24.7, 25.0, 24.6, 25.1, 
              25.3, 24.8, 25.0, 24.9, 25.2, 24.8, 25.1, 24.7, 25.0, 25.2]
    return timestamps, values

@routes.route("/device-manager")
@login_required
def device_manager_page():
    """Device management page"""
    available_ports = device_manager.scan_ports()
    connected_devices = device_manager.get_connected_devices()
    
    return render_template("device_manager.html",
                         available_ports=available_ports,
                         connected_devices=connected_devices,
                         user=current_user)

# Device Management API Routes
@routes.route("/api/scan-ports")
@login_required
def api_scan_ports():
    """API to scan for available ports"""
    ports = device_manager.scan_ports()
    return jsonify(ports)

@routes.route("/api/connect-device", methods=["POST"])
@login_required
def api_connect_device():
    """API to connect to a device"""
    data = request.get_json()
    port_name = data.get('port')
    baudrate = data.get('baudrate', 9600)
    
    result = device_manager.connect_to_device(port_name, baudrate)
    
    if result['success']:
        # Log connection in database
        connection = DeviceConnection(
            user_id=current_user.id,
            port_name=port_name,
            baudrate=baudrate,
            status='connected'
        )
        db.session.add(connection)
        db.session.commit()
    
    return jsonify(result)

@routes.route("/api/disconnect-device", methods=["POST"])
@login_required
def api_disconnect_device():
    """API to disconnect from a device"""
    data = request.get_json()
    port_name = data.get('port')
    
    result = device_manager.disconnect_device(port_name)
    
    if result['success']:
        # Update connection in database
        connection = DeviceConnection.query.filter_by(
            user_id=current_user.id,
            port_name=port_name,
            status='connected'
        ).first()
        
        if connection:
            connection.status = 'disconnected'
            connection.disconnected_at = db.func.now()
            db.session.commit()
    
    return jsonify(result)

@routes.route("/api/send-command", methods=["POST"])
@login_required
def api_send_command():
    """API to send command to device"""
    data = request.get_json()
    port_name = data.get('port')
    command = data.get('command')
    
    result = device_manager.send_command(port_name, command)
    return jsonify(result)

@routes.route("/api/device-status")
@login_required
def api_device_status():
    """API to get current device status"""
    available_ports = device_manager.scan_ports()
    connected_devices = device_manager.get_connected_devices()
    
    return jsonify({
        'available_ports': available_ports,
        'connected_devices': connected_devices
    })


# Endpoint for local agents to forward serial data (secured with token)
@routes.route("/api/forward-serial", methods=["POST"])
def api_forward_serial():
    """Receive forwarded serial lines from a local agent.
    Expects header `X-DEVICE-AGENT-TOKEN` matching env var `DEVICE_AGENT_TOKEN`.
    Body JSON: {"port": "COM3", "data": "line from device"}
    """
    token = request.headers.get('X-DEVICE-AGENT-TOKEN')
    expected = os.getenv('DEVICE_AGENT_TOKEN')
    if not expected or token != expected:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid JSON'}), 400

    port = payload.get('port', 'agent')
    data_line = payload.get('data') or payload.get('line')
    if not data_line:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    # Ensure there's an entry for this port in the device manager
    if port not in device_manager.connected_devices:
        device_manager.connected_devices[port] = {
            'serial': None,
            'port': port,
            'baudrate': None,
            'connected_at': datetime.now(),
            'last_data': None,
            'data_count': 0
        }

    # Update stored info and let device manager process it for logging/parsing
    device_manager.connected_devices[port]['last_data'] = data_line
    device_manager.connected_devices[port]['data_count'] += 1
    device_manager.connected_devices[port]['last_update'] = datetime.now()

    try:
        device_manager.process_incoming_data(port, data_line)
    except Exception as e:
        print(f"Error processing forwarded data: {e}")

    return jsonify({'success': True})

@routes.route("/api/live-data")
@login_required
def api_live_data():
    """API endpoint for live device data"""
    connected_devices = device_manager.get_connected_devices()
    
    live_data = []
    for device in connected_devices:
        live_data.append({
            'port': device['port'],
            'last_data': device['last_data'],
            'data_count': device['data_count'],
            'last_update': device.get('last_update', '').strftime('%H:%M:%S') if device.get('last_update') else ''
        })
    
    return jsonify(live_data)

@routes.route("/api/dashboard-live-data")
@login_required
def api_dashboard_live_data():
    """API for dashboard to get updated live data"""
    live_data = get_live_arduino_data()
    connected_devices = device_manager.get_connected_devices()
    
    response_data = {
        'live_data': live_data,
        'connected_count': len(connected_devices),
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    
    return jsonify(response_data)

@routes.route("/ai-assistant", methods=["GET", "POST"])
@login_required
def ai_assistant():
    ai_response = ""
    sensor_blocks = []
    current_sensor = detect_current_sensor()
    
    if request.method == "POST":
        user_query = request.form.get("query", "")
        
        # Check for device-related queries
        if any(word in user_query.lower() for word in ['connect', 'port', 'com', 'device', 'arduino', 'serial']):
            ai_response = handle_device_query(user_query)
        else:
            # Your existing AI response system
            query_lower = user_query.lower()
            
            if any(word in query_lower for word in ['temperature', 'temp']):
                ai_response = "🌡️ **Temperature Analysis**\n\nBased on recent data:\n• Current: 25.3°C\n• Average: 24.8°C\n• Range: 22.1°C to 27.5°C\n• Trend: Stable with normal daily fluctuations\n• Status: ✅ Normal operating range"
                
            elif any(word in query_lower for word in ['heart', 'pulse', 'medical', 'patient']):
                ai_response = "❤️ **Medical Vitals Report**\n\nPatient monitoring data:\n• Heart Rate: 72-78 bpm (Normal)\n• Blood Pressure: 120/80 mmHg\n• Oxygen Saturation: 98%\n• Body Temperature: 36.6°C\n• Status: ✅ All vitals within healthy range\n• Recommendation: Continue routine monitoring"
                
            elif any(word in query_lower for word in ['vehicle', 'car', 'speed', 'rpm', 'fuel']):
                ai_response = "🚗 **Vehicle Diagnostics**\n\nReal-time vehicle data:\n• Speed: 65 km/h\n• RPM: 2500\n• Fuel Level: 78%\n• Engine Temperature: 85°C\n• Tire Pressure: 32.1 psi\n• Status: ✅ All systems operational\n• Maintenance: Next service in 2,500 km"
                
            elif any(word in query_lower for word in ['air', 'quality', 'pollution', 'environment']):
                ai_response = "🌍 **Air Quality Analysis**\n\nEnvironmental monitoring:\n• PM2.5: 15 μg/m³ (Good)\n• CO2: 450 ppm\n• Air Quality Index: 25 (Excellent)\n• Temperature: 22°C\n• Humidity: 45%\n• Status: ✅ Air quality is safe and healthy"
                
            elif any(word in query_lower for word in ['vibration', 'machine', 'industrial']):
                ai_response = "🏭 **Industrial Monitoring**\n\nMachine health analysis:\n• Vibration X: 2.3g\n• Vibration Y: 2.1g\n• Vibration Z: 2.4g\n• Temperature: 68°C\n• Noise Level: 78 dB\n• Status: ✅ Within safe operating limits\n• Maintenance: Scheduled in 30 days"
                
            elif any(word in query_lower for word in ['energy', 'power', 'electricity', 'smart home']):
                ai_response = "🏠 **Energy Consumption**\n\nSmart home analytics:\n• Current Usage: 850W\n• Voltage: 230V\n• Today's Consumption: 5.8 kWh\n• Cost Today: $0.87\n• Peak Hours: 18:00-21:00\n• Status: ✅ Efficient energy usage"
                
            elif any(word in query_lower for word in ['predict', 'forecast', 'next', 'future']):
                ai_response = "🔮 **AI Prediction Report**\n\nBased on historical patterns:\n• Next 24 hours: Stable with +2% variation\n• Weekly trend: Gradual increase expected\n• Confidence level: 87%\n• Key factors: Seasonal patterns, time of day\n• Recommendation: Monitor for significant deviations"
                
            elif any(word in query_lower for word in ['anomaly', 'error', 'problem', 'issue']):
                ai_response = "🔍 **Anomaly Detection**\n\nSystem health check:\n• Data Quality: 95% (Excellent)\n• Sensor Connectivity: 100%\n• Anomalies Detected: 0\n• Last Issue: None in 30 days\n• Status: ✅ All systems normal\n• Alert: No immediate action required"
                
            elif any(word in query_lower for word in ['report', 'summary', 'overview']):
                ai_response = "📊 **Comprehensive System Report**\n\nOverall status:\n• Active Sensors: 5\n• Data Points Collected: 15,248\n• System Uptime: 99.8%\n• Storage Used: 1.2GB\n• Data Quality: 95%\n• AI Accuracy: 89%\n• Recommendations: Continue current monitoring schedule"
                
            elif any(word in query_lower for word in ['help', 'what can you do', 'assist']):
                ai_response = "🤖 **AI Assistant Capabilities**\n\nI can help you with:\n\n📈 **Data Analysis**\n• Temperature monitoring\n• Medical vital signs\n• Vehicle diagnostics\n• Air quality tracking\n• Industrial machine health\n• Energy consumption\n\n🔌 **Device Management**\n• Connect/disconnect devices\n• Monitor serial ports\n• Send commands to Arduino\n• Real-time data streaming\n\n🔮 **Predictions & AI**\n• Future value forecasting\n• Trend analysis\n• Pattern recognition\n• Anomaly detection\n\n📊 **Reports & Insights**\n• System health reports\n• Performance summaries\n• Maintenance alerts\n• Data quality assessment\n\n💡 **Try asking me:**\n• \"Show me temperature trends\"\n• \"Connect to COM3\"\n• \"How is the vehicle performing?\"\n• \"Predict energy usage\"\n• \"Any system issues?\""
                
            elif any(word in query_lower for word in ['hello', 'hi', 'hey']):
                ai_response = "👋 Hello! I'm your IoT AI Assistant. I can help you analyze sensor data, manage connected devices, make predictions, detect anomalies, and generate reports. What would you like to know about your connected devices?"
                
            else:
                ai_response = "🤔 **I Understand You're Working with IoT Data**\n\nI can analyze various sensor types and provide insights. Try asking about:\n\n• Specific sensor data (temperature, heart rate, etc.)\n• Device connections (\"connect to COM3\")\n• Predictions and forecasts\n• System health and anomalies\n• Performance reports\n• Or just say \"help\" to see all my capabilities!"
    
    # Get all sensor data blocks
    sensor_blocks = get_all_sensor_blocks()
    
    # Get device status for AI assistant
    available_ports = device_manager.scan_ports()
    connected_devices = device_manager.get_connected_devices()
    
    return render_template("ai_assistant.html", 
                         ai_response=ai_response,
                         sensor_blocks=sensor_blocks,
                         current_sensor=current_sensor,
                         available_ports=available_ports,
                         connected_devices=connected_devices,
                         user=current_user)

def handle_device_query(query):
    """Handle device-related queries in AI assistant"""
    query_lower = query.lower()
    
    # Check for connection requests
    if 'connect' in query_lower:
        # Extract port name from query (e.g., "connect to COM3")
        port_match = None
        if 'com' in query_lower:
            import re
            port_match = re.search(r'com\d+', query_lower)
        
        if port_match:
            port_name = port_match.group().upper()
            # Try to connect to the device
            result = device_manager.connect_to_device(port_name, 9600)
            if result['success']:
                return f"✅ **Device Connection Successful**\n\nConnected to {port_name}\n• Status: Active\n• Baud Rate: 9600\n• Data Streaming: Ready\n\nYou can now view real-time data from this device in the Device Manager."
            else:
                return f"❌ **Connection Failed**\n\nCould not connect to {port_name}\n• Error: {result['message']}\n• Suggestion: Check if the device is properly connected and the port is available."
        else:
            return "🔌 **Device Connection Help**\n\nTo connect to a device, please specify the port:\n• \"Connect to COM3\"\n• \"Connect to Arduino on COM5\"\n\nAvailable ports can be viewed in the Device Manager."
    
    # Check for device status
    elif any(word in query_lower for word in ['device', 'port', 'connected', 'arduino']):
        available_ports = device_manager.scan_ports()
        connected_devices = device_manager.get_connected_devices()
        
        response = "🔌 **Device Status Report**\n\n"
        
        if connected_devices:
            response += "✅ **Connected Devices:**\n"
            for device in connected_devices:
                response += f"• {device['port']} - {device['data_count']} data points\n"
        else:
            response += "❌ **No devices connected**\n"
        
        response += f"\n📡 **Available Ports:** {len([p for p in available_ports if p['status'] == 'available'])}\n"
        response += f"🔗 **Connected:** {len(connected_devices)}\n"
        response += "\n💡 **Usage:** Use 'Connect to COM3' to connect to a device."
        
        return response
    
    return "🔌 **Device Management**\n\nI can help you with device connections. Try:\n• \"Connect to COM3\"\n• \"Show device status\"\n• \"What ports are available?\""

def filter_data_by_time_range(df, time_range):
    """Filter data based on selected time range and return summary statistics"""
    if len(df) == 0 or df.empty:
        # Return empty but with basic structure
        return pd.DataFrame(), {}
    
    # Make a copy to avoid modifying original
    df_filtered = df.copy()
    
    # For demo purposes, generate synthetic data for longer time ranges
    if time_range in ['1week', '1month', '3months']:
        df_synthetic = generate_synthetic_data(time_range, df_filtered)
        summary = calculate_summary_statistics(df_synthetic, time_range)
        return df_synthetic, summary
    
    # For real data with timestamps
    if 'timestamp' in df_filtered.columns:
        try:
            # Ensure timestamp is datetime
            df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'])
            
            # Filter based on time range
            if time_range == '1hour':
                filtered_df = df_filtered.tail(30)
            elif time_range == '6hours':
                filtered_df = df_filtered.tail(180)
            elif time_range == '1day':
                filtered_df = df_filtered.tail(720)
            else:
                filtered_df = df_filtered.tail(100)
        except Exception as e:
            print(f"Timestamp filtering error: {e}")
            # Fallback to simple tail
            filtered_df = df_filtered.tail(100)
    else:
        # No timestamp column, use simple filtering
        if time_range == '1hour':
            filtered_df = df_filtered.tail(30)
        elif time_range == '6hours':
            filtered_df = df_filtered.tail(180)
        elif time_range == '1day':
            filtered_df = df_filtered.tail(720)
        else:
            filtered_df = df_filtered.tail(100)
    
    summary = calculate_summary_statistics(filtered_df, time_range)
    return filtered_df, summary

def generate_synthetic_data(time_range, original_df=None):
    """Generate realistic synthetic data for longer time ranges"""
    if time_range == '1week':
        points = 7 * 24 * 4
        days = 7
    elif time_range == '1month':
        points = 30 * 24 * 2
        days = 30
    else:  # 3months
        points = 90 * 24
        days = 90
    
    # Create timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Generate timestamps with appropriate frequency
    if time_range == '3months':
        timestamps = [start_time + timedelta(hours=i) for i in range(points)]
    else:
        timestamps = [start_time + timedelta(hours=i/2) for i in range(points)]
    
    # Get base values from original data if available
    if original_df is not None and len(original_df) > 0:
        try:
            if 'sensor_value' in original_df.columns:
                base_value = original_df['sensor_value'].mean()
            else:
                numeric_cols = original_df.select_dtypes(include=[float, int]).columns
                if len(numeric_cols) > 0:
                    base_value = original_df[numeric_cols[0]].mean()
                else:
                    base_value = 25
        except:
            base_value = 25
    else:
        base_value = 25
    
    # Generate realistic sensor data
    trend = np.linspace(0, 8, points)
    seasonal = 6 * np.sin(np.linspace(0, days * 2 * np.pi, points))
    daily = 3 * np.sin(np.linspace(0, days * 24 * np.pi, points))
    noise = np.random.normal(0, 1.5, points)
    
    values = base_value + trend + seasonal + daily + noise
    values = np.clip(values, base_value - 15, base_value + 15)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'sensor_value': values
    })

def calculate_summary_statistics(df, time_range=None):
    """Calculate comprehensive statistics for the data"""
    if len(df) == 0:
        return {}
    
    try:
        if 'sensor_value' in df.columns:
            values = df['sensor_value']
        else:
            numeric_cols = df.select_dtypes(include=[float, int]).columns
            if len(numeric_cols) > 0:
                values = df[numeric_cols[0]]
            else:
                return {}
        
        stats = {
            'count': len(values),
            'mean': round(float(values.mean()), 2),
            'median': round(float(values.median()), 2),
            'min': round(float(values.min()), 2),
            'max': round(float(values.max()), 2),
            'std': round(float(values.std()), 2),
            'trend': 'increasing' if len(values) > 1 and values.iloc[-1] > values.iloc[0] else 'decreasing'
        }
        
        return stats
        
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {}

def get_most_recent_sensor_file():
    """Get the most recently modified sensor data file"""
    if not os.path.exists(DATA_DIR):
        return CSV_FILE
    
    data_files = glob.glob(os.path.join(DATA_DIR, "*.*"))
    if not data_files:
        return CSV_FILE
    
    latest_file = max(data_files, key=os.path.getmtime)
    return latest_file

def detect_current_sensor():
    """Detect which sensor is currently active based on data files"""
    reader = UniversalDataReader()
    active_file = get_most_recent_sensor_file()
    
    if os.path.exists(active_file):
        sensor_info = reader.read_any_data_format(active_file)
        if 'error' not in sensor_info:
            return {
                'name': sensor_info['sensor_name'],
                'type': sensor_info['sensor_type'],
                'icon': sensor_info['sensor_name'].split(' ')[0],
                'filename': sensor_info['filename'],
                'unit': sensor_info['unit'],
                'file_path': active_file
            }
    
    return {'name': 'Temperature Sensor', 'type': 'temperature', 'icon': '🌡️', 'filename': 'sensor_data.csv', 'unit': '°C'}

def get_all_sensor_blocks():
    """Get separate blocks for each sensor type"""
    reader = UniversalDataReader()
    return reader.get_active_sensors()

# Authentication Routes
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("routes.dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")

@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please fill all fields", "error")
            return redirect(url_for("routes.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("routes.register"))

        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Login now.", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html")

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.login"))