from .serial_manager import device_manager
from .device_scanner import device_scanner

# Start automatic device scanning
device_scanner.start_scanning()