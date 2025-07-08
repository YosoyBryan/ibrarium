#!/usr/bin/env python3
"""
IBRARIUM GPIO Control System
Manages interactions with Raspberry Pi GPIO pins for relays, etc.
"""

import sys
import logging
import json
import os
from gpiozero import OutputDevice, InputDevice
from time import sleep

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IBRARIUM GPIO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ibrarium.log'),
        logging.StreamHandler()
    ]
)

class IbrariumGPIOControl:
    """Manages GPIO pin interactions."""

    def __init__(self, config_file='ibrarium_config.json'):
        """Initializes GPIO control with configuration."""
        self.config = self.load_config(config_file)
        self.gpio_devices = {}
        self.setup_gpio_devices()
        logging.info("GPIO Control initialized.")

    def load_config(self, config_file):
        """Loads configuration from JSON file."""
        default_config = {
            "gpio_devices": {
                "garage_trigger": {"pin": 17, "type": "output", "active_high": False, "initial_value": False},
                "lampe_salon": {"pin": 22, "type": "output", "active_high": False, "initial_value": False},
                "pompe_eau": {"pin": 27, "type": "output", "active_high": False, "initial_value": False},
                # Add more GPIO devices as needed
            },
            "gpio_commands": {
                # Mappings: "Telegram_command_phrase": {"device": "device_name", "action": "on|off|toggle|pulse", "pulse_duration": 0.5}
                "garage ouvre": {"device": "garage_trigger", "action": "pulse", "pulse_duration": 0.5},
                "garage ferme": {"device": "garage_trigger", "action": "pulse", "pulse_duration": 0.5},
                "lampe salon allume": {"device": "lampe_salon", "action": "on"},
                "lampe salon eteint": {"device": "lampe_salon", "action": "off"},
                "lampe salon bascule": {"device": "lampe_salon", "action": "toggle"},
                "pompe eau active": {"device": "pompe_eau", "action": "on"},
                "pompe eau desactive": {"device": "pompe_eau", "action": "off"},
                # Specific command for watering duration (will be handled by plant_watering.py)
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge GPIO commands if config file exists
                    if 'gpio_devices' in user_config:
                        default_config['gpio_devices'].update(user_config['gpio_devices'])
                    if 'gpio_commands' in user_config:
                        default_config['gpio_commands'].update(user_config['gpio_commands'])
                    logging.info(f"GPIO configuration loaded from {config_file}")
            except Exception as e:
                logging.warning(f"GPIO config read error: {e}. Using default config.")
        else:
            pass # main_ibrarium or plant_watering will create it if not present

        return default_config

    def setup_gpio_devices(self):
        """Configures GPIO devices based on loaded config."""
        for name, params in self.config['gpio_devices'].items():
            try:
                if params['type'] == 'output':
                    self.gpio_devices[name] = OutputDevice(
                        params['pin'],
                        active_high=params.get('active_high', False),
                        initial_value=params.get('initial_value', False)
                    )
                    logging.info(f"Configured OutputDevice: {name} on pin {params['pin']}")
                elif params['type'] == 'input':
                    self.gpio_devices[name] = InputDevice(
                        params['pin'],
                        pull_up=params.get('pull_up', True) # Common for input buttons/switches
                    )
                    logging.info(f"Configured InputDevice: {name} on pin {params['pin']}")
                else:
                    logging.warning(f"Unknown device type '{params['type']}' for {name}. Skipping.")
            except Exception as e:
                logging.error(f"Error configuring GPIO device {name}: {e}")

    def perform_action(self, device_name, action_type, pulse_duration=None):
        """Performs an action on a specified GPIO device."""
        device = self.gpio_devices.get(device_name)
        if not device:
            logging.error(f"GPIO device '{device_name}' not found in configuration.")
            return f"GPIO ERROR: Appareil '{device_name}' non configuré."

        try:
            if action_type == "on":
                if isinstance(device, OutputDevice):
                    device.on()
                    return f"GPIO: '{device_name}' activé."
                else:
                    return f"GPIO ERROR: '{device_name}' n'est pas un appareil de sortie."
            elif action_type == "off":
                if isinstance(device, OutputDevice):
                    device.off()
                    return f"GPIO: '{device_name}' désactivé."
                else:
                    return f"GPIO ERROR: '{device_name}' n'est pas un appareil de sortie."
            elif action_type == "toggle":
                if isinstance(device, OutputDevice):
                    device.toggle()
                    return f"GPIO: '{device_name}' basculé."
                else:
                    return f"GPIO ERROR: '{device_name}' n'est pas un appareil de sortie."
            elif action_type == "pulse":
                if isinstance(device, OutputDevice):
                    if pulse_duration is None:
                        pulse_duration = 0.5 # Default pulse duration
                    device.on()
                    sleep(pulse_duration)
                    device.off()
                    return f"GPIO: '{device_name}' pulsé pendant {pulse_duration}s."
                else:
                    return f"GPIO ERROR: '{device_name}' n'est pas un appareil de sortie."
            elif action_type == "read": # For input devices
                if isinstance(device, InputDevice):
                    state = "actif" if device.is_active else "inactif"
                    return f"GPIO: '{device_name}' est {state}."
                else:
                    return f"GPIO ERROR: '{device_name}' n'est pas un appareil d'entrée."
            else:
                return f"GPIO ERROR: Action '{action_type}' non reconnue pour '{device_name}'."
        except Exception as e:
            logging.error(f"Error performing action '{action_type}' on '{device_name}': {e}")
            return f"GPIO ERROR: Erreur lors de l'action sur '{device_name}': {e}"

    def get_device_status(self, device_name):
        """Gets the current status of a GPIO device."""
        device = self.gpio_devices.get(device_name)
        if not device:
            return f"GPIO ERROR: Appareil '{device_name}' non configuré."
        
        try:
            if isinstance(device, OutputDevice):
                state = "activé" if device.is_active else "désactivé"
                return f"GPIO: '{device_name}' est {state}."
            elif isinstance(device, InputDevice):
                state = "actif" if device.is_active else "inactif"
                return f"GPIO: '{device_name}' est {state}."
            else:
                return f"GPIO ERROR: Type d'appareil inconnu pour '{device_name}'."
        except Exception as e:
            logging.error(f"Error getting status for '{device_name}': {e}")
            return f"GPIO ERROR: Erreur lors de la lecture du statut de '{device_name}': {e}"

    def list_devices(self):
        """Lists all configured GPIO devices."""
        if not self.gpio_devices:
            return "GPIO: Aucun appareil configuré."
        
        device_list = []
        for name, device in self.gpio_devices.items():
            device_type = "sortie" if isinstance(device, OutputDevice) else "entrée"
            pin_number = device.pin.number
            device_list.append(f"{name} (pin {pin_number}, {device_type})")
        
        return f"GPIO: Appareils configurés: {', '.join(device_list)}"

    def cleanup(self):
        """Cleans up all GPIO resources."""
        for device in self.gpio_devices.values():
            try:
                if hasattr(device, 'close'):
                    device.close()
            except Exception as e:
                logging.warning(f"Error during GPIO cleanup for device: {e}")
        logging.info("GPIO cleanup completed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        gpio_controller = IbrariumGPIOControl()
        command_text = " ".join(sys.argv[1:]).lower()

        # Special commands for system information
        if command_text == "list":
            print(gpio_controller.list_devices())
            gpio_controller.cleanup()
            sys.exit(0)

        # Find the best matching command
        matched_command_params = None
        matched_phrase = None
        for cmd_phrase, params in gpio_controller.config['gpio_commands'].items():
            if cmd_phrase in command_text:
                matched_command_params = params
                matched_phrase = cmd_phrase
                break # Take the first match

        if matched_command_params:
            device_name = matched_command_params.get("device")
            action = matched_command_params.get("action")
            pulse_duration = matched_command_params.get("pulse_duration")

            if device_name and action:
                print(gpio_controller.perform_action(device_name, action, pulse_duration))
            else:
                print(f"GPIO: Commande mappée '{matched_phrase}' incomplète pour GPIO.")
        else:
            print(f"GPIO: Commande GPIO '{command_text}' non mappée ou non trouvée.")

        gpio_controller.cleanup()
    else:
        print("GPIO: Usage: python3 ibrarium_gpio_control.py <telegram_command_text>")
        print("GPIO: Commandes spéciales: 'list' pour lister les appareils")
