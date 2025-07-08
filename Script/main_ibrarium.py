#!/usr/bin/env python3
"""
IBRARIUM - Intelligent Home Automation System
Created by James and GMN
Optimized version with error handling, logging, and enhanced security
"""

import telebot
import subprocess
import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import threading
import queue

# Load environment variables
load_dotenv()

# Configuration
@dataclass
class Config:
    """Centralized configuration for IBRARIUM"""
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    AUTHORIZED_USER_IDS: List[int] = [int(x) for x in os.getenv('AUTHORIZED_USER_IDS', '').split(',') if x]
    SCRIPTS_ACTION_PATH: str = os.getenv('SCRIPTS_ACTION_PATH', '/home/pi/ibrarium/scripts/')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/var/log/ibrarium.log')
    MAX_RETRY_ATTEMPTS: int = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    COMMAND_TIMEOUT: int = int(os.getenv('COMMAND_TIMEOUT', '30'))
    RATE_LIMIT: int = int(os.getenv('RATE_LIMIT', '10'))  # Commands per minute

# Global configuration
config = Config()

# Logging configuration
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('IBRARIUM')

# Configuration validation
def validate_config() -> bool:
    """Validates configuration at startup"""
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN missing in environment variables")
        return False
    
    if not config.AUTHORIZED_USER_IDS:
        logger.error("AUTHORIZED_USER_IDS missing in environment variables")
        return False
    
    if not Path(config.SCRIPTS_ACTION_PATH).exists():
        logger.error(f"Scripts directory {config.SCRIPTS_ACTION_PATH} does not exist")
        return False
    
    return True

