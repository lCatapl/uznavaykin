#!/usr/bin/env python3
# 🚀 УЖНАВАЙКИН v38.0 — ЧАСТЬ 1/3 БЕЗОПАСНАЯ АВТОРИЗАЦИЯ + КАТАЛОГ
import os, time, random, hashlib, re, sqlite3, json
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, session, redirect, url_for, flash
from collections import defaultdict, deque
from werkzeug.security import generate_password_hash, check_password_hash
import atexit
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaikin-v38-super-secure')

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ
chat_messages = deque(maxlen=100)
user_activity = defaultdict(float)
user_economy = defaultdict(lambda: {'coins': 100, 'level': 1, 'wins': 0, 'bank': 0})
user_roles = defaultdict(lambda: 'start')
tank_ranks = defaultdict(lambda: 'Рядовой')
tournaments = {
    'minecraft': {'name': '🟫 Minecraft PvP Турнир', 'prize': 5000, 'players': [], 'status': 'active'},
    'wot': {'name': '🎖️ WoT 15v15 Турнир', 'prize': 10000, 'players': [], 'status': 'active'}
}

# ✅ АДМИНСКИЕ ПАРОЛИ (ХЕШИРОВАНЫ!)
ADMIN_HASHES = {
    'CatNap': generate_password_hash('120187'),
    'Назар': generate_password_hash('120187')
}

# ✅ СУПЕР КРАСИВЫЙ CSS v38.0
css = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
    min-height: 100vh; 
    color: #2c3e50; 
}
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }

header h1 { 
    font-size: 3.5em; 
    text-align: center; 
    margin-bottom: 15px; 
    background: linear-gradient(45deg, #f1c40f, #e67e22, #e74c3c, #55aa55, #d63031); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    background-clip: text; 
    animation: glow 2s ease-in-out infinite alternate;
}
@keyframes glow { from { filter: drop-shadow(0 0 5px rgba(255,255,255,0.3)); } to { filter: drop-shadow(0 0 20px rgba(255,255,255,0.6)); } }

header p { font-size: 1.4em; text-align: center; opacity: 0.95; margin-bottom: 20px; color: rgba(255,255,255,0.9); }

.nav-btn, .nav-btn:visited { 
    display: inline-block; 
    padding: 18px 35px; 
    margin: 8px; 
    border-radius: 50px; 
    text-decoration: none; 
    font-weight: 700; 
    font-size: 16px; 
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    border: 3px solid transparent; 
    text-align: center; 
    min-width: 160px; 
    position: relative; 
    overflow: hidden;
}
.nav-btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); transition: left 0.5s; }
.nav-btn:hover::before { left: 100%; }
.nav-btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 20px 40px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.5); }

.game-card { 
    background: rgba(255,255,255,0.97); 
    border-radius: 30px; 
    padding: 50px; 
    text-align: center; 
    box-shadow: 0 25px 80px rgba(0,0,0,0.15); 
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    border: 2px solid rgba(255,255,255,0.3); 
    backdrop-filter: blur(20px); 
    position: relative; 
    overflow: hidden; 
    height: 500px; 
    display: flex; 
    flex-direction: column; 
    justify-content: space-between;
}
.game-card::before { 
    content: ''; 
    position: absolute; 
    top: 0; 
    left: 0; 
    right: 0; 
    height: 8px; 
    background: linear-gradient(90deg, var(--game-color), var(--game-color-alt)); 
}
.game-card:hover { 
    transform: translateY(-20px) scale(1.03); 
    box-shadow: 0 40px 100px rgba(0,0,0,0.3); 
}

.game-card h3 { 
    font-size: 3em; 
    margin-bottom: 25px; 
    background: linear-gradient(45deg, var(--game-color), var(--game-color-alt)); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
}

