#!/usr/bin/env python3
"""
List available serial ports and details.
Usage:
    python agent/list_ports.py
"""
import sys
try:
    import serial.tools.list_ports
except Exception:
    print('pyserial not installed. Run: pip install pyserial')
    sys.exit(1)

ports = list(serial.tools.list_ports.comports())
if not ports:
    print('No serial ports found.')
else:
    print(f'Found {len(ports)} port(s):')
    for p in ports:
        print('-----')
        print(f'device: {p.device}')
        print(f'description: {p.description}')
        print(f'hwid: {p.hwid}')
        print(f'manufacturer: {p.manufacturer}')
        print(f'product: {p.product}')
        print(f'interface: {p.interface}')
