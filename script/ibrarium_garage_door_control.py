#!/usr/bin/env python3
"""
IBRARIUM Garage Door Control System - Enhanced Version
Manages the garage door (open/close/stop) via GPIO on Raspberry Pi.
Includes sensor support for door state detection and safety features.
"""

import sys
import logging
import json
import os
import time
from gpiozero import OutputDevice, InputDevice
from threading import Timer
from enum import Enum
from datetime import datetime

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IBRARIUM GARAGE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ibrarium.log'),
        logging.StreamHandler()
    ]
)

class DoorState(Enum):
    UNKNOWN = "unknown"
    OPEN = "open"
    CLOSED = "closed"
    OPENING = "opening"
    CLOSING = "closing"
    STOPPED = "stopped"

class GarageDoorControl:
    """Enhanced garage door control with sensor support and safety features."""

    def __init__(self, config_file='ibrarium_config.json'):
        """Initializes garage door control with configuration."""
        self.config = self.load_config(config_file)
        self.trigger_pin = self.config['garage_door']['trigger_pin']
        self.pulse_duration = self.config['garage_door']['pulse_duration']
        self.active_high_relay = self.config['garage_door']['active_high_relay']
        self.max_operation_time = self.config['garage_door']['max_operation_time']
        self.safety_timeout = self.config['garage_door']['safety_timeout']
        
        # State management
        self.current_state = DoorState.UNKNOWN
        self.last_operation_time = None
        self.operation_timer = None
        
        self.setup_gpio()
        self.setup_sensors()
        self.detect_initial_state()
        
        logging.info("Enhanced Garage Door Control initialized.")

    def load_config(self, config_file):
        """Loads configuration from JSON file with enhanced options."""
        default_config = {
            "garage_door": {
                "trigger_pin": 17,              # GPIO pin connected to the relay for the garage button
                "pulse_duration": 0.5,          # Duration (seconds) to simulate button press
                "active_high_relay": False,     # True if relay is active high, False if active low
                "open_sensor_pin": None,        # GPIO pin for open position sensor (optional)
                "closed_sensor_pin": None,      # GPIO pin for closed position sensor (optional)
                "max_operation_time": 30,       # Maximum time for door operation (seconds)
                "safety_timeout": 5,            # Safety timeout between operations (seconds)
                "sensor_pull_up": True,         # Use internal pull-up resistor for sensors
                "enable_safety_checks": True    # Enable safety checks and timeouts
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    if 'garage_door' in user_config:
                        default_config['garage_door'].update(user_config['garage_door'])
                    logging.info(f"Garage door configuration loaded from {config_file}")
            except Exception as e:
                logging.warning(f"Garage door config read error: {e}. Using default config.")

        return default_config

    def setup_gpio(self):
        """Configures the GPIO pin for the garage door trigger."""
        try:
            self.trigger_device = OutputDevice(
                self.trigger_pin,
                active_high=self.active_high_relay,
                initial_value=False
            )
            logging.info(f"Garage door trigger configured on GPIO pin {self.trigger_pin}")
        except Exception as e:
            logging.error(f"Failed to configure GPIO for garage door: {e}")
            raise

    def setup_sensors(self):
        """Sets up optional position sensors for door state detection."""
        self.open_sensor = None
        self.closed_sensor = None
        
        if self.config['garage_door']['open_sensor_pin']:
            try:
                self.open_sensor = InputDevice(
                    self.config['garage_door']['open_sensor_pin'],
                    pull_up=self.config['garage_door']['sensor_pull_up']
                )
                logging.info(f"Open sensor configured on GPIO pin {self.config['garage_door']['open_sensor_pin']}")
            except Exception as e:
                logging.warning(f"Failed to configure open sensor: {e}")
                
        if self.config['garage_door']['closed_sensor_pin']:
            try:
                self.closed_sensor = InputDevice(
                    self.config['garage_door']['closed_sensor_pin'],
                    pull_up=self.config['garage_door']['sensor_pull_up']
                )
                logging.info(f"Closed sensor configured on GPIO pin {self.config['garage_door']['closed_sensor_pin']}")
            except ception as e:
                logging.warning(f"Failed to configure closed sensor: {e}")

    def detect_initial_state(self):
        """Detects the initial state of the garage door using sensors."""
        if self.open_sensor and self.closed_sensor:
            if self.open_sensor.is_active:
                self.current_state = DoorState.OPEN
            elif self.closed_sensor.is_active:
                self.current_state = DoorState.CLOSED
            else:
                self.current_state = DoorState.UNKNOWN
        else:
            self.current_state = DoorState.UNKNOWN
        
        logging.info(f"Initial door state: {self.current_state.value}")

    def get_door_state(self):
        """Returns the current door state based on sensors or last known state."""
        if self.open_sensor and self.closed_sensor:
            if self.open_sensor.is_active:
                return DoorState.OPEN
            elif self.closed_sensor.is_active:
                return DoorState.CLOSED
            else:
                return DoorState.UNKNOWN
        else:
            return self.current_state

    def can_operate(self):
        """Checks if the door can be operated based on safety conditions."""
        if not self.config['garage_door']['enable_safety_checks']:
            return True, ""
        
        # Check if enough time has passed since last operation
        if self.last_operation_time:
            time_since_last = time.time() - self.last_operation_time
            if time_since_last < self.safety_timeout:
                return False, f"Opération trop récente. Attendez {self.safety_timeout - time_since_last:.1f}s."
        
        # Check if door is currently moving
        if self.current_state in [DoorState.OPENING, DoorState.CLOSING]:
            return False, "La porte est en cours de mouvement."
        
        return True, ""

    def on_operation_timeout(self):
        """Called when operation timeout is reached."""
        logging.warning("Garage door operation timed out")
        self.current_state = DoorState.STOPPED
        self.operation_timer = None

    def toggle_door(self):
        """Simulates a button press to toggle the garage door state with safety checks."""
        can_operate, reason = self.can_operate()
        if not can_operate:
            return f"IBRARIUM GARAGE: Opération refusée - {reason}"
        
        try:
            current_state = self.get_door_state()
            
            logging.info(f"Triggering garage door via pin {self.trigger_pin} for {self.pulse_duration}s...")
            logging.info(f"Current state: {current_state.value}")
            
            # Trigger the relay
            self.trigger_device.on()
            time.sleep(self.pulse_duration)
            self.trigger_device.off()
            
            # Update state and timing
            self.last_operation_time = time.time()
            
            # Predict next state based on current state
            if current_state == DoorState.OPEN:
                self.current_state = DoorState.CLOSING
                action = "fermeture"
            elif current_state == DoorState.CLOSED:
                self.current_state = DoorState.OPENING
                action = "ouverture"
            else:
                self.current_state = DoorState.UNKNOWN
                action = "bascule"
            
            # Set operation timeout
            if self.operation_timer:
                self.operation_timer.cancel()
            self.operation_timer = Timer(self.max_operation_time, self.on_operation_timeout)
            self.operation_timer.start()
            
            success_message = f"IBRARIUM GARAGE: Commande de {action} envoyée avec succès."
            logging.info(success_message)
            return success_message
            
        except Exception as e:
            error_message = f"IBRARIUM GARAGE ERROR: Impossible d'activer la porte: {e}"
            logging.error(error_message)
            return error_message

    def get_status(self):
        """Returns detailed status information."""
        current_state = self.get_door_state()
        
        status_info = {
            'state': current_state.value,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sensors_available': bool(self.open_sensor and self.closed_sensor),
            'last_operation': self.last_operation_time,
            'can_operate': self.can_operate()[0]
        }
        
        if self.open_sensor and self.closed_sensor:
            status_info['open_sensor'] = self.open_sensor.is_active
            status_info['closed_sensor'] = self.closed_sensor.is_active
        
        return status_info

    def emergency_stop(self):
        """Emergency stop function to immediately halt door operation."""
        try:
            logging.warning("Emergency stop activated")
            self.toggle_door()  # Send stop command
            self.current_state = DoorState.STOPPED
            return "IBRARIUM GARAGE: Arrêt d'urgence activé."
        except Exception as e:
            return f"IBRARIUM GARAGE ERROR: Erreur lors de l'arrêt d'urgence: {e}"

    def cleanup(self):
        """Cleans up GPIO resources and timers."""
        try:
            if self.operation_timer:
                self.operation_timer.cancel()
                
            if hasattr(self, 'trigger_device'):
                self.trigger_device.off()
                self.trigger_device.close()
                
            if self.open_sensor:
                self.open_sensor.close()
                
            if self.closed_sensor:
                self.closed_sensor.close()
                
            logging.info("Garage door GPIO cleanup completed.")
        except Exception as e:
            logging.warning(f"Error during garage door GPIO cleanup: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command_text = " ".join(sys.argv[1:]).lower()
        garage_control = GarageDoorControl()

        try:
            if "ouvre" in command_text or "ouvrir" in command_text:
                current_state = garage_control.get_door_state()
                if current_state == DoorState.OPEN:
                    print("IBRARIUM GARAGE: La porte est déjà ouverte.")
                else:
                    print(garage_control.toggle_door())
                    
            elif "ferme" in command_text or "fermer" in command_text:
                current_state = garage_control.get_door_state()
                if current_state == DoorState.CLOSED:
                    print("IBRARIUM GARAGE: La porte est déjà fermée.")
                else:
                    print(garage_control.toggle_door())
                    
            elif "stop" in command_text or "arrêt" in command_text:
                print(garage_control.emergency_stop())
                
            elif "bascule" in command_text or "toggle" in command_text:
                print(garage_control.toggle_door())
                
            elif "status" in command_text or "état" in command_text:
                status = garage_control.get_status()
                print(f"IBRARIUM GARAGE: État actuel: {status['state']}")
                print(f"IBRARIUM GARAGE: Horodatage: {status['timestamp']}")
                if status['sensors_available']:
                    print(f"IBRARIUM GARAGE: Capteur ouvert: {'Activé' if status['open_sensor'] else 'Désactivé'}")
                    print(f"IBRARIUM GARAGE: Capteur fermé: {'Activé' if status['closed_sensor'] else 'Désactivé'}")
                else:
                    print("IBRARIUM GARAGE: Capteurs de position non configurés.")
                print(f"IBRARIUM GARAGE: Peut opérer: {'Oui' if status['can_operate'] else 'Non'}")
                
            else:
                print("IBRARIUM GARAGE: Commande non reconnue.")
                print("IBRARIUM GARAGE: Commandes disponibles: 'ouvre', 'ferme', 'stop', 'bascule', 'status'.")
                
        finally:
            garage_control.cleanup()
    else:
        print("IBRARIUM GARAGE: Usage: python3 ibrarium_garage_door_control.py <command>")
        print("IBRARIUM GARAGE: Commandes: 'ouvre', 'ferme', 'stop', 'bascule', 'status'.")
