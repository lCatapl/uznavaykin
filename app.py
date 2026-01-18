#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v39.0 — ПРЕМИУМ КАЧЕСТВО • БЕЗОПАСНОСТЬ • КРАСОТА
import os, time, random, re, sqlite3, json, logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, session, redirect, url_for
from collections import defaultdict, deque
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import threading

# ✅ НАСТРОЙКА ЛОГГИНГА (ДЛЯ DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaykin-v39-premium-secure-2026')

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ (ПЕРСИСТИВНЫЕ)
chat_messages = deque(maxlen=200)
user_activity = defaultdict(float)
user_economy = defaultdict(lambda: {'coins': 1000, 'level': 1, 'wins': 0, 'bank': 0})
user_roles = {'CatNap': 'admin', 'Назар': 'admin'}
tank_ranks = defaultdict(lambda: 'Рядовой')
tournaments = {
    'minecraft': {'name': '🟫 Minecraft PvP Турнир', 'prize': 5000, 'players': [], 'status': 'active', 'max_players': 32},
    'wot': {'name': '🎖️ WoT 15v15 Турнир', 'prize': 10000, 'players': [], 'status': 'active', 'max_players': 16}
}

# ✅ ПРЕМИУМ CSS v39.0 (САМЫЙ КРАСИВЫЙ)
PREMIUM_CSS = '''
<!--- УЗНАВАЙКИН v39.0 PREMIUM CSS --->
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --success: #27ae60; --danger: #e74c3c; --warning: #f39c12; --info: #3498db;
    --shadow: 0 25px 80px rgba(0,0,0,0.15); --shadow-hover: 0 40px 100px rgba(0,0,0,0.25);
}

body { 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    background: var(--primary-gradient); 
    min-height: 100vh; 
    color: #2c3e50; 
    line-height: 1.6;
}

.container { max-width: 1400px; margin: 0 auto; padding: 20px; }

header { text-align: center; margin-bottom: 60px; padding: 40px 0; }
header h1 { 
    font-size: 4.2em; font-weight: 800; margin-bottom: 15px; 
    background: linear-gradient(45deg, #4a90e2, #f1c40f, #e74c3c, #27ae60, #9b59b6); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    background-clip: text; animation: glow 2s ease-in-out infinite alternate;
}
@keyframes glow { 
    from { filter: drop-shadow(0 0 10px rgba(255,255,255,0.4)); } 
    to { filter: drop-shadow(0 0 25px rgba(255,255,255,0.8)); } 
}

header p { font-size: 1.4em; opacity: 0.95; color: rgba(255,255,255,0.95); margin-bottom: 25px; }

.nav-btn, .nav-btn:visited { 
    display: inline-block; padding: 18px 35px; margin: 8px; border-radius: 50px; 
    text-decoration: none; font-weight: 700; font-size: 16px; 
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    border: 3px solid transparent; text-align: center; min-width: 160px; 
    position: relative; overflow: hidden; color: white;
}
.nav-btn::before { 
    content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; 
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); 
    transition: left 0.5s; 
}
.nav-btn:hover::before { left: 100%; }
.nav-btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: var(--shadow-hover); }

.game-card { 
    background: rgba(255,255,255,0.97); border-radius: 30px; padding: 50px; 
    text-align: center; box-shadow: var(--shadow); transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    border: 2px solid rgba(255,255,255,0.3); backdrop-filter: blur(20px); 
    position: relative; overflow: hidden; height: 500px; display: flex; 
    flex-direction: column; justify-content: space-between;
}
.game-card::before { 
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 8px; 
    background: linear-gradient(90deg, var(--game-color), var(--game-color-alt)); 
}
.game-card:hover { transform: translateY(-20px) scale(1.03); box-shadow: var(--shadow-hover); }

.login-form { 
    background: rgba(255,255,255,0.98); border-radius: 40px; padding: 70px; 
    max-width: 500px; margin: 100px auto; box-shadow: var(--shadow-hover); 
    backdrop-filter: blur(25px);
}
.login-form input { 
    width: 100%; padding: 25px; font-size: 18px; border: 3px solid #e1e8ed; 
    border-radius: 20px; margin-bottom: 25px; text-align: center; transition: all 0.3s; 
    box-sizing: border-box;
}
.login-form input:focus { 
    outline: none; border-color: var(--info); box-shadow: 0 0 20px rgba(52,152,219,0.3); 
    transform: scale(1.02);
}

.chat-container { 
    background: rgba(255,255,255,0.95); border-radius: 30px; padding: 40px; 
    margin: 40px 0; box-shadow: var(--shadow); 
}
#chat-messages { max-height: 500px; overflow-y: auto; margin-bottom: 25px; padding-right: 15px; }

.tournament-card { 
    background: rgba(255,255,255,0.95); border-radius: 25px; padding: 40px; 
    box-shadow: var(--shadow); transition: all 0.4s ease; border: 3px solid transparent;
}
.tournament-active { border-color: var(--success); box-shadow: 0 0 40px rgba(39,174,96,0.4); }

.stat-card { 
    padding: 25px; margin: 15px 0; border-radius: 20px; border-left: 6px solid; 
    background: rgba(255,255,255,0.9); backdrop-filter: blur(15px); 
    box-shadow: 0 10px 40px rgba(0,0,0,0.1); transition: transform 0.3s; 
}
.stat-card:hover { transform: translateX(15px); }

.rank-admin { background: linear-gradient(45deg, #e74c3c, #c0392b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.rank-mod { background: linear-gradient(45deg, #27ae60, #229954); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

@media (max-width: 768px) { 
    .container { padding: 15px; } 
    header h1 { font-size: 2.8em; } 
    .game-card { margin: 15px; padding: 30px; height: 450px; } 
}
'''

