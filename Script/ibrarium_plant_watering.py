#!/usr/bin/env python3
"""
IBRARIUM Plant Watering System
Automatic watering control via GPIO on Raspberry Pi
"""

import sys
import re
import logging
from gpiozero import OutputDevice, InputDevice, MCP3008
from time import sleep
from datetime import datetime
import json
import os

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IBRARIUM - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ibrarium.log'),
        logging.StreamHandler()
    ]
)

class IbrariumWateringSystem:
    """Intelligent IBRARIUM watering system"""
    
    def __init__(self, config_file='ibrarium_config.json'):
        """Initialize the system with configuration"""
        self.config = self.load_config(config_file)
        self.setup_gpio()
        self.watering_log = []
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "gpio_pin_pump": 27,
            "gpio_pin_moisture": 4,
            "active_high_relay": False,
            "max_watering_duration": 300,  # 5 minutes max
            "min_watering_duration": 5,    # 5 seconds min
            "soil_moisture_threshold": 30,  # Moisture threshold in %
            "adc_channel": 0,              # ADC channel for analog sensor
            "safety_interval": 3600        # Min interval between waterings (1h)
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logging.info(f"Configuration loaded from {config_file}")
            except Exception as e:
                logging.warning(f"Config read error: {e}. Using default config.")
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                logging.info(f"Configuration file created: {config_file}")
        
        return default_config
    
    def setup_gpio(self):
        """Configure GPIO pins"""
        try:
            # Pump configuration
            self.pump_relay = OutputDevice(
                self.config['gpio_pin_pump'],
                active_high=self.config['active_high_relay'],
                initial_value=False
            )
            
            # Moisture sensor configuration (ADC)
            try:
                self.adc = MCP3008(channel=self.config['adc_channel'])
                self.moisture_sensor_available = True
                logging.info("Moisture sensor ADC initialized")
            except Exception as e:
                logging.warning(f"ADC sensor not available: {e}")
                self.moisture_sensor_available = False
                
            logging.info("GPIO configured successfully")
            
        except Exception as e:
            logging.error(f"GPIO configuration error: {e}")
            raise
    
    def read_soil_moisture(self):
        """Read soil moisture level"""
        if not self.moisture_sensor_available:
            return None
            
        try:
            # ADC reading (0-1) converted to percentage
            # Adjust this formula according to your sensor
            raw_value = self.adc.value
            # Assume 0.2 = dry (100%) and 0.8 = wet (0%)
            moisture_percent = max(0, min(100, (0.8 - raw_value) / 0.6 * 100))
            
            logging.info(f"Soil moisture: {moisture_percent:.1f}%")
            return moisture_percent
            
        except Exception as e:
            logging.error(f"Moisture sensor read error: {e}")
            return None
    
    def is_watering_needed(self):
        """Determine if watering is needed"""
        moisture = self.read_soil_moisture()
        if moisture is None:
            return False, "Moisture sensor not available"
            
        threshold = self.config['soil_moisture_threshold']
        
        if moisture < threshold:
            return True, f"Low moisture ({moisture:.1f}% < {threshold}%)"
        else:
            return False, f"Sufficient moisture ({moisture:.1f}% >= {threshold}%)"
    
    def check_safety_interval(self):
        """Check safety interval between waterings"""
        if not self.watering_log:
            return True, "No previous watering"
            
        last_watering = datetime.fromisoformat(self.watering_log[-1]['timestamp'])
        now = datetime.now()
        elapsed = (now - last_watering).total_seconds()
        
        if elapsed < self.config['safety_interval']:
            remaining = self.config['safety_interval'] - elapsed
            return False, f"Safety interval: {remaining:.0f}s remaining"
        
        return True, "Safety interval respected"
    
    def water_plants(self, duration_seconds, force=False):
        """Activate watering pump with safety checks"""
        
        # Duration validation
        if duration_seconds < self.config['min_watering_duration']:
            return f"ERROR: Duration too short (min: {self.config['min_watering_duration']}s)"
            
        if duration_seconds > self.config['max_watering_duration']:
            return f"ERROR: Duration too long (max: {self.config['max_watering_duration']}s)"
        
        # Safety interval check
        if not force:
            safety_ok, safety_msg = self.check_safety_interval()
            if not safety_ok:
                return f"IBRARIUM: {safety_msg}"
        
        # Execute watering
        try:
            logging.info(f"Starting watering for {duration_seconds} seconds...")
            
            # Record watering event
            watering_event = {
                'timestamp': datetime.now().isoformat(),
                'duration': duration_seconds,
                'forced': force,
                'moisture_before': self.read_soil_moisture()
            }
            
            # Activate pump
            self.pump_relay.on()
            sleep(duration_seconds)
            self.pump_relay.off()
            
            # Complete watering record
            watering_event['moisture_after'] = self.read_soil_moisture()
            watering_event['success'] = True
            self.watering_log.append(watering_event)
            
            logging.info(f"Watering completed successfully after {duration_seconds} seconds")
            return f"IBRARIUM: Watering completed after {duration_seconds} seconds."
            
        except Exception as e:
            logging.error(f"Watering error: {e}")
            # Ensure pump is off in case of error
            try:
                self.pump_relay.off()
            except:
                pass
            return f"IBRARIUM GPIO ERROR: Unable to control pump: {e}"
    
    def get_status(self):
        """Get system status"""
        moisture = self.read_soil_moisture()
        needed, reason = self.is_watering_needed()
        safety_ok, safety_msg = self.check_safety_interval()
        
        status = {
            'moisture_level': moisture,
            'watering_needed': needed,
            'reason': reason,
            'safety_check': safety_ok,
            'safety_message': safety_msg,
            'last_watering': self.watering_log[-1] if self.watering_log else None,
            'total_waterings': len(self.watering_log)
        }
        
        return status
    
    def auto_water(self):
        """Automatic watering based on soil moisture"""
        needed, reason = self.is_watering_needed()
        
        if not needed:
            return f"IBRARIUM: No watering needed - {reason}"
        
        # Use default duration of 15 seconds for auto watering
        default_duration = 15
        return self.water_plants(default_duration)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            if hasattr(self, 'pump_relay'):
                self.pump_relay.off()
                self.pump_relay.close()
            logging.info("GPIO cleanup completed")
        except Exception as e:
            logging.error(f"Cleanup error: {e}")

