#!/usr/bin/env python3
"""
Machine Control Module for Laser Engraving
Handles detection, connection, and control of laser engraving machines via USB/Serial/Bluetooth.
"""

import os
import time
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not installed. USB/Serial device detection disabled.")
    print("Install with: pip install pyserial")


class MachineStatus(Enum):
    """Machine status states."""
    DISCONNECTED = "disconnected"
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    HOMING = "homing"
    ALARM = "alarm"


class MachineType(Enum):
    """Supported machine types."""
    GRBL = "GRBL"  # GRBL-based (most DIY lasers)
    MARLIN = "Marlin"  # Marlin firmware (3D printers with laser)
    RUIDA = "Ruida"  # Ruida controllers (commercial CO2 lasers)
    SMOOTHIE = "Smoothieware"  # Smoothieware
    UNKNOWN = "Unknown"


@dataclass
class MachineInfo:
    """Information about a detected machine."""
    port: str
    name: str
    description: str
    machine_type: MachineType
    status: MachineStatus
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    work_area: Optional[Tuple[float, float]] = None  # (width, height) in mm
    connected: bool = False
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['machine_type'] = self.machine_type.value
        data['status'] = self.status.value
        return data


class MachineController:
    """
    Controls connected laser engraving machines.
    Supports USB/Serial and Bluetooth connections.
    """
    
    # Known laser engraver VID/PID combinations (extend this list)
    KNOWN_DEVICES = [
        # GRBL-based devices
        {"vid": 0x1A86, "pid": 0x7523, "name": "CH340 Serial (Common GRBL)", "type": MachineType.GRBL},
        {"vid": 0x2341, "pid": 0x0043, "name": "Arduino Uno (GRBL)", "type": MachineType.GRBL},
        {"vid": 0x2341, "pid": 0x0001, "name": "Arduino Mega (GRBL)", "type": MachineType.GRBL},
        {"vid": 0x16C0, "pid": 0x0483, "name": "Teensy (Smoothie)", "type": MachineType.SMOOTHIE},
        # Add more as needed
    ]
    
    def __init__(self):
        """Initialize the machine controller."""
        self.machines: Dict[str, MachineInfo] = {}
        self.active_connection: Optional[serial.Serial] = None
        self.active_port: Optional[str] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.should_monitor = False
    
    def scan_devices(self) -> List[MachineInfo]:
        """
        Scan for connected laser engraving machines.
        
        Returns:
            List of detected machines
        """
        if not SERIAL_AVAILABLE:
            return []
        
        detected_machines = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            machine_type = self._identify_machine_type(port)
            
            # Create machine info
            machine = MachineInfo(
                port=port.device,
                name=self._get_friendly_name(port, machine_type),
                description=port.description,
                machine_type=machine_type,
                status=MachineStatus.DISCONNECTED,
                serial_number=port.serial_number
            )
            
            detected_machines.append(machine)
            self.machines[port.device] = machine
        
        return detected_machines
    
    def _identify_machine_type(self, port) -> MachineType:
        """
        Identify the type of machine based on VID/PID or port description.
        
        Args:
            port: Serial port object
            
        Returns:
            MachineType enum
        """
        # Check against known devices
        if port.vid and port.pid:
            for device in self.KNOWN_DEVICES:
                if port.vid == device["vid"] and port.pid == device["pid"]:
                    return device["type"]
        
        # Check description for keywords
        desc_lower = port.description.lower()
        if "grbl" in desc_lower or "cnc" in desc_lower or "laser" in desc_lower:
            return MachineType.GRBL
        elif "marlin" in desc_lower:
            return MachineType.MARLIN
        elif "smoothie" in desc_lower:
            return MachineType.SMOOTHIE
        elif "ch340" in desc_lower or "ch341" in desc_lower:
            # CH340/CH341 chips are commonly used with GRBL
            return MachineType.GRBL
        
        return MachineType.UNKNOWN
    
    def _get_friendly_name(self, port, machine_type: MachineType) -> str:
        """Generate a friendly name for the machine."""
        if machine_type != MachineType.UNKNOWN:
            return f"{machine_type.value} Laser Engraver"
        return port.description or "Laser Engraver"
    
    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """
        Connect to a specific machine.
        
        Args:
            port: Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
            baudrate: Communication speed (default: 115200)
            
        Returns:
            True if connection successful
        """
        if not SERIAL_AVAILABLE:
            return False
        
        try:
            # Close existing connection
            self.disconnect()
            
            # Open new connection
            self.active_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=2,
                write_timeout=2
            )
            
            self.active_port = port
            time.sleep(2)  # Wait for connection to stabilize
            
            # Update machine status
            if port in self.machines:
                self.machines[port].connected = True
                self.machines[port].status = MachineStatus.IDLE
            
            # Start monitoring thread
            self._start_monitoring()
            
            return True
            
        except Exception as e:
            print(f"Error connecting to {port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the active machine."""
        self._stop_monitoring()
        
        if self.active_connection and self.active_connection.is_open:
            try:
                self.active_connection.close()
            except Exception:
                pass
        
        if self.active_port and self.active_port in self.machines:
            self.machines[self.active_port].connected = False
            self.machines[self.active_port].status = MachineStatus.DISCONNECTED
        
        self.active_connection = None
        self.active_port = None
    
    def send_command(self, command: str) -> Optional[str]:
        """
        Send a command to the connected machine.
        
        Args:
            command: G-code or machine command
            
        Returns:
            Response from machine, or None if error
        """
        if not self.active_connection or not self.active_connection.is_open:
            return None
        
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            
            self.active_connection.write(command.encode())
            
            # Read response (timeout after 2 seconds)
            response = self.active_connection.readline().decode().strip()
            return response
            
        except Exception as e:
            print(f"Error sending command: {e}")
            return None
    
    def send_gcode_file(self, filepath: str, progress_callback=None) -> bool:
        """
        Send a G-code file to the machine line by line.
        
        Args:
            filepath: Path to G-code file
            progress_callback: Optional function to call with progress (0-100)
            
        Returns:
            True if successful
        """
        if not self.active_connection or not self.active_connection.is_open:
            return False
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith(';') or line.startswith('('):
                    continue
                
                # Send line
                response = self.send_command(line)
                
                # Check for error
                if response and 'error' in response.lower():
                    print(f"Error on line {i}: {response}")
                    return False
                
                # Update progress
                if progress_callback:
                    progress = int((i + 1) / total_lines * 100)
                    progress_callback(progress)
            
            return True
            
        except Exception as e:
            print(f"Error sending G-code file: {e}")
            return False
    
    def get_status(self) -> Optional[MachineStatus]:
        """
        Get current machine status.
        
        Returns:
            MachineStatus or None if not connected
        """
        if not self.active_port or self.active_port not in self.machines:
            return None
        
        return self.machines[self.active_port].status
    
    def home(self) -> bool:
        """Send homing command to machine."""
        if self.active_port:
            self.machines[self.active_port].status = MachineStatus.HOMING
        
        response = self.send_command("$H")  # GRBL homing command
        return response is not None
    
    def pause(self) -> bool:
        """Pause the current job."""
        if self.active_port:
            self.machines[self.active_port].status = MachineStatus.PAUSED
        
        response = self.send_command("!")  # GRBL pause (feed hold)
        return response is not None
    
    def resume(self) -> bool:
        """Resume paused job."""
        if self.active_port:
            self.machines[self.active_port].status = MachineStatus.RUNNING
        
        response = self.send_command("~")  # GRBL resume (cycle start)
        return response is not None
    
    def stop(self) -> bool:
        """Stop the current job (soft reset)."""
        if self.active_port:
            self.machines[self.active_port].status = MachineStatus.IDLE
        
        response = self.send_command("\x18")  # GRBL soft reset (Ctrl-X)
        return response is not None
    
    def emergency_stop(self) -> bool:
        """Emergency stop (resets machine)."""
        if self.active_port:
            self.machines[self.active_port].status = MachineStatus.ALARM
        
        response = self.send_command("\x18")  # GRBL reset
        return response is not None
    
    def _start_monitoring(self):
        """Start background thread to monitor machine status."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.should_monitor = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def _stop_monitoring(self):
        """Stop monitoring thread."""
        self.should_monitor = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Background loop to monitor machine status."""
        while self.should_monitor and self.active_connection:
            try:
                # Send status query (GRBL style)
                if self.active_connection.is_open:
                    self.active_connection.write(b'?')
                    
                    # Read response
                    response = self.active_connection.readline().decode().strip()
                    
                    if response and self.active_port in self.machines:
                        # Parse status from response
                        # Example GRBL response: <Idle|MPos:0.000,0.000,0.000|FS:0,0>
                        if 'Idle' in response:
                            self.machines[self.active_port].status = MachineStatus.IDLE
                        elif 'Run' in response:
                            self.machines[self.active_port].status = MachineStatus.RUNNING
                        elif 'Alarm' in response:
                            self.machines[self.active_port].status = MachineStatus.ALARM
                
                time.sleep(1)  # Query every second
                
            except Exception:
                time.sleep(1)  # Wait before retry


# Global controller instance
_controller = None


def get_controller() -> MachineController:
    """Get or create the global machine controller instance."""
    global _controller
    if _controller is None:
        _controller = MachineController()
    return _controller


def scan_for_machines() -> List[Dict]:
    """
    Convenience function to scan for machines and return as dictionaries.
    
    Returns:
        List of machine information dictionaries
    """
    controller = get_controller()
    machines = controller.scan_devices()
    return [m.to_dict() for m in machines]