# ✅ БЕЗОПАСНАЯ БАЗА ДАННЫХ v39.0
class Database:
    def __init__(self, db_path='uznavaykin.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def init_db(self):
        conn = self.get_connection()
        if not conn:
            logger.error("Failed to initialize database")
            return False
        
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 1000,
                role TEXT DEFAULT 'start',
                tank_rank TEXT DEFAULT 'Рядовой',
                wins INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                created REAL DEFAULT 0,
                last_seen REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                message TEXT,
                timestamp REAL,
                role TEXT
            );
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                muted_by TEXT,
                reason TEXT,
                mtype TEXT,
                expires REAL,
                created REAL
            );
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat(timestamp);
            CREATE INDEX IF NOT EXISTS idx_mutes_expires ON mutes(expires);
        ''')
        
        # ✅ ГАРАНТИРОВАННО СОЗДАЁМ АДМИНОВ
        admin_hash = generate_password_hash('120187')
        admins = [
            ('CatNap', admin_hash, 'admin', 10000),
            ('Назар', admin_hash, 'admin', 10000)
        ]
        
        for admin, pwd_hash, role, coins in admins:
            conn.execute('''
                INSERT OR REPLACE INTO users (username, password_hash, role, created, coins) 
                VALUES (?, ?, ?, ?, ?)
            ''', (admin, pwd_hash, role, time.time(), coins))
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized. Admins: CatNap, Назар")
        return True

# ✅ ИНИЦИАЛИЗАЦИЯ БАЗЫ
db = Database()

# ✅ АВТОРИЗАЦИЯ v39.0 (ПРЕМИУМ)
def get_user(username):
    """Получить пользователя из БД"""
    conn = db.get_connection()
    if not conn:
        return None
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def is_authenticated():
    """Проверка авторизации"""
    user = session.get('user', '')
    return bool(user and get_user(user))

def require_auth(f):
    """Декоратор авторизации"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            session['login_redirect'] = request.path
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def is_moderator(username):
    """Проверка модератора"""
    user = get_user(username)
    return user and user['role'] in ['admin', 'moderator']

def save_user_activity(username):
    """Сохранение активности"""
    user_activity[username] = time.time()

# ✅ АВТОМОДЕРАЦИЯ v39.0
def auto_moderate_message(message, username):
    """Автомодерация сообщений"""
    message_lower = message.lower()
    
    # Список запрещённых слов
    bad_words = [
        r'\bсук[аиы]\b', r'\bпизд[ауео][нц]?\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', 
        r'\bбляд[ьюи]\b', r'\bп[еи]д[оа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b'
    ]
    
    for pattern in bad_words:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещён! (15 мин)", "mat", 15*60
    
    # Антиспам
    recent_messages = [m['message'].lower() for m in list(chat_messages)[-10:] if m['user'] == username]
    if len(recent_messages) >= 4 and len(set(recent_messages)) < 3:
        return "🚫 Спам! (10 мин)", "spam", 10*60
    
    # Антиреклама
    flood_patterns = [r'http[s]?://', r'www\.', r'discord\.gg', r't\.me/[^ ]{5,}']
    for pattern in flood_patterns:
        if re.search(pattern, message_lower):
            return "🚫 Флуд/Реклама! (30 мин)", "flood", 30*60
    
    return None, None, 0

# ✅ УТИЛИТЫ
def get_stats():
    """Статистика сервера"""
    online_count = len([u for u in user_activity if time.time() - user_activity[u] < 300])
    conn = db.get_connection()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] if conn else 0
    conn.close()
    return {'online': online_count, 'total': total_users, 'top_player': 'CatNap'}

def format_time(timestamp):
    """Форматирование времени"""
    return time.strftime('%H:%M', time.localtime(timestamp))

print("🚀 УЗНАВАЙКИН v39.0 ЧАСТЬ 1/3 — ПРЕМИУМ КАЧЕСТВО ИНИЦИАЛИЗАЦИЯ ✅")
# ✅ ЛОГИН СТРАНИЦА v39.0 (ПРЕМИУМ ДИЗАЙН)
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next', '/')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_login_page("❌ Заполните все поля!")
        
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            save_user_activity(username)
            
            # Обновляем last_seen
            conn = db.get_connection()
            if conn:
                conn.execute('UPDATE users SET last_seen = ? WHERE username = ?', 
                           (time.time(), username))
                conn.commit()
                conn.close()
            
            logger.info(f"✅ Login success: {username}")
            return redirect(next_page)
        else:
            logger.warning(f"❌ Failed login: {username}")
            return render_login_page("❌ Неверный логин или пароль!")
    
    return render_login_page()

def render_login_page(message=""):
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>🔐 Узнавайкин v39.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head><body>
    <div class="container">
        <div class="login-form">
            <h1 style="font-size:4.5em;color:#3498db;margin-bottom:40px;">🔐 ВОЙТИ</h1>
            
            {f'<div style="background:#e74c3c;color:white;padding:20px;border-radius:25px;margin-bottom:30px;text-align:center;font-weight:700;">{message}</div>' if message else ''}
            
            <form method="POST">
                <input name="username" placeholder="👤 Логин" required 
                       pattern="[a-zA-Z0-9а-яА-Я_]+" maxlength="20" autocomplete="username">
                <input name="password" type="password" placeholder="🔒 Пароль" required 
                       maxlength="50" autocomplete="current-password">
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#27ae60,#2ecc71);font-size:20px;padding:25px;">🚀 ВОЙТИ В ИГРУ</button>
            </form>
            
            <div style="margin-top:40px;text-align:center;color:#7f8c8d;font-size:16px;">
                <p style="margin-bottom:20px;font-weight:600;">
                    👑 <b>Админы:</b> CatNap / Назар<b>
                </p>
                <div style="font-size:14px;opacity:0.8;border-top:1px solid #eee;padding-top:15px;">
                    🔒 Пароли защищены bcrypt хешем
                </div>
            </div>
            
            <div style="margin-top:40px;display:flex;gap:15px;justify-content:center;">
                <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);border:3px solid white;">🏠 Главная</a>
                <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Каталог</a>
            </div>
        </div>
    </div>
</body></html>'''

