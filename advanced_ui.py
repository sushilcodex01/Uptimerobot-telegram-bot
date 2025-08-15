"""
Advanced UI components for Telegram URL Monitor Bot
Provides enhanced interactive elements, animations, and modern interface features
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import format_uptime_message, get_status_emoji, truncate_url

logger = logging.getLogger(__name__)

class AdvancedUI:
    def __init__(self, url_monitor, config):
        self.url_monitor = url_monitor
        self.config = config
        self.loading_frames = ["⏳", "⌛", "⏳", "⌛"]
        self.progress_frames = ["▱▱▱▱▱", "▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
        
    async def create_animated_loading(self, message, duration: int = 3):
        """Create animated loading effect"""
        original_text = message.text
        
        for i in range(duration * 2):  # 2 frames per second
            frame = self.loading_frames[i % len(self.loading_frames)]
            animated_text = f"{frame} Processing...\n\n{original_text}"
            
            try:
                await message.edit_text(animated_text, parse_mode='Markdown')
                await asyncio.sleep(0.5)
            except Exception:
                break  # Stop if message can't be edited
    
    def create_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create enhanced main menu with modern design"""
        keyboard = [
            [
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                InlineKeyboardButton("🗑️ Remove URL", callback_data="remove_url_menu")
            ],
            [
                InlineKeyboardButton("🌐 View URLs", callback_data="main_urls"),
                InlineKeyboardButton("📊 Stats", callback_data="main_stats")
            ],
            [
                InlineKeyboardButton("⚡ Quick Ping", callback_data="quick_ping"),
                InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")
            ],
            [
                InlineKeyboardButton("🔔 Alerts", callback_data="view_alerts"),
                InlineKeyboardButton("📈 Analytics", callback_data="analytics")
            ],
            [
                InlineKeyboardButton("👥 Admin Panel", callback_data="admin_panel"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help_menu")
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_url_management_keyboard(self, urls: Dict[str, Any]) -> InlineKeyboardMarkup:
        """Create enhanced URL management interface"""
        keyboard = []
        
        # Add URL cards (max 5 for clean display)
        displayed_urls = list(urls.items())[:5]
        for url, data in displayed_urls:
            status = data.get("status", "pending")
            emoji = get_status_emoji(status)
            short_url = truncate_url(url, 25)
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{emoji} {short_url}",
                    callback_data=f"url_detail:{hash(url) % 10000}"
                ),
                InlineKeyboardButton("🗑️", callback_data=f"remove_url:{hash(url) % 10000}")
            ])
        
        # Action buttons
        keyboard.append([
            InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
            InlineKeyboardButton("🔄 Refresh All", callback_data="refresh_urls")
        ])
        
        if len(urls) > 5:
            keyboard.append([
                InlineKeyboardButton("📋 View All", callback_data="view_all_urls")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_remove_url_keyboard(self, urls: Dict[str, Any]) -> InlineKeyboardMarkup:
        """Create dedicated remove URL interface"""
        keyboard = []
        
        if not urls:
            keyboard.append([
                InlineKeyboardButton("📭 No URLs to Remove", callback_data="no_action")
            ])
        else:
            # Add remove buttons for each URL
            for url, data in list(urls.items())[:8]:  # Show max 8 URLs
                status = data.get("status", "pending")
                emoji = get_status_emoji(status)
                short_url = truncate_url(url, 30)
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"🗑️ {emoji} {short_url}",
                        callback_data=f"remove_url:{hash(url) % 10000}"
                    )
                ])
            
            if len(urls) > 8:
                keyboard.append([
                    InlineKeyboardButton("📋 View All URLs", callback_data="main_urls")
                ])
        
        # Navigation buttons
        keyboard.extend([
            [
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                InlineKeyboardButton("🌐 View URLs", callback_data="main_urls")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_stats_dashboard_keyboard(self) -> InlineKeyboardMarkup:
        """Create advanced statistics dashboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 24h Stats", callback_data="stats_24h"),
                InlineKeyboardButton("📈 7d Trends", callback_data="stats_7d")
            ],
            [
                InlineKeyboardButton("⚡ Response Times", callback_data="response_times"),
                InlineKeyboardButton("📉 Incidents", callback_data="view_incidents")
            ],
            [
                InlineKeyboardButton("🎯 Top Performers", callback_data="top_urls"),
                InlineKeyboardButton("⚠️ Problem URLs", callback_data="problem_urls")
            ],
            [
                InlineKeyboardButton("📱 Export Data", callback_data="export_data"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_quick_actions_keyboard(self) -> InlineKeyboardMarkup:
        """Create quick action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("🚀 Ping All Now", callback_data="ping_all_instant"),
                InlineKeyboardButton("🔥 Emergency Check", callback_data="emergency_check")
            ],
            [
                InlineKeyboardButton("📱 Mobile View", callback_data="mobile_view"),
                InlineKeyboardButton("💻 Desktop View", callback_data="desktop_view")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_settings_keyboard(self) -> InlineKeyboardMarkup:
        """Create advanced settings interface"""
        keyboard = [
            [
                InlineKeyboardButton("⏰ Ping Interval", callback_data="set_interval"),
                InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")
            ],
            [
                InlineKeyboardButton("📊 Report Format", callback_data="report_format"),
                InlineKeyboardButton("🎨 UI Theme", callback_data="ui_theme")
            ],
            [
                InlineKeyboardButton("🔒 Security", callback_data="security_settings"),
                InlineKeyboardButton("💾 Data Management", callback_data="data_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def create_progress_animation(self, message, total_steps: int, current_step: int):
        """Create progress bar animation"""
        progress_index = min(int((current_step / total_steps) * len(self.progress_frames)), len(self.progress_frames) - 1)
        progress_bar = self.progress_frames[progress_index]
        percentage = int((current_step / total_steps) * 100)
        
        animated_text = f"🔄 **Processing URLs**\n\n"
        animated_text += f"Progress: {progress_bar} {percentage}%\n"
        animated_text += f"Step {current_step}/{total_steps}\n\n"
        animated_text += "Please wait..."
        
        try:
            await message.edit_text(animated_text, parse_mode='Markdown')
        except Exception:
            pass  # Ignore edit errors
    
    def format_enhanced_url_list(self, urls: Dict[str, Any], page: int = 0, per_page: int = 5) -> Tuple[str, InlineKeyboardMarkup]:
        """Format URL list with enhanced visual design"""
        if not urls:
            message = "📭 **No URLs Being Monitored**\n\n"
            message += "🚀 Ready to add your first URL?\n"
            message += "Click **Add URL** to get started!"
            
            keyboard = [[InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard")]]
            return message, InlineKeyboardMarkup(keyboard)
        
        # Pagination
        total_urls = len(urls)
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, total_urls)
        
        url_items = list(urls.items())
        current_urls = url_items[start_idx:end_idx]
        
        message = f"🌐 **URL Dashboard** ({total_urls} total)\n\n"
        
        for i, (url, data) in enumerate(current_urls, 1):
            status = data.get("status", "pending")
            last_check = data.get("last_check")
            response_time = data.get("response_time")
            
            # Status with enhanced emojis
            status_emojis = {
                "online": "🟢",
                "offline": "🔴",
                "pending": "🟡"
            }
            emoji = status_emojis.get(status, "⚪")
            
            message += f"**{start_idx + i}.** {emoji} **{status.upper()}**\n"
            message += f"   🌐 `{truncate_url(url, 50)}`\n"
            
            if last_check:
                try:
                    check_time = datetime.fromisoformat(last_check).strftime("%H:%M:%S")
                    message += f"   🕐 {check_time}"
                except:
                    message += f"   🕐 {last_check}"
            else:
                message += "   🕐 Never checked"
            
            if response_time:
                if response_time < 1.0:
                    speed_emoji = "⚡"
                elif response_time < 3.0:
                    speed_emoji = "🟡"
                else:
                    speed_emoji = "🔴"
                message += f" | {speed_emoji} {response_time:.3f}s"
            
            message += "\n\n"
        
        # Create pagination keyboard
        keyboard = []
        
        # Pagination controls
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"urls_page:{page-1}"))
        if end_idx < total_urls:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"urls_page:{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_urls")
            ],
            [
                InlineKeyboardButton("📊 View Stats", callback_data="main_stats"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        message += f"📄 Page {page + 1} of {(total_urls - 1) // per_page + 1}"
        
        return message, InlineKeyboardMarkup(keyboard)
    
    def format_advanced_stats(self, urls: Dict[str, Any]) -> Tuple[str, InlineKeyboardMarkup]:
        """Format advanced statistics with visual elements"""
        if not urls:
            message = "📊 **Statistics Dashboard**\n\n"
            message += "📭 No data available yet.\n"
            message += "Add some URLs to see statistics!"
            
            keyboard = [[InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard")]]
            return message, InlineKeyboardMarkup(keyboard)
        
        message = "📊 **Advanced Statistics Dashboard**\n\n"
        
        # Overall stats
        total_urls = len(urls)
        online_count = sum(1 for data in urls.values() if data.get("status") == "online")
        offline_count = sum(1 for data in urls.values() if data.get("status") == "offline")
        pending_count = sum(1 for data in urls.values() if data.get("status") == "pending")
        
        overall_uptime = (online_count / total_urls * 100) if total_urls > 0 else 0
        
        # Visual health indicator
        if overall_uptime >= 95:
            health_emoji = "💚"
            health_status = "EXCELLENT"
        elif overall_uptime >= 80:
            health_emoji = "💛"
            health_status = "GOOD"
        elif overall_uptime >= 50:
            health_emoji = "🧡"
            health_status = "WARNING"
        else:
            health_emoji = "❤️"
            health_status = "CRITICAL"
        
        message += f"🎯 **Overall Health: {health_emoji} {health_status}**\n"
        message += f"📈 **Uptime: {overall_uptime:.1f}%**\n\n"
        
        message += f"📊 **Quick Overview**\n"
        message += f"🟢 Online: {online_count}\n"
        message += f"🔴 Offline: {offline_count}\n"
        message += f"🟡 Pending: {pending_count}\n"
        message += f"📋 Total: {total_urls}\n\n"
        
        # Individual URL stats (top 3)
        message += "🏆 **Top Performing URLs**\n"
        online_urls = [(url, data) for url, data in urls.items() if data.get("status") == "online"]
        
        if online_urls:
            for i, (url, data) in enumerate(online_urls[:3], 1):
                response_time = data.get("response_time", 0)
                message += f"{i}. ⚡ `{truncate_url(url, 30)}` ({response_time:.3f}s)\n"
        else:
            message += "No online URLs currently\n"
        
        message += f"\n🕐 **Last Updated:** {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_stats"),
                InlineKeyboardButton("📈 Trends", callback_data="stats_trends")
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="main_stats"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
    
    def create_url_detail_view(self, url: str, url_data: Dict[str, Any]) -> Tuple[str, InlineKeyboardMarkup]:
        """Create detailed view for a specific URL"""
        status = url_data.get("status", "unknown")
        last_check = url_data.get("last_check")
        response_time = url_data.get("response_time")
        added_at = url_data.get("added_at")
        
        emoji = get_status_emoji(status)
        
        message = f"🔍 **URL Details**\n\n"
        message += f"{emoji} **Status:** {status.upper()}\n"
        message += f"🌐 **URL:** `{url}`\n\n"
        
        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check).strftime("%Y-%m-%d %H:%M:%S")
                message += f"🕐 **Last Check:** {check_time}\n"
            except:
                message += f"🕐 **Last Check:** {last_check}\n"
        
        if response_time is not None:
            if response_time < 1.0:
                speed_text = "⚡ Fast"
            elif response_time < 3.0:
                speed_text = "🟡 Normal"
            else:
                speed_text = "🔴 Slow"
            message += f"⏱️ **Response Time:** {response_time:.3f}s ({speed_text})\n"
        
        if added_at:
            try:
                added_time = datetime.fromisoformat(added_at).strftime("%Y-%m-%d")
                message += f"📅 **Added:** {added_time}\n"
            except:
                message += f"📅 **Added:** {added_at}\n"
        
        # Get uptime stats for this URL
        stats = self.url_monitor.get_uptime_stats(url, 24)
        uptime = stats.get("uptime_percentage", 0)
        
        message += f"\n📊 **24h Uptime:** {uptime}%\n"
        
        if uptime >= 99:
            performance_text = "🟢 Excellent"
        elif uptime >= 95:
            performance_text = "🟡 Good"
        elif uptime >= 80:
            performance_text = "🟠 Fair"
        else:
            performance_text = "🔴 Poor"
        
        message += f"📈 **Performance:** {performance_text}"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Test Now", callback_data=f"test_url:{hash(url) % 10000}"),
                InlineKeyboardButton("📊 Full Stats", callback_data=f"url_stats:{hash(url) % 10000}")
            ],
            [
                InlineKeyboardButton("🗑️ Remove", callback_data=f"remove_url:{hash(url) % 10000}"),
                InlineKeyboardButton("⚙️ Settings", callback_data=f"url_settings:{hash(url) % 10000}")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
    
    async def show_typing_animation(self, chat_id, bot, duration: int = 2):
        """Show typing indicator for better UX"""
        try:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(duration)
        except Exception:
            pass  # Ignore errors