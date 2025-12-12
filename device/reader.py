import os
import csv
import time
import random
from datetime import datetime

# Build absolute path to /data/sensor_data.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
CSV_FILE = os.path.join(DATA_DIR, "sensor_data.csv")

print("📊 Fake sensor data generator started...")
print(f"💾 Saving data to: {CSV_FILE}")

# Ensure /data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# Create CSV & header if first time
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "sensor_value"])
    print("✅ Created new sensor data file")

print("🔄 Generating fake sensor data...")

# Generate initial base value
base_value = random.uniform(20, 30)

# Continuous fake data generation
while True:
    try:
        # Generate realistic sensor data with some variation
        variation = random.uniform(-1, 1)
        sensor_value = round(base_value + variation, 2)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"📈 Generated: {sensor_value} at {timestamp}")
        
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, sensor_value])
        
        # Slowly drift the base value
        base_value += random.uniform(-0.5, 0.5)
        
        # Wait 2 seconds before next reading
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(1)