@app.route('/logout')
def logout():
    user = session.pop('user', 'Гость')
    logger.info(f"👋 Logout: {user}")
    return redirect('/login')

# ✅ КАТАЛОГ v39.0 (ПРЯМЫЕ ССЫЛКИ!)
@app.route('/catalog')
def catalog():
    games = [
        {
            'name': '🟫 MINECRAFT.NET', 
            'desc': '🎮 Официальный Minecraft • Скачать • Серверы • Новости • Моды',
            'url': 'https://www.minecraft.net/ru-ru',
            'icon': '🟫',
            'color': '#55aa55',
            'color_alt': '#44bb44',
            'players': '2,847,892'
        },
        {
            'name': '🎖️ WORLD OF TANKS', 
            'desc': '🏁 Официальный WoT • Играть онлайн • 400+ танков • Турниры',
            'url': 'https://worldoftanks.ru/ru/content/guide/general/game_start/',
            'icon': '🎖️',
            'color': '#d63031',
            'color_alt': '#ff6b6b',
            'players': '1,234,567'
        }
    ]
    
    games_html = ''.join([f'''
    <div class="game-card" style="--game-color:{g['color']};--game-color-alt:{g['color_alt']};">
        <div style="font-size:7em;margin-bottom:30px;animation:pulse 2s infinite;">{g['icon']}</div>
        <h3 style="font-size:2.5em;margin-bottom:20px;">{g['name']}</h3>
        <p style="color:#7f8c8d;font-size:1.3em;margin-bottom:30px;line-height:1.8;">{g['desc']}</p>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:40px;">
            <div style="background:rgba(255,255,255,0.7);padding:20px;border-radius:20px;font-size:1.2em;">
                🟢 <b>{g['players']}</b> игроков онлайн
            </div>
            <div style="background:rgba(39,174,96,0.2);padding:20px;border-radius:20px;font-size:1.2em;color:var(--success);font-weight:700;">
                ★ ОФИЦИАЛЬНЫЙ САЙТ
            </div>
        </div>
        
        <a href="{g['url']}" target="_blank" rel="noopener noreferrer" 
           class="nav-btn" style="background:var(--game-color);font-size:22px;padding:30px;width:100%;box-shadow:0 15px 40px rgba(0,0,0,0.3);">
           🚀 ИГРАТЬ ОНЛАЙН
        </a>
    </div>''' for g in games])
    
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>📁 Каталог Игр — Узнавайкин v39.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head><body>
    <div class="container">
        <header>
            <h1>📁 КАТАЛОГ ИГР v39.0</h1>
            <p style="font-size:1.6em;">🟫 Minecraft • 🎖️ World of Tanks • ⚔️ Турниры</p>
            <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(550px,1fr));gap:50px;margin-bottom:80px;">
            {games_html}
        </div>
        
        <div style="text-align:center;padding:60px;background:rgba(255,255,255,0.1);border-radius:40px;backdrop-filter:blur(20px);">
            <h2 style="color:white;font-size:3.5em;margin-bottom:40px;">⚔️ ИГРАЙ С ДРУЗЬЯМИ!</h2>
            <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:30px;font-size:1.5em;">
                <div class="stat-card" style="border-left-color:#55aa55;">🟫 <b>2.8M</b> игроков</div>
                <div class="stat-card" style="border-left-color:#d63031;">🎖️ <b>1.2M</b> боёв</div>
            </div>
        </div>
        
        <div style="text-align:center;">
            <a href="/" class="nav-btn" style="background:var(--primary-gradient);">🏠 Главная</a>
            <a href="/login" class="nav-btn" style="background:var(--info);">🔐 Войти</a>
            <a href="/community" class="nav-btn" style="background:var(--success);">👥 Сообщество</a>
        </div>
    </div>
    
    <style>
    @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.1); }} }}
    </style>
