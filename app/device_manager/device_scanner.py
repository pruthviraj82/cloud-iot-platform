import threading
import time
from .serial_manager import device_manager

class DeviceScanner:
    def __init__(self):
        self.scan_interval = 5  # seconds
        self.is_scanning = False
        self.scan_thread = None
    
    def start_scanning(self):
        """Start automatic port scanning"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self._scan_loop)
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def stop_scanning(self):
        """Stop automatic port scanning"""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=1)
    
    def _scan_loop(self):
        """Continuous port scanning loop"""
        while self.is_scanning:
            try:
                device_manager.scan_ports()
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"Scanning error: {e}")
                time.sleep(self.scan_interval)

# Global scanner instance
device_scanner = DeviceScanner()