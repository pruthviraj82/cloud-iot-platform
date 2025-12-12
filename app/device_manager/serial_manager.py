import serial
import serial.tools.list_ports
import threading
import time
import json
from datetime import datetime

class SerialDeviceManager:
    def __init__(self):
        self.connected_devices = {}
        self.available_ports = []
        self.serial_threads = {}
        self.is_running = False
        
    def scan_ports(self):
        """Scan all available serial ports"""
        self.available_ports = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            port_info = {
                'device': port.device,
                'name': port.description,
                'hwid': port.hwid,
                'manufacturer': port.manufacturer,
                'product': port.product,
                'interface': port.interface,
                'status': self.check_port_status(port.device)
            }
            self.available_ports.append(port_info)
        
        return self.available_ports
    
    def check_port_status(self, port_name):
        """Check if port is busy or available"""
        try:
            # Try to open port to check if it's busy
            ser = serial.Serial(port_name)
            ser.close()
            return 'available'
        except (OSError, serial.SerialException):
            return 'busy'
    
    def connect_to_device(self, port_name, baudrate=9600):
        """Connect to a serial device"""
        try:
            if port_name in self.connected_devices:
                return {'success': False, 'message': 'Already connected to this port'}
            
            ser = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            
            # Store connection
            device_info = {
                'serial': ser,
                'port': port_name,
                'baudrate': baudrate,
                'connected_at': datetime.now(),
                'last_data': None,
                'data_count': 0
            }
            
            self.connected_devices[port_name] = device_info
            
            # Start reading thread
            self.start_reading_thread(port_name)
            
            return {'success': True, 'message': f'Connected to {port_name}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}
    
    def disconnect_device(self, port_name):
        """Disconnect from a device"""
        try:
            if port_name in self.connected_devices:
                # Stop reading thread
                if port_name in self.serial_threads:
                    self.serial_threads[port_name] = False
                
                # Close serial connection
                self.connected_devices[port_name]['serial'].close()
                del self.connected_devices[port_name]
                
                return {'success': True, 'message': f'Disconnected from {port_name}'}
            else:
                return {'success': False, 'message': 'Not connected to this port'}
                
        except Exception as e:
            return {'success': False, 'message': f'Disconnection failed: {str(e)}'}
    
    def start_reading_thread(self, port_name):
        """Start a thread to read data from serial device"""
        def read_serial():
            while port_name in self.serial_threads and self.serial_threads[port_name]:
                try:
                    if port_name in self.connected_devices:
                        ser = self.connected_devices[port_name]['serial']
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').strip()
                            if line:
                                # Process incoming data
                                self.process_incoming_data(port_name, line)
                except Exception as e:
                    print(f"Error reading from {port_name}: {e}")
                    time.sleep(1)
        
        self.serial_threads[port_name] = True
        thread = threading.Thread(target=read_serial)
        thread.daemon = True
        thread.start()
    
    def process_incoming_data(self, port_name, data):
        """Process incoming data from Arduino"""
        try:
            # Update device info
            self.connected_devices[port_name]['last_data'] = data
            self.connected_devices[port_name]['data_count'] += 1
            self.connected_devices[port_name]['last_update'] = datetime.now()
            
            # Try to parse JSON data (common in Arduino projects)
            try:
                parsed_data = json.loads(data)
                print(f"JSON data from {port_name}: {parsed_data}")
            except:
                print(f"Raw data from {port_name}: {data}")
                
        except Exception as e:
            print(f"Error processing data: {e}")
    
    def send_command(self, port_name, command):
        """Send command to connected device"""
        try:
            if port_name in self.connected_devices:
                ser = self.connected_devices[port_name]['serial']
                ser.write(f"{command}\n".encode('utf-8'))
                return {'success': True, 'message': 'Command sent'}
            else:
                return {'success': False, 'message': 'Device not connected'}
        except Exception as e:
            return {'success': False, 'message': f'Command failed: {str(e)}'}
    
    def get_connected_devices(self):
        """Get list of connected devices with status"""
        connected = []
        for port_name, info in self.connected_devices.items():
            device_info = {
                'port': port_name,
                'connected_at': info['connected_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'last_data': info['last_data'],
                'data_count': info['data_count'],
                'status': 'connected'
            }
            connected.append(device_info)
        
        return connected

# Global instance
device_manager = SerialDeviceManager()