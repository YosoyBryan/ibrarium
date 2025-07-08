#!/usr/bin/env python3
"""
IBRARIUM Wi-Fi Plug Generic Control System (Enhanced Version)
Manages various Wi-Fi smart plugs by dynamically installing and using
the appropriate Python libraries with improved error handling and async support.
"""

import sys
import logging
import json
import os
import importlib.util
import subprocess
import asyncio
import platform
from typing import Dict, Optional, Any, Union
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IBRARIUM WIFI GENERIC - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ibrarium.log'),  # Ensure this path is writable
        logging.StreamHandler()
    ]
)

class PlugController(ABC):
    """Abstract base class for plug controllers."""
    
    @abstractmethod
    async def control_device(self, device_config: Dict[str, Any], action: str) -> str:
        """Control a device with the specified action."""
        pass

class KasaController(PlugController):
    """Controller for Kasa/TP-Link smart plugs."""
    
    def __init__(self, module):
        self.module = module
    
    async def control_device(self, device_config: Dict[str, Any], action: str) -> str:
        """Control a Kasa device."""
        from kasa import SmartPlug, Discover
        
        ip_address = device_config.get('ip_address')
        
        try:
            if ip_address and ip_address != "192.168.1.XXX":  # Skip placeholder IPs
                plug = SmartPlug(ip_address)
            else:
                # Try discovery if IP is not provided or is placeholder
                logging.info(f"Attempting to discover Kasa plug for '{device_config.get('friendly_name', 'unnamed')}'...")
                found_plugs = await Discover.discover(timeout=5)
                plug = None
                
                # Try to match by friendly name first
                for discovered_plug in found_plugs.values():
                    if hasattr(discovered_plug, 'alias') and discovered_plug.alias == device_config.get('friendly_name'):
                        plug = discovered_plug
                        break
                
                if not plug:
                    return "KASA ERROR: Prise Kasa non trouvée. Vérifiez l'IP ou le nom."
            
            await plug.update()  # Get latest state
            
            if action == "on":
                await plug.turn_on()
                return f"KASA: Commande 'ON' envoyée à '{device_config.get('friendly_name', device_config.get('ip_address'))}'."
            elif action == "off":
                await plug.turn_off()
                return f"KASA: Commande 'OFF' envoyée à '{device_config.get('friendly_name', device_config.get('ip_address'))}'."
            elif action == "toggle":
                if hasattr(plug, 'toggle'):
                    await plug.toggle()
                else:
                    # Manual toggle if not available
                    if plug.is_on:
                        await plug.turn_off()
                    else:
                        await plug.turn_on()
                return f"KASA: Commande 'TOGGLE' envoyée à '{device_config.get('friendly_name', device_config.get('ip_address'))}'."
            elif action == "status":
                return f"KASA: '{device_config.get('friendly_name')}' est actuellement {'ON' if plug.is_on else 'OFF'}."
            else:
                return f"KASA ERROR: Action '{action}' non supportée pour Kasa."
        except Exception as e:
            logging.error(f"Error controlling Kasa device '{device_config.get('friendly_name')}': {e}")
            return f"KASA ERROR: Erreur lors du contrôle de la prise Kasa: {e}"

