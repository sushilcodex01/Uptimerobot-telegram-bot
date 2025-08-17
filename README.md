# 🌐 Advanced Telegram URL Monitor Bot (@Gamaspyowner)

A comprehensive Telegram bot application designed to monitor URL uptime and availability with a modern, interactive user interface. The bot provides keep-alive pings for websites, sends real-time status alerts, and features an enhanced UI with animations, progress indicators, and smart dashboards.

![Bot Status](https://img.shields.io/badge/Bot-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Database](https://img.shields.io/badge/Database-Notion-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
## ✨ Replit link = https://replit.com/@casale9543/URLWatchdog
## ✨ Key Features

### 🔔 **Real-time Monitoring System**
- Continuous URL health checks every 60 seconds
- Instant downtime/uptime notifications via Telegram
- Response time tracking and comprehensive analytics
- Keep-alive ping functionality with detailed reporting

### 🌍 **Open Access & Scalable Architecture**
- **Open to All Users**: No admin restrictions - any Telegram user can use the bot
- **Per-User Data Isolation**: Each user's URLs are stored separately in Notion database
- **Unlimited Scalability**: Notion-based storage supports unlimited users and URLs
- **Data Privacy**: Users can only see and manage their own monitored URLs

### 🗄️ **Notion Database Integration**
- **Complete Migration**: From JSON to Notion database storage for better scalability
- **Structured Storage**: Organized data with proper schema (user_id, url, status, timestamps)
- **Real-time Updates**: Status changes immediately reflected in Notion
- **API Integration**: Uses Notion API for all data operations

### 📱 **Advanced Interactive UI**
- **Smart Dashboard**: Main menu with quick access to all features
- **Animated Loading**: Progress bars and loading indicators for better UX
- **URL Management Panel**: Enhanced interface with pagination and detailed views
- **Statistics Dashboard**: Real-time analytics with performance summaries
- **Mobile-Optimized**: Responsive design optimized for mobile Telegram usage

### 🌐 **Web Server & Health Monitoring**
- Beautiful welcome page on port 5000
- Health check endpoints for deployment monitoring
- Status API for service information
- Mobile-friendly responsive design

### ⚡ **Smart Automation Features**
- Automatic protocol detection (adds https:// if missing)
- Bulk URL management through inline keyboards
- Advanced confirmation system for URL removal
- Comprehensive error handling and logging
- Predictive analytics planning and smart scheduling concepts

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Notion Integration Secret and Database ID
- Basic understanding of Telegram bots

### Replit Deployment (Recommended)

1. **Fork this Replit project**
2. **Set up required secrets in Replit:**
   - `BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `NOTION_INTEGRATION_SECRET`: Your Notion integration secret
   - `NOTION_DATABASE_ID`: Your Notion database ID

3. **Run the project**
   - Click the "Run" button in Replit
   - Bot will automatically start and be accessible via web interface on port 5000

### Local Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telegram-url-monitor-bot
```

2. **Install dependencies**
```bash
pip install python-telegram-bot aiohttp
```

3. **Configure environment variables**
```bash
export BOT_TOKEN="your_bot_token_here"
export NOTION_INTEGRATION_SECRET="your_notion_secret"
export NOTION_DATABASE_ID="your_database_id"
```

4. **Run the bot**
```bash
python main.py
```

## 🗄️ Notion Database Setup

### Step 1: Create Notion Integration
1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Click "New Integration"
3. Give it a name and select your workspace
4. Copy the "Internal Integration Secret"

### Step 2: Create Database
1. Create a new Notion page
2. Add a database with these columns:
   - `user_id` (Title)
   - `url` (URL)
   - `status` (Select: online, offline, pending)
   - `added_at` (Date)
   - `last_check` (Date)
   - `response_time` (Number)
   - `username` (Text)

### Step 3: Connect Integration
1. Click "Share" on your database page
2. Add your integration to the page
3. Copy the database ID from the URL

### Step 4: Deploy to Replit
1. **Fork this Replit project**
2. **Add these secrets:**
   - `BOT_TOKEN`: From @BotFather
   - `NOTION_INTEGRATION_SECRET`: From step 1
   - `NOTION_DATABASE_ID`: From step 3
3. **Run the project** - Bot will start automatically

## 🛠️ Configuration

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ | None | Telegram bot token from @BotFather |
| `NOTION_INTEGRATION_SECRET` | ✅ | None | Notion integration secret |
| `NOTION_DATABASE_ID` | ✅ | None | Notion database ID |
| `PING_INTERVAL` | ❌ | 60 | Monitoring interval in seconds |
| `REQUEST_TIMEOUT` | ❌ | 30 | HTTP request timeout |
| `PORT` | ❌ | 5000 | Web server port |

### Bot Configuration (`config.py`)
```python
class Config:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.notion_secret = os.getenv('NOTION_INTEGRATION_SECRET')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.ping_interval = int(os.getenv('PING_INTERVAL', 60))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
        self.port = int(os.getenv('PORT', 5000))
```

## 📖 Usage Guide

### Basic Commands (Available to All Users)
- `/start` - Initialize the bot and show main interactive dashboard
- `/help` - Display help information and command list
- `/seturl <url>` - Add a URL for monitoring (stored in your personal space)
- `/removeurl <url>` - Remove a URL from your monitoring list
- `/listurls` - Show all your monitored URLs with real-time status
- `/status` - Get comprehensive bot and monitoring status
- `/pingnow` - Perform immediate ping of all your URLs

### No Admin System
This bot now operates with **open access** - any Telegram user can:
- Add and monitor their own URLs
- Receive real-time alerts for their websites
- Access comprehensive analytics for their URLs
- Use all features without restrictions

### Advanced Interactive Interface
Modern dashboard with animated elements and smart navigation:

#### 🏠 **Smart Dashboard**
- **Real-time Overview**: Health indicators and uptime percentage
- **Quick Actions**: Instant access to frequently used features
- **Status Cards**: Visual representation of URL health
- **Mobile-Optimized**: Responsive design for seamless mobile experience

#### 🌐 **URL Management Panel**
- ➕ **Add URL Wizard** - Smart URL addition with validation
- 🗑️ **Remove URL** - Safe removal with confirmation
- 📋 **Enhanced URL List** - Paginated view with detailed metrics
- 🔄 **Real-time Updates** - Live status updates every 60 seconds

#### 📊 **Analytics Dashboard**
- **Performance Metrics**: Response time tracking and trends
- **Uptime Statistics**: Historical data and availability percentages
- **Health Indicators**: Visual status representation (🟢🟡🔴)
- **Quick Ping**: Instant testing with detailed reports

#### 🎨 **Enhanced UI Elements**
- **Progress Animations**: Loading bars for better user experience
- **Status Indicators**: Color-coded health visualization
- **Card-based Layout**: Clean, organized information display
- **Interactive Buttons**: Smooth navigation between features

## 🌐 API Endpoints

The web server exposes several endpoints:

### `GET /` - Welcome Dashboard
Beautiful welcome page with comprehensive bot information:
- Feature overview and capabilities
- Getting started guide
- Real-time bot status
- Contact information and support

### `GET /health` - Health Check Endpoint
```json
{
    "status": "healthy",
    "service": "Advanced Telegram URL Monitor Bot",
    "port": 5000,
    "database": "notion",
    "monitoring": "active"
}
```

### `GET /status` - Detailed Service Status
```json
{
    "bot_status": "running",
    "web_server": "active",
    "port": 5000,
    "database": "notion_connected",
    "features": [
        "URL Monitoring",
        "Real-time Alerts", 
        "Open Access",
        "Notion Database Integration",
        "Advanced UI Dashboard",
        "Performance Analytics"
    ],
    "monitoring": {
        "interval": "60 seconds",
        "active_users": "unlimited",
        "storage": "notion_database"
    }
}
```

## 📁 Project Structure

```
telegram-url-monitor-bot/
├── main.py                    # Main application entry point and lifecycle management
├── config.py                  # Centralized configuration management
├── bot_handlers.py            # Enhanced Telegram bot command handlers with UI
├── advanced_ui.py             # Modern UI components with animations and dashboards
├── url_monitor.py             # Core URL monitoring service with async pings
├── notion_data_manager.py     # Notion database integration and data management
├── web_server.py              # Web interface for health checks and status
├── utils.py                   # Common utility functions and URL validation
├── future_features.py         # Planned advanced features and integrations
├── requirements.txt           # Python dependencies
├── README.md                  # Complete project documentation
├── replit.md                  # Project architecture and development guide
├── pyproject.toml            # Python project configuration
├── uv.lock                   # Dependency lock file
└── bot.log                   # Application logs (auto-generated)
```

### Key Components

#### **Core Application (`main.py`)**
Orchestrates the entire application, initializes components, and manages the bot lifecycle with proper error handling and graceful shutdown.

#### **Notion Integration (`notion_data_manager.py`)**
Handles all database operations with Notion API, providing scalable storage for unlimited users with proper data isolation.

#### **Advanced UI System (`advanced_ui.py`)**
Modern interface components with animations, progress indicators, and responsive design optimized for mobile Telegram usage.

#### **URL Monitoring (`url_monitor.py`)**
Asynchronous monitoring service that performs keep-alive pings every 60 seconds with comprehensive error handling and alert system.

## 🔧 Development

### Running in Development Mode
```bash
# Install development dependencies
pip install python-telegram-bot aiohttp

# Set up environment variables
export BOT_TOKEN="your_bot_token"
export NOTION_INTEGRATION_SECRET="your_notion_secret"
export NOTION_DATABASE_ID="your_database_id"

# Run with debug logging
python main.py
```

### Development on Replit
1. Fork the project
2. Set up secrets in Replit environment
3. Modify code with live preview
4. Test changes in real-time
5. Deploy instantly

### Adding New Features
1. Study the modular architecture in `replit.md`
2. Create feature branch
3. Follow existing patterns in `advanced_ui.py` and `bot_handlers.py`
4. Test with multiple users to ensure data isolation
5. Update documentation and submit pull request

## 📊 Monitoring & Logging

### Comprehensive Logging System
- **Bot Activities**: All user interactions and command executions
- **URL Monitoring**: Ping results, response times, and status changes
- **Database Operations**: Notion API calls and data transactions
- **Web Server**: Health check requests and status queries
- **Error Tracking**: Detailed error messages with stack traces

### Log Output
- **Console**: Real-time logging for development and debugging
- **File**: Persistent logging to `bot.log` with rotation
- **Structured**: JSON-like format for easy parsing and analysis

### Performance Metrics
- Response time tracking for each monitored URL
- Success/failure rates and uptime percentages
- User activity patterns and feature usage
- Database performance and API response times

## 🔒 Security & Privacy Features

- **Data Isolation** - Each user's data is completely separate in Notion database
- **Input Validation** - All user inputs are validated and sanitized
- **Rate Limiting** - Built-in protection against spam and abuse
- **Secure API Integration** - Encrypted communication with Notion API
- **Privacy First** - Users can only see and manage their own URLs
- **No Admin Oversight** - No central authority can access user data

## ⚠️ Troubleshooting

### Common Issues

**Bot not responding:**
- Check if bot token is valid
- Verify bot is added to your chat
- Check internet connectivity

**URLs not being monitored:**
- Ensure URLs are valid and accessible
- Check if monitoring service is running
- Verify URL format (http/https)
- Confirm Notion database connection

**Database connection issues:**
- Verify NOTION_INTEGRATION_SECRET is correct
- Check NOTION_DATABASE_ID is valid
- Ensure integration has access to the database
- Confirm database schema matches requirements

**Deployment issues:**
- Check all environment variables are set correctly
- Verify port 5000 is accessible
- Check service logs in `bot.log` for errors
- Test Notion API connectivity

### Getting Help
1. Check the logs in `bot.log`
2. Verify configuration settings
3. Test with `/status` command
4. Use health check endpoint: `/health`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines
- Follow Python coding standards
- Add tests for new features
- Update documentation as needed
- Ensure backward compatibility

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check existing issues for solutions
- Refer to the troubleshooting section

## 🚀 Recent Updates (August 2025)

### ✅ **Completed Enhancements**
- **Notion Database Integration**: Complete migration from JSON to Notion database storage
- **Open Access Model**: Removed admin restrictions - now available to all users
- **Per-User Data Isolation**: Each user's URLs stored separately with full privacy
- **Advanced UI Dashboard**: Modern interface with animations and real-time updates
- **Enhanced Monitoring**: Improved ping system with detailed analytics
- **Scalable Architecture**: Supports unlimited users and URLs

### 🔧 **Technical Improvements**
- **Error Handling**: Comprehensive error management and user feedback
- **Hash-based URL Management**: Consistent URL identification system
- **Async Operations**: Non-blocking monitoring and database operations
- **Mobile Optimization**: Enhanced UI for mobile Telegram usage
- **Performance Metrics**: Real-time response time tracking and uptime statistics

---

## 🎯 **Live Bot Information**

**Bot Username**: [@Gamaspyowner](https://t.me/Gamaspyowner)
**Status**: Active and monitoring URLs 24/7
**Access**: Open to all Telegram users
**Database**: Notion-powered for unlimited scalability

---

**Made with ❤️ for reliable website monitoring and real-time alerts**

⭐ If this project helps you monitor your websites effectively, please consider giving it a star!

🤖 **Try the bot now**: [Start monitoring your URLs](https://t.me/Gamaspyowner)