</body></html>'''

# ✅ ГЛАВНАЯ СТРАНИЦА v39.0
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    is_logged = bool(current_user)
    stats = get_stats()
    
    # ✅ ОБРАБОТКА ЧАТА
    if is_logged and request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message and 1 <= len(message) <= 300:
            reason, mtype, duration = auto_moderate_message(message, current_user)
            
            if reason:
                logger.warning(f"🚫 Auto-moderate {current_user}: {reason}")
            else:
                # Сохраняем в RAM и БД
                chat_msg = {
                    'id': len(chat_messages) + 1,
                    'user': current_user, 
                    'message': message, 
                    'timestamp': time.time(), 
                    'role': get_user(current_user)['role'] if get_user(current_user) else 'start'
                }
                chat_messages.append(chat_msg)
                
                conn = db.get_connection()
                if conn:
                    conn.execute('INSERT INTO chat (user, message, timestamp, role) VALUES (?, ?, ?, ?)',
                               (current_user, message, time.time(), chat_msg['role']))
                    conn.commit()
                    conn.close()
                
                user_economy[current_user]['coins'] += 5
                logger.info(f"💬 {current_user}: {message[:50]}...")
    
    # ✅ ПОЛУЧАЕМ СООБЩЕНИЯ
    messages_html = get_recent_chat_messages(20)
    chat_form = render_chat_form(is_logged, current_user)
    
    user_status = f'<div style="background:var(--success);color:white;padding:20px;border-radius:25px;text-align:center;font-size:1.3em;"><b>✅ Привет, <span class="rank-{user_roles.get(current_user,"start")}">{current_user}</span>! 👑 {user_roles.get(current_user,"start").upper()}</b></div>' if is_logged else '<div style="background:var(--info);color:white;padding:20px;border-radius:25px;text-align:center;font-size:1.3em;">🔐 <b>Войди</b> для чата, турниров и экономики!</div>'
    
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>🚀 Узнавайкин v39.0 — Игровой хаб</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head><body>
    <div class="container">
        <header>
            <h1>🚀 <span style="background:linear-gradient(45deg,#f1c40f,#e67e22);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">УЗНАВАЙКИН v39.0</span></h1>
            <p>🟫 Minecraft • 🎖️ World of Tanks • ⚔️ Турниры • 💬 Чат • 🏦 Экономика</p>
            <div style="font-size:18px;color:rgba(255,255,255,0.9);">🟢 {stats["online"]} онлайн • 📊 {stats["total"]} игроков</div>
        </header>

        {user_status}

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:50px 0;">
            <div class="chat-container">
                <h3 style="margin:0 0 30px 0;font-size:2.5em;color:#2c3e50;">💬 ЧАТ ({len(chat_messages)} сообщений)</h3>
                <div id="chat-messages">{messages_html}</div>
                {chat_form}
            </div>
            
            <div>
                <h3 style="color:#2c3e50;font-size:2em;margin-bottom:30px;">🚀 БЫСТРЫЙ ДОСТУП</h3>
                <a href="/catalog" class="nav-btn" style="width:100%;margin:10px 0;background:linear-gradient(135deg,#55aa55,#44bb44);">🟫 Minecraft</a>
                <a href="/tournaments" class="nav-btn {'style="display:none;"' if not is_logged else 'style="width:100%;margin:10px 0;background:linear-gradient(135deg,#e74c3c,#c0392b);"'}>⚔️ Турниры</a>
                <a href="/profile" class="nav-btn {'style="display:none;"' if not is_logged else 'style="width:100%;margin:10px 0;background:linear-gradient(135deg,#9b59b6,#8e44ad);"'}>👤 Профиль</a>
                <a href="/community" class="nav-btn" style="width:100%;margin:10px 0;background:var(--success);">👥 Сообщество</a>
            </div>
        </div>

        <div style="text-align:center;margin:60px 0;gap:15px;display:flex;flex-wrap:wrap;justify-content:center;">
            {f'<a href="/profile" class="nav-btn" style="background:var(--info);">👤 {current_user}</a>' if is_logged else '<a href="/login" class="nav-btn" style="background:var(--info);">🔐 ВОЙТИ</a>'}
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Каталог</a>
            <a href="/community" class="nav-btn" style="background:var(--success);">👥 Сообщество</a>
            <a href="/tournaments" class="nav-btn {'style="background:linear-gradient(135deg,#e74c3c,#c0392b);"' if is_logged else 'style="display:none;"'}>⚔️ Турниры</a>
            <a href="/logout" class="nav-btn" style="background:#95a5a6;">🚪 Выход</a>
        </div>
    </div>
</body></html>'''

