# 🤖 Telegram URL Monitor Bot

A powerful Telegram bot that monitors your websites and URLs 24/7 with real-time alerts, uptime tracking, and multi-admin support.

![Bot Status](https://img.shields.io/badge/Bot-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
##  Replit link = https://replit.com/@homefe2911/URLWatchdog
## ✨ Features

### 🔔 **Real-time Monitoring**
- Continuous URL health checks every 60 seconds
- Instant down/up notifications via Telegram
- Response time tracking and analytics
- Keep-alive ping functionality

### 👥 **Multi-Admin Support**
- Multiple admins can manage their own URLs independently
- Admin-specific URL lists and monitoring
- Secure admin authentication system
- Primary admin controls for user management

### 📊 **Advanced Analytics**
- Response time monitoring
- Uptime/downtime statistics
- Historical performance data
- Quick ping functionality with detailed reports

### 🌐 **Web Interface**
- Beautiful welcome page on port 5555
- Health check endpoints for deployment monitoring
- Status API for service information
- Mobile-friendly responsive design

### ⚡ **Smart Features**
- Automatic protocol detection (adds https:// if missing)
- Bulk URL management through inline keyboards
- Advanced confirmation system for URL removal
- Comprehensive error handling and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Local Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telegram-url-monitor-bot
```

2. **Install dependencies**
```bash
pip install python-telegram-bot aiohttp flask
```

3. **Configure the bot**
- Edit `config.py` with your bot token and admin chat ID
- Or set environment variables:
```bash
export BOT_TOKEN="your_bot_token_here"
export PRIMARY_ADMIN_CHAT_ID="your_chat_id"
```

4. **Run the bot**
```bash
python main.py
```

## 🌍 Deploy to Render

### Step 1: Prepare Your Repository
Ensure your code is pushed to a GitHub repository with all files including this README.

### Step 2: Create Render Web Service
1. Go to [Render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Build Settings:**
```
Build Command: pip install python-telegram-bot aiohttp flask
Start Command: python main.py
```

**Service Settings:**
```
Name: telegram-url-monitor-bot
Environment: Python
Region: Choose your preferred region
Branch: main (or your default branch)
```

### Step 3: Environment Variables
Add these environment variables in Render dashboard:

| Variable | Value | Description |
|----------|--------|-------------|
| `BOT_TOKEN` | `your_bot_token` | Get from @BotFather |
| `PRIMARY_ADMIN_CHAT_ID` | `your_chat_id` | Your Telegram chat ID |
| `PORT` | `5555` | Web server port (optional) |

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your bot will be live at `https://your-app-name.onrender.com`

## 🛠️ Configuration

### Bot Configuration (`config.py`)
```python
class Config:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
        self.primary_admin_chat_id = os.getenv('PRIMARY_ADMIN_CHAT_ID', 'YOUR_CHAT_ID')
        self.ping_interval = 60  # seconds
        self.request_timeout = 30  # seconds
```

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ | None | Telegram bot token |
| `PRIMARY_ADMIN_CHAT_ID` | ✅ | None | Primary admin's chat ID |
| `PING_INTERVAL` | ❌ | 60 | Monitoring interval in seconds |
| `REQUEST_TIMEOUT` | ❌ | 30 | HTTP request timeout |

## 📖 Usage Guide

### Basic Commands
- `/start` - Initialize the bot and show main menu
- `/help` - Display help information and command list
- `/seturl <url>` - Add a URL for monitoring
- `/removeurl <url>` - Remove a URL from monitoring
- `/listurls` - Show all monitored URLs
- `/status` - Get bot and monitoring status
- `/pingnow` - Perform immediate ping of all URLs

### Admin Commands
- `/addadmin <chat_id>` - Add a new admin (primary admin only)
- `/removeadmin <chat_id>` - Remove an admin (primary admin only)
- `/listadmins` - List all admins

### Interactive Features
Use the inline keyboard buttons for easy navigation:
- ➕ **Add URL** - Smart URL addition wizard
- 🗑️ **Remove URL** - Smart URL removal wizard
- 🌐 **View URLs** - List all monitored URLs with status
- ⚡ **Quick Ping** - Instant ping all URLs
- 📊 **Stats** - View monitoring statistics

## 🌐 API Endpoints

The web server exposes several endpoints:

### `GET /`
Welcome page with bot information and features

### `GET /health`
Health check endpoint for monitoring services
```json
{
    "status": "healthy",
    "service": "Telegram URL Monitor Bot",
    "port": 5555
}
```

### `GET /status`
Detailed service status
```json
{
    "bot_status": "running",
    "web_server": "active",
    "port": 5555,
    "features": [
        "URL Monitoring",
        "Real-time Alerts",
        "Multi-admin Support",
        "Performance Analytics"
    ]
}
```

## 📁 Project Structure

```
telegram-url-monitor-bot/
├── main.py                 # Main application entry point
├── config.py               # Configuration management
├── bot_handlers.py         # Telegram bot command handlers
├── url_monitor.py          # URL monitoring service
├── data_manager.py         # Data storage and management
├── web_server.py           # Flask web server
├── advanced_ui.py          # Advanced UI components
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── urls_data.json         # URL monitoring data (auto-generated)
└── admin_data.json        # Admin data storage (auto-generated)
```

## 🔧 Development

### Running in Development Mode
```bash
# Install development dependencies
pip install python-telegram-bot aiohttp flask

# Run with debug logging
python main.py
```

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## 📊 Monitoring & Logging

The bot includes comprehensive logging:
- Bot activities and errors
- URL monitoring results
- Admin actions
- Web server requests

Logs are written to both console and `bot.log` file.

## 🔒 Security Features

- **Admin Authentication** - Only authorized users can manage URLs
- **Input Validation** - All user inputs are validated and sanitized
- **Rate Limiting** - Built-in protection against spam
- **Secure Data Storage** - JSON-based local storage with proper permissions

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

**Deployment issues:**
- Check environment variables are set correctly
- Verify port 5555 is accessible
- Check service logs for errors

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

---

**Made with ❤️ for reliable website monitoring**

⭐ If this project helps you, please consider giving it a star!
