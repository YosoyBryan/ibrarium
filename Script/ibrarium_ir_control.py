#!/usr/bin/env python3
"""
IBRARIUM Infrared Control System
Manages sending IR commands via LIRC on Raspberry Pi.
"""

import subprocess
import sys
import time
import logging
import json
import os
import re

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IBRARIUM IR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ibrarium.log'),
        logging.StreamHandler()
    ]
)

class IbrariumIRControl:
    """Manages sending infrared commands via LIRC."""

    def __init__(self, config_file='ibrarium_config.json'):
        """Initializes IR control with configuration."""
        self.config = self.load_config(config_file)
        self.ir_commands = self.config.get('ir_commands', {})
        self.command_history = []
        logging.info("IR Control initialized.")

    def load_config(self, config_file):
        """Loads configuration from JSON file."""
        default_config = {
            "ir_commands": {
                # Example mappings: "command_phrase": ["lirc_remote_name", "LIRC_KEY_CODE", repeat_count(optional)]
                "living room ac on 22c": ["my_ac_remote", "POWER_22C"],
                "living room ac off": ["my_ac_remote", "POWER_OFF"],
                "living room tv on": ["my_tv_remote", "POWER"],
                "living room tv off": ["my_tv_remote", "POWER"],
                "tv channel up": ["my_tv_remote", "CHANNEL_UP"],
                "tv channel down": ["my_tv_remote", "CHANNEL_DOWN"],
                "tv volume up": ["my_tv_remote", "VOLUME_UP"],
                "tv volume down": ["my_tv_remote", "VOLUME_DOWN"],
                "stereo volume up": ["my_hifi_remote", "VOLUME_UP", 3], # Press 3 times
                "stereo volume down": ["my_hifi_remote", "VOLUME_DOWN", 3],
                "stereo on": ["my_hifi_remote", "POWER"],
                "stereo off": ["my_hifi_remote", "POWER"],
                "lights on": ["my_light_remote", "POWER_ON"],
                "lights off": ["my_light_remote", "POWER_OFF"],
                # Add your specific IR commands here. Remote names must match your LIRC config.
            },
            "ir_settings": {
                "command_timeout": 5,
                "repeat_delay": 0.1,
                "max_repeat_count": 10
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge IR commands if config file exists
                    if 'ir_commands' in user_config:
                        default_config['ir_commands'].update(user_config['ir_commands'])
                    if 'ir_settings' in user_config:
                        default_config['ir_settings'].update(user_config['ir_settings'])
                    logging.info(f"IR configuration loaded from {config_file}")
            except Exception as e:
                logging.warning(f"IR config read error: {e}. Using default config.")
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                logging.info(f"IR configuration file created: {config_file}")

        return default_config

    def send_ir_command(self, device_name, ir_code, repeat=1):
        """Sends an IR command using irsend."""
        settings = self.config.get('ir_settings', {})
        timeout = settings.get('command_timeout', 5)
        repeat_delay = settings.get('repeat_delay', 0.1)
        max_repeat = settings.get('max_repeat_count', 10)
        
        # Validate repeat count
        repeat = min(repeat, max_repeat)
        
        cmd = ["irsend", "SEND_ONCE", device_name, ir_code]
        
        try:
            for i in range(repeat):
                result = subprocess.run(
                    cmd, 
                    check=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    logging.error(f"irsend failed: {error_msg}")
                    return f"IR ERROR: {error_msg}"
                
                logging.info(f"Command '{ir_code}' sent to '{device_name}' (repeat {i+1}/{repeat})")
                
                # Add delay between repeats (except for the last one)
                if i < repeat - 1:
                    time.sleep(repeat_delay)
            
            # Record successful command
            self.command_history.append({
                'timestamp': time.time(),
                'device': device_name,
                'code': ir_code,
                'repeat': repeat,
                'success': True
            })
            
            return f"IR: Command '{ir_code}' sent to '{device_name}' successfully."
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            logging.error(f"irsend execution error: {error_msg}")
            return f"IR ERROR: Failed to send IR command. Check LIRC: {error_msg}"
            
        except FileNotFoundError:
            logging.error("'irsend' command not found. Is LIRC installed and configured?")
            return "IR ERROR: 'irsend' not found. Is LIRC installed and configured?"
            
        except subprocess.TimeoutExpired:
            logging.error(f"irsend command timed out for {device_name} {ir_code}")
            return f"IR ERROR: Command timed out after {timeout} seconds."
            
        except Exception as e:
            logging.error(f"Unexpected IR error: {e}")
            return f"IR ERROR: Unexpected error: {e}"

    def find_matching_command(self, command_text):
        """Find the best matching IR command from the input text."""
        command_text = command_text.lower().strip()
        
        # First try exact match
        if command_text in self.ir_commands:
            return self.ir_commands[command_text]
        
        # Then try substring matching
        best_match = None
        best_score = 0
        
        for cmd_phrase, action_params in self.ir_commands.items():
            # Calculate match score based on word overlap
            cmd_words = set(cmd_phrase.lower().split())
            input_words = set(command_text.split())
            
            # Calculate Jaccard similarity
            intersection = cmd_words.intersection(input_words)
            union = cmd_words.union(input_words)
            
            if len(union) > 0:
                score = len(intersection) / len(union)
                
                # Bonus for exact phrase match
                if cmd_phrase in command_text:
                    score += 0.5
                
                if score > best_score and score > 0.3:  # Minimum threshold
                    best_score = score
                    best_match = action_params
        
        return best_match

    def list_available_commands(self):
        """List all available IR commands."""
        if not self.ir_commands:
            return "No IR commands configured."
        
        result = "Available IR commands:\n"
        for cmd_phrase, params in self.ir_commands.items():
            device, code = params[0], params[1]
            repeat = params[2] if len(params) > 2 else 1
            result += f"  '{cmd_phrase}' -> {device}:{code}"
            if repeat > 1:
                result += f" (repeat {repeat}x)"
            result += "\n"
        
        return result.strip()

    def check_lirc_status(self):
        """Check if LIRC is running and configured."""
        try:
            # Check if lircd is running
            result = subprocess.run(
                ["systemctl", "is-active", "lircd"], 
                capture_output=True, 
                text=True
            )
            
            lirc_status = result.stdout.strip()
            
            # List available remotes
            result = subprocess.run(
                ["irsend", "LIST", ""], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                remotes = result.stdout.strip().split('\n')
                return f"LIRC Status: {lirc_status}\nAvailable remotes: {len(remotes)}"
            else:
                return f"LIRC Status: {lirc_status}\nError listing remotes: {result.stderr}"
                
        except Exception as e:
            return f"LIRC Status: Error checking status: {e}"

    def get_command_history(self, count=5):
        """Get recent command history."""
        if not self.command_history:
            return "No command history available."
        
        recent = self.command_history[-count:]
        result = f"Recent IR commands (last {len(recent)}):\n"
        
        for cmd in recent:
            timestamp = time.strftime('%H:%M:%S', time.localtime(cmd['timestamp']))
            result += f"  {timestamp}: {cmd['device']}:{cmd['code']}"
            if cmd['repeat'] > 1:
                result += f" (x{cmd['repeat']})"
            result += "\n"
        
        return result.strip()

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("IBRARIUM IR: Usage: python3 ibrarium_ir_control.py <command_text>")
        print("Commands:")
        print("  - Any IR command phrase (e.g., 'tv on', 'volume up')")
        print("  - 'list' - Show available commands")
        print("  - 'status' - Check LIRC status")
        print("  - 'history' - Show recent commands")
        return

    command_text = " ".join(sys.argv[1:]).lower()
    ir_controller = IbrariumIRControl()

    # Handle special commands
    if command_text == "list":
        print(ir_controller.list_available_commands())
        return
    
    if command_text == "status":
        print(ir_controller.check_lirc_status())
        return
    
    if command_text == "history":
        print(ir_controller.get_command_history())
        return

    # Find and execute IR command
    matched_command = ir_controller.find_matching_command(command_text)

    if matched_command:
        device, code = matched_command[0], matched_command[1]
        repeat = matched_command[2] if len(matched_command) > 2 else 1
        print(ir_controller.send_ir_command(device, code, repeat))
    else:
        print(f"IR: Command '{command_text}' not found or not mapped.")
        print("Use 'python3 ibrarium_ir_control.py list' to see available commands.")

if __name__ == "__main__":
    main()
