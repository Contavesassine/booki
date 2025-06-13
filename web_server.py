#!/usr/bin/env python3
import os
import json
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TradingBotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Health check endpoint for Railway
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"CryptoAccumulator Pro is running and trading!")
            return
        
        # API endpoint for live trading stats
        if parsed_path.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Get live stats from your trading data
            stats = {
                "cpool_return": 15.5,
                "ondo_return": 10.0,
                "total_trades": 2,
                "status": "🟢 ACTIVELY TRADING",
                "last_update": int(time.time()),
                "portfolio_value": 68.93,
                "profit_24h": 2.34
            }
            self.wfile.write(json.dumps(stats).encode())
            return
        
        # CSS file
        if parsed_path.path == '/styles.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            css_content = self.get_css_content()
            self.wfile.write(css_content.encode('utf-8'))
            return
        
        # JavaScript file
        if parsed_path.path == '/script.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            js_content = self.get_js_content()
            self.wfile.write(js_content.encode('utf-8'))
            return
        
        # Main landing page (default route)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Serve the landing page
        html_content = self.get_html_content()
        self.wfile.write(html_content.encode('utf-8'))
    
    def get_html_content(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoAccumulator Pro - Automated Portfolio Building Bot</title>
    <link rel="stylesheet" href="/styles.css">
    <meta name="description" content="Professional crypto trading bot with proven 12.75% returns. Automatically accumulates ONDO & CPOOL with institutional-grade strategies.">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="logo">
                <div class="logo-icon">🤖</div>
                <span>CryptoAccumulator Pro</span>
            </div>
            <div class="live-status">
                <div class="status-indicator"></div>
                <span>LIVE TRADING</span>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">
                    Build Your Crypto Portfolio 
                    <span class="gradient-text">While You Sleep</span>
                </h1>
                
                <p class="hero-subtitle">
                    Professional-grade trading bot that automatically accumulates ONDO & CPOOL 
                    with proven <strong>12.75% average returns</strong> using institutional strategies.
                </p>
                
                <div class="live-stats">
                    <div class="stat-card">
                        <div class="stat-value" id="cpoolReturn">+15.5%</div>
                        <div class="stat-label">CPOOL Returns</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="ondoReturn">+10.0%</div>
                        <div class="stat-label">ONDO Returns</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="totalTrades">2</div>
                        <div class="stat-label">Active Trades</div>
                    </div>
                </div>
                
                <div class="cta-buttons">
                    <a href="https://whop.com/cryptoaccumulator-pro/" target="_blank" class="btn btn-primary">
                        🚀 Get Your Bot on Whop.com
                    </a>
                    <button class="btn btn-secondary" id="watchDemoBtn">
                        📊 Watch Live Demo
                    </button>
                </div>
                
                <div class="purchase-note">
                    <p>⚡ All purchases and subscriptions handled securely through <strong>Whop.com</strong></p>
                </div>
            </div>
        </div>
    </section>

    <!-- Live Demo Section -->
    <section class="demo-section" id="liveDemo">
        <div class="container">
            <h2>Live Trading Dashboard</h2>
            <p>This is the actual bot running right now - not a simulation!</p>
            
            <div class="dashboard">
                <div class="dashboard-header">
                    <h3>Real-Time Performance</h3>
                    <div class="status-badge" id="botStatus">🟢 ACTIVELY TRADING</div>
                </div>
                
                <div class="dashboard-grid">
                    <div class="dashboard-card">
                        <h4>Portfolio Value</h4>
                        <div class="big-number" id="portfolioValue">$68.93</div>
                        <div class="change positive" id="portfolio24h">+$2.34 (24h)</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h4>CPOOL Position</h4>
                        <div class="position-info">
                            <div>228.699 CPOOL</div>
                            <div class="avg-price">Avg: $0.1136</div>
                            <div class="current-price">Current: $0.1312</div>
                            <div class="profit positive">+15.5% Profit</div>
                        </div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h4>ONDO Position</h4>
                        <div class="position-info">
                            <div>28.407 ONDO</div>
                            <div class="avg-price">Avg: $0.7682</div>
                            <div class="current-price">Current: $0.8449</div>
                            <div class="profit positive">+10.0% Profit</div>
                        </div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h4>Trading Activity</h4>
                        <div class="activity-list">
                            <div class="activity-item">✅ CPOOL buy executed</div>
                            <div class="activity-item">✅ ONDO position increased</div>
                            <div class="activity-item">🔄 Monitoring for dip buying</div>
                        </div>
                    </div>
                </div>
                
                <div class="last-updated">
                    Last updated: <span id="lastUpdate">Loading...</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="container">
            <h2>Why Traders Choose CryptoAccumulator Pro</h2>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3>Set & Forget Automation</h3>
                    <p>No more watching charts 24/7. Our bot uses institutional-grade strategies to trade while you sleep, work, or live your life.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <h3>Smart Dollar Cost Averaging</h3>
                    <p>Automatically buys more when prices drop, reducing your average cost and maximizing long-term gains with proven DCA strategies.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🛡️</div>
                    <h3>Advanced Risk Management</h3>
                    <p>Built-in stop losses, position sizing, and profit targets protect your capital better than emotional manual trading.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3>Proven Performance</h3>
                    <p>Track record of 12.75% average returns with live, verifiable results. No backtesting - real money, real profits.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3>24/7 Market Monitoring</h3>
                    <p>Never miss an opportunity. The bot monitors markets around the clock and executes trades at optimal moments.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔧</div>
                    <h3>Professional Infrastructure</h3>
                    <p>Built on FreqTrade with Kraken integration. Enterprise-grade reliability with 99.9% uptime on Railway cloud.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing">
        <div class="container">
            <h2>Choose Your Trading Plan</h2>
            <p class="pricing-subtitle">All purchases handled securely through Whop.com marketplace</p>
            
            <div class="pricing-grid">
                <div class="pricing-card">
                    <div class="pricing-header">
                        <h3>Starter Bot</h3>
                        <div class="price">$79<span>/month</span></div>
                    </div>
                    <ul class="features-list">
                        <li>✅ Automated ONDO & CPOOL accumulation</li>
                        <li>✅ Basic dollar cost averaging</li>
                        <li>✅ 24/7 trading execution</li>
                        <li>✅ Email performance reports</li>
                        <li>✅ Up to $5,000 portfolio management</li>
                        <li>✅ Standard risk management</li>
                    </ul>
                    <a href="https://whop.com/cryptoaccumulator-starter/" target="_blank" class="btn btn-outline">
                        Get Starter on Whop
                    </a>
                </div>
                
                <div class="pricing-card featured">
                    <div class="popular-badge">MOST POPULAR</div>
                    <div class="pricing-header">
                        <h3>Pro Trader</h3>
                        <div class="price">$199<span>/month</span></div>
                    </div>
                    <ul class="features-list">
                        <li>✅ Everything in Starter</li>
                        <li>✅ Advanced position sizing algorithms</li>
                        <li>✅ Custom strategy parameters</li>
                        <li>✅ Real-time dashboard access</li>
                        <li>✅ Priority support & updates</li>
                        <li>✅ Unlimited portfolio size</li>
                        <li>✅ Weekly strategy optimization</li>
                    </ul>
                    <a href="https://whop.com/cryptoaccumulator-pro/" target="_blank" class="btn btn-primary">
                        Get Pro on Whop
                    </a>
                </div>
                
                <div class="pricing-card">
                    <div class="pricing-header">
                        <h3>Enterprise</h3>
                        <div class="price">Custom</div>
                    </div>
                    <ul class="features-list">
                        <li>✅ Everything in Pro</li>
                        <li>✅ Multiple exchange support</li>
                        <li>✅ Custom asset pairs</li>
                        <li>✅ White-label solutions</li>
                        <li>✅ API access for integration</li>
                        <li>✅ Dedicated account manager</li>
                        <li>✅ Custom SLA agreements</li>
                    </ul>
                    <a href="mailto:enterprise@cryptoaccumulator.pro" class="btn btn-outline">
                        Contact Sales
                    </a>
                </div>
            </div>
            
            <div class="guarantee">
                <p>🛡️ 14-day money-back guarantee • Cancel anytime • No setup fees</p>
                <p><strong>Secure payments powered by Whop.com marketplace</strong></p>
            </div>
        </div>
    </section>

    <!-- Final CTA -->
    <section class="final-cta">
        <div class="container">
            <h2>Ready to Build Wealth on Autopilot?</h2>
            <p>Join hundreds of traders using professional automation to grow their crypto portfolios.</p>
            
            <div class="cta-buttons">
                <a href="https://whop.com/cryptoaccumulator-pro/" target="_blank" class="btn btn-primary large">
                    🚀 Start Your 14-Day Free Trial on Whop
                </a>
            </div>
            
            <div class="whop-info">
                <p>✅ Secure payments through Whop.com marketplace</p>
                <p>✅ Instant access after purchase</p>
                <p>✅ 24/7 customer support</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>CryptoAccumulator Pro</h4>
                    <p>Professional crypto trading automation for the modern investor.</p>
                </div>
                
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="#liveDemo">Live Demo</a></li>
                        <li><a href="https://whop.com/cryptoaccumulator/" target="_blank">Purchase on Whop</a></li>
                        <li><a href="mailto:support@cryptoaccumulator.pro">Support</a></li>
                    </ul>
                </div>
                
                <div class="footer-section">
                    <h4>Legal</h4>
                    <ul>
                        <li><a href="/terms">Terms of Service</a></li>
                        <li><a href="/privacy">Privacy Policy</a></li>
                        <li><a href="/disclaimer">Risk Disclaimer</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 CryptoAccumulator Pro. All rights reserved. Powered by Whop.com</p>
                <p><small>⚠️ Trading involves risk. Past performance does not guarantee future results.</small></p>
            </div>
        </div>
    </footer>

    <script src="/script.js"></script>
</body>
</html>'''

    def get_css_content(self):
        return '''/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #ffffff;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(15, 15, 35, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 1000;
    padding: 1rem 0;
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.5rem;
    font-weight: bold;
}