def parse_command(command_text):
    """Parse text command and extract watering duration"""
    command_text = command_text.lower()
    
    # Default duration
    duration = 10
    
    # Look for duration in seconds
    seconds_match = re.search(r'(\d+)\s*(?:second|sec)', command_text)
    if seconds_match:
        duration = int(seconds_match.group(1))
    
    # Look for duration in minutes
    minutes_match = re.search(r'(\d+)\s*(?:minute|min)', command_text)
    if minutes_match:
        duration = int(minutes_match.group(1)) * 60
    
    # Check for force flag
    force = 'force' in command_text
    
    return duration, force

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("IBRARIUM: Usage: python3 ibrarium_plant_watering.py <text_command>")
        print("Commands:")
        print("  - water [duration] [force]")
        print("  - status")
        print("  - auto")
        return
    
    command_text = " ".join(sys.argv[1:]).lower()
    
    try:
        # Initialize system
        system = IbrariumWateringSystem()
        
        if "water" in command_text:
            duration, force = parse_command(command_text)
            print(system.water_plants(duration, force))
            
        elif "status" in command_text:
            status = system.get_status()
            print(f"IBRARIUM Status:")
            print(f"  Moisture: {status['moisture_level']:.1f}%" if status['moisture_level'] else "  Moisture: N/A")
            print(f"  Watering needed: {status['watering_needed']}")
            print(f"  Reason: {status['reason']}")
            print(f"  Safety check: {status['safety_check']}")
            print(f"  Total waterings: {status['total_waterings']}")
            
        elif "auto" in command_text:
            print(system.auto_water())
            
        else:
            print(f"IBRARIUM: Unknown command: '{command_text}'")
            print("Available commands: water, status, auto")
    
    except Exception as e:
        logging.error(f"System error: {e}")
        print(f"IBRARIUM SYSTEM ERROR: {e}")
    
    finally:
        # Cleanup
        try:
            system.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()