class TuyaController(PlugController):
    """Controller for Tuya/Smart Life smart plugs."""
    
    def __init__(self, module):
        self.module = module
    
    async def control_device(self, device_config: Dict[str, Any], action: str) -> str:
        """Control a Tuya device."""
        device_id = device_config.get('device_id')
        local_key = device_config.get('local_key')
        ip_address = device_config.get('ip_address')
        
        if not all([device_id, local_key]) or device_id == "YOUR_TUYA_DEVICE_ID":
            return "TUYA ERROR: ID de l'appareil ou clé locale manquante/invalide dans la configuration."
        
        try:
            if not ip_address or ip_address == "192.168.1.YYY":
                logging.info(f"Attempting Tuya discovery for device ID {device_id}...")
                # Run discovery in a separate thread since it's blocking
                loop = asyncio.get_event_loop()
                devices = await loop.run_in_executor(None, self.module.deviceScan, False, 5)
                found_device = next((d for d in devices.values() if d['id'] == device_id), None)
                if found_device:
                    ip_address = found_device['ip']
                    logging.info(f"Tuya device '{device_id}' discovered at IP: {ip_address}")
                else:
                    return "TUYA ERROR: Prise Tuya non trouvée. Spécifiez l'IP ou vérifiez le réseau."
            
            device = self.module.OutletDevice(device_id, ip_address, local_key)
            device.set_version(3.3)
            
            if action == "on":
                await asyncio.get_event_loop().run_in_executor(None, device.turn_on)
                return f"TUYA: Commande 'ON' envoyée à '{device_config.get('friendly_name', device_id)}'."
            elif action == "off":
                await asyncio.get_event_loop().run_in_executor(None, device.turn_off)
                return f"TUYA: Commande 'OFF' envoyée à '{device_config.get('friendly_name', device_id)}'."
            elif action == "status":
                data = await asyncio.get_event_loop().run_in_executor(None, device.status)
                if data and 'dps' in data and '1' in data['dps']:
                    is_on = data['dps']['1']
                    return f"TUYA: '{device_config.get('friendly_name')}' est actuellement {'ON' if is_on else 'OFF'}."
                else:
                    logging.warning(f"Could not get detailed status for Tuya device {device_id}. Data: {data}")
                    return f"TUYA: Statut de '{device_config.get('friendly_name')}' : Inconnu (impossible de lire le DPS)."
            else:
                return f"TUYA ERROR: Action '{action}' non supportée pour Tuya."
        except Exception as e:
            logging.error(f"Error controlling Tuya device '{device_config.get('friendly_name')}': {e}")
            return f"TUYA ERROR: Erreur lors du contrôle de la prise Tuya: {e}"

