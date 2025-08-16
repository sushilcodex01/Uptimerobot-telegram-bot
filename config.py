"""
Configuration management for Telegram URL Monitor Bot
"""

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.bot_token = "8405898835:AAE6g8TGXPjHeLt0NObIqFQv4mLreqxM"
        self.primary_admin_chat_id = 1691680798  # Main admin who can manage other admins
        self.admin_chat_ids = [1691680798]  # List of all admin chat IDs
        self.admin_data_file = "admin_data.json"  # File to store admin list
        self.ping_interval = 60  # seconds
        self.request_timeout = 30  # seconds
        self.data_file = "urls_data.json"
        self.log_file = "bot.log"
        self._load_admin_data()
        
    def _get_bot_token(self):
        """Get bot token from environment variables"""
        token = os.getenv("BOT_TOKEN", "8405898835:AAE6ga8TGXPjHeLt0NObIqFQv4mLreqxM")
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")
        return token
    
    def _get_admin_chat_id(self):
        """Get admin chat ID from environment variables"""
        chat_id = os.getenv("ADMIN_CHAT_ID", "1691680798")
        if not chat_id:
            raise ValueError("ADMIN_CHAT_ID environment variable is required")
        
        try:
            return int(chat_id)
        except ValueError:
            raise ValueError("ADMIN_CHAT_ID must be a valid integer")
    
    def _load_admin_data(self):
        """Load admin chat IDs from file"""
        import json
        try:
            with open(self.admin_data_file, 'r') as f:
                data = json.load(f)
                self.admin_chat_ids = data.get('admin_chat_ids', [self.primary_admin_chat_id])
                # Ensure primary admin is always in the list
                if self.primary_admin_chat_id not in self.admin_chat_ids:
                    self.admin_chat_ids.append(self.primary_admin_chat_id)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default admin data file
            self._save_admin_data()
            logger.info("Created default admin data file")
    
    def _save_admin_data(self):
        """Save admin chat IDs to file"""
        import json
        try:
            data = {
                'admin_chat_ids': self.admin_chat_ids,
                'primary_admin': self.primary_admin_chat_id
            }
            with open(self.admin_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved admin data with {len(self.admin_chat_ids)} admins")
        except Exception as e:
            logger.error(f"Error saving admin data: {e}")
    
    def is_admin(self, chat_id):
        """Check if the given chat ID is an admin"""
        return chat_id in self.admin_chat_ids
    
    def is_primary_admin(self, chat_id):
        """Check if the given chat ID is the primary admin"""
        return chat_id == self.primary_admin_chat_id
    
    def add_admin(self, chat_id):
        """Add a new admin chat ID"""
        if chat_id not in self.admin_chat_ids:
            self.admin_chat_ids.append(chat_id)
            self._save_admin_data()
            logger.info(f"Added new admin: {chat_id}")
            return True
        return False
    
    def remove_admin(self, chat_id):
        """Remove an admin chat ID (except primary admin)"""
        if chat_id == self.primary_admin_chat_id:
            return False  # Cannot remove primary admin
        if chat_id in self.admin_chat_ids:
            self.admin_chat_ids.remove(chat_id)
            self._save_admin_data()
            logger.info(f"Removed admin: {chat_id}")
            return True
        return False
    
    def get_admin_list(self):
        """Get list of all admin chat IDs"""
        return self.admin_chat_ids.copy()
    
    def validate_config(self):
        """Validate all configuration parameters"""
        errors = []
        
        if not self.bot_token:
            errors.append("Bot token is missing")
        
        if not self.admin_chat_id:
            errors.append("Admin chat ID is missing")
        
        if self.ping_interval <= 0:
            errors.append("Ping interval must be positive")
        
        if self.request_timeout <= 0:
            errors.append("Request timeout must be positive")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        logger.info("Configuration validated successfully")
        return True
