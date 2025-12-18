import os
from .serial_manager import device_manager
from .device_scanner import device_scanner

# Control automatic device scanning via environment variable:
# Set ENABLE_SERIAL_SCAN=true to enable scanning (default: disabled)
enable_scan = os.getenv('ENABLE_SERIAL_SCAN', 'false').lower() in ('1', 'true', 'yes')
if enable_scan:
	print('Device scanning enabled (ENABLE_SERIAL_SCAN=true)')
	device_scanner.start_scanning()
else:
	print('Device scanning disabled (set ENABLE_SERIAL_SCAN=true to enable)')