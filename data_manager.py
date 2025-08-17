"""
Data persistence manager for URL monitoring data
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_file: str = "urls_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        default_data = {
            "admin_data": {},  # admin_chat_id -> {urls: {}, ping_history: {}, downtime_incidents: {}}
            # Legacy support - will be migrated
            "urls": {},  
            "ping_history": {},  
            "downtime_incidents": {}  
        }
        
        if not os.path.exists(self.data_file):
            logger.info(f"Data file {self.data_file} not found, creating new one")
            self._save_data(default_data)
            return default_data
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all required keys exist
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                logger.info(f"Loaded data from {self.data_file}")
                # Migrate legacy data if needed
                data = self._migrate_legacy_data(data)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading data file: {e}")
            logger.info("Creating new data file with default structure")
            self._save_data(default_data)
            return default_data
    
    def _save_data(self, data: Optional[Dict[str, Any]] = None):
        """Save data to JSON file"""
        try:
            data_to_save = data if data is not None else self.data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            logger.debug(f"Data saved to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def _migrate_legacy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy shared data structure to per-admin structure"""
        if "admin_data" not in data:
            data["admin_data"] = {}
        
        # If legacy data exists, migrate it to primary admin
        if data.get("urls") or data.get("ping_history") or data.get("downtime_incidents"):
            primary_admin_id = "1691680798"  # Primary admin from config
            
            if primary_admin_id not in data["admin_data"]:
                data["admin_data"][primary_admin_id] = {
                    "urls": data.get("urls", {}),
                    "ping_history": data.get("ping_history", {}),
                    "downtime_incidents": data.get("downtime_incidents", {})
                }
                logger.info(f"Migrated legacy data to admin {primary_admin_id}")
            
            # Clear legacy data after migration
            data["urls"] = {}
            data["ping_history"] = {}
            data["downtime_incidents"] = {}
            
            self._save_data(data)
        
        return data
    
    def _ensure_admin_data(self, admin_chat_id: str):
        """Ensure admin has their own data structure"""
        if admin_chat_id not in self.data["admin_data"]:
            self.data["admin_data"][admin_chat_id] = {
                "urls": {},
                "ping_history": {},
                "downtime_incidents": {}
            }
    
    def add_url(self, url: str, admin_chat_id: str) -> bool:
        """Add a new URL to monitor for specific admin"""
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]
        
        if url in admin_data["urls"]:
            logger.info(f"URL {url} already exists for admin {admin_chat_id}, updating timestamp")
        
        admin_data["urls"][url] = {
            "added_at": datetime.now().isoformat(),
            "last_check": None,
            "status": "pending",
            "response_time": None
        }
        
        if url not in admin_data["ping_history"]:
            admin_data["ping_history"][url] = []
        
        if url not in admin_data["downtime_incidents"]:
            admin_data["downtime_incidents"][url] = []
        
        self._save_data()
        logger.info(f"Added URL: {url} for admin {admin_chat_id}")
        return True
    
    def remove_url(self, url: str, admin_chat_id: str) -> bool:
        """Remove a URL from monitoring for specific admin"""
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]
        
        if url not in admin_data["urls"]:
            logger.warning(f"URL {url} not found for admin {admin_chat_id}")
            return False
        
        # Remove from admin's data structures
        del admin_data["urls"][url]
        
        if url in admin_data["ping_history"]:
            del admin_data["ping_history"][url]
        
        if url in admin_data["downtime_incidents"]:
            del admin_data["downtime_incidents"][url]
        
        self._save_data()
        logger.info(f"Removed URL: {url} for admin {admin_chat_id}")
        return True
    
    def get_urls(self, admin_chat_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all monitored URLs for specific admin"""
        self._ensure_admin_data(admin_chat_id)
        return self.data["admin_data"][admin_chat_id]["urls"].copy()
    
    def get_all_urls(self) -> Dict[str, str]:
        """Get all URLs from all admins for monitoring purposes (returns url -> admin_id mapping)"""
        all_urls = {}
        for admin_id, admin_data in self.data["admin_data"].items():
            for url in admin_data["urls"]:
                all_urls[url] = admin_id
        return all_urls
    
    def update_url_status(self, url: str, admin_chat_id: str, status_code: int, response_time: float, success: bool):
        """Update URL status after a ping for specific admin"""
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]
        
        if url not in admin_data["urls"]:
            logger.warning(f"Attempted to update status for unknown URL: {url} for admin {admin_chat_id}")
            return
        
        now = datetime.now()
        
        # Update main URL data
        admin_data["urls"][url].update({
            "last_check": now.isoformat(),
            "status": "online" if success else "offline",
            "response_time": response_time
        })
        
        # Add to ping history
        ping_record = {
            "timestamp": now.isoformat(),
            "status_code": status_code,
            "response_time": response_time,
            "success": success
        }
        
        admin_data["ping_history"][url].append(ping_record)
        
        # Keep only last 1000 ping records per URL to prevent file bloat
        if len(admin_data["ping_history"][url]) > 1000:
            admin_data["ping_history"][url] = admin_data["ping_history"][url][-1000:]
        
        # Handle downtime incidents
        self._update_downtime_incidents(url, admin_chat_id, success, now)
        
        self._save_data()
    
    def _update_downtime_incidents(self, url: str, admin_chat_id: str, success: bool, timestamp: datetime):
        """Track downtime incidents for specific admin"""
        admin_data = self.data["admin_data"][admin_chat_id]
        incidents = admin_data["downtime_incidents"][url]
        
        if not success:
            # Check if this is a new incident or continuation of existing one
            if not incidents or (incidents[-1].get("end_time") is not None):
                # New incident
                incidents.append({
                    "start_time": timestamp.isoformat(),
                    "end_time": None,
                    "duration": None
                })
        else:
            # URL is back online, close any open incident
            if incidents and incidents[-1].get("end_time") is None:
                start_time = datetime.fromisoformat(incidents[-1]["start_time"])
                duration = (timestamp - start_time).total_seconds()
                incidents[-1].update({
                    "end_time": timestamp.isoformat(),
                    "duration": duration
                })
    
    def get_uptime_stats(self, url: str, admin_chat_id: str, hours: int = 24) -> Dict[str, Any]:
        """Calculate uptime statistics for the last N hours for specific admin"""
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]
        
        if url not in admin_data["ping_history"]:
            return {"uptime_percentage": 0, "total_pings": 0, "successful_pings": 0}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_pings = [
            ping for ping in admin_data["ping_history"][url]
            if datetime.fromisoformat(ping["timestamp"]) > cutoff_time
        ]
        
        if not recent_pings:
            return {"uptime_percentage": 0, "total_pings": 0, "successful_pings": 0}
        
        total_pings = len(recent_pings)
        successful_pings = sum(1 for ping in recent_pings if ping["success"])
        uptime_percentage = (successful_pings / total_pings) * 100
        
        # Calculate average response time for successful pings
        successful_response_times = [
            ping["response_time"] for ping in recent_pings 
            if ping["success"] and ping["response_time"] is not None
        ]
        avg_response_time = (
            sum(successful_response_times) / len(successful_response_times)
            if successful_response_times else 0
        )
        
        return {
            "uptime_percentage": round(uptime_percentage, 2),
            "total_pings": total_pings,
            "successful_pings": successful_pings,
            "failed_pings": total_pings - successful_pings,
            "avg_response_time": round(avg_response_time, 3) if avg_response_time else None
        }
    
    def get_recent_incidents(self, url: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent downtime incidents"""
        if url not in self.data["downtime_incidents"]:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_incidents = []
        
        for incident in self.data["downtime_incidents"][url]:
            start_time = datetime.fromisoformat(incident["start_time"])
            if start_time > cutoff_time:
                recent_incidents.append(incident)
        
        return recent_incidents
    
    def cleanup_old_data(self, days: int = 7):
        """Clean up old ping history data"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for url in self.data["ping_history"]:
            original_count = len(self.data["ping_history"][url])
            self.data["ping_history"][url] = [
                ping for ping in self.data["ping_history"][url]
                if datetime.fromisoformat(ping["timestamp"]) > cutoff_time
            ]
            cleaned_count = len(self.data["ping_history"][url])
            
            if original_count != cleaned_count:
                logger.info(f"Cleaned {original_count - cleaned_count} old ping records for {url}")
        
        self._save_data()
