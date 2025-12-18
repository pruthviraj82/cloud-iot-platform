#!/usr/bin/env python3
"""
Attempt to open a serial port to test availability.
Usage:
    python agent/check_port.py --port COM3 --baud 9600
"""
import argparse
import sys
import time

try:
    import serial
except Exception:
    print('pyserial not installed. Run: pip install pyserial')
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('--port', required=True)
parser.add_argument('--baud', type=int, default=9600)
args = parser.parse_args()

port = args.port
baud = args.baud

print(f'Testing open on {port} @ {baud}...')
try:
    ser = serial.Serial(port, baud, timeout=1)
    print('Opened port successfully. Closing...')
    ser.close()
    print('Success: port is available')
except Exception as e:
    print(f'Failed to open port: {e}')
    print('If you are on Windows, ensure the port name is correct and another program is not using it.')