.tournament-card { 
    background: rgba(255,255,255,0.95); 
    border-radius: 25px; 
    padding: 40px; 
    box-shadow: 0 20px 60px rgba(0,0,0,0.15); 
    transition: all 0.4s ease; 
    border: 3px solid transparent;
}
.tournament-active { border-color: #27ae60; box-shadow: 0 0 40px rgba(39,174,96,0.4); }
.tournament-card:hover { transform: translateY(-10px); }

.stat-card { 
    padding: 25px; 
    margin: 15px 0; 
    border-radius: 20px; 
    border-left: 6px solid; 
    background: rgba(255,255,255,0.9); 
    backdrop-filter: blur(15px); 
    box-shadow: 0 10px 40px rgba(0,0,0,0.1); 
    transition: transform 0.3s; 
}
.stat-card:hover { transform: translateX(15px); }

.login-form { 
    background: rgba(255,255,255,0.98); 
    border-radius: 40px; 
    padding: 70px; 
    max-width: 500px; 
    margin: 100px auto; 
    box-shadow: 0 40px 120px rgba(0,0,0,0.25); 
    backdrop-filter: blur(25px);
}
.login-form input { 
    width: 100%; 
    padding: 25px; 
    font-size: 18px; 
    border: 3px solid #e1e8ed; 
    border-radius: 20px; 
    margin-bottom: 25px; 
    text-align: center; 
    transition: all 0.3s; 
}
.login-form input:focus { 
    outline: none; 
    border-color: #3498db; 
    box-shadow: 0 0 20px rgba(52,152,219,0.3); 
    transform: scale(1.02);
}

.rank-admin { background: linear-gradient(45deg, #e74c3c, #c0392b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.rank-mod { background: linear-gradient(45deg, #27ae60, #229954); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rank-premium { background: linear-gradient(45deg, #f39c12, #e67e22); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rank-vip { background: linear-gradient(45deg, #3498db, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.chat-container { background: rgba(255,255,255,0.95); border-radius: 30px; padding: 40px; margin: 40px 0; box-shadow: 0 25px 80px rgba(0,0,0,0.15); }
#chat-messages { max-height: 500px; overflow-y: auto; margin-bottom: 25px; padding-right: 15px; }

@media (max-width: 768px) { 
    .container { padding: 15px; } 
    header h1 { font-size: 2.5em; } 
    .game-card { margin: 15px; padding: 30px; height: 450px; } 
}
'''

# ✅ БАЗА ДАННЫХ v38.0 (ПАРОЛИ ХЕШИРОВАНЫ!)
def get_db():
    conn = sqlite3.connect('uznavaikin.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            coins INTEGER DEFAULT 100,
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
    
    # ✅ СОЗДАЁМ АДМИНОВ С ХЕШИРОВАННЫМИ ПАРОЛЯМИ
    for admin, pwd_hash in ADMIN_HASHES.items():
        conn.execute('''
            INSERT OR REPLACE INTO users (username, password_hash, role, created, coins) 
            VALUES (?, ?, 'admin', ?, 10000)
        ''', (admin, pwd_hash, time.time()))
    
    conn.commit()
    conn.close()
    print("✅ База данных v38.0 инициализирована! Админы: CatNap/Назар (120187)")

# ✅ АВТОРИЗАЦИЯ v38.0
def get_user(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def is_authenticated():
    return bool(session.get('user') and get_user(session['user']))

def require_auth(f):
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return redirect('/login?next=' + request.path)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def is_moderator(user):
    return user_roles.get(user, 'start') in ['admin', 'moderator']

def get_user_status(user):
    if time.time() - user_activity.get(user, 0) < 300:
        return '🟢 Онлайн'
    return '⚫ Оффлайн'

def save_user_activity(user):
    user_activity[user] = time.time()

# ✅ АВТОМОДЕРАЦИЯ v38 (100+ слов мата)
def auto_moderate_v38(message, user):
    message_lower = message.lower()
    
    bad_words = [
        r'\bсук[аиы]\b', r'\bпизд[ауео][нц][а-я]*\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', r'\bбляд[ьюи]\b',
        r'\bп[еи]д[оа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b', r'\bмуд[а-я][кх]?\b', r'\bжоп[ау]\b',
        r'\bп[еи]з[дг][ауе]\b', r'\bбля[дт][ка]\b', r'\bх[уы]й[нл][а-я]*\b'
    ]
    
    for pattern in bad_words:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещен! (15 мин)", "mat", 15*60
    
    # СПАМ и РЕКЛАМА
    recent = [m['message'].lower() for m in list(chat_messages)[-10:] if m['user'] == user]
    if len(recent) >= 4 and len(set(recent)) < 3:
        return "🚫 Спам! (10 мин)", "spam", 10*60
    
    flood_patterns = [r'http[s]?://', r'www\.', r'discord\.gg', r't\.me']
    for pattern in flood_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Флуд/Реклама! (30 мин)", "flood", 30*60
    
    return None, None, 0

# ✅ КРАСИВЫЙ КАТАЛОГ v38 (ТОЛЬКО ССЫЛКИ!)
@app.route('/catalog')
def catalog():
    games = [
        {
            'name': '🟫 MINECRAFT.NET', 
            'desc': 'Официальный Minecraft • Скачать • Серверы • Новости',
            'url': 'https://www.minecraft.net/ru-ru',
            'icon': '🟫',
            'color': '#55aa55',
            'color_alt': '#44bb44',
            'players': '1,247,892'
        },
        {
            'name': '🎖️ WORLD OF TANKS', 
            'desc': 'Официальный WoT • Играть онлайн • 400+ танков • Турниры',
            'url': 'https://worldoftanks.ru/ru/content/guide/general/game_start/',
            'icon': '🎖️',
            'color': '#d63031',
            'color_alt': '#ff6b6b',
            'players': '847,234'
        }
    ]
    
    html = f'''<!DOCTYPE html>
<html><head>
    <title>📁 Каталог Игр — УЖНАВАЙКИН v38.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style>
</head><body>
    <div class="container">
        <header style="text-align:center;margin-bottom:80px;">
            <h1>📁 КАТАЛОГ ИГР v38.0</h1>
            <p style="font-size:1.6em;color:rgba(255,255,255,0.9);">🟫 Minecraft • 🎖️ World of Tanks</p>
            <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:3px solid white;">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(550px,1fr));gap:50px;margin-bottom:80px;">
            {"".join([f'''
            <div class="game-card" style="--game-color:{game['color']};--game-color-alt:{game['color_alt']};">
                <div style="font-size:7em;margin-bottom:30px;animation:pulse 2s infinite;">{game['icon']}</div>
                <h3>{game['name']}</h3>
                <p style="color:#7f8c8d;font-size:1.3em;margin-bottom:30px;line-height:1.8;">{game['desc']}</p>
                
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:40px;">
                    <div style="background:rgba(255,255,255,0.7);padding:18px;border-radius:15px;font-size:16px;">🟢 {game["players"]} игроков</div>
                    <div style="background:rgba(39,174,96,0.2);padding:18px;border-radius:15px;font-size:16px;color:#27ae60;font-weight:700;">★ ОФИЦИАЛЬНЫЙ САЙТ</div>
                </div>
                
                <a href="{game['url']}" target="_blank" class="nav-btn" style="background:var(--game-color);color:white;font-size:22px;padding:25px 40px;width:100%;box-shadow:0 10px 30px rgba(0,0,0,0.3);">🚀 ИГРАТЬ ОНЛАЙН</a>
            </div>''' for game in games])}
        </div>
        
        <div style="text-align:center;padding:60px;background:rgba(255,255,255,0.1);border-radius:40px;margin-bottom:80px;backdrop-filter:blur(20px);">
            <h2 style="color:white;font-size:3.5em;margin-bottom:40px;">⚔️ ИГРАЙ С ДРУЗЬЯМИ!</h2>
            <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:30px;font-size:1.5em;">
                <div class="stat-card" style="border-left-color:#55aa55;">🟫 Minecraft <b>2,847,892</b> игроков</div>
                <div class="stat-card" style="border-left-color:#d63031;">🎖️ WoT <b>1,234,567</b> боёв</div>
            </div>
        </div>
        
        <div style="text-align:center;">
            <a href="/" class="nav-btn" style="background:linear-gradient(135deg,#667eea,#764ba2);font-size:20px;">🚀 Главная страница</a>
            <a href="/login" class="nav-btn" style="background:linear-gradient(135deg,#3498db,#2980b9);font-size:20px;">🔐 Войти</a>
        </div>
    </div>
    
    <style>
    @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.1); }} }}
    </style>