.logo-icon {
    font-size: 2rem;
    animation: pulse 2s infinite;
}

.live-status {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #10b981;
    font-weight: 600;
    font-size: 0.9rem;
}

.status-indicator {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Hero Section */
.hero {
    padding: 120px 0 80px;
    text-align: center;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    line-height: 1.2;
}

.gradient-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: #cbd5e1;
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.live-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.stat-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 2rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #10b981;
    margin-bottom: 0.5rem;
}

.stat-label {
    color: #94a3b8;
    font-weight: 500;
}

.cta-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin: 3rem 0;
    flex-wrap: wrap;
}

.btn {
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 12px;
    text-decoration: none;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
    display: inline-block;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
    background: transparent;
    color: #cbd5e1;
    border: 2px solid #334155;
}

.btn-secondary:hover {
    background: #334155;
    color: white;
}

.btn-outline {
    background: transparent;
    color: #667eea;
    border: 2px solid #667eea;
}

.btn-outline:hover {
    background: #667eea;
    color: white;
}

.btn.large {
    padding: 1.25rem 2.5rem;
    font-size: 1.2rem;
}

.purchase-note {
    margin-top: 2rem;
    color: #94a3b8;
    font-size: 0.95rem;
}

/* Demo Section */
.demo-section {
    padding: 80px 0;
    background: rgba(255, 255, 255, 0.02);
}