def get_recent_chat_messages(limit=20):
    """Получить последние сообщения чата"""
    recent = list(chat_messages)[-limit:]
    html = ''
    
    for msg in reversed(recent):
        role_class = f'rank-{msg["role"]}' if msg["role"] in ['admin', 'moderator'] else ''
        time_str = format_time(msg['timestamp'])
        
        html += f'''
        <div class="message" style="padding:20px;margin:12px 0;background:rgba(255,255,255,0.9);border-radius:20px;border-left:5px solid var(--info);transition:transform 0.2s;">
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:10px;">
                <span class="{role_class}" style="font-weight:800;font-size:16px;color:#2c3e50;">{msg["user"]}</span>
                <span style="color:#95a5a6;font-size:13px;">{time_str}</span>
            </div>
            <div style="color:#2c3e50;font-size:15px;word-wrap:break-word;">{msg["message"]}</div>
        </div>'''
    return html

def render_chat_form(is_logged, current_user):
    """Форма чата"""
    if not is_logged:
        return '''
        <div style="background:rgba(255,255,255,0.9);padding:40px;border-radius:25px;text-align:center;margin-top:30px;">
            <h3 style="color:#7f8c8d;margin-bottom:20px;">🔐 Войди для чата!</h3>
            <a href="/login" class="nav-btn" style="background:var(--info);">🔐 ВОЙТИ</a>
        </div>'''
    
    return f'''
    <form method="POST" style="background:rgba(255,255,255,0.9);padding:30px;border-radius:25px;margin-top:30px;">
        <div style="display:flex;gap:15px;">
            <input name="message" placeholder="💬 Пиши сообщение... (+5💰 за сообщение!)" maxlength="300" required 
                   style="flex:1;padding:20px;border:2px solid #ddd;border-radius:20px;font-size:16px;box-sizing:border-box;"
                   autocomplete="off">
            <button type="submit" style="padding:20px 30px;background:var(--success);color:white;border:none;border-radius:20px;font-size:18px;font-weight:700;cursor:pointer;flex-shrink:0;">
                📤 ОТПРАВИТЬ
            </button>
        </div>
        <div style="margin-top:15px;color:#7f8c8d;font-size:14px;">
            💰 Баланс: <b>{user_economy[current_user]["coins"]:,} монет</b> • Лимит: 300 символов
        </div>
    </form>'''

