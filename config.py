"""
Configuration management for Telegram URL Monitor Bot
"""

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.bot_token = "8060041650:AAHG2XvkP-8wi07B5GQ4D77RqcFEaAfMujU"
        self.ping_interval = 60  # seconds
        self.request_timeout = 30  # seconds
        self.log_file = "bot.log"
        # Bot is now open to all users, no admin restrictions
        self.open_to_all_users = True
        self.primary_admin_chat_id = 1691680798  # Primary admin
        self.admin_list = [1691680798]  # List of admin chat IDs
        
    def _get_bot_token(self):
        """Get bot token from environment variables"""
        token = os.getenv("BOT_TOKEN", "8060041650:AAHG2XvkP-8wi07B5GQ4D77RqcFEaAfMujU")
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
    
    def is_user_allowed(self, chat_id):
        """Check if the user is allowed to use the bot (now open to all)"""
        return True  # Bot is now open to all users
    
    def is_primary_admin(self, chat_id):
        """Check if user is the primary admin"""
        return chat_id == self.primary_admin_chat_id
    
    def add_admin(self, chat_id):
        """Add a new admin"""
        if chat_id not in self.admin_list:
            self.admin_list.append(chat_id)
            return True
        return False
    
    def remove_admin(self, chat_id):
        """Remove an admin (except primary admin)"""
        if chat_id != self.primary_admin_chat_id and chat_id in self.admin_list:
            self.admin_list.remove(chat_id)
            return True
        return False
    
    def get_admin_list(self):
        """Get list of all admins"""
        return self.admin_list.copy()
    
    def validate_config(self):
        """Validate all configuration parameters"""
        errors = []
        
        if not self.bot_token:
            errors.append("Bot token is missing")
        
        if self.ping_interval <= 0:
            errors.append("Ping interval must be positive")
        
        if self.request_timeout <= 0:
            errors.append("Request timeout must be positive")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        logger.info("Configuration validated successfully")
        return True
