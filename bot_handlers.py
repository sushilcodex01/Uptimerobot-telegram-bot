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
from notion_data_manager import NotionDataManager

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, url_monitor: URLMonitor, config: Config):
        self.url_monitor = url_monitor
        self.config = config
        self.notion_data = NotionDataManager()
        self.advanced_ui = AdvancedUI(url_monitor, config)
        self.url_hash_map = {}  # Store URL hash mappings for callbacks
        
    def _generate_url_hash(self, url: str) -> str:
        """Generate consistent hash for URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    async def _refresh_url_hash_map(self, user_chat_id: str) -> None:
        """Refresh URL hash mapping for user"""
        try:
            urls = await self.notion_data.get_user_urls(user_chat_id)
            self.url_hash_map.clear()
            
            for url in urls.keys():
                url_hash = self._generate_url_hash(url)
                self.url_hash_map[url_hash] = url
                
            logger.debug(f"Refreshed hash map with {len(self.url_hash_map)} URLs")
        except Exception as e:
            logger.error(f"Error refreshing URL hash map: {e}")
    
    def _is_user_allowed(self, update: Update) -> bool:
        """Check if the user is allowed to use the bot"""
        if not update.effective_chat:
            return False
        return self.config.is_user_allowed(update.effective_chat.id)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        # Show typing animation for better UX
        await self.advanced_ui.show_typing_animation(update.effective_chat.id, context.bot, 2)
        
        user = update.effective_user
        username = user.username or user.first_name or "User"
        
        welcome_msg = (
            f"👋 Welcome {username}!\n\n"
            "🚀 **URL Monitor Bot** 🚀\n\n"
            "Monitor your websites and get instant alerts when they go down!\n\n"
            "✨ **Features:**\n"
            "📊 Real-time monitoring every 60 seconds\n"
            "⚡ Response time tracking\n"
            "🔔 Instant downtime alerts\n"
            "📈 Statistics and trends\n"
            "💾 All data stored securely in Notion\n\n"
            "Start by adding your first URL to monitor:"
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        help_msg = (
            "🆘 **Help - URL Monitor Bot** 🆘\n\n"
            "🚀 **Available Commands:**\n"
            "📌 `/seturl <url>` - Add URL to monitor\n"
            "🗑️ `/removeurl <url>` - Remove URL from monitoring\n"
            "📋 `/listurls` - View all your monitored URLs\n"
            "📊 `/status` - View statistics and status\n"
            "🔄 `/pingnow` - Test all URLs immediately\n\n"
            "💾 **Notion Integration:**\n"
            "• All your data is stored securely in Notion database\n"
            "• Each user has their own separate data\n"
            "• Real-time monitoring every 60 seconds\n\n"
            "🎨 **Status Indicators:**\n"
            "🟢 Online - Website is working\n"
            "🔴 Offline - Website is down\n"
            "⏳ Pending - First check in progress\n\n"
            "💡 **Tips:**\n"
            "• Start by adding a URL with /seturl\n"
            "• Check your dashboard regularly\n"
            "• You'll get instant alerts for downtime"
        )
        
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
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
        
        # Get user info
        user = update.effective_user
        username = user.username or user.first_name
        
        # Add URL to Notion database
        success = await self.notion_data.add_url(url, str(update.effective_chat.id), username)
        
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        # Check if URL is provided
        if not context.args:
            # Show current URLs for easy removal
            urls = await self.notion_data.get_user_urls(str(update.effective_chat.id))
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
        success = await self.notion_data.remove_url(url, str(update.effective_chat.id))
        
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        urls = await self.notion_data.get_user_urls(str(update.effective_chat.id))
        
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        urls = await self.notion_data.get_user_urls(str(update.effective_chat.id))
        
        if not urls:
            await update.message.reply_text(
                "📊 **No Status Data Available**\n\n"
                "No URLs are currently being monitored.\n"
                "Use `/seturl <url>` to add URLs and start collecting statistics.",
                parse_mode='Markdown'
            )
            return
        
        # Get statistics from Notion database
        stats = await self.notion_data.get_url_statistics(str(update.effective_chat.id))
        
        message = f"📊 **Your URL Statistics**\n\n"
        message += f"**Total URLs:** {stats['total_urls']}\n"
        message += f"🟢 **Online:** {stats['online']}\n"
        message += f"🔴 **Offline:** {stats['offline']}\n"
        message += f"⏳ **Pending:** {stats['pending']}\n"
        message += f"⚡ **Avg Response:** {stats['average_response_time']}ms\n\n"
        
        # Show individual URL statuses
        for url, data in urls.items():
            status_icon = "🟢" if data['status'] == 'online' else "🔴" if data['status'] == 'offline' else "⏳"
            response_time_str = f" ({data['response_time']}ms)" if data['response_time'] else ""
            message += f"{status_icon} `{url}`{response_time_str}\n"
        
        # Add monitoring status
        monitor_status = await self.url_monitor.get_monitoring_status()
        status_icon = "🟢" if monitor_status["is_running"] else "🔴"
        message += f"\n**Monitoring Status:** {status_icon} {'Active' if monitor_status['is_running'] else 'Inactive'}\n"
        message += f"**Ping Interval:** {monitor_status['ping_interval']} seconds\n"
        message += f"**Data Storage:** Notion Database\n"
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
            return
        
        urls = await self.notion_data.get_user_urls(str(update.effective_chat.id))
        
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
            # Perform the pings for this user only
            results = await self.url_monitor.ping_user_urls(str(update.effective_chat.id))
            
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
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command - Admin only"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            await update.message.reply_text(
                "🔒 **Access Denied**\n\n"
                "Only admins can use the broadcast feature.",
                parse_mode='Markdown'
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "📢 **Broadcast Command Usage**\n\n"
                "**Format:** `/broadcast <message>`\n\n"
                "**Example:** `/broadcast 🚀 New features are now available!`\n\n"
                "**Features:**\n"
                "• Send to all active users\n"
                "• Markdown formatting supported\n"
                "• Instant delivery\n"
                "• Delivery confirmation\n\n"
                "**Pro tip:** Use emojis and formatting for better engagement!",
                parse_mode='Markdown'
            )
            return
        
        # Get the broadcast message
        broadcast_message = ' '.join(context.args)
        
        # Show confirmation
        confirm_msg = await update.message.reply_text(
            f"📢 **Broadcast Preview**\n\n"
            f"**Message to broadcast:**\n"
            f"{broadcast_message}\n\n"
            f"⚡ **Preparing broadcast...**\n"
            f"🎯 Getting user list...\n"
            f"📊 Calculating delivery...",
            parse_mode='Markdown'
        )
        
        # Get all users
        all_urls = await self.notion_data.get_all_urls()
        user_ids = set(all_urls.values()) if all_urls else set()
        
        if not user_ids:
            await confirm_msg.edit_text(
                "📢 **Broadcast Status**\n\n"
                "❌ No active users found to broadcast to.\n"
                "Users must have at least one monitored URL to receive broadcasts.",
                parse_mode='Markdown'
            )
            return
        
        # Update status
        await confirm_msg.edit_text(
            f"📢 **Broadcasting Message**\n\n"
            f"**Message:** {broadcast_message}\n\n"
            f"🎯 **Target:** {len(user_ids)} users\n"
            f"⏳ **Status:** Sending...\n"
            f"📨 **Progress:** Starting delivery",
            parse_mode='Markdown'
        )
        
        # Send broadcast to all users
        success_count = 0
        failed_count = 0
        
        for i, user_id in enumerate(user_ids, 1):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 **Admin Broadcast**\n\n{broadcast_message}",
                    parse_mode='Markdown'
                )
                success_count += 1
                
                # Update progress every 5 users or at the end
                if i % 5 == 0 or i == len(user_ids):
                    await confirm_msg.edit_text(
                        f"📢 **Broadcasting Message**\n\n"
                        f"**Message:** {broadcast_message[:50]}{'...' if len(broadcast_message) > 50 else ''}\n\n"
                        f"🎯 **Target:** {len(user_ids)} users\n"
                        f"⏳ **Status:** Sending...\n"
                        f"📨 **Progress:** {i}/{len(user_ids)} ({(i/len(user_ids)*100):.0f}%)\n"
                        f"✅ **Delivered:** {success_count}\n"
                        f"❌ **Failed:** {failed_count}",
                        parse_mode='Markdown'
                    )
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to user {user_id}: {e}")
        
        # Final status report
        await confirm_msg.edit_text(
            f"📢 **Broadcast Complete!** ✅\n\n"
            f"**Message:** {broadcast_message[:100]}{'...' if len(broadcast_message) > 100 else ''}\n\n"
            f"📊 **Delivery Report:**\n"
            f"🎯 **Total Users:** {len(user_ids)}\n"
            f"✅ **Successfully Delivered:** {success_count}\n"
            f"❌ **Failed Deliveries:** {failed_count}\n"
            f"📈 **Success Rate:** {(success_count/len(user_ids)*100):.1f}%\n\n"
            f"⏰ **Completed:** {datetime.now().strftime('%H:%M:%S')}",
            parse_mode='Markdown'
        )
        
        logger.info(f"Broadcast sent by admin {update.effective_chat.id} to {success_count}/{len(user_ids)} users")
    
    async def broadcast_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcastimg command - Admin only"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            await update.message.reply_text(
                "🔒 **Access Denied**\n\n"
                "Only admins can use the image broadcast feature.",
                parse_mode='Markdown'
            )
            return
        
        # Set waiting for image state
        context.user_data['waiting_for_broadcast_image'] = True
        
        await update.message.reply_text(
            "🖼️ **Image Broadcast Setup**\n\n"
            "📸 **Step 1 Complete:** Command received\n"
            "📤 **Step 2:** Please send the image you want to broadcast\n"
            "📝 **Step 3:** Add a caption to your image (optional)\n\n"
            "✨ **Supported formats:** JPG, PNG, GIF\n"
            "📏 **Max size:** 10MB\n"
            "⚡ **Delivery:** Instant to all users\n\n"
            "🚫 **To cancel:** Send `/cancel`",
            parse_mode='Markdown'
        )
    
    async def handle_broadcast_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image for broadcasting"""
        if not self.config.is_primary_admin(update.effective_chat.id):
            return
        
        if not context.user_data.get('waiting_for_broadcast_image'):
            return
        
        if not update.message.photo:
            await update.message.reply_text(
                "❌ Please send an image file (photo).\n\n"
                "Use `/broadcastimg` to start over or `/cancel` to cancel.",
                parse_mode='Markdown'
            )
            return
        
        # Clear waiting state
        context.user_data['waiting_for_broadcast_image'] = False
        
        # Get image and caption
        photo = update.message.photo[-1]  # Get highest resolution
        caption = update.message.caption or ""
        
        # Show confirmation
        confirm_msg = await update.message.reply_text(
            f"🖼️ **Image Broadcast Preview**\n\n"
            f"📸 **Image:** Received ({photo.width}x{photo.height})\n"
            f"📝 **Caption:** {caption[:100]}{'...' if len(caption) > 100 else caption}\n\n"
            f"⚡ **Preparing broadcast...**\n"
            f"🎯 Getting user list...\n"
            f"📊 Calculating delivery...",
            parse_mode='Markdown'
        )
        
        # Get all users
        all_urls = await self.notion_data.get_all_urls()
        user_ids = set(all_urls.values()) if all_urls else set()
        
        if not user_ids:
            await confirm_msg.edit_text(
                "🖼️ **Image Broadcast Status**\n\n"
                "❌ No active users found to broadcast to.\n"
                "Users must have at least one monitored URL to receive broadcasts.",
                parse_mode='Markdown'
            )
            return
        
        # Update status
        await confirm_msg.edit_text(
            f"🖼️ **Broadcasting Image**\n\n"
            f"📸 **Image:** ({photo.width}x{photo.height})\n"
            f"📝 **Caption:** {caption[:50]}{'...' if len(caption) > 50 else caption}\n\n"
            f"🎯 **Target:** {len(user_ids)} users\n"
            f"⏳ **Status:** Sending...\n"
            f"📨 **Progress:** Starting delivery",
            parse_mode='Markdown'
        )
        
        # Send broadcast to all users
        success_count = 0
        failed_count = 0
        
        for i, user_id in enumerate(user_ids, 1):
            try:
                broadcast_caption = f"📢 **Admin Broadcast**\n\n{caption}" if caption else "📢 **Admin Broadcast**"
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo.file_id,
                    caption=broadcast_caption,
                    parse_mode='Markdown'
                )
                success_count += 1
                
                # Update progress every 3 users or at the end
                if i % 3 == 0 or i == len(user_ids):
                    await confirm_msg.edit_text(
                        f"🖼️ **Broadcasting Image**\n\n"
                        f"📸 **Image:** ({photo.width}x{photo.height})\n"
                        f"📝 **Caption:** {caption[:30]}{'...' if len(caption) > 30 else caption}\n\n"
                        f"🎯 **Target:** {len(user_ids)} users\n"
                        f"⏳ **Status:** Sending...\n"
                        f"📨 **Progress:** {i}/{len(user_ids)} ({(i/len(user_ids)*100):.0f}%)\n"
                        f"✅ **Delivered:** {success_count}\n"
                        f"❌ **Failed:** {failed_count}",
                        parse_mode='Markdown'
                    )
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send image broadcast to user {user_id}: {e}")
        
        # Final status report
        await confirm_msg.edit_text(
            f"🖼️ **Image Broadcast Complete!** ✅\n\n"
            f"📸 **Image:** ({photo.width}x{photo.height})\n"
            f"📝 **Caption:** {caption[:80]}{'...' if len(caption) > 80 else caption}\n\n"
            f"📊 **Delivery Report:**\n"
            f"🎯 **Total Users:** {len(user_ids)}\n"
            f"✅ **Successfully Delivered:** {success_count}\n"
            f"❌ **Failed Deliveries:** {failed_count}\n"
            f"📈 **Success Rate:** {(success_count/len(user_ids)*100):.1f}%\n\n"
            f"⏰ **Completed:** {datetime.now().strftime('%H:%M:%S')}",
            parse_mode='Markdown'
        )
        
        logger.info(f"Image broadcast sent by admin {update.effective_chat.id} to {success_count}/{len(user_ids)} users")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        if not self._is_user_allowed(update):
            return
        
        # Check if user is in broadcast image state
        if context.user_data.get('waiting_for_broadcast_image'):
            if update.message.text and update.message.text.lower() == '/cancel':
                context.user_data['waiting_for_broadcast_image'] = False
                await update.message.reply_text(
                    "❌ **Image Broadcast Cancelled**\n\n"
                    "The image broadcast has been cancelled. Use `/broadcastimg` to start over.",
                    parse_mode='Markdown'
                )
                return
            else:
                await update.message.reply_text(
                    "📸 **Waiting for Image**\n\n"
                    "Please send an image file to broadcast, or send `/cancel` to cancel.",
                    parse_mode='Markdown'
                )
                return
        
        # For regular messages, suggest using commands
        message = (
            "👋 **Hi there!**\n\n"
            "I'm your URL Monitor Bot! Use these commands:\n\n"
            "🚀 **Quick Start:**\n"
            "• `/start` - Main dashboard\n"
            "• `/seturl <url>` - Add URL to monitor\n"
            "• `/status` - View status\n"
            "• `/help` - Full help\n\n"
            "💡 **Tip:** Click the buttons in my messages for an interactive experience!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Dashboard", callback_data="main_menu"),
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard")
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data="main_stats"),
                InlineKeyboardButton("❓ Help", callback_data="help_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self._is_user_allowed(update):
            await query.edit_message_text("🔒 Sorry, this bot is currently not available.")
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
        elif callback_data == "broadcast_center":
            await self._handle_broadcast_center_callback(query)
        elif callback_data == "broadcast_text":
            await self._handle_broadcast_text_callback(query)
        elif callback_data == "broadcast_image":
            await self._handle_broadcast_image_callback(query)
        elif callback_data == "user_management":
            await self._handle_user_management_callback(query)
        elif callback_data == "system_analytics":
            await self._handle_system_analytics_callback(query)
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
            url_hash = callback_data.split(":")[1]
            await self._handle_test_url_callback(query, url_hash)
        elif callback_data.startswith("url_detail:"):
            url_hash = callback_data.split(":")[1]
            await self._handle_url_detail_callback(query, url_hash)
        elif callback_data.startswith("remove_url:"):
            url_hash = callback_data.split(":")[1]
            await self._handle_remove_url_callback(query, url_hash)
        elif callback_data.startswith("confirm_remove:"):
            url_hash = callback_data.split(":")[1]
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
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
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
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
        if not urls:
            await query.edit_message_text(
                "📊 **No Status Data Available**\n\n"
                "No URLs are currently being monitored.",
                parse_mode='Markdown'
            )
            return
        
        # Get statistics from Notion database
        stats = await self.notion_data.get_url_statistics(str(query.message.chat.id))
        
        message = f"📊 **Your URL Statistics**\n\n"
        message += f"**Total URLs:** {stats['total_urls']}\n"
        message += f"🟢 **Online:** {stats['online']}\n"
        message += f"🔴 **Offline:** {stats['offline']}\n"
        message += f"⏳ **Pending:** {stats['pending']}\n"
        message += f"⚡ **Avg Response:** {stats['average_response_time']}ms\n\n"
        
        # Show individual URL statuses
        for url, data in urls.items():
            status_icon = "🟢" if data['status'] == 'online' else "🔴" if data['status'] == 'offline' else "⏳"
            response_time_str = f" ({data['response_time']}ms)" if data['response_time'] else ""
            message += f"{status_icon} `{url}`{response_time_str}\n"
        
        # Add monitoring status
        monitor_status = await self.url_monitor.get_monitoring_status()
        status_icon = "🟢" if monitor_status["is_running"] else "🔴"
        message += f"\n**Monitoring Status:** {status_icon} {'Active' if monitor_status['is_running'] else 'Inactive'}\n"
        message += f"**Ping Interval:** {monitor_status['ping_interval']} seconds\n"
        message += f"**Data Storage:** Notion Database\n"
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
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
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
            # Perform the pings for this user only
            results = await self.url_monitor.ping_user_urls(str(query.message.chat.id))
            
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
        if not self._is_user_allowed(update):
            await update.message.reply_text("Sorry, this bot is currently not available.")
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
        """Handle URLs dashboard callback with enhanced UI"""
        try:
            # Show loading animation first
            await query.answer("📊 Loading enhanced dashboard...")
            
            # Refresh URL hash mapping
            await self._refresh_url_hash_map(str(query.message.chat.id))
            
            # Get user URLs from Notion
            urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
            
            # Generate enhanced dashboard
            message, reply_markup = self.advanced_ui.format_enhanced_url_list(urls, page=0, per_page=4)
            
            # Update message with enhanced dashboard
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in main URLs callback: {e}")
            await query.edit_message_text(
                "❌ **Error Loading Dashboard**\n\n"
                "Please try again later or contact support.",
                parse_mode='Markdown'
            )
    
    async def _handle_main_stats_callback(self, query):
        """Handle statistics dashboard callback"""
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
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
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
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
            results = await self.url_monitor.ping_user_urls(str(query.message.chat.id))
            
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
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
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
        """Handle advanced admin panel callback"""
        user_chat_id = query.message.chat.id
        if not self.config.is_primary_admin(user_chat_id):
            await query.edit_message_text(
                f"🔒 **Access Denied**\n\n"
                f"Only the primary admin can access the admin panel.\n\n"
                f"**Your Chat ID:** `{user_chat_id}`\n"
                f"**Required Admin ID:** `{self.config.primary_admin_chat_id}`\n\n"
                f"Contact the bot owner to add your Chat ID as admin.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
            return
        
        # Get system statistics
        all_urls = await self.notion_data.get_all_urls()
        total_users = len(set(all_urls.values())) if all_urls else 0
        total_urls = len(all_urls)
        admin_list = self.config.get_admin_list()
        
        message = "👑 **Advanced Admin Control Panel** 👑\n\n"
        message += f"🎯 **System Overview:**\n"
        message += f"• 👥 Active Users: {total_users}\n"
        message += f"• 🌐 Total URLs: {total_urls}\n"
        message += f"• 🛡️ Admins: {len(admin_list)}\n"
        message += f"• 📊 Database: Notion\n\n"
        
        message += f"🚀 **Admin Features Available:**\n"
        message += f"• 📢 Broadcast Messages & Images\n"
        message += f"• 👥 User Management System\n"
        message += f"• 📊 System Analytics & Reports\n"
        message += f"• 🔧 Database Management Tools\n"
        message += f"• 🛡️ Admin Access Control\n"
        message += f"• 📈 Performance Monitoring\n\n"
        
        message += f"⚡ **Quick Stats:**\n"
        # Get online/offline counts
        online_count = 0
        offline_count = 0
        if all_urls:
            for url in all_urls.keys():
                # Get status from first user who has this URL
                user_id = all_urls[url]
                user_urls = await self.notion_data.get_user_urls(user_id)
                if url in user_urls:
                    status = user_urls[url].get('status', '').lower()
                    if status == 'online':
                        online_count += 1
                    elif status == 'offline':
                        offline_count += 1
        
        message += f"• 🟢 Online URLs: {online_count}\n"
        message += f"• 🔴 Offline URLs: {offline_count}\n"
        message += f"• ⏱️ Last Update: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [
                InlineKeyboardButton("📢 Broadcast Center", callback_data="broadcast_center"),
                InlineKeyboardButton("👥 User Management", callback_data="user_management")
            ],
            [
                InlineKeyboardButton("📊 System Analytics", callback_data="system_analytics"),
                InlineKeyboardButton("🔧 Database Tools", callback_data="database_tools")
            ],
            [
                InlineKeyboardButton("🛡️ Admin Controls", callback_data="admin_controls"),
                InlineKeyboardButton("📈 Performance Monitor", callback_data="performance_monitor")
            ],
            [
                InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_panel"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_broadcast_center_callback(self, query):
        """Handle broadcast center callback"""
        if not self.config.is_primary_admin(query.message.chat.id):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        message = "📢 **Broadcast Control Center** 📢\n\n"
        message += "🎯 **Mass Communication Hub**\n\n"
        message += "✨ **Available Features:**\n"
        message += "• 📝 Broadcast Text Messages\n"
        message += "• 🖼️ Broadcast Images with Captions\n"
        message += "• 🎯 Target Specific Users or All\n"
        message += "• 📊 Delivery Analytics & Reports\n"
        message += "• ⚡ Instant or Scheduled Delivery\n\n"
        
        # Get user statistics
        all_urls = await self.notion_data.get_all_urls()
        total_users = len(set(all_urls.values())) if all_urls else 0
        
        message += f"👥 **Target Audience:**\n"
        message += f"• Active Users: {total_users}\n"
        message += f"• Potential Reach: {total_users} users\n\n"
        
        message += "🚀 **How to Broadcast:**\n"
        message += "1️⃣ Choose message type (text/image)\n"
        message += "2️⃣ Compose your message\n"
        message += "3️⃣ Review and confirm\n"
        message += "4️⃣ Send to all users instantly\n\n"
        
        message += "⚠️ **Important:** Use responsibly!"
        
        keyboard = [
            [
                InlineKeyboardButton("📝 Text Broadcast", callback_data="broadcast_text"),
                InlineKeyboardButton("🖼️ Image Broadcast", callback_data="broadcast_image")
            ],
            [
                InlineKeyboardButton("👥 User List", callback_data="broadcast_users"),
                InlineKeyboardButton("📊 Broadcast Stats", callback_data="broadcast_stats")
            ],
            [
                InlineKeyboardButton("📋 Message Templates", callback_data="message_templates"),
                InlineKeyboardButton("⚙️ Broadcast Settings", callback_data="broadcast_settings")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel"),
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
        """Handle enhanced URL pagination"""
        try:
            await query.answer(f"📄 Loading page {page + 1}...")
            
            # Get URLs from Notion
            urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
            
            # Generate enhanced dashboard with pagination
            message, reply_markup = self.advanced_ui.format_enhanced_url_list(urls, page, per_page=4)
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in URL pagination: {e}")
            await query.edit_message_text(
                "❌ **Error Loading Page**\n\n"
                "Please try refreshing the dashboard.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="main_urls")]
                ])
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
        try:
            # Refresh hash mapping first
            await self._refresh_url_hash_map(str(query.message.chat.id))
            
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
        except Exception as e:
            logger.error(f"Error in remove URL callback: {e}")
            await query.edit_message_text(
                "❌ **Error Processing Request**\n\n"
                "Please try refreshing the dashboard.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh URLs", callback_data="main_urls")]
                ])
            )
    
    async def _handle_url_detail_callback(self, query, url_hash):
        """Handle enhanced URL detail view callback"""
        try:
            await query.answer("📊 Loading URL analytics...")
            
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
            
            # Get URL details from Notion
            url_data = await self.notion_data.get_user_url(str(query.message.chat.id), url)
            
            if not url_data:
                await query.edit_message_text(
                    "❌ URL details not found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Refresh URLs", callback_data="main_urls")]
                    ])
                )
                return
            
            # Use enhanced detail view
            message, reply_markup = self.advanced_ui.create_url_detail_view(url, url_data)
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in URL detail callback: {e}")
            await query.edit_message_text(
                "❌ **Error Loading URL Details**\n\n"
                "Please try again later.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data=f"url_detail:{url_hash}")],
                    [InlineKeyboardButton("🌐 Dashboard", callback_data="main_urls")]
                ])
            )
    
    async def _handle_confirm_remove_callback(self, query, url_hash):
        """Handle confirmed URL removal"""
        try:
            # Refresh hash mapping to ensure we have latest data
            await self._refresh_url_hash_map(str(query.message.chat.id))
            
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
            
            # Show processing message with answer to prevent timeout
            await query.answer("🗑️ Removing URL...")
            await query.edit_message_text(
                f"🗑️ **Removing URL...**\n\n"
                f"**URL:** `{url}`\n\n"
                f"⏳ Stopping monitoring...\n"
                f"⏳ Removing from database...\n"
                f"⏳ Cleaning up resources...",
                parse_mode='Markdown'
            )
            
            # Remove URL from monitoring
            success = await self.url_monitor.remove_url(url, str(query.message.chat.id))
            
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
                    f"This URL will no longer receive keep-alive pings.\n\n"
                    f"🕐 **Removed at:** {datetime.now().strftime('%H:%M:%S')}",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                logger.info(f"Successfully removed URL {url} for user {query.message.chat.id}")
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
                logger.warning(f"Failed to remove URL {url} for user {query.message.chat.id}")
                
        except Exception as e:
            logger.error(f"Error in confirm remove callback: {e}")
            await query.edit_message_text(
                "❌ **Error Removing URL**\n\n"
                "An unexpected error occurred. Please try again.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="main_urls")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ])
            )
    
    async def _handle_view_alerts_callback(self, query):
        """Handle view alerts callback"""
        urls = await self.notion_data.get_user_urls(str(query.message.chat.id))
        
        message = f"🔔 **Alert System** 🔔\n\n"
        
        if not urls:
            message += "📭 **No URLs Monitored**\n\n"
            message += "Add URLs to receive downtime alerts!"
        else:
            offline_urls = [url for url, data in urls.items() if data.get('status') == 'Offline']
            
            if offline_urls:
                message += f"🚨 **Active Alerts** 🚨\n\n"
                for url in offline_urls[:5]:
                    message += f"🔴 `{url}`\n"
                if len(offline_urls) > 5:
                    message += f"... and {len(offline_urls) - 5} more\n"
            else:
                message += "✅ **All Systems Online** ✅\n\n"
                message += "No active alerts. All URLs are working!"
            
            message += f"\n📊 **Alert Summary:**\n"
            message += f"• Total URLs: {len(urls)}\n"
            message += f"• Active Alerts: {len(offline_urls)}\n"
            message += f"• Status: {'🟢 Good' if len(offline_urls) == 0 else '🔴 Issues Detected'}"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh Alerts", callback_data="view_alerts"),
                InlineKeyboardButton("⚡ Quick Ping", callback_data="quick_ping")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="main_stats"),
                InlineKeyboardButton("🌐 URLs", callback_data="main_urls")
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
    
    async def _handle_help_menu_callback(self, query):
        """Handle help menu callback"""
        help_msg = (
            "ℹ️ **Help & Support** ℹ️\n\n"
            "🚀 **Quick Start Guide:**\n"
            "1️⃣ Click '➕ Add URL' to start monitoring\n"
            "2️⃣ Enter your website URL\n"
            "3️⃣ Monitor real-time status\n"
            "4️⃣ Get instant downtime alerts\n\n"
            "🎛️ **Available Features:**\n"
            "• 🌐 URL Management Dashboard\n"
            "• 📊 Real-time Statistics\n"
            "• ⚡ Instant Ping Testing\n"
            "• 🔔 Downtime Alerts\n"
            "• 📈 Performance Analytics\n\n"
            "💡 **Pro Tips:**\n"
            "• Monitor every 60 seconds automatically\n"
            "• Get alerts immediately when sites go down\n"
            "• View response time trends\n"
            "• All data stored securely in Notion\n\n"
            "❓ **Need More Help?**\n"
            "Use the /help command for detailed instructions!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Get Started", callback_data="add_url_wizard"),
                InlineKeyboardButton("📊 View Dashboard", callback_data="main_menu")
            ],
            [
                InlineKeyboardButton("💬 Commands List", callback_data="commands_help"),
                InlineKeyboardButton("🔧 Settings", callback_data="main_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_msg, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_add_url_wizard_callback(self, query):
        """Handle add URL wizard callback"""
        message = (
            "➕ **Add URL Wizard** ➕\n\n"
            "🎯 **Ready to monitor a new website!**\n\n"
            "📋 **How to add a URL:**\n"
            "1️⃣ Use command: `/seturl <your-url>`\n"
            "2️⃣ Example: `/seturl https://myapp.com`\n"
            "3️⃣ Bot will start monitoring immediately\n\n"
            "✅ **Supported URLs:**\n"
            "• https://example.com\n"
            "• http://example.com\n"
            "• https://api.example.com/health\n"
            "• Any publicly accessible URL\n\n"
            "⚡ **What happens next:**\n"
            "• Instant connectivity test\n"
            "• Automatic monitoring every 60 seconds\n"
            "• Real-time alerts for downtime\n"
            "• Performance tracking\n\n"
            "💡 **Tip:** You can monitor multiple URLs!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📋 View Current URLs", callback_data="main_urls"),
                InlineKeyboardButton("📊 Statistics", callback_data="main_stats")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_broadcast_text_callback(self, query):
        """Handle text broadcast setup"""
        if not self.config.is_primary_admin(query.message.chat.id):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        message = "📝 **Text Broadcast Setup** 📝\n\n"
        message += "🎯 **Ready to send message to all users!**\n\n"
        message += "📋 **Instructions:**\n"
        message += "1️⃣ Type: `/broadcast <your message>`\n"
        message += "2️⃣ Example: `/broadcast 🚀 New features available!`\n"
        message += "3️⃣ Message will be sent to all active users\n\n"
        
        message += "✨ **Message Features:**\n"
        message += "• ✅ Markdown formatting supported\n"
        message += "• 📝 Unlimited text length\n"
        message += "• 🔗 Links and formatting allowed\n"
        message += "• ⚡ Instant delivery to all users\n\n"
        
        message += "💡 **Pro Tips:**\n"
        message += "• Use **bold** and *italic* text\n"
        message += "• Add emojis for better engagement\n"
        message += "• Keep messages clear and concise\n"
        message += "• Test formatting with a single message first\n\n"
        
        message += "📊 **Sample Commands:**\n"
        message += "`/broadcast Hello everyone! 👋`\n"
        message += "`/broadcast **Important Update:** New features added!`\n"
        message += "`/broadcast 🔧 Maintenance scheduled for tonight`"
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Message Templates", callback_data="message_templates"),
                InlineKeyboardButton("👥 Target Users", callback_data="broadcast_users")
            ],
            [
                InlineKeyboardButton("🧪 Test Message", callback_data="test_broadcast"),
                InlineKeyboardButton("📊 Delivery Stats", callback_data="broadcast_stats")
            ],
            [
                InlineKeyboardButton("🔙 Broadcast Center", callback_data="broadcast_center"),
                InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_broadcast_image_callback(self, query):
        """Handle image broadcast setup"""
        if not self.config.is_primary_admin(query.message.chat.id):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        message = "🖼️ **Image Broadcast Setup** 🖼️\n\n"
        message += "🎯 **Send images with captions to all users!**\n\n"
        message += "📋 **Instructions:**\n"
        message += "1️⃣ Use command: `/broadcastimg`\n"
        message += "2️⃣ Send the image as a reply to the command\n"
        message += "3️⃣ Add caption with the image\n"
        message += "4️⃣ Image will be sent to all users\n\n"
        
        message += "✨ **Image Features:**\n"
        message += "• 🖼️ JPG, PNG, GIF supported\n"
        message += "• 📝 Rich captions with Markdown\n"
        message += "• 🎯 Broadcast to all active users\n"
        message += "• ⚡ High-quality image delivery\n\n"
        
        message += "💡 **Pro Tips:**\n"
        message += "• Use high-quality images\n"
        message += "• Keep file sizes reasonable (<10MB)\n"
        message += "• Add engaging captions\n"
        message += "• Test with single user first\n\n"
        
        message += "📊 **Usage Examples:**\n"
        message += "1. Send `/broadcastimg`\n"
        message += "2. Reply with image + caption\n"
        message += "3. Confirm broadcast delivery\n"
        message += "4. Monitor delivery status"
        
        keyboard = [
            [
                InlineKeyboardButton("📸 Start Image Broadcast", callback_data="start_img_broadcast"),
                InlineKeyboardButton("🎨 Image Templates", callback_data="image_templates")
            ],
            [
                InlineKeyboardButton("👥 Target Users", callback_data="broadcast_users"),
                InlineKeyboardButton("📊 Image Stats", callback_data="image_broadcast_stats")
            ],
            [
                InlineKeyboardButton("🔙 Broadcast Center", callback_data="broadcast_center"),
                InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_user_management_callback(self, query):
        """Handle user management panel"""
        if not self.config.is_primary_admin(query.message.chat.id):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        # Get user statistics
        all_urls = await self.notion_data.get_all_urls()
        user_ids = set(all_urls.values()) if all_urls else set()
        total_users = len(user_ids)
        
        message = "👥 **User Management Panel** 👥\n\n"
        message += f"📊 **User Statistics:**\n"
        message += f"• Total Active Users: {total_users}\n"
        message += f"• Total URLs Monitored: {len(all_urls)}\n"
        message += f"• Average URLs per User: {len(all_urls) / max(total_users, 1):.1f}\n\n"
        
        message += "🎯 **Management Features:**\n"
        message += "• 👁️ View all user activity\n"
        message += "• 📊 User statistics and metrics\n"
        message += "• 🚫 Block/Unblock users (if needed)\n"
        message += "• 📈 User engagement analytics\n"
        message += "• 📋 Export user data\n\n"
        
        if total_users > 0:
            message += f"🏆 **Top Users (by URLs monitored):**\n"
            # Count URLs per user
            user_url_counts = {}
            for url, user_id in all_urls.items():
                user_url_counts[user_id] = user_url_counts.get(user_id, 0) + 1
            
            # Sort and show top users
            sorted_users = sorted(user_url_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (user_id, url_count) in enumerate(sorted_users[:5], 1):
                message += f"{i}. User `{user_id}`: {url_count} URLs\n"
        
        keyboard = [
            [
                InlineKeyboardButton("👁️ View All Users", callback_data="view_all_users"),
                InlineKeyboardButton("📊 User Analytics", callback_data="user_analytics")
            ],
            [
                InlineKeyboardButton("📈 Activity Report", callback_data="activity_report"),
                InlineKeyboardButton("📋 Export Data", callback_data="export_user_data")
            ],
            [
                InlineKeyboardButton("🔧 User Tools", callback_data="user_tools"),
                InlineKeyboardButton("⚙️ User Settings", callback_data="user_settings_admin")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _handle_system_analytics_callback(self, query):
        """Handle system analytics panel"""
        if not self.config.is_primary_admin(query.message.chat.id):
            await query.edit_message_text("🔒 Access denied. Admin only.")
            return
        
        # Get comprehensive system stats
        all_urls = await self.notion_data.get_all_urls()
        total_users = len(set(all_urls.values())) if all_urls else 0
        total_urls = len(all_urls)
        
        # Calculate status statistics
        online_count = 0
        offline_count = 0
        pending_count = 0
        total_response_time = 0
        response_count = 0
        
        for url in all_urls.keys():
            user_id = all_urls[url]
            user_urls = await self.notion_data.get_user_urls(user_id)
            if url in user_urls:
                status = user_urls[url].get('status', '').lower()
                if status == 'online':
                    online_count += 1
                elif status == 'offline':
                    offline_count += 1
                else:
                    pending_count += 1
                
                response_time = user_urls[url].get('response_time')
                if response_time and response_time > 0:
                    total_response_time += response_time
                    response_count += 1
        
        avg_response = total_response_time / max(response_count, 1)
        uptime_percentage = (online_count / max(total_urls, 1)) * 100
        
        message = "📊 **System Analytics Dashboard** 📊\n\n"
        message += f"🎯 **Overall Health: {('🟢 Excellent' if uptime_percentage >= 95 else '🟡 Good' if uptime_percentage >= 80 else '🔴 Needs Attention')}**\n\n"
        
        message += f"📈 **Key Metrics:**\n"
        message += f"• 🌐 Total URLs: {total_urls}\n"
        message += f"• 👥 Active Users: {total_users}\n"
        message += f"• 🟢 Online: {online_count} ({online_count/max(total_urls,1)*100:.1f}%)\n"
        message += f"• 🔴 Offline: {offline_count} ({offline_count/max(total_urls,1)*100:.1f}%)\n"
        message += f"• ⏳ Pending: {pending_count}\n"
        message += f"• ⚡ Avg Response: {avg_response:.3f}s\n\n"
        
        message += f"📊 **System Performance:**\n"
        message += f"• 📈 Overall Uptime: {uptime_percentage:.1f}%\n"
        message += f"• ⚡ Performance Grade: {'A+' if avg_response < 1 else 'A' if avg_response < 2 else 'B' if avg_response < 3 else 'C'}\n"
        message += f"• 🎯 Service Quality: {'Excellent' if uptime_percentage >= 99 else 'Good' if uptime_percentage >= 95 else 'Fair'}\n\n"
        
        message += f"🔧 **System Status:**\n"
        message += f"• 🔄 Monitoring: Active\n"
        message += f"• 💾 Database: Notion (Connected)\n"
        message += f"• ⏱️ Last Update: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"• 🌟 Bot Status: Running Smoothly"
        
        keyboard = [
            [
                InlineKeyboardButton("📈 Detailed Reports", callback_data="detailed_reports"),
                InlineKeyboardButton("📊 Performance Trends", callback_data="performance_trends")
            ],
            [
                InlineKeyboardButton("🔍 URL Analysis", callback_data="url_analysis"),
                InlineKeyboardButton("👥 User Activity", callback_data="user_activity_analytics")
            ],
            [
                InlineKeyboardButton("📋 Export Analytics", callback_data="export_analytics"),
                InlineKeyboardButton("⚙️ Analytics Settings", callback_data="analytics_settings")
            ],
            [
                InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel"),
                InlineKeyboardButton("🔄 Refresh", callback_data="system_analytics")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