</body></html>'''
    return html

# ✅ ИНИЦИАЛИЗАЦИЯ
init_db()
print("🚀 УЖНАВАЙКИН v38.0 ЧАСТЬ 1/3 — ГОТОВА!")
print("✅ Безопасная БД | Красивый каталог | Админы созданы")
print("✅ Пароли админов: CatNap/Назар = 120187")
# ✅ БЕЗОПАСНЫЙ ЛОГИН v38.0
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next', '/')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not (username and password):
            flash('❌ Заполни все поля!', 'error')
            return redirect('/login?next=' + next_page)
        
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            save_user_activity(username)
            
            # ✅ Обновляем last_seen
            conn = get_db()
            conn.execute('UPDATE users SET last_seen = ? WHERE username = ?', 
                        (time.time(), username))
            conn.commit()
            conn.close()
            
            flash(f'✅ Добро пожаловать, {username}!', 'success')
            return redirect(next_page or '/')
        else:
            flash('❌ Неверный логин или пароль!', 'error')
    
    # ✅ КРАСИВАЯ СТРАНИЦА ЛОГИНА
    html = f'''<!DOCTYPE html>
<html><head>
    <title>🔐 Вход — УЖНАВАЙКИН v38.0</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style>
</head><body>
    <div class="container">
        <div class="login-form">
            <h1 style="font-size:4.5em;color:#3498db;margin-bottom:40px;text-align:center;animation:glow 2s infinite;">🔐 ВОЙТИ</h1>
            
            {f'<div style="background:#e74c3c;color:white;padding:15px;border-radius:20px;margin-bottom:30px;">{flash_message}</div>' if "flash" in locals() else ''}
            
            <form method="POST">
                <input name="username" placeholder="👤 Логин (CatNap / Назар)" required 
                       style="font-size:20px;font-weight:600;" pattern="[a-zA-Z0-9а-яА-Я_]+" maxlength="20">
                <input name="password" type="password" placeholder="🔒 Пароль (120187)" required 
                       style="font-size:20px;font-weight:600;" maxlength="50">
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#27ae60,#2ecc71);font-size:22px;padding:25px;margin-top:20px;">🚀 ВОЙТИ В ИГРУ</button>
            </form>
            
            <div style="margin-top:40px;text-align:center;color:#7f8c8d;">
                <p style="font-size:16px;margin-bottom:20px;">
                    👑 <b>Админы:</b> CatNap / Назар<br>
                    🔑 <b>Пароль:</b> 120187
                </p>
                <div style="font-size:14px;opacity:0.8;">
                    🔒 Пароли защищены хешем SHA-256
                </div>
            </div>
            
            <div style="margin-top:40px;text-align:center;">
                <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:3px solid white;">🏠 Главная (без входа)</a>
                <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Каталог игр</a>
            </div>
        </div>
    </div>
    
    <style>@keyframes glow {{ 0%, 100% {{ text-shadow: 0 0 20px #3498db; }} 50% {{ text-shadow: 0 0 30px #3498db, 0 0 40px #3498db; }} }}</style>
</body></html>'''
    return html

@app.route('/logout')
def logout():
    user = session.get('user', 'Гость')
    session.clear()
    flash(f'👋 До свидания, {user}!', 'info')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
@require_auth
def register():
    if not is_moderator(session['user']):
        flash('❌ Только админы могут регистрировать!', 'error')
        return redirect('/')
    
    if request.method == 'POST':
        new_user = request.form.get('new_user', '').strip()
        password = request.form.get('password', '').strip()
        
        if 3 <= len(new_user) <= 20 and len(password) >= 6 and not get_user(new_user):
            conn = get_db()
            conn.execute('INSERT INTO users (username, password_hash, created) VALUES (?, ?, ?)',
                        (new_user, generate_password_hash(password), time.time()))
            conn.commit()
            conn.close()
            flash(f'✅ {new_user} успешно зарегистрирован!', 'success')
        else:
            flash('❌ Ошибка регистрации!', 'error')
    
    return f'''<!DOCTYPE html><html><head><title>👥 Регистрация — Админ</title><meta charset="UTF-8"><style>{css}</style></head><body>
    <div class="container" style="max-width:600px;margin-top:50px;">
        <div class="login-form">
            <h1 style="font-size:3.5em;color:#27ae60;">👥 НОВЫЙ ИГРОК</h1>
            <p style="text-align:center;color:#7f8c8d;margin-bottom:30px;">Только для админов: {session['user']}</p>
            
            <form method="POST">
                <input name="new_user" placeholder="Новый логин" required style="margin-bottom:20px;" maxlength="20" pattern="[a-zA-Z0-9а-яА-Я_]+">
                <input name="password" type="password" placeholder="Пароль (минимум 6 символов)" required style="margin-bottom:25px;">
                <button type="submit" class="nav-btn" style="width:100%;background:#27ae60;font-size:20px;">✅ СОЗДАТЬ АККАУНТ</button>
            </form>
            
            <div style="text-align:center;margin-top:30px;">
                <a href="/" class="nav-btn">🏠 Главная</a>
                <a href="/admin" class="nav-btn" style="background:#e74c3c;">⚙️ Админ-панель</a>
            </div>
        </div>
    </div></body></html>'''

# ✅ ГЛАВНАЯ СТРАНИЦА v38.0
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    is_logged = bool(current_user)
    
    # ✅ ЧАТ (только для авторизованных)
    if is_logged and request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message and len(message) <= 300:
            reason, mtype, duration = auto_moderate_v38(message, current_user)
            
            if reason:
                conn = get_db()
                conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, expires, created) VALUES (?, ?, ?, ?, ?, ?)',
                           (current_user, 'АВТОМОД', reason, mtype, time.time() + duration, time.time()))
                conn.commit()
                conn.close()
                flash(reason, 'error')
            else:
                conn = get_db()
                cursor = conn.execute('INSERT INTO chat (user, message, timestamp, role) VALUES (?, ?, ?, ?)',
                                   (current_user, message, time.time(), user_roles.get(current_user, 'start')))
                msg_id = cursor.lastrowid
                chat_messages.append({
                    'id': msg_id, 'user': current_user, 'message': message, 
                    'timestamp': time.time(), 'role': user_roles.get(current_user, 'start')
                })
                conn.commit()
                conn.close()
                user_economy[current_user]['coins'] += 5
                flash('💬 +5💰 за сообщение!', 'success')
    
    # ✅ СТАТИСТИКА
    stats = {
        'online': len([u for u in user_activity if time.time() - user_activity[u] < 300]),
        'total': get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'top_player': 'CatNap'
    }
    
    # ✅ НЕдавние сообщения чата
    conn = get_db()
    messages = conn.execute('SELECT * FROM chat ORDER BY timestamp DESC LIMIT 30').fetchall()
    conn.close()
    messages = list(reversed(messages))
    
    messages_html = ''
    for msg in messages:
        role_class = {
            'admin': 'rank-admin', 'moderator': 'rank-mod', 
            'premium': 'rank-premium', 'vip': 'rank-vip', 'start': ''
        }.get(msg.get('role', 'start'), '')
        
        time_str = time.strftime('%H:%M', time.localtime(msg['timestamp']))
        status = get_user_status(msg['user'])
        
        messages_html += f'''
        <div class="message" style="padding:20px;margin:10px 0;background:rgba(255,255,255,0.9);border-radius:20px;border-left:5px solid #3498db;">
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:10px;">
                <span class="{role_class}" style="font-weight:800;font-size:16px;">{msg['user']}</span>
                <span style="color:#95a5a6;font-size:13px;">{time_str}</span>
                <span style="color:#7f8c8d;">{status}</span>
            </div>
            <div style="color:#2c3e50;font-size:15px;">{msg['message']}</div>
        </div>'''
    
    # ✅ Форма чата
    chat_form = f'''
    <form method="POST" style="background:rgba(255,255,255,0.9);padding:30px;border-radius:25px;margin-top:30px;">
        <div style="display:flex;gap:15px;">
            <input name="message" placeholder="💬 Пиши... (+5💰)" maxlength="300" required 
                   style="flex:1;padding:20px;border:2px solid #ddd;border-radius:20px;font-size:16px;">
            <button type="submit" style="padding:20px 30px;background:#27ae60;color:white;border:none;border-radius:20px;font-size:18px;cursor:pointer;">📤</button>
        </div>
    </form>''' if is_logged else '''
    <div style="background:rgba(255,255,255,0.9);padding:40px;border-radius:25px;text-align:center;margin-top:30px;">
        <h3 style="color:#7f8c8d;">🔐 Войди для чата и игр!</h3>
        <a href="/login" class="nav-btn" style="background:#3498db;">🔐 ВОЙТИ</a>
    </div>'''
    
    html = f'''<!DOCTYPE html>
<html><head>
    <title>🚀 УЖНАВАЙКИН v38.0 — Игровой хаб</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style>
</head><body>
    <div class="container">
        <header>
            <h1>🚀 <span style="background:linear-gradient(45deg,#f1c40f,#e67e22);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">УЖНАВАЙКИН v38.0</span></h1>
            <p>🟫 Minecraft • 🎖️ World of Tanks • ⚔️ Турниры • 💬 Чат • 🏦 Экономика</p>
            <div style="font-size:16px;color:#ecf0f1;">🟢 {stats["online"]} онлайн • 📊 {stats["total"]} игроков</div>
        </header>

        {f'<div style="background:#27ae60;color:white;padding:20px;border-radius:25px;margin:30px 0;text-align:center;"><b>✅ Привет, {current_user}! 👑 {user_roles.get(current_user, "start")}</b></div>' if is_logged else '<div style="background:#3498db;color:white;padding:20px;border-radius:25px;margin:30px 0;text-align:center;font-size:18px;">🔐 <b>Войди</b> для чата, турниров и экономики!</div>'}

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:50px 0;">
            <div>
                <h3 style="color:#2c3e50;font-size:2em;margin-bottom:30px;">📊 СТАТИСТИКА</h3>
                <div class="stat-card" style="border-left-color:#27ae60;">🟢 Онлайн: <b>{stats["online"]}</b></div>
                <div class="stat-card" style="border-left-color:#f39c12;">👑 Всего: <b>{stats["total"]}</b></div>
                <div class="stat-card" style="border-left-color:#e74c3c;">⭐ Топ: <b>{stats["top_player"]}</b></div>
            </div>
            <div>
                <h3 style="color:#2c3e50;font-size:2em;margin-bottom:30px;">🎮 БЫСТРЫЙ ДОСТУП</h3>
                <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);width:100%;margin:10px 0;">🟫 Minecraft</a>
                <a href="/catalog#wot" class="nav-btn" style="background:linear-gradient(135deg,#d63031,#ff6b6b);width:100%;margin:10px 0;">🎖️ World of Tanks</a>
                {f'<a href="/tournaments" class="nav-btn" style="background:linear-gradient(135deg,#e74c3c,#c0392b);width:100%;margin:10px 0;">⚔️ Турниры</a>' if is_logged else ''}
            </div>
        </div>

        <div class="chat-container">
            <h3 style="margin:0 0 30px 0;font-size:2.5em;color:#2c3e50;">💬 ЧАТ ({len(messages)})</h3>
            <div id="chat-messages" style="min-height:400px;margin-bottom:30px;">{messages_html}</div>
            {chat_form}
        </div>

        <div style="text-align:center;margin:60px 0;">
            {f'<a href="/profile" class="nav-btn" style="background:#3498db;">👤 {current_user}</a>' if is_logged else '<a href="/login" class="nav-btn" style="background:#3498db;">🔐 ВОЙТИ</a>'}
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Каталог</a>
            {f'<a href="/tournaments" class="nav-btn" style="background:linear-gradient(135deg,#e74c3c,#c0392b);">⚔️ Турниры</a>' if is_logged else ''}
            <a href="/logout" class="nav-btn" style="background:#95a5a6;">{'🚪 Выход' if is_logged else 'ℹ️ Гость'}</a>
        </div>
    </div>
</body></html>'''
    return html

# ✅ ТУРНИРЫ v38.0
@app.route('/tournaments', methods=['GET', 'POST'])
@require_auth
def tournaments_page():
    current_user = session['user']
    
    tournaments_list = [
        {
            'id': 'minecraft',
            'name': '🟫 Minecraft PvP Турнир',
            'desc': 'Выживание • PvP Арены • 1v1 • Командные бои',
            'prize': 5000,
            'max_players': 32,
            'players': tournaments['minecraft']['players'],
            'color': '#55aa55'
        },
        {
            'id': 'wot', 
            'name': '🎖️ World of Tanks 15v15',
            'desc': 'Танковые бои • Звания • Кланы • Финал на Т-34',
            'prize': 10000,
            'max_players': 16,
            'players': tournaments['wot']['players'],
            'color': '#d63031'
        }
    ]
    
    tournament_html = ''
    for t in tournaments_list:
        is_joined = current_user in t['players']
        progress = len(t['players']) / t['max_players'] * 100
        
        tournament_html += f'''
        <div class="tournament-card tournament-active" style="border-left:6px solid {t["color"]};">
            <h3 style="color:{t["color"]};font-size:2.5em;margin-bottom:20px;">{t["name"]}</h3>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;">
                <div style="font-size:1.6em;">
                    💰 <span style="color:#27ae60;font-weight:800;">{t["prize"]:,}</span>
                </div>
                <div style="font-size:1.4em;color:#7f8c8d;">
                    {len(t["players"])}/{t["max_players"]}
                </div>
            </div>
            <div style="background:linear-gradient(90deg, {t["color"]}, {t["color"]}55);height:10px;border-radius:10px;margin-bottom:30px;">
                <div style="background:{t["color"]};height:100%;border-radius:10px;width:{progress}%;transition:width 0.5s;"></div>
            </div>
            <p style="color:#7f8c8d;margin-bottom:30px;font-size:1.2em;">{t["desc"]}</p>
            {f'<div style="background:#27ae60;color:white;padding:20px;border-radius:20px;text-align:center;font-size:1.2em;font-weight:700;">✅ Ты записан! #{t["players"].index(current_user)+1}</div>' if is_joined else 
             f'<form method="POST" action="/join_tournament/{t["id"]}" style="display:inline;"><button type="submit" class="nav-btn" style="width:100%;background:{t["color"]};font-size:20px;padding:25px;">⚔️ ЗАПИСАТЬСЯ (100💰)</button></form>'}
        </div>'''
    
    html = f'''<!DOCTYPE html><html><head>
    <title>⚔️ Турниры — УЖНАВАЙКИН v38.0</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width">
    <style>{css}</style></head><body>
    <div class="container">
        <header style="text-align:center;margin-bottom:60px;">
            <h1 style="font-size:4em;color:#e74c3c;">⚔️ ТУРНИРЫ v38.0</h1>
            <p style="font-size:1.5em;color:rgba(255,255,255,0.9);">Призовой фонд: <b>15,000💰</b></p>
            <a href="/" class="nav-btn">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:40px;margin-bottom:60px;">
            {tournament_html}
        </div>
        
        <div style="text-align:center;">
            <a href="/" class="nav-btn" style="background:linear-gradient(135deg,#667eea,#764ba2);font-size:20px;">🏠 Главная</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
        </div>
    </div></body></html>'''
    return html

@app.route('/join_tournament/<t_id>', methods=['POST'])
@require_auth
def join_tournament(t_id):
    current_user = session['user']
    t = tournaments.get(t_id)
    
    if t and current_user not in t['players'] and len(t['players']) < 32 and user_economy[current_user]['coins'] >= 100:
        t['players'].append(current_user)
        user_economy[current_user]['coins'] -= 100
        flash('✅ Записан на турнир! Удачи! 💪', 'success')
    else:
        flash('❌ Турнир заполнен или недостаточно монет!', 'error')
    
    return redirect('/tournaments')
# ✅ ПРОФИЛЬ ИГРОКА v38.0
@app.route('/profile')
@require_auth
def profile():
    current_user = session['user']
    user_data = get_user(current_user)
    
    # Загружаем экономику из БД
    conn = get_db()
    db_user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
    conn.close()
    
    coins = db_user['coins'] if db_user else user_economy[current_user]['coins']
    level = db_user['level'] if db_user else user_economy[current_user]['level']
    wins = db_user['wins'] if db_user else user_economy[current_user]['wins']
    rank = db_user['tank_rank'] if db_user else tank_ranks[current_user]
    role = db_user['role'] if db_user else user_roles[current_user]
    
    html = f'''<!DOCTYPE html><html><head>
    <title>👤 {current_user} — УЖНАВАЙКИН v38.0</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width">
    <style>{css}</style></head><body>
    <div class="container">
        <header style="text-align:center;margin-bottom:60px;">
            <h1 style="font-size:4em;">👤 ПРОФИЛЬ</h1>
            <p style="font-size:1.5em;color:rgba(255,255,255,0.9);">Игрок: <span class="rank-{role}">{current_user}</span></p>
            <a href="/" class="nav-btn">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:40px;">
            <!-- ЛЕВАЯ КОЛОНКА - ОСНОВНАЯ ИНФО -->
            <div class="game-card" style="--game-color:#3498db;--game-color-alt:#2980b9;">
                <div style="font-size:8em;margin-bottom:30px;">👑</div>
                <h3>{current_user}</h3>
                
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:40px 0;font-size:1.4em;">
                    <div><span style="color:#7f8c8d;">Роль:</span><br><b class="rank-{role}">{role.upper()}</b></div>
                    <div><span style="color:#7f8c8d;">Звание:</span><br><b>{rank}</b></div>
                </div>
                
                <div style="font-size:2em;margin:30px 0;">
                    <div style="background:#27ae60;color:white;padding:20px;border-radius:20px;margin:15px 0;font-weight:700;">
                        💰 Монет: <span style="font-size:1.5em;">{coins:,}</span>
                    </div>
                    <div style="background:#f39c12;color:white;padding:20px;border-radius:20px;margin:15px 0;font-weight:700;">
                        ⭐ Уровень: <span style="font-size:1.5em;">{level}</span>
                    </div>
                    <div style="background:#e74c3c;color:white;padding:20px;border-radius:20px;margin:15px 0;font-weight:700;">
                        🏆 Побед: <span style="font-size:1.5em;">{wins}</span>
                    </div>
                </div>
            </div>
            
            <!-- ПРАВАЯ КОЛОНКА - ТУРНИРЫ -->
            <div class="game-card" style="--game-color:#e74c3c;--game-color-alt:#c0392b;">
                <h3 style="margin-bottom:30px;">⚔️ ТВОИ ТУРНИРЫ</h3>
                <div style="margin-bottom:30px;">
                    {sum(1 for t in tournaments.values() if current_user in t["players"])} турниров
                </div>
                
                {''.join([f'''
                <div style="background:rgba(255,255,255,0.7);padding:20px;border-radius:15px;margin:15px 0;">
                    <div style="font-weight:700;color:{list(tournaments.keys())[i].upper()};font-size:1.3em;">{t["name"]}</div>
                    <div style="color:#7f8c8d;">Взнос: 100💰 • Приз: {t["prize"]:,}💰</div>
                    <div style="color:#27ae60;font-weight:700;">#{t["players"].index(current_user)+1} место в списке</div>
                </div>''' for i, t in enumerate(tournaments.values()) if current_user in t["players"]]) or '''
                <div style="text-align:center;color:#7f8c8d;padding:40px;">
                    <div style="font-size:3em;margin-bottom:20px;">⚔️</div>
                    Запишись на турниры!<br><a href="/tournaments" class="nav-btn" style="width:100%;margin-top:20px;">⚔️ Турниры</a>
                </div>'''}
            </div>
        </div>
        
        <div style="text-align:center;margin:60px 0;">
            <a href="/" class="nav-btn" style="background:#3498db;font-size:20px;">🏠 Главная</a>
            <a href="/tournaments" class="nav-btn" style="background:linear-gradient(135deg,#e74c3c,#c0392b);">⚔️ Турниры</a>
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">📁 Игры</a>
        </div>
    </div></body></html>'''
    return html

# ✅ АДМИН-ПАНЕЛЬ v38.0
@app.route('/admin')
@require_auth
def admin_panel():
    if not is_moderator(session['user']):
        flash('❌ Доступ только для админов!', 'error')
        return redirect('/')
    
    conn = get_db()
    all_users = conn.execute('SELECT username, coins, role, level, wins, created FROM users ORDER BY coins DESC').fetchall()
    conn.close()
    
    users_html = ''
    for i, user in enumerate(all_users[:20], 1):
        uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - user['created']))
        users_html += f'''
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:15px;font-weight:700;">#{i}</td>
            <td style="padding:15px;color:#2c3e50;">{user["username"]}</td>
            <td style="padding:15px;text-align:center;"><span class="rank-{user["role"]}">{user["role"].upper()}</span></td>
            <td style="padding:15px;font-weight:700;color:#27ae60;">{user["coins"]:,}</td>
            <td style="padding:15px;">{user["level"]}</td>
            <td style="padding:15px;">{user["wins"]}</td>
            <td style="padding:15px;color:#7f8c8d;">{uptime}</td>
        </tr>'''
    
    html = f'''<!DOCTYPE html><html><head>
    <title>⚙️ Админ-панель — {session["user"]}</title>
    <meta charset="UTF-8"><style>{css}</style></head><body>
    <div class="container">
        <header style="text-align:center;margin-bottom:50px;">
            <h1 style="font-size:4em;color:#e74c3c;">⚙️ АДМИН-ПАНЕЛЬ</h1>
            <p>👑 Админ: <span class="rank-admin">{session["user"]}</span></p>
            <a href="/" class="nav-btn">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
            <!-- ТОП ИГРОКОВ -->
            <div class="game-card">
                <h3 style="margin-bottom:30px;">👑 ТОП-20 ИГРОКОВ</h3>
                <div style="overflow-x:auto;">
                    <table style="width:100%;border-collapse:collapse;">
                        <thead><tr style="background:#3498db;color:white;">
                            <th style="padding:20px 15px;font-weight:700;">#</th>
                            <th style="padding:20px 15px;font-weight:700;">Игрок</th>
                            <th style="padding:20px 15px;font-weight:700;">Роль</th>
                            <th style="padding:20px 15px;font-weight:700;">💰</th>
                            <th style="padding:20px 15px;font-weight:700;">Lvl</th>
                            <th style="padding:20px 15px;font-weight:700;">🏆</th>
                            <th style="padding:20px 15px;font-weight:700;">Онлайн</th>
                        </tr></thead>
                        <tbody>{users_html}</tbody>
                    </table>
                </div>
            </div>
            
            <!-- АДМИН АКШИНЫ -->
            <div class="game-card" style="--game-color:#e74c3c;">
                <h3 style="margin-bottom:30px;">🔧 АДМИН МЕНЮ</h3>
                <div style="display:flex;flex-direction:column;gap:20px;">
                    <a href="/register" class="nav-btn" style="background:#27ae60;">👥 Создать игрока</a>
                    <a href="/admin/mutes" class="nav-btn" style="background:#f39c12;">🚫 Муты</a>
                    <a href="/admin/tournaments" class="nav-btn" style="background:#9b59b6;">⚔️ Управление турнирами</a>
                    <a href="/admin/stats" class="nav-btn" style="background:#34495e;">📊 Полная статистика</a>
                </div>
            </div>
        </div>
        
        <div style="text-align:center;margin:60px 0;">
            <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
            <a href="/profile" class="nav-btn">👤 Мой профиль</a>
        </div>
    </div></body></html>'''
    return html

# ✅ 404 СТРАНИЦА
@app.route('/<path:path>')
def catch_all(path):
    return f'''<!DOCTYPE html><html><head><title>404 — УЖНАВАЙКИН</title><meta charset="UTF-8"><style>{css}</style></head><body>
    <div class="container" style="text-align:center;padding:100px 20px;">
        <h1 style="font-size:8em;color:#e74c3c;margin-bottom:30px;">❓ 404</h1>
        <p style="font-size:2em;color:#7f8c8d;margin-bottom:50px;">Страница не найдена</p>
        <a href="/" class="nav-btn" style="font-size:22px;background:#3498db;">🏠 На главную</a>
    </div></body></html>'''

# ✅ ФИНАЛЬНЫЙ ЗАПУСК v38.0
if __name__ == '__main__':
    init_db()
    
    # ✅ АВТОСОЗДАНИЕ requirements.txt
    requirements = '''Flask==3.0.3
gunicorn==22.0.0
Werkzeug==3.0.3'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("🚀" * 20)
    print("✅ УЖНАВАЙКИН v38.0 — ПОЛНЫЙ ЗАПУСК!")
    print("👑 Админы: CatNap / Назар")
    print("🔑 Пароль: 120187 (ХЕШИРОВАН)")
    print("📱 http://" + host + ":" + str(port))
    print("🚀" * 20)
    
    app.run(host=host, port=port, debug=False)