# Rate limiting manager
class RateLimiter:
    """Rate limiting manager to prevent spam"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, List[float]] = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """Checks if user can make a request"""
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

# Command manager
@dataclass
class Command:
    """Represents an IBRARIUM command"""
    keywords: List[str]
    script: str
    description: str
    category: str
    requires_args: bool = False
    timeout: int = 30

class CommandManager:
    """Centralized command manager"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.command_history: List[Dict] = []
        self.setup_commands()
    
    def setup_commands(self):
        """Sets up all available commands"""
        commands_config = [
            Command(
                keywords=['clim', 'chauffage', 'climatisation', 'temperature'],
                script='ibrarium_ir_control.py',
                description='Contrôle de la climatisation et du chauffage',
                category='climat'
            ),
            Command(
                keywords=['arrose', 'arrosage', 'plante', 'jardin'],
                script='ibrarium_plant_watering.py',
                description='Système d\'arrosage intelligent',
                category='jardin'
            ),
            Command(
                keywords=['tv', 'television', 'media', 'chaine', 'volume'],
                script='ibrarium_ir_control.py',
                description='Contrôle des appareils média',
                category='media'
            ),
            Command(
                keywords=['garage', 'portail', 'porte'],
                script='ibrarium_gpio_control.py',
                description='Contrôle des accès (garage, portail)',
                category='acces'
            ),
            Command(
                keywords=['lampe', 'lumiere', 'eclairage', 'led'],
                script='ibrarium_gpio_control.py',
                description='Contrôle de l\'éclairage',
                category='eclairage'
            ),
            Command(
                keywords=['cafe', 'café', 'cafetiere'],
                script='ibrarium_playwright_action.py',
                description='Contrôle de la cafetière',
                category='cuisine'
            ),
            Command(
                keywords=['lave-linge', 'machine', 'laver', 'lessive'],
                script='ibrarium_playwright_action.py',
                description='Contrôle du lave-linge',
                category='electromenager'
            ),
            Command(
                keywords=['github', 'depot', 'repo'],
                script='ibrarium_github_action.py',
                description='Gestion des dépôts GitHub',
                category='dev',
                requires_args=True
            ),
            Command(
                keywords=['status', 'statut', 'etat'],
                script='ibrarium_system_status.py',
                description='Statut du système IBRARIUM',
                category='system'
            ),
            Command(
                keywords=['help', 'aide', 'commandes'],
                script='internal_help',
                description='Affiche l\'aide',
                category='system'
            )
        ]
        
        for cmd in commands_config:
            for keyword in cmd.keywords:
                self.commands[keyword] = cmd
    
    def find_command(self, text: str) -> Optional[Command]:
        """Finds a command based on text"""
        text_lower = text.lower().strip()
        
        # Exact search first
        for keyword, command in self.commands.items():
            if keyword in text_lower:
                return command
        
        return None
    
    def log_command(self, user_id: int, command: str, status: str, details: str = ""):
        """Logs command history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'command': command,
            'status': status,
            'details': details
        }
        self.command_history.append(entry)
        
        # Limit history to 1000 entries
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]

class ScriptExecutor:
    """Script executor with error handling and timeout"""
    
    def __init__(self, scripts_path: str):
        self.scripts_path = Path(scripts_path)
        self.execution_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def _worker(self):
        """Worker thread for script execution"""
        while True:
            try:
                task = self.execution_queue.get(timeout=1)
                if task is None:
                    break
                self._execute_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
    
    def _execute_task(self, task: Dict):
        """Executes a script task"""
        script_path = self.scripts_path / task['script']
        command = task['command']
        callback = task['callback']
        timeout = task.get('timeout', config.COMMAND_TIMEOUT)
        
        try:
            if not script_path.exists():
                callback(False, f"Script {task['script']} introuvable")
                return
            
            # Command preparation
            cmd = ['python3', str(script_path), command]
            
            # Execution with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.scripts_path)
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                if process.returncode == 0:
                    callback(True, stdout.strip() if stdout else "Commande exécutée avec succès")
                else:
                    callback(False, f"Erreur d'exécution: {stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                process.kill()
                callback(False, f"Timeout après {timeout} secondes")
                
        except Exception as e:
            callback(False, f"Erreur d'exécution: {str(e)}")
    
    def execute_script(self, script: str, command: str, callback: Callable, timeout: int = None):
        """Adds a script to the execution queue"""
        task = {
            'script': script,
            'command': command,
            'callback': callback,
            'timeout': timeout or config.COMMAND_TIMEOUT
        }
        self.execution_queue.put(task)

class IbrariumBot:
    """Main IBRARIUM bot class"""
    
    def __init__(self):
        if not validate_config():
            sys.exit(1)
        
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        self.command_manager = CommandManager()
        self.script_executor = ScriptExecutor(config.SCRIPTS_ACTION_PATH)
        self.rate_limiter = RateLimiter(config.RATE_LIMIT)
        
        # Handler registration
        self.bot.message_handler(func=lambda message: True)(self.handle_message)
        
        logger.info("IBRARIUM initialized successfully")
    
    def is_authorized(self, user_id: int) -> bool:
        """Checks if user is authorized"""
        return user_id in config.AUTHORIZED_USER_IDS
    
    def handle_message(self, message):
        """Main message handler"""
        try:
            # Authorization check
            if not self.is_authorized(message.from_user.id):
                logger.warning(f"Unauthorized access attempt from {message.from_user.id}")
                self.bot.reply_to(message, "❌ Accès non autorisé à IBRARIUM.")
                return
            
            # Rate limiting check
            if not self.rate_limiter.is_allowed(message.from_user.id):
                self.bot.reply_to(message, "⚠️ Trop de commandes. Veuillez patienter.")
                return
            
            command_text = message.text.strip()
            logger.info(f"Command received from {message.from_user.username}: '{command_text}'")
            
            # Help handling
            if any(keyword in command_text.lower() for keyword in ['help', 'aide', 'commandes']):
                self.send_help(message)
                return
            
            # Command search
            command = self.command_manager.find_command(command_text)
            
            if not command:
                self.bot.reply_to(message, "❓ Commande non reconnue. Tapez 'aide' pour voir les commandes disponibles.")
                self.command_manager.log_command(message.from_user.id, command_text, "NOT_FOUND")
                return
            
            # Command execution
            self.execute_command(message, command, command_text)
            
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            self.bot.reply_to(message, "❌ Erreur interne du système.")
    
    def execute_command(self, message, command: Command, command_text: str):
        """Executes a command"""
        # Confirmation message
        category_emoji = {
            'climat': '🌡️',
            'jardin': '🌱',
            'media': '📺',
            'acces': '🚪',
            'eclairage': '💡',
            'cuisine': '☕',
            'electromenager': '🔌',
            'dev': '💻',
            'system': '⚙️'
        }
        
        emoji = category_emoji.get(command.category, '🔧')
        self.bot.reply_to(message, f"{emoji} IBRARIUM: {command.description}...")
        
        # Result callback
        def execution_callback(success: bool, result: str):
            if success:
                self.bot.send_message(message.chat.id, f"✅ {result}")
                self.command_manager.log_command(message.from_user.id, command_text, "SUCCESS", result)
            else:
                self.bot.send_message(message.chat.id, f"❌ {result}")
                self.command_manager.log_command(message.from_user.id, command_text, "ERROR", result)
        
        # Script execution
        self.script_executor.execute_script(
            command.script,
            command_text,
            execution_callback,
            command.timeout
        )
    
    def send_help(self, message):
        """Sends command help"""
        help_text = "🏠 **IBRARIUM - Commandes Disponibles**\n\n"
        
        categories = {}
        for cmd in set(self.command_manager.commands.values()):
            if cmd.category not in categories:
                categories[cmd.category] = []
            categories[cmd.category].append(cmd)
        
        category_names = {
            'climat': '🌡️ Climat',
            'jardin': '🌱 Jardin',
            'media': '📺 Média',
            'acces': '🚪 Accès',
            'eclairage': '💡 Éclairage',
            'cuisine': '☕ Cuisine',
            'electromenager': '🔌 Électroménager',
            'dev': '💻 Développement',
            'system': '⚙️ Système'
        }
        
        for category, commands in categories.items():
            help_text += f"**{category_names.get(category, category.title())}**\n"
            for cmd in commands:
                keywords = ', '.join(cmd.keywords[:3])  # Limit to 3 keywords
                help_text += f"• {keywords}: {cmd.description}\n"
            help_text += "\n"
        
        help_text += "📝 Tapez simplement un mot-clé pour déclencher une action."
        
        self.bot.reply_to(message, help_text, parse_mode='Markdown')
    
    def run(self):
        """Runs the bot"""
        try:
            logger.info("🚀 IBRARIUM BY JAMES AND GMN est en écoute des commandes Telegram...")
            self.bot.polling(none_stop=True, interval=1, timeout=20)
        except KeyboardInterrupt:
            logger.info("Bot shutdown requested by user")
        except Exception as e:
            logger.error(f"Critical error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        bot = IbrariumBot()
        bot.run()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
