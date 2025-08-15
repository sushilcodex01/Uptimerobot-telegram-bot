#!/usr/bin/env python3
"""
Telegram URL Monitor Bot - Main entry point
Monitors URLs with keep-alive pings and real-time status alerts
"""

import asyncio
import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from bot_handlers import BotHandlers
from url_monitor import URLMonitor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramURLBot:
    def __init__(self):
        self.config = Config()
        self.url_monitor = URLMonitor()
        self.bot_handlers = BotHandlers(self.url_monitor, self.config)
        self.application = None
        
    async def setup_bot(self):
        """Initialize the Telegram bot application"""
        try:
            # Create application
            self.application = Application.builder().token(self.config.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.bot_handlers.start_command))
            self.application.add_handler(CommandHandler("help", self.bot_handlers.help_command))
            self.application.add_handler(CommandHandler("seturl", self.bot_handlers.set_url_command))
            self.application.add_handler(CommandHandler("removeurl", self.bot_handlers.remove_url_command))
            self.application.add_handler(CommandHandler("listurls", self.bot_handlers.list_urls_command))
            self.application.add_handler(CommandHandler("status", self.bot_handlers.status_command))
            self.application.add_handler(CommandHandler("pingnow", self.bot_handlers.ping_now_command))
            
            # Admin management commands
            self.application.add_handler(CommandHandler("addadmin", self.bot_handlers.add_admin_command))
            self.application.add_handler(CommandHandler("removeadmin", self.bot_handlers.remove_admin_command))
            self.application.add_handler(CommandHandler("listadmins", self.bot_handlers.list_admins_command))
            
            # Add callback query handler for inline buttons
            from telegram.ext import CallbackQueryHandler
            self.application.add_handler(CallbackQueryHandler(self.bot_handlers.button_callback))
            
            # Add message handler for non-command messages
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.bot_handlers.handle_message))
            
            logger.info("Bot handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup bot: {e}")
            raise
    
    async def start_monitoring(self):
        """Start the URL monitoring in background"""
        try:
            # Set the bot instance for sending alerts
            self.url_monitor.set_bot_instance(self.application.bot)
            self.url_monitor.set_admin_chat_id(self.config.primary_admin_chat_id)
            
            # Start monitoring task
            monitoring_task = asyncio.create_task(self.url_monitor.start_monitoring())
            logger.info("URL monitoring started")
            return monitoring_task
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise
    
    async def run(self):
        """Run the bot"""
        try:
            logger.info("Starting Telegram URL Monitor Bot...")
            
            # Setup bot
            await self.setup_bot()
            
            # Start monitoring task
            monitoring_task = await self.start_monitoring()
            
            # Initialize and start the bot
            await self.application.initialize()
            await self.application.start()
            
            # Start polling
            logger.info("Bot is running and polling for updates...")
            await self.application.updater.start_polling()
            
            # Keep the bot running
            try:
                await monitoring_task
            except asyncio.CancelledError:
                logger.info("Monitoring task cancelled")
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            # Cleanup
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            logger.info("Bot stopped")

def main():
    """Main entry point"""
    try:
        bot = TelegramURLBot()
        asyncio.run(bot.run())
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()
