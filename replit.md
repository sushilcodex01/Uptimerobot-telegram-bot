# Overview

This is an advanced Telegram bot application designed to monitor URL uptime and availability with a modern, interactive user interface. The bot provides keep-alive pings for websites, sends real-time status alerts, and features an enhanced UI with animations, progress indicators, and smart dashboards. It includes advanced features like predictive analytics planning, smart scheduling concepts, and comprehensive reporting capabilities. The bot is restricted to admin-only access and maintains persistent data storage for monitoring history and downtime incidents.

## Recent Enhancements (August 2025)
- **Advanced UI System**: Complete redesign with modern interactive elements
- **Animated Loading**: Progress bars and loading animations for better user experience  
- **Smart Dashboard**: Real-time analytics with visual health indicators
- **Enhanced Navigation**: Intuitive button-based interface with quick actions
- **Per-Admin Data Isolation**: Complete separation of URL data between administrators (COMPLETED)
- **Data Migration System**: Automatic migration from legacy shared data to per-admin structure
- **Multi-Admin Security**: Each admin can only access their own monitored URLs and statistics
- **Future-Ready Architecture**: Modular design supporting upcoming AI features
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

## Authentication & Authorization
The system implements a multi-admin access control model with hierarchical permissions:
- **Primary Admin**: Main administrator (chat ID: 1691680798) with full management privileges
- **Secondary Admins**: Additional users who can access all URL monitoring features
- **Admin Management**: Primary admin can add/remove other administrators
- **Persistent Admin Storage**: Admin list stored in `admin_data.json` for persistence
- All bot commands require admin authentication
- Non-admin users receive access denied messages

### Admin Management Commands
- `/addadmin <chat_id>` - Add new admin (Primary admin only)
- `/removeadmin <chat_id>` - Remove admin (Primary admin only, cannot remove primary)
- `/listadmins` - View all administrators (Primary admin only)
- **Admin Panel**: Interactive button interface for admin management

## Data Persistence Strategy
The application uses JSON file-based storage for simplicity and portability:
- Single JSON file stores all monitoring data
- Tracks URL status, ping history, and downtime incidents
- Automatic data file creation with default structure
- Error recovery with fallback to default data structure

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