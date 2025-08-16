"""
URL monitoring service with keep-alive pings and status tracking
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from notion_data_manager import NotionDataManager

logger = logging.getLogger(__name__)

class URLMonitor:
    def __init__(self, ping_interval: int = 60, request_timeout: int = 30):
        self.ping_interval = ping_interval
        self.request_timeout = request_timeout
        self.notion_data = NotionDataManager()
        self.is_running = False
        self.bot_instance = None
        self._monitoring_task = None
    
    def set_bot_instance(self, bot):
        """Set the bot instance for sending alerts"""
        self.bot_instance = bot
    

    
    async def ping_url(self, url: str) -> Dict[str, Any]:
        """Ping a single URL and return status information"""
        start_time = datetime.now()
        
        try:
            # Configure session with timeout
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    
                    success = 200 <= response.status < 400
                    
                    result = {
                        "url": url,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": success,
                        "timestamp": start_time.isoformat(),
                        "error": None
                    }
                    
                    logger.debug(f"Pinged {url}: {response.status} ({response_time:.3f}s)")
                    return result
                    
        except asyncio.TimeoutError:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            result = {
                "url": url,
                "status_code": 408,  # Request Timeout
                "response_time": response_time,
                "success": False,
                "timestamp": start_time.isoformat(),
                "error": "Request timeout"
            }
            logger.warning(f"Timeout pinging {url} after {response_time:.3f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            result = {
                "url": url,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "timestamp": start_time.isoformat(),
                "error": str(e)
            }
            logger.error(f"Error pinging {url}: {e}")
            return result
    
    async def ping_all_urls(self) -> Dict[str, Dict[str, Any]]:
        """Ping all monitored URLs concurrently"""
        url_to_user = await self.notion_data.get_all_urls()
        
        if not url_to_user:
            logger.debug("No URLs to ping")
            return {}
        
        # Create ping tasks for all URLs
        ping_tasks = [self.ping_url(url) for url in url_to_user.keys()]
        
        # Execute all pings concurrently
        results = await asyncio.gather(*ping_tasks, return_exceptions=True)
        
        # Process results
        ping_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ping task failed: {result}")
                continue
            
            url = result["url"]
            ping_results[url] = result
            
            # Update Notion database for the URL owner
            user_id = url_to_user[url]
            await self.notion_data.update_url_status(
                url=url,
                user_chat_id=user_id,
                success=result["success"],
                response_time=result["response_time"],
                timestamp=datetime.fromisoformat(result["timestamp"])
            )
            
            # Send alert if URL is down
            if not result["success"]:
                await self._send_alert(result, user_id)
        
        logger.info(f"Completed ping cycle for {len(ping_results)} URLs")
        return ping_results
    
    async def ping_user_urls(self, user_chat_id: str) -> Dict[str, Dict[str, Any]]:
        """Ping only URLs belonging to a specific user"""
        user_urls = await self.notion_data.get_user_urls(user_chat_id)
        
        if not user_urls:
            logger.debug(f"No URLs to ping for user {user_chat_id}")
            return {}
        
        # Create ping tasks for this user's URLs only
        ping_tasks = [self.ping_url(url) for url in user_urls.keys()]
        
        # Execute all pings concurrently
        results = await asyncio.gather(*ping_tasks, return_exceptions=True)
        
        # Process results
        ping_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ping task failed: {result}")
                continue
            
            url = result["url"]
            ping_results[url] = result
            
            # Update Notion database for this user
            await self.notion_data.update_url_status(
                url=url,
                user_chat_id=user_chat_id,
                success=result["success"],
                response_time=result["response_time"],
                timestamp=datetime.fromisoformat(result["timestamp"])
            )
            
            # Send alert if URL is down (only to this user)
            if not result["success"]:
                await self._send_alert(result, user_chat_id)
        
        logger.info(f"Completed ping cycle for {len(ping_results)} URLs for user {user_chat_id}")
        return ping_results
    
    async def _send_alert(self, ping_result: Dict[str, Any], user_chat_id: str):
        """Send alert to specific user when URL is down"""
        if not self.bot_instance:
            logger.warning("Cannot send alert: bot instance not set")
            return
        
        url = ping_result["url"]
        status_code = ping_result["status_code"]
        error = ping_result.get("error", "Unknown error")
        response_time = ping_result["response_time"]
        
        # Create alert message
        alert_msg = f"🚨 **URL DOWN ALERT** 🚨\n\n"
        alert_msg += f"**URL:** `{url}`\n"
        alert_msg += f"**Status Code:** {status_code}\n"
        alert_msg += f"**Response Time:** {response_time:.3f}s\n"
        alert_msg += f"**Error:** {error}\n"
        alert_msg += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        alert_msg += "Please check the URL status immediately."
        
        try:
            await self.bot_instance.send_message(
                chat_id=user_chat_id,
                text=alert_msg,
                parse_mode='Markdown'
            )
            logger.info(f"Alert sent for {url} to user {user_chat_id}")
        except Exception as e:
            logger.error(f"Failed to send alert for {url} to user {user_chat_id}: {e}")
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        logger.info(f"Starting URL monitoring with {self.ping_interval}s interval")
        
        try:
            while self.is_running:
                start_time = datetime.now()
                
                # Ping all URLs
                await self.ping_all_urls()
                
                # Calculate sleep time to maintain consistent interval
                elapsed_time = (datetime.now() - start_time).total_seconds()
                sleep_time = max(0, self.ping_interval - elapsed_time)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.1f}s until next ping cycle")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"Ping cycle took {elapsed_time:.1f}s, longer than interval of {self.ping_interval}s")
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            raise
        finally:
            self.is_running = False
            logger.info("URL monitoring stopped")
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info("Monitoring stop requested")
    
    async def get_monitoring_status(self, user_chat_id: str = None) -> Dict[str, Any]:
        """Get current monitoring status"""
        if user_chat_id:
            urls = await self.notion_data.get_user_urls(user_chat_id)
        else:
            urls = await self.notion_data.get_all_urls()
        
        status = {
            "is_running": self.is_running,
            "total_urls": len(urls),
            "ping_interval": self.ping_interval,
            "request_timeout": self.request_timeout,
            "urls": {}
        }
        
        if user_chat_id:
            for url, data in urls.items():
                status["urls"][url] = {
                    "status": data.get("status", "unknown"),
                    "last_check": data.get("last_check"),
                    "response_time": data.get("response_time")
                }
        
        return status
    
    async def add_url(self, url: str, user_chat_id: str, username: str = None) -> bool:
        """Add a URL to monitoring for specific user"""
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return await self.notion_data.add_url(url, user_chat_id, username)
    
    async def remove_url(self, url: str, user_chat_id: str) -> bool:
        """Remove a URL from monitoring for specific user"""
        return await self.notion_data.remove_url(url, user_chat_id)
    
    async def get_urls(self, user_chat_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all monitored URLs for specific user"""
        return await self.notion_data.get_user_urls(user_chat_id)
    
    def get_uptime_stats(self, url: str, admin_chat_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get uptime statistics for a URL for specific admin"""
        return self.data_manager.get_uptime_stats(url, admin_chat_id, hours)