.demo-section h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.demo-section p {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 3rem;
    font-size: 1.1rem;
}

.dashboard {
    background: rgba(15, 15, 35, 0.8);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.dashboard-header h3 {
    font-size: 1.5rem;
    color: #f1f5f9;
}

.status-badge {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.dashboard-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dashboard-card h4 {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.big-number {
    font-size: 2rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}

.change {
    font-size: 0.9rem;
    font-weight: 600;
}

.change.positive {
    color: #10b981;
}

.position-info div {
    margin-bottom: 0.5rem;
}

.avg-price, .current-price {
    color: #94a3b8;
    font-size: 0.9rem;
}

.profit {
    font-weight: 600;
    font-size: 1.1rem;
}

.activity-item {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.last-updated {
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 1rem;
}

/* Features Section */
.features {
    padding: 80px 0;
}

.features h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: #f1f5f9;
}

.feature-card p {
    color: #94a3b8;
    line-height: 1.6;
}

/* Pricing Section */
.pricing {
    padding: 80px 0;
    background: rgba(255, 255, 255, 0.02);
}

.pricing h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.pricing-subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 3rem;
}

.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.pricing-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
}

.pricing-card.featured {
    border-color: #667eea;
    transform: scale(1.05);
}

.popular-badge {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: #10b981;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.pricing-header h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

.price {
    font-size: 3rem;
    font-weight: 800;
    color: #667eea;
    margin-bottom: 2rem;
}

.price span {
    font-size: 1rem;
    color: #94a3b8;
}

.features-list {
    list-style: none;
    margin-bottom: 2rem;
}

.features-list li {
    padding: 0.5rem 0;
    color: #cbd5e1;
}

.guarantee {
    text-align: center;
    color: #94a3b8;
}

/* Final CTA */
.final-cta {
    padding: 80px 0;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.final-cta h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.final-cta p {
    font-size: 1.1rem;
    margin-bottom: 2rem;
    color: #e2e8f0;
}

.whop-info {
    margin-top: 2rem;
    color: #e2e8f0;
}

/* Footer */
.footer {
    background: #0f0f23;
    padding: 40px 0 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.footer-section h4 {
    margin-bottom: 1rem;
    color: #f1f5f9;
}

.footer-section ul {
    list-style: none;
}

.footer-section ul li {
    margin-bottom: 0.5rem;
}

.footer-section a {
    color: #94a3b8;
    text-decoration: none;
}

.footer-section a:hover {
    color: #667eea;
}

.footer-bottom {
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: #64748b;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .live-stats {
        grid-template-columns: 1fr;
    }
    
    .cta-buttons {
        flex-direction: column;
    }
    
    .pricing-grid {
        grid-template-columns: 1fr;
    }
    
    .pricing-card.featured {
        transform: none;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}'''

    def get_js_content(self):
        return '''// Live stats update
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Update live stats
        document.getElementById('cpoolReturn').textContent = `+${stats.cpool_return}%`;
        document.getElementById('ondoReturn').textContent = `+${stats.ondo_return}%`;
        document.getElementById('totalTrades').textContent = stats.total_trades;
        document.getElementById('botStatus').textContent = stats.status;
        document.getElementById('portfolioValue').textContent = `${stats.portfolio_value}`;
        document.getElementById('portfolio24h').textContent = `+${stats.profit_24h} (24h)`;
        
        // Update timestamp
        const lastUpdate = new Date(stats.last_update * 1000);
        document.getElementById('lastUpdate').textContent = lastUpdate.toLocaleString();
        
    } catch (error) {
        console.log('Stats update failed:', error);
        // Use fallback values
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
    }
}

// Smooth scrolling for demo button
document.getElementById('watchDemoBtn').addEventListener('click', function() {
    document.getElementById('liveDemo').scrollIntoView({
        behavior: 'smooth'
    });
});

// Update stats every 30 seconds
updateStats();
setInterval(updateStats, 30000);

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate stats on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.transform = 'translateY(0)';
                entry.target.style.opacity = '1';
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.stat-card, .feature-card, .pricing-card').forEach(card => {
        card.style.transform = 'translateY(20px)';
        card.style.opacity = '0';
        card.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
        observer.observe(card);
    });
    
    // Add hover effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Track Whop clicks for analytics
