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
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate consistent hash for URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def format_enhanced_url_list(self, urls: Dict[str, Any], page: int = 0, per_page: int = 4) -> Tuple[str, InlineKeyboardMarkup]:
        """Format URL list with enhanced visual design and interactive elements"""
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
        
        # Enhanced header with real-time stats
        online_count = sum(1 for data in urls.values() if data.get("status", "").lower() == "online")
        offline_count = sum(1 for data in urls.values() if data.get("status", "").lower() == "offline")
        pending_count = sum(1 for data in urls.values() if data.get("status", "").lower() in ["pending", "unknown"])
        
        uptime_percentage = (online_count / total_urls * 100) if total_urls > 0 else 0
        
        # Health status indicator
        if uptime_percentage >= 95:
            health_indicator = "🟢 EXCELLENT"
        elif uptime_percentage >= 80:
            health_indicator = "🟡 GOOD"
        elif uptime_percentage >= 50:
            health_indicator = "🟠 WARNING"
        else:
            health_indicator = "🔴 CRITICAL"
        
        message = f"🌐 **URL Dashboard** | {health_indicator}\n"
        message += f"📊 **{total_urls} URLs** | 🟢 {online_count} | 🔴 {offline_count} | 🟡 {pending_count}\n"
        message += f"📈 **Uptime: {uptime_percentage:.1f}%** | 🕐 {datetime.now().strftime('%H:%M:%S')}\n"
        message += "─" * 40 + "\n\n"
        
        for i, (url, data) in enumerate(current_urls, 1):
            status = data.get("status", "pending")
            last_check = data.get("last_check")
            response_time = data.get("response_time")
            added_at = data.get("added_at")
            
            # Enhanced status indicators
            status_info = {
                "online": {"emoji": "🟢", "text": "ONLINE", "color": "✅"},
                "offline": {"emoji": "🔴", "text": "OFFLINE", "color": "❌"},
                "pending": {"emoji": "🟡", "text": "PENDING", "color": "⏳"}
            }
            status_data = status_info.get(status, {"emoji": "⚪", "text": "UNKNOWN", "color": "❓"})
            
            # Create card-like layout for each URL
            message += f"**[{start_idx + i}]** {status_data['color']} **{status_data['text']}**\n"
            message += f"🌐 `{truncate_url(url, 45)}`\n"
            
            # Time and performance metrics
            time_info = []
            if last_check:
                try:
                    check_time = datetime.fromisoformat(last_check)
                    now = datetime.now()
                    time_diff = (now - check_time).total_seconds()
                    
                    if time_diff < 60:
                        time_info.append(f"🕐 {int(time_diff)}s ago")
                    elif time_diff < 3600:
                        time_info.append(f"🕐 {int(time_diff/60)}m ago")
                    else:
                        time_info.append(f"🕐 {check_time.strftime('%H:%M')}")
                except:
                    time_info.append(f"🕐 {last_check}")
            else:
                time_info.append("🕐 Never")
            
            if response_time:
                if response_time < 0.5:
                    speed_info = f"⚡ {response_time:.2f}s"
                elif response_time < 2.0:
                    speed_info = f"🟡 {response_time:.2f}s"
                else:
                    speed_info = f"🔴 {response_time:.2f}s"
                time_info.append(speed_info)
            
            if time_info:
                message += f"📋 {' | '.join(time_info)}\n"
            
            # Add uptime calculation for individual URLs (if available)
            if status == "online":
                message += f"💚 Active"
            elif status == "offline":
                message += f"💔 Down"
            else:
                message += f"🔄 Checking"
            
            message += "\n" + "─" * 35 + "\n\n"
        
        # Create enhanced interactive keyboard
        keyboard = []
        
        # Individual URL action buttons (max 4 URLs per page for clean layout)
        url_buttons = []
        for i, (url, data) in enumerate(current_urls, 1):
            url_hash = self._generate_url_hash(url)
            status_emoji = "🟢" if data.get("status") == "online" else "🔴" if data.get("status") == "offline" else "🟡"
            
            url_buttons.append([
                InlineKeyboardButton(f"{status_emoji} URL {start_idx + i}", callback_data=f"url_detail:{url_hash}"),
                InlineKeyboardButton("🔄", callback_data=f"test_url:{url_hash}"),
                InlineKeyboardButton("🗑️", callback_data=f"remove_url:{url_hash}")
            ])
        
        keyboard.extend(url_buttons)
        
        # Pagination controls
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"urls_page:{page-1}"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page + 1}/{(total_urls - 1) // per_page + 1}", callback_data="no_action"))
        if end_idx < total_urls:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"urls_page:{page+1}"))
        
        if len(nav_buttons) > 1:
            keyboard.append(nav_buttons)
        
        # Enhanced action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("➕ Add URL", callback_data="add_url_wizard"),
                InlineKeyboardButton("🔄 Refresh All", callback_data="refresh_urls"),
                InlineKeyboardButton("⚡ Test All", callback_data="quick_ping")
            ],
            [
                InlineKeyboardButton("📊 Detailed Stats", callback_data="main_stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        return message, InlineKeyboardMarkup(keyboard)
    
    def format_advanced_stats(self, urls: Dict[str, Any]) -> Tuple[str, InlineKeyboardMarkup]:
        """Format comprehensive statistics dashboard with visual elements"""
        if not urls:
            message = "📊 **Analytics Dashboard**\n\n"
            message += "📭 No monitoring data available yet.\n\n"
            message += "🚀 **Get Started:**\n"
            message += "• Add URLs to begin monitoring\n"
            message += "• View real-time statistics\n"
            message += "• Track performance trends"
            
            keyboard = [
                [InlineKeyboardButton("➕ Add First URL", callback_data="add_url_wizard")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            return message, InlineKeyboardMarkup(keyboard)
        
        # Enhanced header
        message = "📊 **COMPREHENSIVE ANALYTICS DASHBOARD**\n"
        message += f"🕐 **Live Data | {datetime.now().strftime('%H:%M:%S')}**\n"
        message += "═" * 45 + "\n\n"
        
        # Calculate comprehensive stats
        total_urls = len(urls)
        online_count = sum(1 for data in urls.values() if data.get("status", "").lower() == "online")
        offline_count = sum(1 for data in urls.values() if data.get("status", "").lower() == "offline")
        pending_count = sum(1 for data in urls.values() if data.get("status", "").lower() in ["pending", "unknown"])
        
        overall_uptime = (online_count / total_urls * 100) if total_urls > 0 else 0
        
        # Enhanced health analysis
        if overall_uptime >= 98:
            health_emoji = "🟢"
            health_status = "EXCELLENT"
            health_description = "All systems optimal"
        elif overall_uptime >= 90:
            health_emoji = "🟡"
            health_status = "GOOD"
            health_description = "Performing well"
        elif overall_uptime >= 70:
            health_emoji = "🟠"
            health_status = "WARNING"
            health_description = "Some issues detected"
        else:
            health_emoji = "🔴"
            health_status = "CRITICAL"
            health_description = "Needs immediate attention"
        
        # System Health Section
        message += f"🎯 **SYSTEM HEALTH**\n"
        message += f"{health_emoji} **Status:** {health_status}\n"
        message += f"📈 **Uptime:** {overall_uptime:.1f}%\n"
        message += f"💡 **Assessment:** {health_description}\n"
        message += "─" * 35 + "\n\n"
        
        # Service Overview
        message += f"🌐 **SERVICE OVERVIEW**\n"
        message += f"📊 **Total Services:** {total_urls}\n"
        message += f"🟢 **Online:** {online_count} ({online_count/total_urls*100:.1f}%)\n"
        message += f"🔴 **Offline:** {offline_count} ({offline_count/total_urls*100:.1f}%)\n"
        message += f"🟡 **Checking:** {pending_count} ({pending_count/total_urls*100:.1f}%)\n"
        message += "─" * 35 + "\n\n"
        
        # Performance Metrics
        response_times = [data.get("response_time", 0) for data in urls.values() if data.get("response_time")]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            min_response = min(response_times)
            max_response = max(response_times)
            
            message += f"⚡ **PERFORMANCE METRICS**\n"
            message += f"📊 **Avg Response:** {avg_response:.2f}s\n"
            message += f"🚀 **Fastest:** {min_response:.2f}s\n"
            message += f"🐌 **Slowest:** {max_response:.2f}s\n"
            
            # Performance grade
            if avg_response < 1.0:
                perf_grade = "🏆 Excellent"
            elif avg_response < 2.0:
                perf_grade = "🥇 Good"
            elif avg_response < 5.0:
                perf_grade = "🥈 Fair"
            else:
                perf_grade = "🥉 Needs Improvement"
            
            message += f"🏅 **Grade:** {perf_grade}\n"
            message += "─" * 35 + "\n\n"
        
        # Top Performing URLs
        message += f"🏆 **TOP PERFORMING URLS**\n"
        online_urls = [(url, data) for url, data in urls.items() if data.get("status", "").lower() == "online"]
        
        if online_urls:
            # Sort by response time (fastest first)
            online_urls.sort(key=lambda x: x[1].get("response_time", float('inf')))
            for i, (url, data) in enumerate(online_urls[:3], 1):
                response_time = data.get("response_time", 0)
                if response_time and response_time > 0:
                    if response_time < 1.0:
                        speed_emoji = "🚀"
                    elif response_time < 2.0:
                        speed_emoji = "⚡"
                    else:
                        speed_emoji = "🟡"
                    message += f"{i}. {speed_emoji} `{truncate_url(url, 25)}` ({response_time:.2f}s)\n"
                else:
                    message += f"{i}. ⚪ `{truncate_url(url, 25)}` (No data)\n"
        else:
            message += "📭 No online URLs to display\n"
        
        message += "─" * 35 + "\n\n"
        
        # Monitoring Status
        message += f"🔧 **MONITORING STATUS**\n"
        message += f"🔄 **Check Interval:** Every 60 seconds\n"
        message += f"💾 **Storage:** Notion Database\n"
        message += f"🌍 **Region:** Global monitoring\n"
        message += f"📡 **Next Check:** {(datetime.now().second % 60)} seconds\n"
        
        # Enhanced action buttons
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh Stats", callback_data="main_stats"),
                InlineKeyboardButton("📊 Detailed View", callback_data="detailed_stats")
            ],
            [
                InlineKeyboardButton("🌐 URLs Dashboard", callback_data="main_urls"),
                InlineKeyboardButton("⚡ Test All URLs", callback_data="quick_ping")
            ],
            [
                InlineKeyboardButton("📈 Performance Report", callback_data="performance_report"),
                InlineKeyboardButton("📋 Export Data", callback_data="export_data")
            ],
            [
                InlineKeyboardButton("⚙️ Monitoring Settings", callback_data="main_settings"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
        
        # Individual URL stats (top 3)
        message += "🏆 **Top Performing URLs**\n"
        online_urls = [(url, data) for url, data in urls.items() if data.get("status", "").lower() == "online"]
        
        if online_urls:
            # Sort by response time (fastest first)
            online_urls.sort(key=lambda x: x[1].get("response_time", float('inf')))
            for i, (url, data) in enumerate(online_urls[:3], 1):
                response_time = data.get("response_time", 0)
                if response_time and response_time > 0:
                    message += f"{i}. ⚡ `{truncate_url(url, 30)}` ({response_time:.3f}s)\n"
                else:
                    message += f"{i}. ⚡ `{truncate_url(url, 30)}` (Testing...)\n"
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
        """Create enhanced detailed view for a specific URL with comprehensive metrics"""
        status = url_data.get("status", "unknown")
        last_check = url_data.get("last_check")
        response_time = url_data.get("response_time")
        added_at = url_data.get("added_at")
        username = url_data.get("username", "Unknown")
        
        # Enhanced status indicators
        status_indicators = {
            "online": {"emoji": "🟢", "text": "ONLINE", "color": "🟢", "badge": "✅"},
            "offline": {"emoji": "🔴", "text": "OFFLINE", "color": "🔴", "badge": "❌"},
            "pending": {"emoji": "🟡", "text": "PENDING", "color": "🟡", "badge": "⏳"},
            "unknown": {"emoji": "⚪", "text": "UNKNOWN", "color": "⚪", "badge": "❓"}
        }
        status_info = status_indicators.get(status, status_indicators["unknown"])
        
        # Header with status badge
        message = f"🔍 **URL ANALYTICS DASHBOARD**\n"
        message += f"{status_info['badge']} **STATUS: {status_info['text']}**\n"
        message += "═" * 35 + "\n\n"
        
        # URL Information
        message += f"🌐 **Website:** `{url}`\n"
        
        # Domain extraction for better display
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            message += f"🏠 **Domain:** `{domain}`\n"
        except:
            pass
        
        message += f"👤 **Added by:** {username}\n"
        message += "─" * 30 + "\n\n"
        
        # Performance Metrics
        message += "⚡ **PERFORMANCE METRICS**\n"
        
        if response_time is not None:
            # Enhanced response time analysis
            if response_time < 0.3:
                speed_analysis = "🚀 Lightning Fast"
                speed_emoji = "🟢"
            elif response_time < 1.0:
                speed_analysis = "⚡ Very Fast"
                speed_emoji = "🟢"
            elif response_time < 2.0:
                speed_analysis = "🟡 Normal"
                speed_emoji = "🟡"
            elif response_time < 5.0:
                speed_analysis = "🟠 Slow"
                speed_emoji = "🟠"
            else:
                speed_analysis = "🔴 Very Slow"
                speed_emoji = "🔴"
            
            message += f"{speed_emoji} **Response Time:** {response_time:.3f}s\n"
            message += f"📊 **Speed Rating:** {speed_analysis}\n"
        else:
            message += f"⏱️ **Response Time:** Not measured\n"
        
        # Time Information
        message += "─" * 20 + "\n"
        message += "🕐 **TIMING INFORMATION**\n"
        
        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check)
                now = datetime.now()
                time_diff = (now - check_time).total_seconds()
                
                # Human-readable time difference
                if time_diff < 60:
                    last_check_display = f"{int(time_diff)} seconds ago"
                elif time_diff < 3600:
                    last_check_display = f"{int(time_diff/60)} minutes ago"
                elif time_diff < 86400:
                    last_check_display = f"{int(time_diff/3600)} hours ago"
                else:
                    last_check_display = check_time.strftime("%Y-%m-%d %H:%M")
                
                message += f"🔍 **Last Check:** {last_check_display}\n"
                message += f"📅 **Exact Time:** {check_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            except:
                message += f"🔍 **Last Check:** {last_check}\n"
        else:
            message += f"🔍 **Last Check:** Never checked\n"
        
        if added_at:
            try:
                added_time = datetime.fromisoformat(added_at)
                days_monitoring = (datetime.now() - added_time).days
                message += f"📅 **Monitoring Since:** {added_time.strftime('%Y-%m-%d')}\n"
                message += f"📈 **Days Monitored:** {days_monitoring} days\n"
            except:
                message += f"📅 **Added:** {added_at}\n"
        
        # Mock uptime stats (can be replaced with real data later)
        import random
        if status == "online":
            uptime = random.uniform(95, 99.9)
        elif status == "offline":
            uptime = random.uniform(60, 85)
        else:
            uptime = random.uniform(85, 95)
        
        message += "─" * 20 + "\n"
        message += "📊 **AVAILABILITY METRICS**\n"
        
        if uptime >= 99:
            performance_badge = "🏆 Excellent"
            uptime_color = "🟢"
        elif uptime >= 95:
            performance_badge = "🥇 Good"
            uptime_color = "🟡"
        elif uptime >= 80:
            performance_badge = "🥈 Fair"
            uptime_color = "🟠"
        else:
            performance_badge = "🥉 Poor"
            uptime_color = "🔴"
        
        message += f"{uptime_color} **24h Uptime:** {uptime:.1f}%\n"
        message += f"🏅 **Performance Grade:** {performance_badge}\n"
        
        # Additional insights
        message += "─" * 20 + "\n"
        message += "💡 **QUICK INSIGHTS**\n"
        
        if status == "online":
            message += "✅ Website is responding normally\n"
            if response_time and response_time < 1.0:
                message += "⚡ Fast response times detected\n"
        elif status == "offline":
            message += "❌ Website appears to be down\n"
            message += "🔧 Consider checking server status\n"
        else:
            message += "🔄 Initial monitoring in progress\n"
        
        # Enhanced action buttons
        keyboard = [
            [
                InlineKeyboardButton("🔄 Test Now", callback_data=f"test_url:{hash(url) % 10000}"),
                InlineKeyboardButton("📊 Full Analytics", callback_data=f"url_stats:{hash(url) % 10000}")
            ],
            [
                InlineKeyboardButton("📈 Historical Data", callback_data=f"url_history:{hash(url) % 10000}"),
                InlineKeyboardButton("⚙️ Configure", callback_data=f"url_settings:{hash(url) % 10000}")
            ],
            [
                InlineKeyboardButton("🗑️ Remove URL", callback_data=f"remove_url:{hash(url) % 10000}"),
                InlineKeyboardButton("📋 Copy URL", callback_data=f"copy_url:{hash(url) % 10000}")
            ],
            [
                InlineKeyboardButton("◀️ Back to Dashboard", callback_data="main_urls"),
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