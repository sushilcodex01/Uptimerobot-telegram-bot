#!/usr/bin/env python3
"""
Web Server Component for Telegram URL Monitor Bot
Serves a welcome page for Render deployment
"""

import asyncio
import threading
from flask import Flask, render_template_string
import logging

logger = logging.getLogger(__name__)

class WebServer:
    def __init__(self, port=5555):
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def welcome():
            return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram URL Monitor Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            text-align: center;
            max-width: 800px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .status {
            background: rgba(46, 204, 113, 0.2);
            border: 2px solid #2ecc71;
            padding: 15px;
            border-radius: 10px;
            margin: 30px 0;
            font-weight: bold;
        }
        
        .telegram-link {
            display: inline-block;
            background: #0088cc;
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1rem;
            transition: transform 0.3s ease;
            margin-top: 20px;
        }
        
        .telegram-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 136, 204, 0.4);
        }
        
        .footer {
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        @media (max-width: 600px) {
            .container {
                margin: 20px;
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .logo {
                font-size: 3rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖📊</div>
        <h1>Telegram URL Monitor Bot</h1>
        <p class="subtitle">Advanced URL monitoring with real-time alerts and keep-alive pings</p>
        
        <div class="status">
            ✅ Bot is running and ready to monitor your URLs!
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>Real-time Monitoring</h3>
                <p>Continuous URL health checks with instant notifications</p>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🔔</div>
                <h3>Smart Alerts</h3>
                <p>Get notified immediately when your URLs go down</p>
            </div>
            
            <div class="feature">
                <div class="feature-icon">📈</div>
                <h3>Performance Analytics</h3>
                <p>Track response times and uptime statistics</p>
            </div>
            
            <div class="feature">
                <div class="feature-icon">👥</div>
                <h3>Multi-Admin Support</h3>
                <p>Multiple admins can manage their own URLs independently</p>
            </div>
        </div>
        
        <a href="https://t.me/your_bot_username" class="telegram-link">
            📱 Open Bot in Telegram
        </a>
        
        <div class="footer">
            <p>🚀 Hosted on Render | Built with Python & Flask</p>
            <p>Keep your websites alive 24/7 with automated monitoring</p>
        </div>
    </div>
</body>
</html>
            """)
        
        @self.app.route('/health')
        def health():
            return {
                "status": "healthy",
                "service": "Telegram URL Monitor Bot",
                "port": self.port
            }
        
        @self.app.route('/status')
        def status():
            return {
                "bot_status": "running",
                "web_server": "active",
                "port": self.port,
                "features": [
                    "URL Monitoring",
                    "Real-time Alerts", 
                    "Multi-admin Support",
                    "Performance Analytics"
                ]
            }
    
    def run_server(self):
        """Run the Flask server in a separate thread"""
        def run_flask():
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        
        # Run Flask in a separate thread so it doesn't block the main event loop
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"Web server started on port {self.port}")
        return flask_thread
    
    async def start_async(self):
        """Start the web server asynchronously"""
        loop = asyncio.get_event_loop()
        
        def run_flask():
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        
        # Run Flask in a thread pool executor
        await loop.run_in_executor(None, run_flask)