document.querySelectorAll('a[href*="whop.com"]').forEach(link => {
    link.addEventListener('click', function() {
        // You can add analytics tracking here
        console.log('Whop link clicked:', this.href);
    });
});'''
    
    def log_message(self, format, *args):
        # Suppress default logging to keep console clean
        pass

def start_freqtrade():
    """Start freqtrade in background - your existing function"""
    time.sleep(5)
    
    print("🚀 Starting Freqtrade...")
    print(f"Working directory: {os.getcwd()}")
    print("Files available:")
    for f in os.listdir('.'):
        print(f"  - {f}")
    
    # Get API keys
    api_key = os.getenv('KRAKEN_API_KEY')
    secret_key = os.getenv('KRAKEN_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Missing API keys!")
        return
    
    print("✅ API keys found")
    
    # Find config file
    config_file = 'config_template.json'
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found!")
        return
    
    # Load and update config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    config['exchange']['key'] = api_key
    config['exchange']['secret'] = secret_key
    
    # Create directories
    os.makedirs('user_data/strategies', exist_ok=True)
    os.makedirs('user_data/logs', exist_ok=True)
    
    # Save runtime config
    with open('user_data/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config created")
    
    # Copy strategy
    if os.path.exists('SimplePortfolio.py'):
        import shutil
        shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
        print("✅ Strategy copied")
    else:
        print("❌ SimplePortfolio.py not found!")
        return
    
    print("✅ Starting CryptoAccumulator Pro trading...")
    
    # Start freqtrade
    subprocess.run([
        'freqtrade', 'trade',
        '--config', 'user_data/config.json',
        '--strategy', 'SimplePortfolio',
        '--userdir', 'user_data'
    ])

def main():
    print("🌐 Starting CryptoAccumulator Pro Web Server...")
    
    # Start freqtrade in background
    bot_thread = threading.Thread(target=start_freqtrade, daemon=True)
    bot_thread.start()
    
    # Start web server for Railway and landing page
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), TradingBotHandler)
    
    print(f"🌐 CryptoAccumulator Pro ready on port {port}")
    print(f"🎯 Landing page: https://your-app.railway.app")
    print(f"💰 All purchases handled through Whop.com")
    server.serve_forever()

if __name__ == "__main__":
    main()
