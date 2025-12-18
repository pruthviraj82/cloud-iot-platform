#!/usr/bin/env python3
"""
Local Serial Agent
Reads lines from a serial port and POSTS them to the app's `/api/forward-serial` endpoint.
Usage:
    python agent/serial_agent.py --port COM3 --baud 9600 --server http://localhost:5000/api/forward-serial --token mytoken

The receiving server must set the environment variable `DEVICE_AGENT_TOKEN` to match `--token`.
"""
import argparse
import time
import sys
import requests

try:
    import serial
except Exception as e:
    print("pyserial is required. Install with: pip install pyserial")
    raise


def main():
    parser = argparse.ArgumentParser(description='Local Serial Agent: forward serial lines to server')
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=9600, help='Baudrate')
    parser.add_argument('--server', required=True, help='Server endpoint URL (e.g. http://localhost:5000/api/forward-serial)')
    parser.add_argument('--token', required=True, help='Agent token to authenticate with server (DEVICE_AGENT_TOKEN)')
    args = parser.parse_args()

    url = args.server
    headers = {'X-DEVICE-AGENT-TOKEN': args.token}

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except Exception as e:
        print(f"Failed to open serial port {args.port}: {e}")
        sys.exit(1)

    print(f"Forwarding from {args.port}@{args.baud} -> {url}")

    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        payload = {'port': args.port, 'data': line}
                        try:
                            resp = requests.post(url, json=payload, headers=headers, timeout=5)
                            if resp.status_code not in (200, 201):
                                print(f"Server error {resp.status_code}: {resp.text}")
                            else:
                                print(f"Forwarded: {line}")
                        except requests.RequestException as re:
                            print(f"Request error: {re}")
                else:
                    time.sleep(0.1)
            except Exception as read_err:
                print(f"Read/forward error: {read_err}")
                time.sleep(1)
    finally:
        ser.close()


if __name__ == '__main__':
    main()