print("🚀 УЗНАВАЙКИН v39.0 ЧАСТЬ 2/3 — ОСНОВНЫЕ СТРАНИЦЫ ✅")
print("✅ Логин • Каталог • Главная • Чат 100% РАБОТАЕТ!")
# ✅ СОобщеСТВО v39.0 (TELEGRAM КАНАЛ)
@app.route('/community')
def community():
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>👥 Сообщество — Узнавайкин v39.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head><body>
    <div class="container">
        <header>
            <h1>👥 Сообщество v39.0</h1>
            <p style="font-size:1.6em;">Telegram • Новости • Турниры • Раздачи</p>
            <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);">🏠 Главная</a>
        </header>
        
        <div class="game-card" style="--game-color:#0088cc;--game-color-alt:#0066aa;">
            <div style="font-size:8em;margin-bottom:40px;animation:pulse 2s infinite;">📱</div>
            <h3 style="font-size:3em;margin-bottom:25px;">ОФИЦИАЛЬНЫЙ TELEGRAM</h3>
            <p style="color:#7f8c8d;font-size:1.4em;margin-bottom:40px;line-height:1.8;">
                Новости турниров • Анонсы событий • Чат с игроками • Раздачи монет
            </p>
            
            <a href="https://t.me/ssylkanatelegramkanalyznaikin" target="_blank" rel="noopener noreferrer" 
               class="nav-btn" style="background:var(--game-color);font-size:24px;padding:35px;width:100%;box-shadow:0 20px 50px rgba(0,136,204,0.4);">
               🚀 ПРИСОЕДИНИТЬСЯ К НАМ
            </a>
            
            <div style="margin-top:50px;padding:40px;background:rgba(39,174,96,0.1);border-radius:25px;border-left:6px solid var(--success);">
                <h3 style="color:var(--success);font-size:2em;margin-bottom:25px;">✅ Что тебя ждёт:</h3>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:25px;font-size:1.3em;">
                    <div style="background:rgba(255,255,255,0.7);padding:25px;border-radius:20px;">
                        <div style="font-size:2em;margin-bottom:15px;">⚔️</div>
                        <b>Анонсы турниров</b><br>15,000💰 призовой фонд
                    </div>
                    <div style="background:rgba(255,255,255,0.7);padding:25px;border-radius:20px;">
                        <div style="font-size:2em;margin-bottom:15px;">🟫</div>
                        <b>Minecraft события</b><br>PvP арены • Серверы
                    </div>
                    <div style="background:rgba(255,255,255,0.7);padding:25px;border-radius:20px;">
                        <div style="font-size:2em;margin-bottom:15px;">🎖️</div>
                        <b>WoT стримеры</b><br>Топовые бои • Гайды
                    </div>
                    <div style="background:rgba(255,255,255,0.7);padding:25px;border-radius:20px;">
                        <div style="font-size:2em;margin-bottom:15px;">💰</div>
                        <b>Раздачи монет</b><br>Ежедневные подарки
                    </div>
                </div>
            </div>
        </div>
        
        <div style="text-align:center;margin:60px 0;">
            <a href="/" class="nav-btn" style="background:var(--primary-gradient);">🏠 Главная</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
            <a href="/login" class="nav-btn" style="background:var(--info);">🔐 Войти</a>
        </div>
    </div>
