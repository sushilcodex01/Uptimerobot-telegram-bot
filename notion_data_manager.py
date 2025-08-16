#!/usr/bin/env python3
"""
Notion Data Manager - Handles all data operations with Notion database
Replaces the JSON-based data storage with Notion database integration
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)

class NotionDataManager:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_INTEGRATION_SECRET')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not self.notion_token or not self.database_id:
            raise ValueError("NOTION_INTEGRATION_SECRET and NOTION_DATABASE_ID environment variables are required")
        
        self.notion = Client(auth=self.notion_token)
        logger.info("Notion Data Manager initialized successfully")
    
    async def add_url(self, url: str, user_chat_id: str, username: str = None) -> bool:
        """Add a new URL to monitor for a user"""
        try:
            # Check if URL already exists for this user
            existing = await self.get_user_url(user_chat_id, url)
            if existing:
                logger.info(f"URL {url} already exists for user {user_chat_id}, updating timestamp")
                # Update existing entry
                await self._update_url_timestamp(existing['id'])
                return True
            
            # Create new entry
            properties = {
                "Name": {"title": [{"text": {"content": f"URL: {url}"}}]},
                "user_id": {"rich_text": [{"text": {"content": str(user_chat_id)}}]},
                "url": {"url": url},
                "status": {"select": {"name": "Unknown"}},
                "added_at": {"date": {"start": datetime.now().isoformat()}},
                "response_time": {"number": 0}
            }
            
            if username:
                properties["username"] = {"rich_text": [{"text": {"content": username}}]}
            
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"Added URL: {url} for user {user_chat_id}")
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error adding URL: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding URL: {e}")
            return False
    
    async def remove_url(self, url: str, user_chat_id: str) -> bool:
        """Remove a URL from monitoring for a user"""
        try:
            # Find the URL entry for this user
            url_entry = await self.get_user_url(user_chat_id, url)
            if not url_entry:
                logger.warning(f"URL {url} not found for user {user_chat_id}")
                return False
            
            # Archive the page (Notion doesn't delete pages, it archives them)
            self.notion.pages.update(
                page_id=url_entry['id'],
                archived=True
            )
            
            logger.info(f"Removed URL: {url} for user {user_chat_id}")
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error removing URL: {e}")
            return False
        except Exception as e:
            logger.error(f"Error removing URL: {e}")
            return False
    
    async def get_user_urls(self, user_chat_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all monitored URLs for a specific user"""
        try:
            # Query database for this user's URLs
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "user_id",
                    "rich_text": {"equals": str(user_chat_id)}
                }
            )
            
            urls = {}
            for page in response['results']:
                props = page['properties']
                
                # Extract URL
                url_prop = props.get('url', {})
                url = url_prop.get('url') if url_prop else ""
                
                if url:
                    # Extract other properties
                    status_prop = props.get('status', {}).get('select')
                    status = status_prop['name'] if status_prop else "unknown"
                    
                    added_at_prop = props.get('added_at', {}).get('date')
                    added_at = added_at_prop['start'] if added_at_prop else None
                    
                    last_check_prop = props.get('last_check', {}).get('date')
                    last_check = last_check_prop['start'] if last_check_prop else None
                    
                    response_time = props.get('response_time', {}).get('number')
                    
                    urls[url] = {
                        "id": page['id'],
                        "added_at": added_at,
                        "last_check": last_check,
                        "status": status,
                        "response_time": response_time
                    }
            
            return urls
            
        except APIResponseError as e:
            logger.error(f"Notion API error getting user URLs: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting user URLs: {e}")
            return {}
    
    async def get_all_urls(self) -> Dict[str, str]:
        """Get all URLs from all users for monitoring purposes (returns url -> user_id mapping)"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id
            )
            
            all_urls = {}
            for page in response['results']:
                props = page['properties']
                
                # Extract URL and user_id
                url_prop = props.get('url', {})
                url = url_prop.get('url') if url_prop else ""
                
                user_id_prop = props.get('user_id', {}).get('rich_text', [])
                user_id = user_id_prop[0]['text']['content'] if user_id_prop else ""
                
                if url and user_id:
                    all_urls[url] = user_id
            
            return all_urls
            
        except APIResponseError as e:
            logger.error(f"Notion API error getting all URLs: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting all URLs: {e}")
            return {}
    
    async def get_user_url(self, user_chat_id: str, url: str) -> Optional[Dict[str, Any]]:
        """Get a specific URL entry for a user"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "user_id",
                            "rich_text": {"equals": str(user_chat_id)}
                        },
                        {
                            "property": "url",
                            "url": {"equals": url}
                        }
                    ]
                }
            )
            
            if response['results']:
                page = response['results'][0]
                props = page['properties']
                
                status_prop = props.get('status', {}).get('select')
                status = status_prop['name'] if status_prop else "unknown"
                
                added_at_prop = props.get('added_at', {}).get('date')
                added_at = added_at_prop['start'] if added_at_prop else None
                
                last_check_prop = props.get('last_check', {}).get('date')
                last_check = last_check_prop['start'] if last_check_prop else None
                
                response_time = props.get('response_time', {}).get('number')
                
                return {
                    "id": page['id'],
                    "url": url,
                    "status": status,
                    "added_at": added_at,
                    "last_check": last_check,
                    "response_time": response_time
                }
            
            return None
            
        except APIResponseError as e:
            logger.error(f"Notion API error getting user URL: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting user URL: {e}")
            return None
    
    async def update_url_status(self, url: str, user_chat_id: str, success: bool, response_time: float = None, timestamp: datetime = None):
        """Update the status and response time of a URL"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Find the URL entry
            url_entry = await self.get_user_url(user_chat_id, url)
            if not url_entry:
                logger.warning(f"URL {url} not found for user {user_chat_id}")
                return
            
            # Update the entry
            properties = {
                "status": {"select": {"name": "Online" if success else "Offline"}},
                "last_check": {"date": {"start": timestamp.isoformat()}}
            }
            
            if response_time is not None:
                properties["response_time"] = {"number": response_time}
            
            self.notion.pages.update(
                page_id=url_entry['id'],
                properties=properties
            )
            
            logger.debug(f"Updated status for {url} (user: {user_chat_id}): {'online' if success else 'offline'}")
            
        except APIResponseError as e:
            logger.error(f"Notion API error updating URL status: {e}")
        except Exception as e:
            logger.error(f"Error updating URL status: {e}")
    
    async def _update_url_timestamp(self, page_id: str):
        """Update the added_at timestamp of a URL entry"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "added_at": {"date": {"start": datetime.now().isoformat()}}
                }
            )
        except Exception as e:
            logger.error(f"Error updating URL timestamp: {e}")
    
    async def get_url_statistics(self, user_chat_id: str) -> Dict[str, Any]:
        """Get statistics for user's URLs"""
        try:
            urls = await self.get_user_urls(user_chat_id)
            
            if not urls:
                return {
                    "total_urls": 0,
                    "online": 0,
                    "offline": 0,
                    "pending": 0,
                    "average_response_time": 0
                }
            
            online = sum(1 for url_data in urls.values() if url_data['status'] == 'online')
            offline = sum(1 for url_data in urls.values() if url_data['status'] == 'offline')
            pending = sum(1 for url_data in urls.values() if url_data['status'] == 'pending')
            
            # Calculate average response time
            response_times = [url_data['response_time'] for url_data in urls.values() 
                            if url_data['response_time'] is not None]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "total_urls": len(urls),
                "online": online,
                "offline": offline,
                "pending": pending,
                "average_response_time": round(avg_response_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting URL statistics: {e}")
            return {
                "total_urls": 0,
                "online": 0,
                "offline": 0,
                "pending": 0,
                "average_response_time": 0
            }
    
    async def cleanup_old_data(self, days: int = 7):
        """Cleanup method for compatibility - Notion handles data persistence differently"""
        # Notion doesn't require cleanup like JSON files
        # This method is kept for compatibility with the existing interface
        logger.info(f"Notion data cleanup requested for {days} days - no action needed")
        pass

    # Legacy compatibility methods to maintain interface with existing code
    def add_url_sync(self, url: str, user_chat_id: str, username: str = None) -> bool:
        """Synchronous wrapper for add_url"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.add_url(url, user_chat_id, username))
    
    def remove_url_sync(self, url: str, user_chat_id: str) -> bool:
        """Synchronous wrapper for remove_url"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.remove_url(url, user_chat_id))
    
    def get_user_urls_sync(self, user_chat_id: str) -> Dict[str, Dict[str, Any]]:
        """Synchronous wrapper for get_user_urls"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.get_user_urls(user_chat_id))
    
    def get_all_urls_sync(self) -> Dict[str, str]:
        """Synchronous wrapper for get_all_urls"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.get_all_urls())