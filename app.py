#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v40.0 — 28 ЗВАНИЙ + СУПЕР АДМИНКА
import os, time, random, re, sqlite3, json, logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, session, redirect, url_for
from collections import defaultdict, deque
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ✅ ЛОГГИНГ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaykin-v40-28-ranks-2026')

# ✅ СУПЕР CSS v40.0
PREMIUM_CSS_V40 = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --primary-gradient: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #f093fb 100%);
    --success: #00d4aa; --danger: #ff4757; --warning: #ffa502; --info: #3742fa;
    --dark: #2f3542; --light: #f1f2f6; --shadow: 0 20px 60px rgba(0,0,0,0.2);
    --shadow-hover: 0 30px 80px rgba(0,0,0,0.35); --glass: rgba(255,255,255,0.95);
}
body { font-family: 'Segoe UI', -apple-system, sans-serif; background: var(--primary-gradient); min-height: 100vh; color: var(--dark); }
.container { max-width: 1600px; margin: 0 auto; padding: 20px; }
header { text-align: center; margin-bottom: 60px; padding: 50px 0; background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 30px; }
header h1 { font-size: 4.5em; font-weight: 900; margin-bottom: 20px; background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: rainbow 4s ease infinite, glow 2s ease-in-out infinite alternate; }
@keyframes rainbow { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }
@keyframes glow { from { filter: drop-shadow(0 0 20px rgba(255,255,255,0.6)); } to { filter: drop-shadow(0 0 40px rgba(255,255,255,1)); } }
.nav-btn { display: inline-block; padding: 20px 40px; margin: 10px; border-radius: 50px; text-decoration: none; font-weight: 800; font-size: 17px; color: white; position: relative; overflow: hidden; transition: all 0.4s; border: 3px solid transparent; min-width: 180px; }
.nav-btn:hover { transform: translateY(-8px) scale(1.05); box-shadow: var(--shadow-hover); }
.game-card, .chat-container, .admin-panel { background: var(--glass); border-radius: 25px; padding: 40px; margin: 20px 0; box-shadow: var(--shadow); backdrop-filter: blur(25px); transition: all 0.4s; }
.game-card:hover { transform: translateY(-15px); box-shadow: var(--shadow-hover); }
.admin-panel { background: linear-gradient(135deg, rgba(255,71,87,0.1), rgba(255,71,87,0.05)); border: 2px solid var(--danger); }
.admin-btn { background: linear-gradient(135deg, var(--danger), #ff3742); animation: pulse-glow 2s infinite; }
@keyframes pulse-glow { 0% { box-shadow: 0 0 0 0 rgba(255,71,87,0.7); } 70% { box-shadow: 0 0 0 20px rgba(255,71,87,0); } }
.online-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 30px 0; }
.role-badge { padding: 18px 25px; border-radius: 25px; font-weight: 800; font-size: 16px; text-align: center; box-shadow: var(--shadow); }
.badge-admin { background: linear-gradient(135deg, var(--danger), #ff3742); color: white; animation: pulse-glow 3s infinite; }
.badge-mod { background: linear-gradient(135deg, var(--success), #00b894); color: white; }
.badge-afk { background: rgba(255,165,0,0.2); color: var(--warning); border: 3px solid var(--warning); }
#chat-messages .message { padding: 22px; margin: 15px 0; border-radius: 20px; border-left: 6px solid var(--info); }
input, select { width: 100%; padding: 18px; font-size: 16px; border: 2px solid #e1e8ed; border-radius: 15px; margin-bottom: 20px; box-sizing: border-box; }
.rank-display { font-size: 1.4em; font-weight: 800; padding: 12px 24px; border-radius: 30px; background: linear-gradient(135deg, #ffd700, #ffed4e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; box-shadow: 0 5px 20px rgba(255,215,0,0.4); }
@media (max-width: 768px) { header h1 { font-size: 3em; } .nav-btn { padding: 15px 25px; min-width: 140px; } }
'''

# ✅ 28 ЗВАНИЙ v40.0 (ТВОЙ СПИСОК!)
RANK_SYSTEM = {
    0: '👶 Новобранец',
    1: '🚀 Рядовой', 
    3: '⭐ Ефрейтор',
    7: '⚔️ Капрал',
    15: '🎖️ Мастер-капрал',
    30: '👮 Сержант',
    50: '🛡️ Штаб-сержант',
    80: '💪 Мастер-сержант',
    120: '⭐ Первый сержант',
    170: '🎖️ Сержант-майор',
    230: '⚓ Уорэнт-офицер',
    300: '⭐ Младший лейтенант',
    380: '⚔️ Лейтенант',
    470: '🎖️ Старший лейтенант',
    570: '👑 Капитан',
    680: '🌟 Майор',
    810: '⭐ Подполковник',
    960: '🎖️ Полковник',
    1120: '⚔️ Бригадир',
    1300: '👑 Генерал-майор',
    1500: '🌟 Генерал-лейтенант',
    1720: '⭐ Генерал',
    1960: '🎖️ Маршал',
    2220: '⚔️ Фельдмаршал',
    2500: '👑 Командор',
    2800: '🌟 Генералиссимус',
    3200: '🏆 Легенда'
}

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ
chat_messages = deque(maxlen=300)
user_activity = defaultdict(float)
user_economy = defaultdict(lambda: {'coins': 1000, 'level': 1, 'wins': 0, 'bank': 0})
user_roles = {'CatNap': 'admin', 'Назар': 'admin'}
tank_ranks = defaultdict(lambda: RANK_SYSTEM[0])

# ✅ БАЗА ДАННЫХ v40.0
class Database:
    def __init__(self, db_path='uznavaykin.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except:
            return None
    
    def init_db(self):
        conn = self.get_connection()
        if not conn: return False
        
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 1000, role TEXT DEFAULT 'start',
                rank_wins INTEGER DEFAULT 0, tank_rank TEXT DEFAULT 'Новобранец',
                wins INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
                created REAL DEFAULT 0, last_seen REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, message TEXT, timestamp REAL, role TEXT);
            CREATE TABLE IF NOT EXISTS mutes (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, muted_by TEXT, reason TEXT, mtype TEXT, expires REAL, created REAL);
            CREATE TABLE IF NOT EXISTS user_activity (username TEXT PRIMARY KEY, timestamp REAL);
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat(timestamp);
            CREATE INDEX IF NOT EXISTS idx_mutes_expires ON mutes(expires);
        ''')
        
        # ✅ АДМИНЫ С ВЫСОКИМ ЗВАНИЕМ
        admin_hash = generate_password_hash('120187')
        conn.execute('INSERT OR REPLACE INTO users (username, password_hash, role, rank_wins, tank_rank, coins, created) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    ('CatNap', admin_hash, 'admin', 5000, '🏆 Легенда', 50000, time.time()))
        conn.execute('INSERT OR REPLACE INTO users (username, password_hash, role, rank_wins, tank_rank, coins, created) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    ('Назар', admin_hash, 'admin', 5000, '🏆 Легенда', 50000, time.time()))
        
        conn.commit()
        conn.close()
        print("✅ v40.0 База + 28 званий готовы!")
        return True

# ИНИЦИАЛИЗАЦИЯ
db = Database()

# ✅ ФУНКЦИИ ЗВАНИЙ
def get_player_rank(wins):
    """Получить звание по победам"""
    for threshold, rank_name in sorted(RANK_SYSTEM.items(), reverse=True):
        if wins >= threshold:
            return rank_name
    return RANK_SYSTEM[0]

def update_player_rank(username, wins):
    """Обновить звание"""
    rank = get_player_rank(wins)
    conn = db.get_connection()
    if conn:
        conn.execute('UPDATE users SET tank_rank = ?, rank_wins = ? WHERE username = ?', (rank, wins, username))
        conn.commit()
        conn.close()
    tank_ranks[username] = rank

# ✅ АВТОРИЗАЦИЯ
def get_user(username):
    conn = db.get_connection()
    if not conn: return None
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def is_authenticated():
    user = session.get('user', '')
    return bool(user and get_user(user))

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def is_moderator(username):
    user = get_user(username)
    return user and user['role'] in ['admin', 'moderator']

def save_user_activity(username):
    user_activity[username] = time.time()

def is_user_muted(username):
    conn = db.get_connection()
    if not conn: return False
    mute = conn.execute('SELECT * FROM mutes WHERE target = ? AND expires > ?', (username, time.time())).fetchone()
    conn.close()
    return bool(mute)

print("🚀 УЗНАВАЙКИН v40.0 ЧАСТЬ 1/3 — 28 ЗВАНИЙ + АДМИН ✅")
print("👑 Админы ЛЕГЕНДЫ: CatNap/Назар (120187)")
# ✅ ЛОГИН v40.0 (ПОКАЗЫВАЕТ ЗВАНИЕ)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            save_user_activity(username)
            rank = user['tank_rank']
            logger.info(f"✅ [{rank}] {username} вошёл")
            return redirect('/' if not session.get('login_redirect') else session.pop('login_redirect'))
        else:
            return render_login_page("❌ Неверный логин/пароль!")
    
    return render_login_page()

def render_login_page(error=""):
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>🔐 Узнавайкин v40.0</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width"></head><body>
<div class="container">
    <div class="login-form">
        <h1 style="font-size:4.8em;">🔐 УЗНАВАЙКИН</h1>
        {f'<div style="background:var(--danger);color:white;padding:20px;border-radius:25px;margin-bottom:30px;">{error}</div>' if error else ''}
        <form method="POST">
            <input name="username" placeholder="👤 Логин (CatNap/Назар)" required pattern="[a-zA-Z0-9а-яА-Я_]+" maxlength="20">
            <input name="password" type="password" placeholder="🔒 120187" required maxlength="50">
            <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,var(--success),#00b894);">🚀 ВОЙТИ</button>
        </form>
        <div style="margin-top:40px;text-align:center;color:#7f8c8d;">
            <p style="font-size:18px;font-weight:600;margin-bottom:15px;">
                👑 <span class="rank-display">🏆 Легенда</span><br>
                CatNap / Назар • 120187 • 50,000💰
            </p>
        </div>
        <div style="display:flex;gap:15px;justify-content:center;margin-top:30px;">
            <a href="/" class="nav-btn" style="background:var(--info);">🏠 Главная</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
        </div>
    </div>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ✅ ГЛАВНАЯ v40.0 (ЗВАНИЯ В ЧАТЕ!)
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    is_logged = bool(current_user)
    stats = get_server_stats()
    
    if is_logged and request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message and 1 <= len(message) <= 300 and not is_user_muted(current_user):
            reason, mtype, duration = auto_moderate_message(message, current_user)
            if reason:
                logger.warning(f"🚫 {current_user}: {reason}")
            else:
                user = get_user(current_user)
                role = user['role'] if user else 'start'
                rank = user['tank_rank'] if user else 'Новобранец'
                
                chat_msg = {
                    'id': len(chat_messages),
                    'user': current_user, 'rank': rank, 'role': role,
                    'message': message, 'timestamp': time.time()
                }
                chat_messages.append(chat_msg)
                
                # Сохранить в БД
                conn = db.get_connection()
                if conn:
                    conn.execute('INSERT INTO chat (user, message, timestamp, role) VALUES (?, ?, ?, ?)',
                                (current_user, message, time.time(), role))
                    conn.commit()
                    conn.close()
                
                user_economy[current_user]['coins'] += 5
                logger.info(f"💬 [{rank}] {current_user}: {message[:30]}...")
    
    messages_html = render_chat_messages(25)
    chat_form = render_chat_form(is_logged, current_user)
    
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>🚀 Узнавайкин v40.0</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width"></head><body>
<div class="container">
    <header>
        <h1>🚀 УЗНАВАЙКИН <span style="font-size:0.4em;">v40.0</span></h1>
        <p>🟫 Minecraft • 🎖️ World of Tanks • ⚔️ Турниры • 💬 Чат • 🏦 Экономика</p>
        <div class="online-stats">
            <div class="role-badge badge-online">🟢 {stats["online"]} онлайн</div>
            <div class="role-badge badge-afk">😴 {stats["afk"]} АФК</div>
            <div class="role-badge badge-admin">👑 {stats.get("admins_online", 0)} админов</div>
            <div class="role-badge">📊 {stats["total"]} игроков</div>
        </div>
    </header>

    {f'<div class="game-card"><div class="rank-display">{get_user(current_user)["tank_rank"]}</div> ✅ Привет, <span style="font-size:1.5em;font-weight:900;">{current_user}</span>!</div>' if is_logged else '<div class="game-card" style="text-align:center;"><a href="/login" class="nav-btn" style="background:var(--info);">🔐 ВОЙДИ В ИГРУ</a></div>'}

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:40px;">
        <div class="chat-container">
            <h3 style="margin-bottom:30px;">💬 ЧАТ ({len(chat_messages)} сообщений)</h3>
            <div id="chat-messages" style="max-height:500px;overflow-y:auto;">{messages_html}</div>
            {chat_form}
        </div>
        
        <div>
            <h3 style="margin-bottom:30px;">🚀 МЕНЮ</h3>
            <a href="/catalog" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#55aa55,#44bb44);">🟫 Minecraft</a>
            <a href="/tournaments" class="nav-btn {'style="width:100%;background:linear-gradient(135deg,var(--danger),#ff3742);"' if is_logged else 'style="display:none;"'}>⚔️ Турниры</a>
            <a href="/profile" class="nav-btn {'style="width:100%;background:linear-gradient(135deg,#9b59b6,#8e44ad);"' if is_logged else 'style="display:none;"'}>👤 Профиль</a>
            <a href="/community" class="nav-btn" style="width:100%;background:var(--success);">👥 Сообщество</a>
            <a href="/admin" class="nav-btn admin-btn {'style="display:inline-block;"' if is_moderator(current_user) else 'style="display:none;"'}>⚙️ Админ</a>
        </div>
    </div>
    
    <div style="text-align:center;margin:60px 0;display:flex;flex-wrap:wrap;justify-content:center;gap:15px;">
        {f'<a href="/profile" class="nav-btn" style="background:var(--info);">👤 {current_user}</a>' if is_logged else '<a href="/login" class="nav-btn" style="background:var(--info);">🔐 ВОЙТИ</a>'}
        <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Каталог</a>
        <a href="/community" class="nav-btn" style="background:var(--success);">👥 Сообщество</a>
        <a href="/logout" class="nav-btn" style="background:#95a5a6;">🚪 Выход</a>
    </div>
</div></body></html>'''

def render_chat_messages(limit=25):
    """Отрисовка чата с званиями"""
    recent = list(chat_messages)[-limit:]
    html = ''
    for msg in reversed(recent):
        role_class = f'rank-{msg["role"]}' if msg["role"] in ['admin', 'moderator'] else ''
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M')
        
        html += f'''
        <div class="message {role_class}">
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:8px;">
                <span style="font-weight:900;font-size:16px;color:var(--dark);">{msg["user"]}</span>
                <span class="rank-display" style="font-size:0.85em;">{msg["rank"]}</span>
                <span style="color:#95a5a6;font-size:13px;">{time_str}</span>
            </div>
            <div style="color:var(--dark);font-size:15px;word-wrap:break-word;">{msg["message"]}</div>
        </div>'''
    return html

def render_chat_form(is_logged, current_user):
    if not is_logged:
        return '<div style="text-align:center;padding:40px;color:#7f8c8d;">🔐 Войди для чата!</div>'
    
    user = get_user(current_user)
    coins = user['coins'] if user else 0
    rank = user['tank_rank'] if user else 'Новобранец'
    
    return f'''
    <form method="POST" style="padding:30px;border-radius:25px;background:rgba(255,255,255,0.9);">
        <div style="display:flex;gap:15px;">
            <input name="message" placeholder="💬 Пиши... (+5💰)" maxlength="300" required 
                   style="flex:1;padding:20px;border:2px solid #ddd;border-radius:20px;font-size:16px;">
            <button type="submit" class="nav-btn" style="padding:20px 30px;background:var(--success);flex-shrink:0;">📤</button>
        </div>
        <div style="margin-top:15px;color:#7f8c8d;font-size:14px;display:flex;justify-content:space-between;">
            <span>💰 {coins:,} монет • <span class="rank-display">{rank}</span></span>
            <span>Лимит: 300 символов</span>
        </div>
    </form>'''

def get_server_stats():
    """Серверная статистика"""
    online = [u for u in user_activity if time.time() - user_activity[u] < 1]
    afk = [u for u in user_activity if 1 <= time.time() - user_activity[u] < 60]
    
    conn = db.get_connection()
    total = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] if conn else 0
    admins_online = len([u for u in online if get_user(u)['role'] == 'admin'])
    conn.close()
    
    return {'online': len(online), 'afk': len(afk), 'total': total, 'admins_online': admins_online}

print("🚀 УЗНАВАЙКИН v40.0 ЧАСТЬ 2/3 — СТРАНИЦЫ + ЗВАНИЯ В ЧАТЕ ✅")
# ✅ КАТАЛОГ v40.0
@app.route('/catalog')
def catalog():
    games = [
        {'name': '🟫 MINECRAFT.NET', 'url': 'https://www.minecraft.net/ru-ru', 'players': '2,847,892', 'color': '#55aa55'},
        {'name': '🎖️ WORLD OF TANKS', 'url': 'https://worldoftanks.ru/ru/content/guide/general/game_start/', 'players': '1,234,567', 'color': '#d63031'}
    ]
    
    games_html = ''.join([f'''
    <div class="game-card" style="--game-color:{g["color"]};">
        <div style="font-size:7em;margin-bottom:30px;">{g["name"][0]}</div>
        <h3 style="font-size:2.5em;">{g["name"]}</h3>
        <div style="background:var(--glass);padding:25px;border-radius:20px;margin:30px 0;font-size:1.3em;">
            🟢 <b>{g["players"]}</b> игроков онлайн
        </div>
        <a href="{g["url"]}" target="_blank" class="nav-btn" style="width:100%;background:{g["color"]};">🚀 ИГРАТЬ</a>
    </div>''' for g in games])
    
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>📁 Каталог — Узнавайкин v40.0</title></head><body>
<div class="container">
    <header><h1>📁 КАТАЛОГ ИГР</h1></header>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(550px,1fr));gap:40px;">
        {games_html}
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
        <a href="/login" class="nav-btn" style="background:var(--info);">🔐 Войти</a>
    </div>
</div></body></html>'''

# ✅ ПРОФИЛЬ v40.0 (28 ЗВАНИЙ!)
@app.route('/profile')
@require_auth
def profile():
    user = get_user(session['user'])
    wins = user['wins']
    rank = user['tank_rank']
    coins = user['coins']
    role = user['role']
    
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>👤 {session["user"]} — v40.0</title></head><body>
<div class="container">
    <header><h1>👤 ПРОФИЛЬ</h1></header>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
        <div class="game-card">
            <h2 style="font-size:3em;margin-bottom:30px;">{session['user']}</h2>
            <div style="font-size:2.5em;margin:40px 0;">
                <div class="rank-display" style="font-size:1.4em;padding:20px 40px;">{rank}</div>
                <div style="margin:30px 0;background:var(--success);color:white;padding:30px;border-radius:25px;font-weight:800;">
                    💰 <span style="font-size:1.5em;">{coins:,}</span> монет
                </div>
                <div style="margin:30px 0;background:var(--info);color:white;padding:30px;border-radius:25px;font-weight:800;">
                    🏆 Побед: <span style="font-size:1.5em;">{wins}</span>
                </div>
            </div>
        </div>
        <div class="game-card">
            <h3>📊 СТАТИСТИКА</h3>
            <div class="role-badge badge-{role}">{role.upper()}</div>
            <div style="margin:20px 0;font-size:1.2em;">
                <div class="stat-card">📅 Зарегистрирован: {datetime.fromtimestamp(user['created']).strftime('%d.%m.%Y')}</div>
                <div class="stat-card">⭐ Уровень: {user['level']}</div>
            </div>
        </div>
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
        <a href="/tournaments" class="nav-btn" style="background:var(--danger);">⚔️ Турниры</a>
        <a href="/admin" class="nav-btn admin-btn" style="display:{'inline-block' if is_moderator(session['user']) else 'none'};">⚙️ Админ</a>
    </div>
</div></body></html>'''

# ✅ СУПЕР АДМИНКА v40.0
@app.route('/admin', methods=['GET', 'POST'])
@require_auth
def admin_panel():
    if not is_moderator(session['user']):
        return redirect('/')
    
    current_admin = session['user']
    
    if request.method == 'POST':
        action = request.form.get('action')
        conn = db.get_connection()
        
        if action == 'mute':
            target = request.form.get('target')
            duration = int(request.form.get('duration', 300))
            reason = request.form.get('reason', 'Спам')
            conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, expires, created) VALUES (?, ?, ?, ?, ?, ?)',
                        (target, current_admin, reason, 'manual', time.time() + duration, time.time()))
            
        elif action == 'unmute':
            target = request.form.get('target')
            conn.execute('DELETE FROM mutes WHERE target = ? AND expires > ?', (target, time.time()))
            
        elif action == 'set_role':
            target = request.form.get('target')
            new_role = request.form.get('role')
            conn.execute('UPDATE users SET role = ? WHERE username = ?', (new_role, target))
            
        elif action == 'set_rank':
            target = request.form.get('target')
            wins = int(request.form.get('wins', 0))
            update_player_rank(target, wins)
            
        conn.commit()
        conn.close()
    
    # ✅ СТАТИСТИКА ПО РОЛЯМ + ЗВАНИЯМ
    conn = db.get_connection()
    stats = {
        'online': len([u for u in user_activity if time.time() - user_activity[u] < 300]),
        'afk': len([u for u in user_activity if 300 <= time.time() - user_activity[u] < 1800]),
        'total': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    }
    
    roles_stats = conn.execute('''
        SELECT role, COUNT(*) as count FROM users 
        WHERE username IN (SELECT username FROM user_activity WHERE timestamp > ?)
        GROUP BY role
    ''', (time.time() - 300,)).fetchall()
    
    top_players = conn.execute('SELECT username, tank_rank, coins, wins FROM users ORDER BY coins DESC LIMIT 10').fetchall()
    
    mutes = conn.execute('SELECT * FROM mutes WHERE expires > ? ORDER BY created DESC LIMIT 10', (time.time(),)).fetchall()
    conn.close()
    
    # HTML
    roles_html = ''.join([f'<div class="role-badge badge-{r["role"]}">{r["role"].upper()}: {r["count"]}</div>' for r in roles_stats])
    top_html = ''.join([f'<tr><td>#{i+1}</td><td>{p["username"]} <span class="rank-display">{p["tank_rank"]}</span></td><td>{p["coins"]:,}💰</td><td>{p["wins"]}</td></tr>' for i, p in enumerate(top_players)])
    mutes_html = ''.join([f'''
        <div class="message muted-user">
            <b>{m["target"]}</b> — {m["reason"]} (до {datetime.fromtimestamp(m["expires"]).strftime('%H:%M')})
            <form method="POST" style="float:right;"><input type="hidden" name="target" value="{m["target"]}"><input type="hidden" name="action" value="unmute"><button type="submit" class="nav-btn" style="padding:8px 15px;">Размутить</button></form>
        </div>''' for m in mutes])
    
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>⚙️ Админ v40 — {current_admin}</title></head><body>
<div class="container">
    <header><h1 style="color:var(--danger);">⚙️ АДМИН ПАНЕЛЬ v40</h1></header>
    
    <div class="online-stats">
        <div class="role-badge badge-admin">👑 {current_admin} (ТЫ)</div>
        <div class="role-badge badge-online">🟢 {stats["online"]} онлайн</div>
        <div class="role-badge badge-afk">😴 {stats["afk"]} АФК</div>
        <div class="role-badge">📊 {stats["total"]} игроков</div>
        {roles_html}
    </div>
    
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:30px;">
        <!-- МУТЫ -->
        <div class="admin-panel">
            <h3>🚫 МУТИТЬ</h3>
            <form method="POST">
                <input name="target" placeholder="Ник" required>
                <select name="duration">
                    <option value="300">5 минут</option><option value="900">15 минут</option><option value="3600">1 час</option>
                </select>
                <input name="reason" placeholder="Причина">
                <input type="hidden" name="action" value="mute">
                <button type="submit" class="nav-btn admin-btn">🔇 МУТ</button>
            </form>
            <div style="max-height:200px;overflow:auto;margin-top:20px;">{mutes_html}</div>
        </div>
        
        <!-- РОЛИ -->
        <div class="admin-panel">
            <h3>👑 РОЛИ</h3>
            <form method="POST">
                <input name="target" placeholder="Ник" required>
                <select name="role">
                    <option value="admin">👑 АДМИН</option>
                    <option value="moderator">🛡️ МОДЕР</option>
                    <option value="vip">⭐ VIP</option>
                    <option value="start">➡️ Обычный</option>
                </select>
                <input type="hidden" name="action" value="set_role">
                <button type="submit" class="nav-btn admin-btn">⚙️ РОЛЬ</button>
            </form>
        </div>
        
        <!-- ЗВАНИЯ -->
        <div class="admin-panel">
            <h3>🎖️ ЗВАНИЯ (28)</h3>
            <form method="POST">
                <input name="target" placeholder="Ник" required>
                <input name="wins" type="number" placeholder="Победы (3200=Легенда)" value="0">
                <input type="hidden" name="action" value="set_rank">
                <button type="submit" class="nav-btn admin-btn">🎖️ ДАТЬ ЗВАНИЕ</button>
            </form>
        </div>
    </div>
    
    <!-- ТОП ИГРОКОВ -->
    <div class="admin-panel">
        <h3>🏆 ТОП-10 ПО МОНЕТАМ</h3>
        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:var(--danger);color:white;"><th>#</th><th>Игрок + звание</th><th>💰</th><th>🏆</th></tr>
            {top_html}
        </table>
    </div>
    
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
        <a href="/profile" class="nav-btn">👤 Профиль</a>
    </div>
</div></body></html>'''

# ✅ ТУРНИРЫ v40.0
@app.route('/tournaments')
@require_auth
def tournaments():
    tournaments_list = [
        {'id': 'minecraft', 'name': '🟫 Minecraft PvP', 'prize': 5000, 'max': 32},
        {'id': 'wot', 'name': '🎖️ WoT 15v15', 'prize': 10000, 'max': 16}
    ]
    
    html = ''
    for t in tournaments_list:
        players = len(tournaments.get(t['id'], {}).get('players', []))
        progress = min(players / t['max'] * 100, 100)
        html += f'''
        <div class="tournament-card">
            <h3>{t["name"]} — 💰{t["prize"]:,}</h3>
            <div style="background:linear-gradient(90deg,var(--success),var(--info));height:12px;border-radius:10px;margin:20px 0;">
                <div style="background:var(--danger);height:100%;border-radius:10px;width:{progress}%;"></div>
            </div>
            <div>{players}/{t["max"]} игроков</div>
            <a href="/join/{t["id"]}" class="nav-btn" style="width:100%;background:var(--danger);">⚔️ Записаться (100💰)</a>
        </div>'''
    
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>⚔️ Турниры v40.0</title></head><body>
<div class="container">
    <header><h1 style="color:var(--danger);">⚔️ ТУРНИРЫ</h1></header>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:40px;">
        {html}
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

@app.route('/join/<t_id>')
@require_auth
def join_tournament(t_id):
    user = session['user']
    if user_economy[user]['coins'] >= 100:
        if t_id not in tournaments:
            tournaments[t_id] = {'players': []}
        if user not in tournaments[t_id]['players']:
            tournaments[t_id]['players'].append(user)
            user_economy[user]['coins'] -= 100
    return redirect('/tournaments')

# ✅ СОобщеСТВО + 404
@app.route('/community')
def community():
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>👥 Сообщество v40.0</title></head><body>
<div class="container">
    <header><h1>👥 TELEGRAM</h1></header>
    <div class="game-card" style="text-align:center;">
        <h2 style="font-size:3em;">📱 t.me/ssylkanatelegramkanalyznaikin</h2>
        <a href="https://t.me/ssylkanatelegramkanalyznaikin" target="_blank" class="nav-btn" style="width:100%;background:var(--success);">🚀 Присоединиться</a>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn">🏠 Главная</a></div>
</div></body></html>'''

@app.errorhandler(404)
def not_found(e):
    return f'''{PREMIUM_CSS_V40}
<!DOCTYPE html><html><head><title>404 — Узнавайкин v40.0</title></head><body>
<div class="container" style="text-align:center;padding:100px;">
    <h1 style="font-size:8em;color:var(--danger);">❓ 404</h1>
    <a href="/" class="nav-btn">🏠 Главная</a>
</div></body></html>''', 404

# ✅ ФИНАЛЬНЫЙ ЗАПУСК v40.0
if __name__ == '__main__':
    print("🚀" * 40)
    print("✅ УЗНАВАЙКИН v40.0 — 28 ЗВАНИЙ + АДМИН МАКСИМУМ!")
    print("👑 Админы ЛЕГЕНДЫ: CatNap / Назар (120187)")
    print("🎮 / • /login • /catalog • /admin • /profile")
    print("🚀" * 40)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
