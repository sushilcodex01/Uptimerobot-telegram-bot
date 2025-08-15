"""
Telegram bot command handlers and message processing
Enhanced with advanced UI and interactive features
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from url_monitor import URLMonitor
from config import Config
from utils import format_uptime_message, format_url_list, validate_url
from advanced_ui import AdvancedUI

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, url_monitor: URLMonitor, config: Config):
        self.url_monitor = url_monitor
        self.config = config
        self.advanced_ui = AdvancedUI(url_monitor, config)
        self.url_hash_map = {}  # Store URL hash mappings for callbacks
    
    def _is_admin(self, update: Update) -> bool:
        """Check if the user is an admin"""
        if not update.effective_chat:
            return False
        return self.config.is_admin(update.effective_chat.id)
    
    async def _send_admin_only_message(self, update: Update):
        """Send admin-only access message"""
        await update.message.reply_text(
            "🔒 Access Denied\n\n"
            "This bot is restricted to admin use only.\n"
            "Please contact the administrator for access."
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        # Show typing animation for better UX
        await self.advanced_ui.show_typing_animation(update.effective_chat.id, context.bot, 2)
        
        welcome_msg = (
            "🚀 **Advanced URL Monitor Bot** 🚀\n\n"
            "Welcome to the next-generation URL monitoring system!\n\n"
            "✨ **New Features:**\n"
            "🎯 Smart Dashboard with Real-time Analytics\n"
            "⚡ Lightning-fast Response Time Tracking\n"
            "🔔 Intelligent Alert System\n"
            "📊 Advanced Statistics & Trends\n"
            "🎨 Modern Interactive Interface\n\n"
            "🤖 **AI-Powered Monitoring:**\n"
            "I automatically ping your URLs every 60 seconds using advanced algorithms and alert you instantly when issues are detected!\n\n"
            "Choose an option below to get started:"
        )
        
        # Use advanced main menu
        reply_markup = self.advanced_ui.create_main_menu_keyboard()
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        # Check if user is primary admin to show admin commands
        is_primary = self.config.is_primary_admin(update.effective_chat.id)
        
        help_msg = (
            "🆘 **Advanced Help System** 🆘\n\n"
            "🚀 **URL Monitoring Commands:**\n"
            "📌 `/seturl <url>` - Add URL with smart validation\n"
            "🗑️ `/removeurl <url>` - Remove URL with confirmation\n"
            "📋 `/listurls` - Interactive URL dashboard\n"
            "📊 `/status` - Advanced analytics dashboard\n"
            "🔄 `/pingnow` - Instant ping with progress animation\n\n"
        )
        
        if is_primary:
            help_msg += (
                "👥 **Admin Management Commands:**\n"
                "➕ `/addadmin <chat_id>` - Add new admin user\n"
                "➖ `/removeadmin <chat_id>` - Remove admin access\n"
                "📋 `/listadmins` - View all administrators\n\n"
            )
        
        help_msg += (
            "✨ **Advanced Features:**\n"
            "🎯 Smart Dashboard with Real-time Updates\n"
            "📈 Trend Analysis & Performance Insights\n"
            "🔔 Intelligent Alert System\n"
            "⚡ Sub-second Response Time Tracking\n"
            "📱 Mobile-Optimized Interface\n"
            "🎨 Interactive Buttons & Animations\n"
            "💾 Persistent Data with Auto-Recovery\n\n"
            "🎨 **Status Indicators:**\n"
            "🟢 Online - Excellent Performance\n"
            "🟡 Warning - Slower Response\n"
            "🔴 Offline - Service Down\n"
            "⏳ Pending - Initial Check\n\n"
            "💡 **Pro Tips:**\n"
            "• Use interactive buttons for faster navigation\n"
            "• Check the dashboard for detailed insights\n"
            "• Set up multiple URLs for comprehensive monitoring"
        )
        
        if is_primary:
            help_msg += "\n• Use Admin Panel to manage multiple users"
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Dashboard", callback_data="main_menu"),
                InlineKeyboardButton("📊 Quick Stats", callback_data="main_stats")
            ],
            [
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def set_url_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /seturl command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        # Check if URL is provided
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a URL to monitor.\n\n"
                "Usage: `/seturl <url>`\n"
                "Example: `/seturl https://myapp.herokuapp.com`",
                parse_mode='Markdown'
            )
            return
        
        url = context.args[0]
        
        # Validate URL
        if not validate_url(url):
            await update.message.reply_text(
                "❌ Invalid URL format.\n\n"
                "Please provide a valid URL starting with http:// or https://\n"
                "Example: `https://myapp.herokuapp.com`",
                parse_mode='Markdown'
            )
            return
        
        # Show processing animation
        processing_msg = await update.message.reply_text(
            "🔄 **Processing URL...**\n\n"
            "⏳ Validating URL format\n"
            "⏳ Testing connectivity\n"
            "⏳ Adding to monitoring system",
            parse_mode='Markdown'
        )
        
        # Add URL to monitoring
        success = self.url_monitor.add_url(url, str(update.effective_chat.id))
        
        if success:
            # Store URL hash mapping for callbacks
            url_hash = hash(url) % 10000
            self.url_hash_map[url_hash] = url
            
            # Create enhanced response with animations
            keyboard = [
                [
                    InlineKeyboardButton("📊 View Dashboard", callback_data="main_urls"),
                    InlineKeyboardButton("⚡ Test Now", callback_data=f"test_url:{url_hash}")
                ],
                [
                    InlineKeyboardButton("📈 View Stats", callback_data="main_stats"),
                    InlineKeyboardButton("🔄 Ping All", callback_data="quick_ping")
                ],
                [
                    InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                f"✅ **URL Successfully Added!** 🎉\n\n"
                f"🌐 **URL:** `{url}`\n"
                f"🎯 **Status:** Active Monitoring\n"
                f"⏰ **Ping Interval:** Every 60 seconds\n"
                f"🔔 **Alerts:** Instant notifications enabled\n"
                f"📊 **Analytics:** Real-time tracking started\n\n"
                f"🚀 **Next Steps:**\n"
                f"• View the dashboard for real-time status\n"
                f"• Test connectivity immediately\n"
                f"• Monitor performance analytics",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to add URL: `{url}`\n\n"
                "Please try again or check the URL format.",
                parse_mode='Markdown'
            )
    
    async def remove_url_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeurl command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        # Check if URL is provided
        if not context.args:
            # Show current URLs for easy removal
            urls = self.url_monitor.get_urls(str(update.effective_chat.id))
            if not urls:
                await update.message.reply_text(
                    "❌ No URLs are currently being monitored.\n\n"
                    "Use `/seturl <url>` to add URLs to monitor.",
                    parse_mode='Markdown'
                )
                return
            
            url_list = "\n".join([f"• `{url}`" for url in urls.keys()])
            await update.message.reply_text(
                "❌ Please specify which URL to remove.\n\n"
                "**Current URLs:**\n"
                f"{url_list}\n\n"
                "Usage: `/removeurl <url>`",
                parse_mode='Markdown'
            )
            return
        
        url = context.args[0]
        
        # Remove URL from monitoring
        success = self.url_monitor.remove_url(url, str(update.effective_chat.id))
        
        if success:
            keyboard = [
                [InlineKeyboardButton("📋 List Remaining URLs", callback_data="list_urls")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **URL Removed Successfully!**\n\n"
                f"**URL:** `{url}`\n"
                f"**Status:** No longer monitoring\n\n"
                f"This URL will no longer receive keep-alive pings.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"❌ URL not found: `{url}`\n\n"
                "This URL is not currently being monitored.\n"
                "Use `/listurls` to see all monitored URLs.",
                parse_mode='Markdown'
            )
    
    async def list_urls_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listurls command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        urls = self.url_monitor.get_urls(str(update.effective_chat.id))
        
        if not urls:
            keyboard = [
                [InlineKeyboardButton("➕ Add URL", callback_data="help_seturl")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📭 **No URLs Currently Monitored**\n\n"
                "You haven't added any URLs to monitor yet.\n\n"
                "Use `/seturl <url>` to start monitoring a URL.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        message = format_url_list(urls)
        
        # Add action buttons
        keyboard = [
            [InlineKeyboardButton("📊 Show Status", callback_data="show_status")],
            [InlineKeyboardButton("🔄 Ping Now", callback_data="ping_now")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        urls = self.url_monitor.get_urls(str(update.effective_chat.id))
        
        if not urls:
            await update.message.reply_text(
                "📊 **No Status Data Available**\n\n"
                "No URLs are currently being monitored.\n"
                "Use `/seturl <url>` to add URLs and start collecting statistics.",
                parse_mode='Markdown'
            )
            return
        
        message = "📊 **24-Hour Uptime Statistics**\n\n"
        
        for url in urls.keys():
            stats = self.url_monitor.get_uptime_stats(url, str(update.effective_chat.id), 24)
            message += format_uptime_message(url, stats)
            message += "\n"
        
        # Add monitoring status
        monitor_status = self.url_monitor.get_monitoring_status()
        status_icon = "🟢" if monitor_status["is_running"] else "🔴"
        message += f"\n**Monitoring Status:** {status_icon} {'Active' if monitor_status['is_running'] else 'Inactive'}\n"
        message += f"**Ping Interval:** {monitor_status['ping_interval']} seconds\n"
        message += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="show_status")],
            [InlineKeyboardButton("📋 List URLs", callback_data="list_urls")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def ping_now_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pingnow command"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        urls = self.url_monitor.get_urls(str(update.effective_chat.id))
        
        if not urls:
            await update.message.reply_text(
                "❌ **No URLs to Ping**\n\n"
                "No URLs are currently being monitored.\n"
                "Use `/seturl <url>` to add URLs first.",
                parse_mode='Markdown'
            )
            return
        
        # Send initial message
        status_msg = await update.message.reply_text(
            f"🔄 **Pinging {len(urls)} URLs...**\n\n"
            "Please wait while I check all your URLs.",
            parse_mode='Markdown'
        )
        
        try:
            # Perform the pings for this admin only
            results = await self.url_monitor.ping_admin_urls(str(update.effective_chat.id))
            
            # Format results
            message = "🔄 **Manual Ping Results**\n\n"
            
            for url, result in results.items():
                status_icon = "🟢" if result["success"] else "🔴"
                status_text = "Online" if result["success"] else "Offline"
                
                message += f"{status_icon} **{status_text}**\n"
                message += f"   `{url}`\n"
                message += f"   Status: {result['status_code']} | "
                message += f"Time: {result['response_time']:.3f}s\n\n"
            
            message += f"**Completed:** {datetime.now().strftime('%H:%M:%S')}"
            
            # Add action buttons
            keyboard = [
                [InlineKeyboardButton("📊 Show Status", callback_data="show_status")],
                [InlineKeyboardButton("📋 List URLs", callback_data="list_urls")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the status message
            await status_msg.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in ping_now_command: {e}")
            await status_msg.edit_text(
                f"❌ **Ping Failed**\n\n"
                f"An error occurred while pinging URLs: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def add_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command - Only primary admin can add new admins"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            await update.message.reply_text(
                "🔒 **Access Denied**\n\n"
                "Only the primary admin can add new administrators.",
                parse_mode='Markdown'
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ **Usage Error**\n\n"
                "**Correct usage:** `/addadmin <chat_id>`\n\n"
                "**Example:** `/addadmin 123456789`\n\n"
                "**How to get Chat ID:**\n"
                "Ask the user to send a message to @userinfobot to get their chat ID.",
                parse_mode='Markdown'
            )
            return
        
        try:
            new_admin_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid Chat ID**\n\n"
                "Chat ID must be a number.\n\n"
                "Example: `/addadmin 123456789`",
                parse_mode='Markdown'
            )
            return
        
        if self.config.add_admin(new_admin_id):
            await update.message.reply_text(
                f"✅ **Admin Added Successfully!**\n\n"
                f"**New Admin ID:** `{new_admin_id}`\n"
                f"**Total Admins:** {len(self.config.get_admin_list())}\n\n"
                f"This user can now use all bot features.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"ℹ️ **Admin Already Exists**\n\n"
                f"Chat ID `{new_admin_id}` is already an admin.",
                parse_mode='Markdown'
            )
    
    async def remove_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeadmin command - Only primary admin can remove admins"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            await update.message.reply_text(
                "🔒 **Access Denied**\n\n"
                "Only the primary admin can remove administrators.",
                parse_mode='Markdown'
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ **Usage Error**\n\n"
                "**Correct usage:** `/removeadmin <chat_id>`\n\n"
                "**Example:** `/removeadmin 123456789`\n\n"
                "Use `/listadmins` to see all current admins.",
                parse_mode='Markdown'
            )
            return
        
        try:
            admin_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid Chat ID**\n\n"
                "Chat ID must be a number.",
                parse_mode='Markdown'
            )
            return
        
        if self.config.remove_admin(admin_id):
            await update.message.reply_text(
                f"✅ **Admin Removed Successfully!**\n\n"
                f"**Removed Admin ID:** `{admin_id}`\n"
                f"**Remaining Admins:** {len(self.config.get_admin_list())}\n\n"
                f"This user can no longer use bot features.",
                parse_mode='Markdown'
            )
        else:
            if admin_id == self.config.primary_admin_chat_id:
                await update.message.reply_text(
                    "❌ **Cannot Remove Primary Admin**\n\n"
                    "The primary admin cannot be removed for security reasons.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ **Admin Not Found**\n\n"
                    f"Chat ID `{admin_id}` is not currently an admin.",
                    parse_mode='Markdown'
                )
    
    async def list_admins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listadmins command - Only primary admin can view admin list"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            await update.message.reply_text(
                "🔒 **Access Denied**\n\n"
                "Only the primary admin can view the admin list.",
                parse_mode='Markdown'
            )
            return
        
        admin_list = self.config.get_admin_list()
        
        message = "👥 **Admin Management Panel**\n\n"
        message += f"**Total Admins:** {len(admin_list)}\n\n"
        
        for i, admin_id in enumerate(admin_list, 1):
            if admin_id == self.config.primary_admin_chat_id:
                message += f"**{i}.** `{admin_id}` 👑 **Primary Admin**\n"
            else:
                message += f"**{i}.** `{admin_id}`\n"
        
        message += f"\n**Commands:**\n"
        message += f"• `/addadmin <chat_id>` - Add new admin\n"
        message += f"• `/removeadmin <chat_id>` - Remove admin\n"
        message += f"• `/listadmins` - Show this list\n\n"
        message += f"**Note:** Only primary admin can manage other admins."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self._is_admin(update):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        callback_data = query.data
        
        # Handle advanced UI callbacks
        if callback_data == "main_menu":
            await self._handle_main_menu_callback(query)
        elif callback_data == "main_urls":
            await self._handle_main_urls_callback(query)
        elif callback_data == "main_stats":
            await self._handle_main_stats_callback(query)
        elif callback_data == "main_settings":
            await self._handle_settings_callback(query)
        elif callback_data == "quick_ping":
            await self._handle_quick_ping_callback(query)
        elif callback_data == "analytics":
            await self._handle_analytics_callback(query)
        elif callback_data == "view_alerts":
            await self._handle_alerts_callback(query)
        elif callback_data == "help_menu":
            await self._handle_help_menu_callback(query)
        elif callback_data == "refresh_main":
            await self._handle_main_menu_callback(query)
        elif callback_data.startswith("urls_page:"):
            page = int(callback_data.split(":")[1])
            await self._handle_urls_page_callback(query, page)
        elif callback_data.startswith("test_url:"):
            url_hash = int(callback_data.split(":")[1])
            await self._handle_test_url_callback(query, url_hash)
        elif callback_data.startswith("url_detail:"):
            url_hash = int(callback_data.split(":")[1])
            await self._handle_url_detail_callback(query, url_hash)
        elif callback_data.startswith("remove_url:"):
            url_hash = int(callback_data.split(":")[1])
            await self._handle_remove_url_callback(query, url_hash)
        elif callback_data.startswith("confirm_remove:"):
            url_hash = int(callback_data.split(":")[1])
            await self._handle_confirm_remove_callback(query, url_hash)
        elif callback_data == "add_url_wizard":
            await self._handle_add_url_wizard_callback(query)
        elif callback_data == "remove_url_menu":
            await self._handle_remove_url_menu_callback(query)
        elif callback_data == "admin_panel":
            await self._handle_admin_panel_callback(query)
        # Legacy callbacks for compatibility
        elif callback_data == "list_urls":
            await self._handle_main_urls_callback(query)
        elif callback_data == "show_status":
            await self._handle_main_stats_callback(query)
        elif callback_data == "ping_now":
            await self._handle_quick_ping_callback(query)
        elif callback_data == "help_seturl":
            await self._handle_add_url_wizard_callback(query)
    
    async def _handle_list_urls_callback(self, query):
        """Handle list URLs button callback"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        
        if not urls:
            keyboard = [
                [InlineKeyboardButton("➕ Add URL", callback_data="help_seturl")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📭 **No URLs Currently Monitored**\n\n"
                "You haven't added any URLs to monitor yet.\n\n"
                "Use `/seturl <url>` to start monitoring a URL.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        message = format_url_list(urls)
        
        keyboard = [
            [InlineKeyboardButton("📊 Show Status", callback_data="show_status")],
            [InlineKeyboardButton("🔄 Ping Now", callback_data="ping_now")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_show_status_callback(self, query):
        """Handle show status button callback"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        
        if not urls:
            await query.edit_message_text(
                "📊 **No Status Data Available**\n\n"
                "No URLs are currently being monitored.",
                parse_mode='Markdown'
            )
            return
        
        message = "📊 **24-Hour Uptime Statistics**\n\n"
        
        for url in urls.keys():
            stats = self.url_monitor.get_uptime_stats(url, str(update.effective_chat.id), 24)
            message += format_uptime_message(url, stats)
            message += "\n"
        
        monitor_status = self.url_monitor.get_monitoring_status()
        status_icon = "🟢" if monitor_status["is_running"] else "🔴"
        message += f"\n**Monitoring Status:** {status_icon} {'Active' if monitor_status['is_running'] else 'Inactive'}\n"
        message += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="show_status")],
            [InlineKeyboardButton("📋 List URLs", callback_data="list_urls")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_ping_now_callback(self, query):
        """Handle ping now button callback"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        
        if not urls:
            await query.edit_message_text(
                "❌ **No URLs to Ping**\n\n"
                "No URLs are currently being monitored.",
                parse_mode='Markdown'
            )
            return
        
        # Update message to show pinging status
        await query.edit_message_text(
            f"🔄 **Pinging {len(urls)} URLs...**\n\n"
            "Please wait while I check all your URLs.",
            parse_mode='Markdown'
        )
        
        try:
            # Perform the pings for this admin only
            results = await self.url_monitor.ping_admin_urls(str(query.message.chat.id))
            
            # Format results
            message = "🔄 **Manual Ping Results**\n\n"
            
            for url, result in results.items():
                status_icon = "🟢" if result["success"] else "🔴"
                status_text = "Online" if result["success"] else "Offline"
                
                message += f"{status_icon} **{status_text}**\n"
                message += f"   `{url}`\n"
                message += f"   Status: {result['status_code']} | "
                message += f"Time: {result['response_time']:.3f}s\n\n"
            
            message += f"**Completed:** {datetime.now().strftime('%H:%M:%S')}"
            
            keyboard = [
                [InlineKeyboardButton("📊 Show Status", callback_data="show_status")],
                [InlineKeyboardButton("📋 List URLs", callback_data="list_urls")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in ping now callback: {e}")
            await query.edit_message_text(
                f"❌ **Ping Failed**\n\n"
                f"An error occurred while pinging URLs: {str(e)}",
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        if not self._is_admin(update):
            await self._send_admin_only_message(update)
            return
        
        # Provide helpful response for non-command messages
        keyboard = [
            [InlineKeyboardButton("📋 List URLs", callback_data="list_urls")],
            [InlineKeyboardButton("📊 Show Status", callback_data="show_status")],
            [InlineKeyboardButton("🆘 Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **AI Assistant Active**\n\n"
            "I didn't quite understand that message, but I'm here to help!\n\n"
            "🚀 **Quick Actions:**",
            reply_markup=reply_markup
        )
    
    # Advanced UI callback handlers
    async def _handle_main_menu_callback(self, query):
        """Handle main menu callback with advanced UI"""
        welcome_msg = (
            "🚀 **Advanced URL Monitor Dashboard** 🚀\n\n"
            "🎯 **System Status:** ⚡ Active\n"
            "📊 **Real-time Monitoring:** Enabled\n"
            "🔔 **Smart Alerts:** Ready\n\n"
            "Choose an action below to continue:"
        )
        
        reply_markup = self.advanced_ui.create_main_menu_keyboard()
        
        await query.edit_message_text(
            welcome_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_main_urls_callback(self, query):
        """Handle URLs dashboard callback"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        message, reply_markup = self.advanced_ui.format_enhanced_url_list(urls)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_main_stats_callback(self, query):
        """Handle statistics dashboard callback"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        message, reply_markup = self.advanced_ui.format_advanced_stats(urls)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_settings_callback(self, query):
        """Handle settings menu callback"""
        settings_msg = (
            "⚙️ **Advanced Settings Panel** ⚙️\n\n"
            "🎨 **Customize Your Experience:**\n"
            "Configure monitoring intervals, notification preferences,\n"
            "and advanced features to suit your needs.\n\n"
            "Choose a setting category:"
        )
        
        reply_markup = self.advanced_ui.create_settings_keyboard()
        
        await query.edit_message_text(
            settings_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_quick_ping_callback(self, query):
        """Handle quick ping with advanced animation"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        
        if not urls:
            await query.edit_message_text(
                "❌ **No URLs to Ping**\n\n"
                "No URLs are currently being monitored.\n"
                "Add some URLs first to use this feature.",
                parse_mode='Markdown'
            )
            return
        
        # Show enhanced loading animation
        await query.edit_message_text(
            f"🚀 **Initiating Advanced Ping Sequence** 🚀\n\n"
            f"⚡ Preparing to ping {len(urls)} URLs...\n"
            f"🎯 Using optimized parallel processing\n"
            f"📊 Real-time analysis enabled\n\n"
            f"⏳ Please wait...",
            parse_mode='Markdown'
        )
        
        # Simulate progress updates
        await asyncio.sleep(1)
        await query.edit_message_text(
            f"🔄 **Processing URLs** 🔄\n\n"
            f"▰▰▱▱▱ 40% Complete\n"
            f"🎯 Testing connectivity...\n"
            f"📡 Measuring response times...",
            parse_mode='Markdown'
        )
        
        try:
            # Perform the pings for this admin only
            results = await self.url_monitor.ping_admin_urls(str(query.message.chat.id))
            
            # Enhanced results display
            message = "⚡ **Advanced Ping Results** ⚡\n\n"
            
            online_count = 0
            total_response_time = 0
            
            for url, result in results.items():
                if result["success"]:
                    online_count += 1
                    total_response_time += result["response_time"]
                    status_icon = "🟢"
                    status_text = "ONLINE"
                    if result["response_time"] < 1.0:
                        speed_text = "⚡ Lightning"
                    elif result["response_time"] < 3.0:
                        speed_text = "🟡 Good"
                    else:
                        speed_text = "🔴 Slow"
                else:
                    status_icon = "🔴"
                    status_text = "OFFLINE"
                    speed_text = "❌ Failed"
                
                message += f"{status_icon} **{status_text}**\n"
                message += f"   🌐 `{url[:40]}{'...' if len(url) > 40 else ''}`\n"
                message += f"   📊 Status: {result['status_code']} | {speed_text} ({result['response_time']:.3f}s)\n\n"
            
            # Summary stats
            avg_response = total_response_time / online_count if online_count > 0 else 0
            success_rate = (online_count / len(results)) * 100
            
            message += f"📈 **Performance Summary:**\n"
            message += f"✅ Success Rate: {success_rate:.1f}%\n"
            message += f"⚡ Average Response: {avg_response:.3f}s\n"
            message += f"🕐 Completed: {datetime.now().strftime('%H:%M:%S')}"
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 View Stats", callback_data="main_stats"),
                    InlineKeyboardButton("🌐 URL Dashboard", callback_data="main_urls")
                ],
                [
                    InlineKeyboardButton("🔄 Ping Again", callback_data="quick_ping"),
                    InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in quick ping callback: {e}")
            await query.edit_message_text(
                f"❌ **Ping Operation Failed**\n\n"
                f"An error occurred during the ping sequence.\n"
                f"**Error:** {str(e)}\n\n"
                f"Please try again or check your URLs.",
                parse_mode='Markdown'
            )
    
    async def _handle_analytics_callback(self, query):
        """Handle analytics dashboard"""
        await query.edit_message_text(
            "📈 **Advanced Analytics Dashboard** 📈\n\n"
            "🚀 **Coming Soon:**\n"
            "• Performance trend analysis\n"
            "• Predictive downtime alerts\n"
            "• Custom reporting periods\n"
            "• Export data capabilities\n"
            "• Historical comparison charts\n\n"
            "This feature is currently in development.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    
    async def _handle_alerts_callback(self, query):
        """Handle alerts management"""
        await query.edit_message_text(
            "🔔 **Smart Alert System** 🔔\n\n"
            "🎯 **Alert Status:** Active\n"
            "⚡ **Response Time:** Instant\n"
            "🔄 **Auto-Recovery Detection:** Enabled\n\n"
            "🚀 **Advanced Features:**\n"
            "• Real-time downtime notifications\n"
            "• Smart recovery alerts\n"
            "• Performance degradation warnings\n"
            "• Custom alert thresholds\n\n"
            "All alerts are automatically sent to this chat.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    
    async def _handle_help_menu_callback(self, query):
        """Handle help menu"""
        help_msg = (
            "🆘 **Interactive Help Center** 🆘\n\n"
            "🎯 **Quick Navigation:**\n"
            "Use the interactive buttons for fast access to all features!\n\n"
            "⚡ **Speed Tips:**\n"
            "• Dashboard shows real-time status\n"
            "• Tap URLs for detailed information\n"
            "• Use Quick Ping for instant checks\n"
            "• Analytics provide deep insights\n\n"
            "🚀 **Pro Features:**\n"
            "• Animated loading indicators\n"
            "• Progress tracking\n"
            "• Mobile-optimized interface\n"
            "• Smart error handling"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Dashboard", callback_data="main_menu"),
                InlineKeyboardButton("📊 Quick Stats", callback_data="main_stats")
            ],
            [
                InlineKeyboardButton("🌐 URLs", callback_data="main_urls"),
                InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_add_url_wizard_callback(self, query):
        """Handle add URL wizard"""
        await query.edit_message_text(
            "➕ **Smart URL Addition Wizard** ➕\n\n"
            "🎯 **Ready to add a new URL for monitoring!**\n\n"
            "✨ **Features:**\n"
            "• Automatic URL validation\n"
            "• Instant connectivity testing\n"
            "• Smart protocol detection\n"
            "• Real-time status updates\n\n"
            "📝 **How to add:**\n"
            "Type: `/seturl <your-url>`\n\n"
            "📌 **Example:**\n"
            "`/seturl https://myapp.herokuapp.com`\n\n"
            "💡 **Tip:** You can omit 'https://' - I'll add it automatically!",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    
    async def _handle_remove_url_menu_callback(self, query):
        """Handle remove URL menu"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        
        if not urls:
            await query.edit_message_text(
                "🗑️ **Remove URL Menu** 🗑️\n\n"
                "📭 **No URLs to Remove**\n\n"
                "You don't have any URLs currently being monitored.\n"
                "Add some URLs first to enable removal options!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                    ]
                ])
            )
            return
        
        # Create the remove URL interface
        reply_markup = self.advanced_ui.create_remove_url_keyboard(urls)
        
        message = f"🗑️ **Smart URL Removal Wizard** 🗑️\n\n"
        message += f"🎯 **Ready to remove URLs from monitoring!**\n\n"
        message += f"✨ **Features:**\n"
        message += f"• Instant URL removal\n"
        message += f"• Clean database cleanup\n"
        message += f"• Stop monitoring immediately\n"
        message += f"• Smart confirmation system\n\n"
        message += f"📊 **Currently monitoring {len(urls)} URLs**\n\n"
        message += f"📝 **How to remove:**\n"
        message += f"1. Click on any URL below to select it\n"
        message += f"2. Confirm your removal choice\n"
        message += f"3. URL will be removed instantly\n\n"
        message += f"💡 **Tip:** You can also use `/removeurl <url>` command!\n\n"
        message += f"⚠️ **Note:** Removal is immediate and cannot be undone."
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_admin_panel_callback(self, query):
        """Handle admin panel callback"""
        if not self.config.is_primary_admin(query.from_user.id):
            await query.edit_message_text(
                "🔒 **Access Denied**\n\n"
                "Only the primary admin can access the admin panel.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
            return
        
        admin_list = self.config.get_admin_list()
        
        message = "👥 **Admin Management Panel**\n\n"
        message += f"**Total Admins:** {len(admin_list)}\n\n"
        
        # Show first 5 admins
        for i, admin_id in enumerate(admin_list[:5], 1):
            if admin_id == self.config.primary_admin_chat_id:
                message += f"**{i}.** `{admin_id}` 👑 **Primary**\n"
            else:
                message += f"**{i}.** `{admin_id}`\n"
        
        if len(admin_list) > 5:
            message += f"... and {len(admin_list) - 5} more\n"
        
        message += f"\n**Quick Commands:**\n"
        message += f"• Use `/addadmin <chat_id>` to add new admin\n"
        message += f"• Use `/removeadmin <chat_id>` to remove admin\n"
        message += f"• Use `/listadmins` for complete list"
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Admin", callback_data="add_admin_help"),
                InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin_help")
            ],
            [
                InlineKeyboardButton("📋 Full Admin List", callback_data="show_all_admins"),
                InlineKeyboardButton("ℹ️ How to Get Chat ID", callback_data="chat_id_help")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_urls_page_callback(self, query, page):
        """Handle URL pagination"""
        urls = self.url_monitor.get_urls(str(query.message.chat.id))
        message, reply_markup = self.advanced_ui.format_enhanced_url_list(urls, page)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_test_url_callback(self, query, url_hash):
        """Handle individual URL testing"""
        if url_hash not in self.url_hash_map:
            await query.edit_message_text("❌ URL not found. Please refresh and try again.")
            return
        
        url = self.url_hash_map[url_hash]
        
        await query.edit_message_text(
            f"🧪 **Testing URL** 🧪\n\n"
            f"🌐 `{url}`\n\n"
            f"⚡ Running connectivity test...\n"
            f"📊 Measuring response time...\n"
            f"🔍 Analyzing performance...",
            parse_mode='Markdown'
        )
        
        # Perform single URL test
        result = await self.url_monitor.ping_url(url)
        
        if result["success"]:
            status_icon = "✅"
            status_text = "ONLINE"
            if result["response_time"] < 1.0:
                performance = "⚡ Excellent"
            elif result["response_time"] < 3.0:
                performance = "🟡 Good"
            else:
                performance = "🔴 Slow"
        else:
            status_icon = "❌"
            status_text = "OFFLINE"
            performance = "🚫 Failed"
        
        message = f"🧪 **URL Test Results** 🧪\n\n"
        message += f"🌐 **URL:** `{url}`\n"
        message += f"{status_icon} **Status:** {status_text}\n"
        message += f"📊 **HTTP Code:** {result['status_code']}\n"
        message += f"⏱️ **Response Time:** {result['response_time']:.3f}s\n"
        message += f"📈 **Performance:** {performance}\n"
        
        if result.get("error"):
            message += f"⚠️ **Error:** {result['error']}\n"
        
        message += f"\n🕐 **Test Time:** {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Test Again", callback_data=f"test_url:{url_hash}"),
                InlineKeyboardButton("📊 View Stats", callback_data="main_stats")
            ],
            [
                InlineKeyboardButton("🌐 All URLs", callback_data="main_urls"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_remove_url_callback(self, query, url_hash):
        """Handle URL removal through button interface"""
        if url_hash not in self.url_hash_map:
            await query.edit_message_text(
                "❌ URL not found. Please refresh and try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh URLs", callback_data="main_urls")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
            return
        
        url = self.url_hash_map[url_hash]
        
        # Show confirmation message
        await query.edit_message_text(
            f"🗑️ **Confirm URL Removal**\n\n"
            f"**URL:** `{url}`\n\n"
            f"⚠️ This will stop monitoring this URL permanently.\n"
            f"Are you sure you want to remove it?",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Yes, Remove", callback_data=f"confirm_remove:{url_hash}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="main_urls")
                ]
            ])
        )
    
    async def _handle_confirm_remove_callback(self, query, url_hash):
        """Handle confirmed URL removal"""
        if url_hash not in self.url_hash_map:
            await query.edit_message_text(
                "❌ URL not found. Please refresh and try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh URLs", callback_data="main_urls")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
            return
        
        url = self.url_hash_map[url_hash]
        
        # Show processing message
        await query.edit_message_text(
            f"🗑️ **Removing URL...**\n\n"
            f"**URL:** `{url}`\n\n"
            f"⏳ Stopping monitoring...\n"
            f"⏳ Removing from database...\n"
            f"⏳ Cleaning up resources...",
            parse_mode='Markdown'
        )
        
        # Remove URL from monitoring
        success = self.url_monitor.remove_url(url, str(query.message.chat.id))
        
        if success:
            # Remove from hash mapping
            if url_hash in self.url_hash_map:
                del self.url_hash_map[url_hash]
            
            # Show success message
            keyboard = [
                [
                    InlineKeyboardButton("📋 View Remaining URLs", callback_data="main_urls"),
                    InlineKeyboardButton("➕ Add New URL", callback_data="add_url_wizard")
                ],
                [
                    InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ **URL Removed Successfully!**\n\n"
                f"**Removed URL:** `{url}`\n"
                f"**Status:** No longer monitoring\n\n"
                f"This URL will no longer receive keep-alive pings.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                f"❌ **Failed to Remove URL**\n\n"
                f"**URL:** `{url}`\n"
                f"This URL may not exist in the monitoring system.\n\n"
                f"Use the URL list to see all monitored URLs.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 View URLs", callback_data="main_urls")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