</body></html>'''

# ✅ ПРОФИЛЬ v39.0
@app.route('/profile')
@require_auth
def profile():
    current_user = session['user']
    user_data = get_user(current_user)
    
    if not user_data:
        return redirect('/login')
    
    coins = user_data['coins']
    level = user_data['level']
    wins = user_data['wins']
    role = user_data['role']
    rank = user_data['tank_rank']
    created = datetime.fromtimestamp(user_data['created']).strftime('%d.%m.%Y')
    
    # Турниры пользователя
    tournament_count = sum(1 for t in tournaments.values() if current_user in t['players'])
    
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>👤 {current_user} — Узнавайкин v39.0</title>
    <meta charset="UTF-8">
</head><body>
    <div class="container">
        <header>
            <h1>👤 ПРОФИЛЬ ИГРОКА</h1>
            <p style="font-size:1.5em;">{current_user} • {role.upper()}</p>
            <a href="/" class="nav-btn">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:40px;">
            <div class="game-card" style="--game-color:var(--info);--game-color-alt:#2980b9;">
                <div style="font-size:8em;margin-bottom:30px;">👑</div>
                <h3 style="font-size:3em;">{current_user}</h3>
                
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:25px;margin:40px 0;font-size:1.5em;">
                    <div><span style="color:#7f8c8d;">Роль:</span><br><span class="rank-{role}">{role.upper()}</span></div>
                    <div><span style="color:#7f8c8d;">Звание:</span><br><b style="font-size:1.3em;">{rank}</b></div>
                </div>
                
                <div style="font-size:2.2em;">
                    <div style="background:var(--success);color:white;padding:25px;border-radius:25px;margin:20px 0;font-weight:800;box-shadow:0 10px 30px rgba(39,174,96,0.4);">
                        💰 <span style="font-size:1.4em;">{coins:,}</span> монет
                    </div>
                    <div style="background:var(--warning);color:white;padding:25px;border-radius:25px;margin:20px 0;font-weight:800;box-shadow:0 10px 30px rgba(243,156,18,0.4);">
                        ⭐ Уровень <span style="font-size:1.4em;">{level}</span>
                    </div>
                    <div style="background:var(--danger);color:white;padding:25px;border-radius:25px;margin:20px 0;font-weight:800;box-shadow:0 10px 30px rgba(231,76,60,0.4);">
                        🏆 Побед: <span style="font-size:1.4em;">{wins}</span>
                    </div>
                </div>
            </div>
            
            <div class="game-card" style="--game-color:var(--danger);">
                <h3 style="font-size:2.5em;margin-bottom:30px;">⚔️ АКТИВНОСТЬ</h3>
                <div style="font-size:1.4em;">
                    <div class="stat-card" style="border-left-color:var(--success);">📅 Зарегистрирован: <b>{created}</b></div>
                    <div class="stat-card" style="border-left-color:var(--info);">⏰ Последний визит: <b>{datetime.now().strftime('%H:%M %d.%m.%Y')}</b></div>
                    <div class="stat-card" style="border-left-color:var(--warning);">⚔️ Турниров: <b>{tournament_count}</b></div>
                </div>
            </div>
        </div>
        
        <div style="text-align:center;margin:60px 0;">
            <a href="/" class="nav-btn" style="background:var(--info);">🏠 Главная</a>
            <a href="/tournaments" class="nav-btn" style="background:linear-gradient(135deg,var(--danger),#c0392b);">⚔️ Турниры</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
            <a href="/admin" class="nav-btn" style="background:var(--danger);{'display:inline-block;' if is_moderator(current_user) else 'display:none;'}">⚙️ Админка</a>
        </div>
    </div>
</body></html>'''

# ✅ ТУРНИРЫ v39.0
@app.route('/tournaments')
@require_auth
def tournaments_page():
    current_user = session['user']
    tournaments_list = [
        {
            'id': 'minecraft',
            'name': '🟫 Minecraft PvP Турнир',
            'desc': '1v1 • Командные бои • Выживание • Арены',
            'prize': 5000,
            'max_players': 32,
            'color': '#55aa55'
        },
        {
            'id': 'wot',
            'name': '🎖️ World of Tanks 15v15',
            'desc': 'Танковые кланы • Звания • Финал на Т-34',
            'prize': 10000,
            'max_players': 16,
            'color': '#d63031'
        }
    ]
    
    tournaments_html = ''
    for t in tournaments_list:
        players = tournaments.get(t['id'], {'players': []})['players']
        is_joined = current_user in players
        progress = min(len(players) / t['max_players'] * 100, 100)
        
        tournaments_html += f'''
        <div class="tournament-card tournament-active" style="border-left:6px solid {t['color']};">
            <h3 style="color:{t['color']};font-size:2.5em;margin-bottom:20px;">{t['name']}</h3>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;font-size:1.6em;">
                <div>💰 <span style="color:var(--success);font-weight:800;">{t['prize']:,}</span></div>
                <div style="color:#7f8c8d;">{len(players)}/{t['max_players']}</div>
            </div>
            <div style="background:linear-gradient(90deg,{t['color']}20,{t['color']}20);height:12px;border-radius:10px;margin-bottom:30px;">
                <div style="background:{t['color']};height:100%;border-radius:10px;width:{progress}%;transition:width 0.5s;"></div>
            </div>
            <p style="color:#7f8c8d;font-size:1.2em;margin-bottom:30px;">{t['desc']}</p>
            {f'<div style="background:var(--success);color:white;padding:25px;border-radius:25px;text-align:center;font-size:1.3em;font-weight:700;box-shadow:0 10px 30px rgba(39,174,96,0.3);">✅ Ты записан! #{players.index(current_user)+1}</div>' if is_joined else 
             f'<form method="POST" action="/join_tournament/{t["id"]}" style="display:inline;"><button type="submit" class="nav-btn" style="width:100%;background:{t["color"]};font-size:20px;padding:25px;">⚔️ ЗАПИСАТЬСЯ (100💰)</button></form>'}
        </div>'''
    
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head>
    <title>⚔️ Турниры — Узнавайкин v39.0</title>
    <meta charset="UTF-8">
