# Overview

This is an advanced Telegram bot application designed to monitor URL uptime and availability with a modern, interactive user interface. The bot provides keep-alive pings for websites, sends real-time status alerts, and features an enhanced UI with animations, progress indicators, and smart dashboards. It includes advanced features like predictive analytics planning, smart scheduling concepts, and comprehensive reporting capabilities. The bot is restricted to admin-only access and maintains persistent data storage for monitoring history and downtime incidents.

## Recent Enhancements (August 2025)
- **Notion Database Integration**: Complete migration from JSON to Notion database storage (COMPLETED)
- **Database Schema Setup**: Added required columns (user_id, url, status, added_at, last_check, response_time, username) (COMPLETED)
- **Open Access**: Bot now available to all users, no admin restrictions (COMPLETED)
- **Per-User Data Isolation**: Each user has their own data stored in Notion database
- **Advanced UI System**: Modern interactive elements with progress indicators
- **Real-time Monitoring**: Continuous URL monitoring with instant alerts
- **Scalable Architecture**: Notion-based storage supports unlimited users
- **Mobile-Optimized**: Responsive design optimized for mobile Telegram usage

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The application follows a modular architecture with clear separation of concerns and advanced UI capabilities:

- **Main Entry Point (`main.py`)**: Orchestrates the entire application, initializes components, and manages the bot lifecycle
- **Bot Handlers (`bot_handlers.py`)**: Enhanced with advanced UI, implements all Telegram bot command handlers and interactive user interfaces
- **Advanced UI (`advanced_ui.py`)**: Modern UI components with animations, progress indicators, and smart dashboards
- **URL Monitor (`url_monitor.py`)**: Core monitoring service that performs keep-alive pings and status tracking
- **Data Manager (`data_manager.py`)**: Handles persistent data storage using JSON files
- **Configuration (`config.py`)**: Centralized configuration management with environment variable support
- **Utilities (`utils.py`)**: Common helper functions for URL validation and message formatting
- **Future Features (`future_features.py`)**: Advanced features planned for future implementation including AI insights, predictive analytics, and integration hub

## User Access & Data Management
The system now provides open access to all users with individual data isolation:
- **Open Access**: Any Telegram user can use the bot
- **Per-User Data**: Each user's URLs are stored separately in Notion database
- **Data Privacy**: Users can only see and manage their own monitored URLs
- **No Admin System**: Removed admin-only restrictions for broader accessibility
- **Scalable Storage**: Notion database handles unlimited users and URLs

## Data Persistence Strategy
The application uses Notion database for scalable and reliable storage:
- **Notion Integration**: All data stored in structured Notion database
- **User Isolation**: Each user's data is completely separate
- **Real-time Updates**: Status changes are immediately reflected in Notion
- **Scalable Storage**: Handles unlimited users and monitoring data
- **API Integration**: Uses Notion API for all data operations
- **Required Secrets**: NOTION_INTEGRATION_SECRET and NOTION_DATABASE_ID

## Monitoring Architecture
The URL monitoring system operates on an asynchronous ping model:
- Configurable ping intervals (default 60 seconds)
- HTTP/HTTPS request validation with timeout handling
- Status tracking with success/failure detection
- Real-time alert system through Telegram notifications
- Historical data collection for uptime statistics

## Bot Command Structure & Advanced UI
The Telegram integration provides a comprehensive command interface with modern interactive elements:

### Traditional Commands (Enhanced)
- URL management (add, remove, list) with animated processing
- Status monitoring with real-time dashboards
- Advanced statistics with visual health indicators  
- Immediate ping requests with progress tracking

### Advanced Interactive Interface
- **Smart Dashboard**: Main menu with quick access to all features
- **Animated Loading**: Progress bars and loading indicators for better UX
- **URL Management Panel**: Enhanced interface with pagination and detailed views
- **Statistics Dashboard**: Real-time analytics with performance summaries
- **Settings Panel**: Comprehensive configuration options
- **Quick Actions**: Instant access to frequently used features
- **Mobile-Optimized**: Responsive design for seamless mobile experience

### Future-Ready Features
- **AI Insights**: Planned predictive analytics and pattern recognition
- **Multi-Region Monitoring**: Geographic performance testing capabilities
- **Advanced Reporting**: Comprehensive PDF/HTML reports with charts
- **Integration Hub**: Webhook support for Slack, Discord, email alerts
- **Smart Scheduling**: Adaptive ping intervals based on traffic patterns

# External Dependencies

## Telegram Bot API
- **python-telegram-bot**: Primary library for Telegram Bot API integration
- **Purpose**: Handles all bot communication, command processing, and message formatting
- **Key Features**: Command handlers, callback query support, inline keyboards

## HTTP Client
- **aiohttp**: Asynchronous HTTP client for URL ping operations
- **Purpose**: Performs keep-alive requests to monitored URLs
- **Configuration**: Timeout handling, redirect following, session management

## Environment Configuration
- **BOT_TOKEN**: Telegram Bot API token (required)
- **ADMIN_CHAT_ID**: Admin user's Telegram chat ID (required)
- **Purpose**: Secure configuration without hardcoded credentials

## Data Storage
- **JSON File System**: Local file-based persistence
- **File**: `urls_data.json` for monitoring data storage
- **Logging**: File-based logging to `bot.log` with console output