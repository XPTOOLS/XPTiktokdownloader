import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from config import PORT, BOT_TOKEN, API_ID, API_HASH, BOT_NAME, BOT_USERNAME, OWNER_USERNAME, WEBSITE_URL, START_PHOTO_URL, SUPPORT_GROUP_URL, SOURCE_CODE_URL
import json
from datetime import datetime
import socket
from loguru import logger

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            logger.info(f"🔍 Received HTTP {self.command} request for path: {self.path}")
            logger.debug(f"📨 Client: {self.client_address[0]}:{self.client_address[1]}")
            logger.debug(f"📋 Headers: {dict(self.headers)}")
            
            if self.path == '/ping':
                logger.info("🏓 Processing /ping endpoint")
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
                logger.success("✅ /ping request handled successfully")
                
            elif self.path == '/':
                logger.info("🏠 Processing main status page")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Get bot info
                logger.debug("🔄 Getting bot status and current time")
                bot_status = "🟢 Online" if self.is_bot_running() else "🔴 Offline"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.debug(f"🤖 Bot status: {bot_status}")
                logger.debug(f"🕒 Current time: {current_time}")
                
                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{BOT_NAME} - TikTok Downloader</title>
                    <style>
                        body {{
                            font-family: 'Arial', sans-serif;
                            max-width: 1000px;
                            margin: 0 auto;
                            padding: 20px;
                            background: linear-gradient(135deg, #ff0050 0%, #00f2ea 100%);
                            color: #333;
                            min-height: 100vh;
                        }}
                        .container {{
                            background: rgba(255, 255, 255, 0.95);
                            padding: 40px;
                            border-radius: 20px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                            margin-top: 20px;
                        }}
                        h1 {{
                            text-align: center;
                            margin-bottom: 10px;
                            font-size: 2.5em;
                            color: #ff0050;
                            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                        }}
                        .tagline {{
                            text-align: center;
                            font-size: 1.2em;
                            color: #00f2ea;
                            margin-bottom: 30px;
                            font-weight: bold;
                        }}
                        .status-card {{
                            background: linear-gradient(135deg, #ff0050, #00f2ea);
                            color: white;
                            padding: 25px;
                            margin: 20px 0;
                            border-radius: 15px;
                            text-align: center;
                            box-shadow: 0 8px 25px rgba(255, 0, 80, 0.3);
                        }}
                        .status-badge {{
                            display: inline-block;
                            padding: 10px 25px;
                            border-radius: 25px;
                            font-weight: bold;
                            font-size: 1.2em;
                            background: rgba(255, 255, 255, 0.2);
                            margin-bottom: 15px;
                        }}
                        .info-grid {{
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 20px;
                            margin-top: 30px;
                        }}
                        .info-item {{
                            background: rgba(255, 255, 255, 0.8);
                            padding: 20px;
                            border-radius: 12px;
                            border-left: 4px solid #ff0050;
                        }}
                        .feature-grid {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                            gap: 15px;
                            margin-top: 20px;
                        }}
                        .feature-item {{
                            background: linear-gradient(135deg, #ff0050, #00f2ea);
                            color: white;
                            padding: 15px;
                            border-radius: 10px;
                            text-align: center;
                            box-shadow: 0 5px 15px rgba(255, 0, 80, 0.3);
                        }}
                        .tiktok-logo {{
                            color: #ff0050;
                            font-size: 1.5em;
                            animation: pulse 1.5s ease-in-out infinite;
                        }}
                        @keyframes pulse {{
                            0% {{ transform: scale(1); }}
                            50% {{ transform: scale(1.1); }}
                            100% {{ transform: scale(1); }}
                        }}
                        .footer {{
                            text-align: center;
                            margin-top: 40px;
                            padding-top: 20px;
                            border-top: 1px solid #ddd;
                            color: #636e72;
                        }}
                        h3 {{
                            color: #2d3436;
                            border-bottom: 2px solid #ff0050;
                            padding-bottom: 10px;
                        }}
                        .emoji {{
                            font-size: 1.3em;
                            margin-right: 8px;
                        }}
                        .links a {{
                            display: inline-block;
                            margin: 5px 10px;
                            padding: 10px 20px;
                            background: #ff0050;
                            color: white;
                            text-decoration: none;
                            border-radius: 25px;
                            transition: all 0.3s;
                        }}
                        .links a:hover {{
                            background: #00f2ea;
                            transform: translateY(-2px);
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🎵 {BOT_NAME}</h1>
                        <div class="tagline">Download TikTok Videos Without Watermark - Fast & Free!</div>
                        
                        <div class="status-card">
                            <div class="status-badge">
                                <span class="tiktok-logo">⚡</span> {bot_status} <span class="tiktok-logo">⚡</span>
                            </div>
                            <p><strong>Last Updated:</strong> {current_time}</p>
                            <p><strong>Server:</strong> Render • <strong>Port:</strong> {PORT}</p>
                            <p><strong>Bot Username:</strong> @{BOT_USERNAME}</p>
                            <p><strong>Access URL:</strong> http://localhost:{PORT}/</p>
                        </div>
                        
                        <div class="info-grid">
                            <div class="info-item">
                                <h3>🤖 Bot Identity</h3>
                                <p><strong>Name:</strong> {BOT_NAME}</p>
                                <p><strong>Username:</strong> @{BOT_USERNAME}</p>
                                <p><strong>Owner:</strong> @{OWNER_USERNAME}</p>
                                <p><strong>Platform:</strong> Telegram</p>
                                <p><strong>Framework:</strong> Pyrogram</p>
                            </div>
                            
                            <div class="info-item">
                                <h3>🔧 Technical Info</h3>
                                <p><strong>API ID:</strong> {API_ID if API_ID else 'Configured'}</p>
                                <p><strong>API Hash:</strong> {'*' * len(API_HASH) if API_HASH else 'Not set'}</p>
                                <p><strong>Bot Token:</strong> {BOT_TOKEN[:15] + '...' if BOT_TOKEN else 'Not set'}</p>
                                <p><strong>Port:</strong> {PORT}</p>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <h3>🚀 Core Features</h3>
                            <div class="feature-grid">
                                <div class="feature-item">
                                    <span class="emoji">📥</span> No Watermark Download
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">⚡</span> Fast Processing
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">🎵</span> Audio Extraction
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">📱</span> Mobile Optimized
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">🔗</span> Multiple Formats
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">🌐</span> Web Interface
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">📊</span> User Statistics
                                </div>
                                <div class="feature-item">
                                    <span class="emoji">🆓</span> Completely Free
                                </div>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <h3>🌟 Quick Links</h3>
                            <div class="links" style="text-align: center;">
                                <a href="https://t.me/{BOT_USERNAME}" target="_blank">🤖 Start Bot</a>
                                <a href="{SUPPORT_GROUP_URL}" target="_blank">👥 Support Group</a>
                                <a href="{SOURCE_CODE_URL}" target="_blank">💻 Source Code</a>
                                <a href="{WEBSITE_URL}" target="_blank">🌐 Website</a>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <h3>📋 How to Use</h3>
                            <ol style="line-height: 1.8;">
                                <li><strong>Find TikTok Video:</strong> Open TikTok app and find the video you want to download</li>
                                <li><strong>Copy Link:</strong> Tap "Share" and copy the video link</li>
                                <li><strong>Send to Website:</strong> Send the link to {WEBSITE_URL}</li>
                                <li><strong>Download:</strong> The Website will process and send you the video without watermark!</li>
                            </ol>
                        </div>
                        
                        <div class="footer">
                            <p>⚡ Powered by Pyrogram & TikTok Downloader API</p>
                            <p>🌐 Hosted on Render • 🕒 24/7 Uptime</p>
                            <p style="margin-top: 10px; font-size: 0.9em;">
                                "Download TikTok videos effortlessly - No watermark, just pure content! 🎵"
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                logger.debug("📝 Sending HTML response to client")
                self.wfile.write(html_content.encode('utf-8'))
                logger.success("✅ Main status page sent successfully")
                
            else:
                logger.warning(f"❌ Unknown path requested: {self.path}")
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"404 - Page not found")
                logger.info("📤 Sent 404 response for unknown path")
                
        except Exception as e:
            logger.error(f"💥 Error handling request {self.path}: {e}")
            try:
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"500 - Internal Server Error")
                logger.error("📤 Sent 500 error response")
            except Exception as send_error:
                logger.critical(f"🚨 Failed to send error response: {send_error}")

    def is_bot_running(self):
        """Check if the bot is running."""
        try:
            logger.debug("🔍 Checking if bot is running...")
            # Add actual bot status check logic here if needed
            return True
        except Exception as e:
            logger.error(f"❌ Error checking bot status: {e}")
            return False

    def log_message(self, format, *args):
        """Override to use loguru instead of default logging."""
        logger.info(f"🌐 HTTP {self.command} {self.path} - {self.client_address[0]} - {args[0] if args else ''}")

def run_health_server():
    """Run a simple HTTP server to respond to health checks and display bot info."""
    try:
        logger.info(f"🚀 Starting health server on port {PORT}...")
        logger.debug(f"🔧 Server configuration: 0.0.0.0:{PORT}")
        
        server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
        logger.success(f"🌐 Health server started successfully on port {PORT}")
        logger.info(f"🎵 {BOT_NAME} status page: http://0.0.0.0:{PORT}/")
        logger.info(f"🎵 External URL: http://localhost:{PORT}/")
        logger.info(f"🏓 Health check endpoint: http://0.0.0.0:{PORT}/ping")
        
        logger.info("🔄 Starting server forever loop...")
        server.serve_forever()
        
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"💥 Port {PORT} is already in use! Please use a different port.")
        else:
            logger.error(f"💥 OSError starting health server: {e}")
        raise
    except Exception as e:
        logger.critical(f"💥 Failed to start health server: {e}")
        logger.exception("Full traceback:")
        raise

def start_keep_alive():
    """Start the keep-alive system with health server and periodic pings."""
    try:
        logger.info("🔗 Starting keep-alive system...")
        
        # Start health server in a separate thread
        logger.debug("🧵 Creating health server thread...")
        health_thread = threading.Thread(target=run_health_server, daemon=True)
        health_thread.name = "HealthServerThread"
        
        logger.info("▶️ Starting health server thread...")
        health_thread.start()
        logger.success("✅ Health server thread started successfully")
        
        # Give the server a moment to start
        logger.debug("⏳ Waiting for health server to initialize...")
        time.sleep(2)
        
        # Periodic pings to keep the server alive
        logger.info("🔄 Starting periodic ping loop...")
        session = requests.Session()
        ping_count = 0
        
        while True:
            try:
                ping_count += 1
                logger.debug(f"🏓 Sending keep-alive ping #{ping_count}...")
                
                # Ping the local health endpoint
                response = session.get(f'http://localhost:{PORT}/ping', timeout=5)
                
                if response.status_code == 200:
                    logger.success(f"✅ Keep-alive ping #{ping_count} successful: {response.status_code}")
                else:
                    logger.warning(f"⚠️ Keep-alive ping #{ping_count} returned non-200 status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Keep-alive ping #{ping_count} timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"🔌 Keep-alive ping #{ping_count} connection error - server may not be ready")
            except Exception as e:
                logger.error(f"💥 Keep-alive ping #{ping_count} failed: {e}")
            
            logger.debug(f"💤 Sleeping for 300 seconds (5 minutes)...")
            time.sleep(300)  # Ping every 5 minutes
            
    except Exception as e:
        logger.critical(f"💥 Keep-alive system crashed: {e}")
        logger.exception("Full traceback:")
        raise

if __name__ == "__main__":
    logger.info("🔧 Running keep_alive.py as standalone script")
    start_keep_alive()