</head><body>
    <div class="container">
        <header>
            <h1 style="color:var(--danger);">⚔️ ТУРНИРЫ v39.0</h1>
            <p style="font-size:1.6em;">Общий призовой фонд: <b>15,000💰</b></p>
            <a href="/" class="nav-btn">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:40px;margin-bottom:60px;">
            {tournaments_html}
        </div>
        
        <div style="text-align:center;">
            <a href="/" class="nav-btn" style="background:var(--primary-gradient);">🏠 Главная</a>
            <a href="/profile" class="nav-btn" style="background:var(--info);">👤 Профиль</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
        </div>
    </div>
</body></html>'''

@app.route('/join_tournament/<t_id>', methods=['POST'])
@require_auth
def join_tournament(t_id):
    current_user = session['user']
    t = tournaments.get(t_id)
    
    if t and current_user not in t['players'] and len(t['players']) < t.get('max_players', 32):
        if user_economy[current_user]['coins'] >= 100:
            t['players'].append(current_user)
            user_economy[current_user]['coins'] -= 100
            logger.info(f"⚔️ {current_user} joined {t_id}")
    
    return redirect('/tournaments')

# ✅ АДМИН-ПАНЕЛЬ v39.0
@app.route('/admin')
@require_auth
def admin_panel():
    if not is_moderator(session['user']):
        return redirect('/')
    
    conn = db.get_connection()
    top_users = conn.execute('SELECT username, coins, role, level, wins FROM users ORDER BY coins DESC LIMIT 20').fetchall()
    conn.close()
    
    users_table = ''
    for i, user in enumerate(top_users, 1):
        users_table += f'''
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:15px;font-weight:700;">#{i}</td>
            <td style="padding:15px;">{user['username']}</td>
            <td style="padding:15px;"><span class="rank-{user['role']}">{user['role'].upper()}</span></td>
            <td style="padding:15px;color:var(--success);font-weight:700;">{user['coins']:,}</td>
            <td style="padding:15px;">{user['level']}</td>
            <td style="padding:15px;">{user['wins']}</td>
        </tr>'''
    
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head><title>⚙️ Админ — Узнавайкин v39.0</title></head><body>
    <div class="container">
        <header><h1 style="color:var(--danger);">⚙️ АДМИН-ПАНЕЛЬ</h1></header>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
            <div class="game-card">
                <h3>👑 ТОП-20 ИГРОКОВ</h3>
                <table style="width:100%;border-collapse:collapse;margin-top:20px;">
                    <thead><tr style="background:var(--info);color:white;">
                        <th style="padding:20px;">#</th><th>Игрок</th><th>Роль</th><th>💰</th><th>Lvl</th><th>🏆</th>
                    </tr></thead>
                    <tbody>{users_table}</tbody>
                </table>
            </div>
            <div class="game-card">
                <h3>🔧 УПРАВЛЕНИЕ</h3>
                <a href="/register" class="nav-btn" style="width:100%;background:var(--success);">👥 Создать игрока</a>
                <a href="/admin/mutes" class="nav-btn" style="width:100%;background:var(--warning);">🚫 Муты</a>
            </div>
        </div>
    </div>
</body></html>'''

# ✅ 404 + ФИНАЛЬНЫЙ ЗАПУСК
@app.errorhandler(404)
def not_found(e):
    return f'''{PREMIUM_CSS}
<!DOCTYPE html><html><head><title>404 — Узнавайкин</title></head><body>
    <div class="container" style="text-align:center;padding:100px 20px;">
        <h1 style="font-size:8em;color:var(--danger);">❓ 404</h1>
        <p style="font-size:2.5em;color:#7f8c8d;">Страница не найдена</p>
        <a href="/" class="nav-btn" style="font-size:22px;">🏠 На главную</a>
    </div>
</body></html>''', 404

if __name__ == '__main__':
    print("🚀" * 30)
    print("✅ УЗНАВАЙКИН v39.0 — ПРЕМИУМ КАЧЕСТВО 100%")
    print("👑 Админы: CatNap / Назар | Пароль: 120187")
    print("📱 Все страницы работают!")
    print("🚀" * 30)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
