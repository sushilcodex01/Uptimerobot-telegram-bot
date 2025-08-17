"""
Utility functions for the Telegram URL Monitor Bot
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    try:
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse the URL
        result = urlparse(url)
        
        # Check if it has both scheme and netloc
        return all([result.scheme, result.netloc])
    
    except Exception as e:
        logger.debug(f"URL validation error for '{url}': {e}")
        return False

def format_url_list(urls: Dict[str, Dict[str, Any]]) -> str:
    """Format the list of URLs for display"""
    if not urls:
        return "📭 No URLs are currently being monitored."
    
    message = f"📋 **Monitored URLs ({len(urls)})**\n\n"
    
    for url, data in urls.items():
        # Get status info
        status = data.get("status", "pending")
        last_check = data.get("last_check")
        response_time = data.get("response_time")
        
        # Status icon
        if status == "online":
            status_icon = "🟢"
            status_text = "Online"
        elif status == "offline":
            status_icon = "🔴"
            status_text = "Offline"
        else:
            status_icon = "⏳"
            status_text = "Pending"
        
        message += f"{status_icon} **{status_text}**\n"
        message += f"   `{url}`\n"
        
        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check)
                time_str = check_time.strftime("%H:%M:%S")
                message += f"   Last check: {time_str}"
            except:
                message += f"   Last check: {last_check}"
        else:
            message += "   Last check: Never"
        
        if response_time is not None:
            message += f" | {response_time:.3f}s"
        
        message += "\n\n"
    
    return message

def format_uptime_message(url: str, stats: Dict[str, Any]) -> str:
    """Format uptime statistics for a URL"""
    uptime = stats.get("uptime_percentage", 0)
    total_pings = stats.get("total_pings", 0)
    successful_pings = stats.get("successful_pings", 0)
    failed_pings = stats.get("failed_pings", 0)
    avg_response_time = stats.get("avg_response_time")
    
    # Determine status icon based on uptime
    if uptime >= 99:
        status_icon = "🟢"
    elif uptime >= 95:
        status_icon = "🟡"
    else:
        status_icon = "🔴"
    
    message = f"{status_icon} **{uptime}% Uptime**\n"
    message += f"   `{url}`\n"
    
    if total_pings > 0:
        message += f"   Checks: {successful_pings}✅ / {failed_pings}❌ (Total: {total_pings})\n"
        
        if avg_response_time is not None:
            message += f"   Avg Response: {avg_response_time:.3f}s\n"
    else:
        message += "   No ping data available\n"
    
    return message

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def truncate_url(url: str, max_length: int = 50) -> str:
    """Truncate URL for display purposes"""
    if len(url) <= max_length:
        return url
    
    # Try to keep the domain visible
    parsed = urlparse(url)
    domain = parsed.netloc
    
    if len(domain) < max_length - 3:
        return f"{domain}...{url[-(max_length - len(domain) - 3):]}"
    else:
        return url[:max_length - 3] + "..."

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_emojis = {
        "online": "🟢",
        "offline": "🔴",
        "pending": "⏳",
        "unknown": "⚪"
    }
    return status_emojis.get(status.lower(), "⚪")

def parse_command_args(text: str, command: str) -> List[str]:
    """Parse command arguments from message text"""
    # Remove the command from the beginning
    if text.startswith(f"/{command}"):
        args_text = text[len(f"/{command}"):].strip()
        if args_text:
            return args_text.split()
    return []

def is_valid_http_status(status_code: int) -> bool:
    """Check if HTTP status code indicates success"""
    return 200 <= status_code < 400

def format_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format ISO timestamp string to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime(format_str)
    except:
        return timestamp_str

def calculate_uptime_percentage(successful: int, total: int) -> float:
    """Calculate uptime percentage"""
    if total == 0:
        return 0.0
    return (successful / total) * 100

def sanitize_url(url: str) -> str:
    """Sanitize URL for safe display"""
    # Remove any potential markdown characters that could break formatting
    return url.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")

def log_performance(func_name: str, start_time: datetime, end_time: datetime):
    """Log function performance"""
    duration = (end_time - start_time).total_seconds()
    logger.debug(f"Function {func_name} took {duration:.3f}s")

def create_url_keyboard(urls: List[str], action_prefix: str):
    """Create inline keyboard with URL buttons"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = []
    for url in urls:
        # Truncate URL for button display
        display_url = truncate_url(url, 30)
        callback_data = f"{action_prefix}:{url}"
        
        # Telegram callback data limit is 64 characters
        if len(callback_data) > 64:
            # Use URL hash or truncate
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            callback_data = f"{action_prefix}:{url_hash}"
        
        keyboard.append([InlineKeyboardButton(display_url, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(keyboard)

def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message for user display"""
    error_msg = "❌ **An error occurred**\n\n"
    if context:
        error_msg += f"**Context:** {context}\n"
    error_msg += f"**Error:** {str(error)}\n\n"
    error_msg += "Please try again or contact the administrator if the problem persists."
    return error_msg

def is_url_reachable(url: str) -> bool:
    """Quick check if URL format is reachable (basic validation)"""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except:
        return False