class WifiPlugGenericControl:
    """Enhanced Wi-Fi plug control system with proper async support."""
    
    def __init__(self, config_file: str = 'ibrarium_config.json'):
        self.config = self._load_config(config_file)
        self.devices = self.config.get('wifi_devices', {})
        self.libraries_map = self.config.get('wifi_plug_libraries', {})
        self.loaded_modules = {}
        self.controllers = {}
        self._ensure_libraries_installed()
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration with enhanced validation."""
        default_config = {
            "wifi_devices": {
                "coffee_machine": {
                    "type": "kasa",
                    "ip_address": "192.168.1.XXX",
                    "friendly_name": "Machine à café"
                },
                "desk_lamp": {
                    "type": "tuya",
                    "device_id": "YOUR_TUYA_DEVICE_ID",
                    "local_key": "YOUR_TUYA_LOCAL_KEY",
                    "ip_address": "192.168.1.YYY",
                    "friendly_name": "Lampe de bureau"
                }
            },
            "wifi_plug_libraries": {
                "kasa": "python-kasa",
                "tuya": "tinytuya",
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config['wifi_devices'].update(user_config.get('wifi_devices', {}))
                    default_config['wifi_plug_libraries'].update(user_config.get('wifi_plug_libraries', {}))
                    logging.info(f"Configuration loaded from {config_file}")
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in config file {config_file}: {e}")
            except Exception as e:
                logging.warning(f"Error reading config from {config_file}: {e}. Using defaults.")
        else:
            logging.info(f"Config file {config_file} not found. Using defaults.")
        
        return default_config
    
    def _is_library_installed(self, lib_name: str) -> bool:
        """Check if a Python library is installed."""
        module_name = lib_name.replace('-', '_')
        if module_name == 'python_kasa':
            module_name = 'kasa'
        
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    
    def _install_library(self, lib_name: str) -> bool:
        """Install a Python library using pip."""
        logging.info(f"Installing missing library: '{lib_name}'...")
        try:
            # Use sys.executable to ensure we use the correct Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", lib_name],
                check=True,
                capture_output=True,
                text=True
            )
            logging.info(f"Successfully installed '{lib_name}'")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install '{lib_name}': {e.stderr}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error installing '{lib_name}': {e}")
            return False
    
    def _ensure_libraries_installed(self):
        """Ensure all required libraries are installed and create controllers."""
        for plug_type, lib_name in self.libraries_map.items():
            if not self._is_library_installed(lib_name):
                logging.warning(f"Library '{lib_name}' for plug type '{plug_type}' is not installed.")
                if not self._install_library(lib_name):
                    logging.error(f"Could not install library '{lib_name}'. Control for '{plug_type}' devices will fail.")
                    self.loaded_modules[plug_type] = None
                    continue
            
            # Load the module and create controller
            try:
                if plug_type == "kasa":
                    module = importlib.import_module("kasa")
                    self.controllers[plug_type] = KasaController(module)
                elif plug_type == "tuya":
                    module = importlib.import_module("tinytuya")
                    self.controllers[plug_type] = TuyaController(module)
                # Add other plug types here
                else:
                    module = importlib.import_module(lib_name.replace('-', '_'))
                
                self.loaded_modules[plug_type] = module
                logging.info(f"Module for '{plug_type}' loaded successfully.")
            except ImportError as e:
                logging.error(f"Failed to load module for '{plug_type}': {e}")
                self.loaded_modules[plug_type] = None
    
    def validate_device_config(self, device_name: str, device_config: Dict[str, Any]) -> Optional[str]:
        """Validate device configuration and return error message if invalid."""
        if not device_config.get('type'):
            return f"Device '{device_name}' is missing 'type' field."
        
        plug_type = device_config['type']
        
        if plug_type == 'tuya':
            if not device_config.get('device_id') or device_config.get('device_id') == 'YOUR_TUYA_DEVICE_ID':
                return f"Tuya device '{device_name}' needs a valid device_id."
            if not device_config.get('local_key') or device_config.get('local_key') == 'YOUR_TUYA_LOCAL_KEY':
                return f"Tuya device '{device_name}' needs a valid local_key."
        
        return None
    
    async def control_device(self, device_name: str, action: str) -> str:
        """Control a Wi-Fi device with proper async support."""
        device_config = self.devices.get(device_name)
        if not device_config:
            return f"WIFI ERROR: Device '{device_name}' not found in configuration."
        
        # Validate device configuration
        validation_error = self.validate_device_config(device_name, device_config)
        if validation_error:
            return f"WIFI ERROR: {validation_error}"
        
        plug_type = device_config['type']
        
        if plug_type not in self.controllers:
            return f"WIFI ERROR: No controller available for plug type '{plug_type}'."
        
        controller = self.controllers[plug_type]
        return await controller.control_device(device_config, action)
    
    def list_devices(self) -> str:
        """List all configured devices."""
        if not self.devices:
            return "No devices configured."
        
        result = "Configured devices:\n"
        for name, config in self.devices.items():
            result += f"  - {name} ({config.get('type', 'unknown')}): {config.get('friendly_name', 'No name')}\n"
        return result

# Enhanced main execution
async def main():
    """Main async function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python3 ibrarium_wifi_plug_generic.py <command> [device_name] [action]")
        print("Commands:")
        print("  list                            - List all configured devices")
        print("  <device_name> <action>          - Control a device")
        print("  validate                        - Validate configuration")
        print("Example: python3 ibrarium_wifi_plug_generic.py coffee_machine on")
        print("Supported actions: on, off, toggle, status")
        return
    
    controller = WifiPlugGenericControl()
    
    if sys.argv[1] == "list":
        print(controller.list_devices())
    elif sys.argv[1] == "validate":
        errors = []
        for device_name, device_config in controller.devices.items():
            error = controller.validate_device_config(device_name, device_config)
            if error:
                errors.append(error)
        
        if errors:
            print("Configuration errors found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Configuration is valid.")
    elif len(sys.argv) >= 3:
        device_name = sys.argv[1].lower()
        action = sys.argv[2].lower()
        
        try:
            result = await controller.control_device(device_name, action)
            print(result)
        except Exception as e:
            logging.error(f"Error controlling device: {e}")
            print(f"WIFI ERROR: Unexpected error: {e}")
    else:
        print("Invalid command. Use --help for usage information.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        print(f"SYSTEM ERROR: {e}")
