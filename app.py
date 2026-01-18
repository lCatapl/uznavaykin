#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v43.0 — 15+ НОВЫХ СИСТЕМ + СУПЕР-АДМИНКА
import os, time, random, re, sqlite3, json, logging, hashlib, asyncio
from datetime import datetime, timedelta
from flask import Flask, request, session, redirect, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
from collections import defaultdict, deque, Counter
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps, lru_cache
import threading
from typing import Dict, List, Tuple, Optional

# ✅ ЛОГГИНГ + МЕТРИКИ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaykin-v43-mega-features-2026')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=False)

# ✅ CSS v43.0 (PWA + Particles + Темы)
PREMIUM_CSS_V43 = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json">
<style>*{margin:0;padding:0;box-sizing:border-box;}
:root{--primary-gradient:linear-gradient(135deg,#1e3c72 0%,#2a5298 50%,#f093fb 100%);--success:#00d4aa;--danger:#ff4757;--warning:#ffa502;--info:#3742fa;--dark:#2f3542;--light:#f1f2f6;--shadow:0 20px 60px rgba(0,0,0,0.2);--glass:rgba(255,255,255,0.95);}
[data-theme="dark"]{--glass:rgba(47,53,66,0.95);--light:#2f3542;}
body{font-family:'Segoe UI',sans-serif;background:var(--primary-gradient);min-height:100vh;color:var(--dark);transition:all 0.3s;}
.theme-toggle{position:fixed;top:20px;right:20px;z-index:999;background:var(--glass);padding:15px;border-radius:50px;cursor:pointer;font-size:20px;box-shadow:var(--shadow);}
.container{max-width:1600px;margin:0 auto;padding:20px;}
header{text-align:center;margin-bottom:60px;padding:50px 0;background:var(--glass);backdrop-filter:blur(20px);border-radius:30px;box-shadow:var(--shadow);}
header h1{font-size:4.5em;font-weight:900;background:linear-gradient(45deg,#ff6b6b,#feca57,#48dbfb,#00d4aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:rainbow 4s ease infinite;}
@keyframes rainbow{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.premium-badge{background:linear-gradient(135deg,#ffd700,#ffed4e);color:#1a1a2e;padding:12px 30px;border-radius:50px;font-weight:800;font-size:18px;display:inline-block;box-shadow:0 5px 20px rgba(255,215,0,0.4);animation:pulse 2s infinite;}
@keyframes pulse{0%{transform:scale(1);}50%{transform:scale(1.05);}100%{transform:scale(1);}}
.nav-btn{display:inline-block;padding:20px 40px;margin:10px;border-radius:50px;text-decoration:none;font-weight:800;font-size:17px;color:white;transition:all 0.4s;border:3px solid transparent;min-width:180px;background:linear-gradient(135deg,var(--info),#5a6fd8);}
.nav-btn:hover{transform:translateY(-8px) scale(1.05);box-shadow:var(--shadow);}
.game-card{background:var(--glass);border-radius:25px;padding:40px;margin:20px 0;box-shadow:var(--shadow);transition:all 0.4s;backdrop-filter:blur(25px);}
.game-card:hover{transform:translateY(-10px);box-shadow:0 30px 80px rgba(0,0,0,0.3);}
.role-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:15px;margin:20px 0;}
.role-card{padding:20px;border-radius:20px;text-align:center;font-weight:800;font-size:16px;box-shadow:var(--shadow);transition:all 0.3s;}
.role-card:hover{transform:scale(1.05);}
.role-start{background:rgba(108,117,125,0.2);color:#495057;border-left:6px solid #6c757d;}
.role-vip,.role-premium{background:linear-gradient(135deg,#ffd700,#ffed4e);color:#1a1a2e;border-left:6px solid #ffd700;}
.role-mod{background:linear-gradient(135deg,var(--success),#00b894);color:white;border-left:6px solid var(--success);}
.role-admin{background:linear-gradient(135deg,var(--danger),#ff3742);color:white;border-left:6px solid var(--danger);animation:pulse-glow 3s infinite;}
@keyframes pulse-glow{0%{box-shadow:0 0 0 0 rgba(255,71,87,0.7);}70%{box-shadow:0 0 0 25px rgba(255,71,87,0);}}
.leaderboard{position:sticky;top:20px;background:var(--glass);border-radius:20px;padding:20px;box-shadow:var(--shadow);}
.particles-canvas{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;}
#chat-messages{max-height:450px;overflow-y:auto;padding:20px;}
.message{padding:20px;margin:15px 0;border-radius:20px;border-left:6px solid var(--info);background:rgba(255,255,255,0.8);transition:all 0.3s;}
.message:hover{transform:translateX(10px);box-shadow:var(--shadow);}
input,select,textarea{width:100%;padding:18px;font-size:16px;border:2px solid #e1e8ed;border-radius:15px;margin-bottom:20px;box-sizing:border-box;background:var(--glass);}
input:focus{outline:none;border-color:var(--info);box-shadow:0 0 20px rgba(55,66,250,0.2);transform:scale(1.02);}
.notification{animation:notify 0.5s ease-out;}
@keyframes notify{0%{transform:translateY(-100px);opacity:0;}100%{transform:translateY(0);opacity:1;}}
.achievement-popup{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:linear-gradient(135deg,var(--success),#00b894);color:white;padding:40px 60px;border-radius:30px;box-shadow:var(--shadow);text-align:center;z-index:1000;display:none;}
@media (max-width:768px){header h1{font-size:3em;}.nav-btn{padding:15px 25px;min-width:140px;}.role-stats{grid-template-columns:1fr;}}</style>
<script>let particles=[];function createParticles(x,y,color="#ffd700"){for(let i=0;i<15;i++){particles.push({x,y,vx:Math.random()*10-5,vy:Math.random()*10-5,life:1,size:Math.random()*8+4,color,opacity:1});}}function animateParticles(){const c=document.getElementById('particles');const ctx=c.getContext('2d');c.width=window.innerWidth;c.height=window.innerHeight;ctx.clearRect(0,0,c.width,c.height);particles=particles.filter(p=>p.life>0);particles.forEach(p=>{ctx.save();ctx.globalAlpha=p.opacity;ctx.fillStyle=p.color;ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();p.x+=p.vx;p.y+=p.vy;p.vy+=0.2;p.life-=0.02;p.opacity=p.life;p.size*=0.98;ctx.restore()});requestAnimationFrame(animateParticles);}</script>'''

# ✅ 30+ ЗВАНИЙ v43.0 + ACHIEVEMENTS
RANK_SYSTEM = {
    0: '👶 Новобранец', 1: '🚀 Рядовой', 3: '⭐ Ефрейтор', 7: '⚔️ Капрал',
    15: '🎖️ Мастер-капрал', 30: '👮 Сержант', 50: '🛡️ Штаб-сержант', 80: '💪 Мастер-сержант',
    120: '⭐⭐ Первый сержант', 170: '🎖️🎖️ Сержант-майор', 230: '⚓ Уорэнт-офицер',
    300: '⭐⭐⭐ Младший лейтенант', 380: '⚔️⚔️ Лейтенант', 470: '🎖️🎖️🎖️ Старший лейтенант',
    570: '👑 Капитан', 680: '🌟 Майор', 810: '⭐⭐⭐⭐ Подполковник', 960: '🎖️🎖️🎖️🎖️ Полковник',
    1120: '⚔️⚔️⚔️ Бригадир', 1300: '👑👑 Генерал-майор', 1500: '🌟🌟 Генерал-лейтенант',
    1720: '⭐⭐⭐⭐⭐ Генерал', 1960: '🎖️🎖️🎖️🎖️🎖️ Маршал', 2220: '⚔️⚔️⚔️⚔️ Фельдмаршал', 2500: '👑👑👑 Командор',
    2800: '🌟🌟🌟 Генералиссимус', 3200: '🏆 Легенда', 10000: '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран'
}

ACHIEVEMENTS = {
    'first_chat': {'name': '🗣️ Первый чат', 'reward': 50, 'desc': 'Написал первое сообщение'},
    'chat_master': {'name': '💬 Болтун', 'reward': 500, 'desc': '100 сообщений в чате'},
    'casino_lucky': {'name': '🍀 Удачник', 'reward': 1000, 'desc': 'Выиграл 1000+ в казино'},
    'daily_streak': {'name': '📅 Регулярный', 'reward': 250, 'desc': '7 дней подряд'},
    'tournament_win': {'name': '⚔️ Чемпион', 'reward': 2000, 'desc': 'Победил в турнире'},
    'rich_man': {'name': '💰 Миллионер', 'reward': 5000, 'desc': '1M монет на счету'}
}

# ✅ ГЛОБАЛЬНЫЕ СИСТЕМЫ v43.0
chat_messages = deque(maxlen=1000)
user_activity = defaultdict(float)
user_economy = defaultdict(lambda: {'coins': 1000, 'level': 1, 'wins': 0, 'bank': 0, 'premium': False})
user_achievements = defaultdict(set)
user_streaks = defaultdict(int)
spam_counters = defaultdict(list)
tournaments = {
    'minecraft': {'players': [], 'prize': 5000, 'max_players': 32, 'status': 'active'},
    'wot': {'players': [], 'prize': 10000, 'max_players': 16, 'status': 'active'}
}
casino_history = deque(maxlen=500)
notifications = deque(maxlen=100)
particles_cache = []

# ✅ СУПЕР-БАЗА v43.0 (все таблицы)
class MegaDatabase:
    def __init__(self, db_path='uznavaykin_v43.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON; PRAGMA journal_mode=WAL;')
            return conn
        except: return None
    
    def init_db(self):
        conn = self.get_connection()
        if not conn: return False
        
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 1000, bank INTEGER DEFAULT 0, daily_bonus REAL DEFAULT 0,
                role TEXT DEFAULT 'start', premium INTEGER DEFAULT 0, streak INTEGER DEFAULT 0,
                rank_wins INTEGER DEFAULT 0, tank_rank TEXT DEFAULT 'Новобранец',
                wins INTEGER DEFAULT 0, level INTEGER DEFAULT 1, messages INTEGER DEFAULT 0,
                created REAL DEFAULT 0, last_seen REAL DEFAULT 0,
                casino_wins INTEGER DEFAULT 0, tournament_wins INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0, friends TEXT DEFAULT '[]',
                achievements TEXT DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, message TEXT, 
                timestamp REAL, role TEXT, rank TEXT, room TEXT DEFAULT 'global'
            );
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, muted_by TEXT, 
                reason TEXT, mtype TEXT, duration INTEGER, expires REAL, created REAL
            );
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, ach_id TEXT,
                reward INTEGER, unlocked REAL, FOREIGN KEY(username) REFERENCES users(username)
            );
            CREATE TABLE IF NOT EXISTS daily_logins (
                username TEXT, date TEXT, bonus INTEGER, PRIMARY KEY(username, date)
            );
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, amount INTEGER,
                type TEXT, interest REAL, timestamp REAL
            );
            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, leader TEXT,
                members INTEGER DEFAULT 1, coins INTEGER DEFAULT 0, created REAL
            );
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat(timestamp);
            CREATE INDEX IF NOT EXISTS idx_mutes_expires ON mutes(expires);
            CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(username);
        ''')
        
        # ✅ СУПЕР-АДМИНЫ v43
        admin_hash = generate_password_hash('120187')
        super_admins = [
            ('CatNap', admin_hash, 'admin', True, 15000, '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран', 100000, 500),
            ('Назар', admin_hash, 'admin', True, 15000, '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран', 100000, 500)
        ]
        for username, pwd, role, premium, rank_wins, rank, coins, streak in super_admins:
            conn.execute('''INSERT OR REPLACE INTO users 
                (username, password_hash, role, premium, rank_wins, tank_rank, coins, streak, created) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (username, pwd, role, int(premium), rank_wins, rank, coins, streak, time.time()))
        
        conn.commit()
        conn.close()
        logger.info("✅ v43.0 MegaDB готова! 2 супер-админа!")
        return True

# ✅ ИНИЦИАЛИЗАЦИЯ
db = MegaDatabase()

# ✅ СУПЕР-ФУНКЦИИ v43.0
def get_user(username: str) -> Optional[sqlite3.Row]:
    conn = db.get_connection()
    if not conn: return None
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

@lru_cache(maxsize=128)
def get_role_stats() -> Dict[str, int]:
    """Расширенная статистика ролей + Premium"""
    conn = db.get_connection()
    if not conn: 
        return {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 2}
    
    stats = {
        'start': conn.execute("SELECT COUNT(*) FROM users WHERE role='start'").fetchone()[0],
        'vip': conn.execute("SELECT COUNT(*) FROM users WHERE role='vip'").fetchone()[0],
        'premium': conn.execute("SELECT COUNT(*) FROM users WHERE premium=1").fetchone()[0],
        'moderator': conn.execute("SELECT COUNT(*) FROM users WHERE role='moderator'").fetchone()[0],
        'admin': conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
    }
    conn.close()
    return stats

def get_player_rank(wins: int) -> str:
    for threshold, rank_name in sorted(RANK_SYSTEM.items(), reverse=True):
        if wins >= threshold: return rank_name
    return RANK_SYSTEM[0]

def advanced_moderation(message: str, username: str, history: List[str]) -> Tuple[Optional[str], str, int]:
    """🚫 СУПЕР-МОДЕРАТОР v43 (3 уровня)"""
    message_lower = message.lower().strip()
    
    # 1️⃣ МАТ = +10 мин (600 сек)
    bad_words = [r'\\bсук[аиы]\\b', r'\\bпизд[ауео][нц]?\\b', r'\\bху[йя]\\b', r'\\bбл[яь][дт]\\b']
    for pattern in bad_words:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат = 10 минут!", "mat", 600
    
    # 2️⃣ СПАМ (3+ одинаковых сообщений)
    recent = history[-10:]  # Последние 10 сообщений
    if len([m for m in recent if m == message]) >= 3:
        return "🚫 Спам (3+ одинаковых) = 15 минут!", "spam", 900
    
    # 3️⃣ ФЛУД/РЕКЛАМА = 30 мин
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
    if len(links) > 0 or len(message) < 3 and len(recent) >= 5:
        return "🚫 Флуд/Реклама = 30 минут!", "flood", 1800
    
    return None, None, 0

def grant_achievement(username: str, ach_id: str) -> bool:
    """💎 Выдача достижения + монеты"""
    if ach_id in user_achievements[username]: return False
    
    user = get_user(username)
    if not user: return False
    
    reward = ACHIEVEMENTS[ach_id]['reward']
    conn = db.get_connection()
    if conn:
        conn.execute('INSERT INTO achievements (username, ach_id, reward, unlocked) VALUES (?, ?, ?, ?)',
                    (username, ach_id, reward, time.time()))
        conn.execute('UPDATE users SET coins = coins + ?, achievements = json_insert(COALESCE(achievements,\'[]\'), \'$\', ?) WHERE username = ?',
                    (reward, json.dumps(list(user_achievements[username]) + [ach_id]), username))
        conn.commit()
        conn.close()
    
    user_achievements[username].add(ach_id)
    notifications.append({'user': username, 'type': 'achievement', 'title': ACHIEVEMENTS[ach_id]['name'], 'reward': reward})
    logger.info(f"💎 {username} получил '{ACHIEVEMENTS[ach_id]['name']}' (+{reward}💰)")
    return True

def get_daily_bonus(username: str) -> Tuple[int, bool]:
    """📅 Ежедневный бонус + стрик"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = db.get_connection()
    if not conn: return 0, False
    
    streak = conn.execute('SELECT streak FROM users WHERE username = ?', (username,)).fetchone()
    current_streak = streak['streak'] if streak else 0
    
    last_bonus = conn.execute('SELECT date FROM daily_logins WHERE username = ? ORDER BY date DESC LIMIT 1', (username,)).fetchone()
    is_new_day = not last_bonus or last_bonus['date'] != today
    
    if is_new_day:
        bonus = 100 * (current_streak + 1)
        new_streak = current_streak + 1 if last_bonus and (datetime.now().date() - datetime.strptime(last_bonus['date'], '%Y-%m-%d').date()).days == 1 else 1
        
        conn.execute('INSERT OR REPLACE INTO daily_logins (username, date, bonus) VALUES (?, ?, ?)', (username, today, bonus))
        conn.execute('UPDATE users SET coins = coins + ?, streak = ?, daily_bonus = ? WHERE username = ?', 
                    (bonus, new_streak, time.time(), username))
        conn.commit()
        
        grant_achievement(username, 'daily_streak') if new_streak >= 7 else None
        conn.close()
        return bonus, True
    conn.close()
    return 0, False

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """🏆 Глобальный лидерборд"""
    conn = db.get_connection()
    if not conn: return []
    top = conn.execute('''
        SELECT username, coins, tank_rank, premium, streak 
        FROM users ORDER BY coins DESC, streak DESC LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [{'username': u['username'], 'coins': u['coins'], 'rank': u['tank_rank'], 'premium': u['premium'], 'streak': u['streak']} for u in top]

def is_authenticated():
    return bool(session.get('user') and get_user(session.get('user')))

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            session['login_redirect'] = request.path
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def is_moderator(username: str) -> bool:
    user = get_user(username)
    return user and user['role'] in ['admin', 'moderator']

# ✅ PWA MANIFEST
@app.route('/manifest.json')
def manifest():
    return {
        "name": "🚀 Узнавайкин v43.0",
        "short_name": "УЗv43",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}],
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#1e3c72",
        "background_color": "#f1f2f6"
    }

print("🚀" * 40)
print("✅ УЗНАВАЙКИН v43.0 ЧАСТЬ 1/3 — 15+ МЕГА-ФИЧ!")
print("💎 Достижения • Ежедневки • Лидерборд • Супер-Модератор")
print("👑 CatNap/Назар (120187) — Ветераны (100k💰 + 500 стрик!)")
# ✅ Socket.IO ЧАТ v43 (Реал-тайм + VIP комнаты)
@socketio.on('join')
def on_join(data):
    username = session.get('user', 'guest')
    room = data['room']
    join_room(room)
    user = get_user(username)
    emit('status', {'msg': f'{username} зашёл в {room}'}, room=room)
    logger.info(f"🔗 {username} подключился к {room}")

@socketio.on('leave')
def on_leave(data):
    username = session.get('user', 'guest')
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{username} покинул {room}'}, room=room)

@socketio.on('message')
def handle_message(data):
    username = session.get('user')
    if not username or is_user_muted(username): return
    
    message = data['message']
    room = data.get('room', 'global')
    
    # ✅ СУПЕР-МОДЕРАТОР v43
    user_history = spam_counters[username]
    reason, mtype, duration = advanced_moderation(message, username, user_history)
    
    if reason:
        emit('system_message', {'msg': f"{username}: {reason}", 'type': 'mute'}, room=room)
        if duration > 0:
            conn = db.get_connection()
            conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, duration, expires, created) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (username, 'AUTO', reason, mtype, duration, time.time() + duration, time.time()))
            conn.commit()
            conn.close()
        return
    
    # ✅ Сохранить + монеты + достижения
    user = get_user(username)
    chat_messages.append({
        'user': username, 'rank': user['tank_rank'], 'role': user['role'], 
        'message': message, 'timestamp': time.time(), 'premium': user['premium'], 'room': room
    })
    
    conn = db.get_connection()
    if conn:
        conn.execute('INSERT INTO chat (user, message, timestamp, role, rank, room) VALUES (?, ?, ?, ?, ?, ?)',
                    (username, message, time.time(), user['role'], user['tank_rank'], room))
        coins = 5 + (15 if user['premium'] else 0)
        conn.execute('UPDATE users SET coins = coins + ?, messages = messages + 1 WHERE username = ?', (coins, username))
        
        # ✅ Достижения
        msg_count = conn.execute('SELECT messages FROM users WHERE username = ?', (username,)).fetchone()['messages']
        if msg_count == 1: grant_achievement(username, 'first_chat')
        elif msg_count == 100: grant_achievement(username, 'chat_master')
        
        conn.commit()
        conn.close()
    
    # ✅ Отправить всем
    emit('message', {
        'user': username, 'rank': user['tank_rank'], 'role': user['role'],
        'message': message, 'timestamp': time.time(), 'premium': user['premium']
    }, room=room)

# ✅ ЛОГИН v43 (PWA + рефералки)
@app.route('/login', methods=['GET', 'POST'])
def login():
    ref = request.args.get('ref')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            save_user_activity(username)
            
            # ✅ Рефералка
            if ref and ref != username:
                conn = db.get_connection()
                if conn:
                    conn.execute('UPDATE users SET coins = coins + 500, referrals = referrals + 1 WHERE username IN (?, ?)',
                               (username, ref))
                    conn.commit()
                    conn.close()
                notifications.append({'user': username, 'type': 'referral', 'reward': 500})
            
            return redirect(request.args.get('next', '/'))
    
    ref_link = f"/login?ref={session.get('user', '')}" if session.get('user') else ""
    return f'{PREMIUM_CSS_V43}<div class="container"><div class="game-card" style="max-width:500px;margin:100px auto;">' + \
           f'<h1 style="font-size:5em;">🔐 ВХОД v43</h1><form method="POST"><input name="username" placeholder="👤 Ник" required>' + \
           f'<input name="password" type="password" placeholder="🔒 Пароль" required>' + \
           f'<button type="submit" class="nav-btn" style="width:100%;background:var(--success);">🚀 ВОЙТИ</button></form>' + \
           f'<div style="margin-top:40px;"><div class="premium-badge">👑 CatNap / Назар</div></div>' + \
           f'<div style="margin-top:20px;font-size:14px;"><span>Твоя рефка: </span><code style="background:var(--glass);padding:5px;">{ref_link}</code></div></div></div>'

# ✅ ГЛАВНАЯ v43 (SocketIO + Лидерборд + Темы)
@app.route('/', methods=['GET', 'POST'])
@require_auth
def index():
    current_user = session['user']
    user = get_user(current_user)
    role_stats = get_role_stats()
    leaderboard = get_leaderboard(5)
    
    # ✅ Ежедневный бонус
    bonus, claimed = get_daily_bonus(current_user)
    
    lb_html = ''.join(f'''
        <div style="display:flex;align-items:center;gap:15px;padding:15px;background:rgba(0,0,0,0.1);border-radius:15px;margin:10px 0;">
            <div style="font-size:2em;font-weight:900;">#{i+1}</div>
            <div style="flex:1;">{u["username"]}</div>
            <div style="color:var(--success);font-weight:800;">{u["coins"]:,}💰</div>
            {f'<span class="premium-badge" style="font-size:14px;">PREMIUM</span>' if u["premium"] else ""}
        </div>''' for i, u in enumerate(leaderboard))
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🚀 Узнавайкин v43.0</title><script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script></head><body>
<canvas id="particles" class="particles-canvas"></canvas>
<div class="theme-toggle" onclick="toggleTheme()">🌙</div>
<div class="achievement-popup" id="achievementPopup"><h2 id="achTitle"></h2><p id="achReward"></p><button class="nav-btn" onclick="hideAchievement()">OK</button></div>
<div class="container">
    <header>
        <h1>🚀 УЗНАВАЙКИН <span style="font-size:0.4em;">v43.0</span> 
            <span class="premium-badge">MEGA</span></h1>
        <div class="role-stats">
            <div class="role-card role-start">👤 {role_stats['start']}</div>
            <div class="role-card role-vip">⭐ {role_stats['vip']}</div>
            <div class="role-card role-premium">💎 {role_stats['premium']}</div>
            <div class="role-card role-mod">🛡️ {role_stats['moderator']}</div>
            <div class="role-card role-admin">👑 {role_stats['admin']}</div>
        </div>
        {f'<div style="font-size:24px;margin-top:20px;">🎉 +{bonus:,}💰 Ежедневка! (стрик: {user["streak"]}🔥)</div>' if bonus > 0 else ""}
    </header>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:40px;">
        <!-- ✅ Socket.IO ЧАТ -->
        <div class="game-card">
            <h3>💬 ГЛОБАЛЬНЫЙ ЧАТ <span style="font-size:14px;">({len(chat_messages)})</span></h3>
            <div id="chat-messages" style="height:450px;overflow-y:auto;"></div>
            <div id="chat-form">
                <input id="chat-input" placeholder="💬 Пиши (+{5+(15 if user['premium'] else 0)}💰)" maxlength="300">
                <button onclick="sendMessage()" class="nav-btn" style="width:120px;">📤</button>
            </div>
        </div>
        
        <!-- ✅ ЛИДЕРБОРД + МЕНЮ -->
        <div class="leaderboard">
            <h3 style="margin-bottom:20px;">🏆 ТОП-5</h3>
            {lb_html}
            <div style="margin-top:30px;">
                <a href="/daily" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">📅 Ежедневка</a>
                <a href="/leaderboard" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">🏆 Полный топ</a>
                <a href="/bank" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">🏦 Банк</a>
            </div>
        </div>
    </div>
</div>
<script>
const socket = io();
let theme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', theme);
function toggleTheme(){theme=theme==='light'?'dark':'light';localStorage.setItem('theme',theme);document.documentElement.setAttribute('data-theme',theme);}
socket.on('message',msg=>{addMessage(msg);scrollChat();});
socket.on('system_message',msg=>{addSystemMessage(msg.msg);scrollChat();});
function addMessage(msg){
    const div=document.createElement('div');div.className='message';
    div.innerHTML=`<div style="display:flex;gap:12px;align-items:center;"><span style="font-weight:900;">${msg.user}</span>
    <span style="font-size:0.9em;">${msg.rank}</span><span style="color:#95a9a6;">${new Date(msg.timestamp*1000).toLocaleTimeString()}</span>
    ${msg.premium?'💎':''}</div><div>${msg.message}</div>`;
    document.getElementById('chat-messages').appendChild(div);
}
function addSystemMessage(msg){
    const div=document.createElement('div');div.style.cssText='color:var(--danger);font-weight:800;padding:15px;background:rgba(255,71,87,0.1);border-radius:15px;margin:10px 0;';
    div.textContent=msg;div.classList.add('notification');document.getElementById('chat-messages').appendChild(div);
}
function sendMessage(){const input=document.getElementById('chat-input');const msg=input.value.trim();if(msg){socket.emit('message',{message:msg,room:'global'});input.value='';}}
document.getElementById('chat-input').addEventListener('keypress',e=>{{if(e.key==='Enter')sendMessage();}});
function scrollChat(){document.getElementById('chat-messages').scrollTop=document.getElementById('chat-messages').scrollHeight;}
socket.emit('join',{{room:'global'}});
animateParticles();hideAchievement();
</script></body></html>'''

# ✅ РЕФЕРАЛКИ + ДРУЗЬЯ
@app.route('/referrals')
@require_auth
def referrals():
    user = get_user(session['user'])
    ref_link = f"https://{request.host}/login?ref={session['user']}"
    return f'<h1>🤝 РЕФЕРАЛКИ</h1><p>Приглашай: <code>{ref_link}</code></p><p>+500💰 за друга!</p>'

print("🚀 УЗНАВАЙКИН v43.0 ЧАСТЬ 2/3 — SocketIO + Реал-тайм!")
print("✅ Чат мгновенный • Лидерборд • Ежедневки • Темная тема")
# ✅ ЛИДЕРБОРД ПОЛНЫЙ v43
@app.route('/leaderboard')
@require_auth
def leaderboard():
    top_players = get_leaderboard(50)
    lb_html = ''.join(f'''
    <tr style="border-bottom:1px solid rgba(0,0,0,0.1);">
        <td style="padding:15px;text-align:center;font-weight:900;">#{i+1}</td>
        <td style="padding:15px;display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.5em;">{u['username']}</span>
            <span class="rank-display" style="font-size:0.8em;">{u['rank']}</span>
        </td>
        <td style="padding:15px;text-align:right;font-weight:800;color:var(--success);">{u['coins']:,}💰</td>
        <td style="padding:15px;text-align:center;">{u['streak']}🔥</td>
    </tr>''' for i, u in enumerate(top_players))
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🏆 Лидерборд v43</title></head><body>
<div class="container">
    <header><h1>🏆 ГЛОБАЛЬНЫЙ ЛИДЕРБОРД</h1></header>
    <div class="game-card" style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:var(--info);color:white;">
                <th style="padding:20px;font-size:1.2em;">#</th>
                <th style="padding:20px;font-size:1.2em;">ИГРОК</th>
                <th style="padding:20px;font-size:1.2em;">💰 МОНЕТЫ</th>
                <th style="padding:20px;font-size:1.2em;">🔥 СТРИК</th>
            </tr></thead>
            <tbody>{lb_html}</tbody>
        </table>
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ БАНК v43 (5% годовых + ежедневный %)
@app.route('/bank', methods=['GET', 'POST'])
@require_auth
def bank():
    current_user = session['user']
    user = get_user(current_user)
    
    if request.method == 'POST':
        action = request.form.get('action')
        amount = int(request.form.get('amount', 0))
        
        conn = db.get_connection()
        if conn:
            if action == 'deposit' and user['coins'] >= amount:
                conn.execute('UPDATE users SET coins = coins - ?, bank = bank + ? WHERE username = ?', 
                           (amount, amount, current_user))
                conn.execute('INSERT INTO bank_transactions (username, amount, type, timestamp) VALUES (?, ?, ?, ?)',
                           (current_user, amount, 'deposit', time.time()))
            elif action == 'withdraw' and user['bank'] >= amount:
                interest = amount * 0.05  # 5% бонус
                conn.execute('UPDATE users SET coins = coins + ?, bank = bank - ? WHERE username = ?', 
                           (amount + interest, amount, current_user))
                conn.execute('INSERT INTO bank_transactions (username, amount, type, interest, timestamp) VALUES (?, ?, ?, ?, ?)',
                           (current_user, amount, 'withdraw', interest, time.time()))
            conn.commit()
            conn.close()
    
    # ✅ Рассчитать ежедневный %
    daily_interest = user['bank'] * 0.05 / 365
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🏦 Банк v43</title></head><body>
<div class="container">
    <header><h1>🏦 ПРЕМИУМ БАНК <span class="premium-badge">5% ГОДОВЫХ</span></h1></header>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
        <div class="game-card">
            <h3>💰 ТВОЙ СЧЕТ</h3>
            <div style="font-size:3em;text-align:center;margin:40px 0;">
                <div style="color:var(--success);">💳 {user['coins']:,}</div>
                <div style="color:var(--info);">🏦 {user['bank']:,}</div>
                <div style="font-size:1.2em;color:var(--warning);">📈 +{daily_interest:,.0f} в день</div>
            </div>
        </div>
        <div class="game-card">
            <h3>⚡ ОПЕРАЦИИ</h3>
            <form method="POST">
                <input type="hidden" name="action" value="deposit">
                <input name="amount" type="number" min="100" max="{user['coins']}" placeholder="Сумма (мин.100)" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--success);">➤ ПОПОЛНИТЬ</button>
            </form>
            <form method="POST" style="margin-top:20px;">
                <input type="hidden" name="action" value="withdraw">
                <input name="amount" type="number" min="100" max="{user['bank']}" placeholder="Сумма (мин.100)" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--danger);">➤ СНЯТЬ (+5% бонус)</button>
            </form>
        </div>
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ КЛАНЫ v43
@app.route('/clans', methods=['GET', 'POST'])
@require_auth
def clans():
    current_user = session['user']
    
    if request.method == 'POST':
        action = request.form.get('action')
        conn = db.get_connection()
        if action == 'create':
            clan_name = request.form.get('clan_name')
            if conn.execute('SELECT id FROM clans WHERE name = ?', (clan_name,)).fetchnone():
                conn.execute('INSERT INTO clans (name, leader, created) VALUES (?, ?, ?)', 
                           (clan_name, current_user, time.time()))
                conn.commit()
        conn.close()
    
    conn = db.get_connection()
    clans_list = conn.execute('SELECT * FROM clans ORDER BY members DESC, coins DESC LIMIT 20').fetchall()
    conn.close()
    
    clans_html = ''.join(f'''
    <div class="game-card" style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <h4 style="margin:0;">{c['name']}</h4>
            <div>👑 {c['leader']} | 👥 {c['members']} | 💰 {c['coins']:,}</div>
        </div>
        <a href="/clan/{c['id']}" class="nav-btn" style="padding:10px 20px;">Присоединиться</a>
    </div>''' for c in clans_list)
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>👥 Кланы v43</title></head><body>
<div class="container">
    <header><h1>👥 КЛАНОВАЯ СИСТЕМА</h1></header>
    <div style="display:grid;gap:20px;">
        <form method="POST" style="background:var(--glass);padding:30px;border-radius:25px;">
            <input type="hidden" name="action" value="create">
            <input name="clan_name" placeholder="Название клана" maxlength="20" required>
            <button type="submit" class="nav-btn" style="width:100%;background:var(--info);">👑 СОЗДАТЬ КЛАН</button>
        </form>
        <h3>🔥 ТОП КЛАНЫ</h3>
        {clans_html}
    </div>
</div></body></html>'''

# ✅ КАЗИНО v2 (Новые игры + Лотерея)
@app.route('/casino', methods=['GET', 'POST'])
@require_auth
def casino_v2():
    current_user = session['user']
    user = get_user(current_user)
    
    if request.method == 'POST':
        game = request.form.get('game')
        bet = int(request.form.get('bet', 0))
        
        if bet > 0 and user['coins'] >= bet:
            if game == 'roulette':
                result = random.randint(0, 36)
                color = 'red' if result in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else 'black' if result else 'green'
                win = result == 0  # Только зеро
                reward = bet * 35 if win else 0
            elif game == 'lottery':
                ticket = random.randint(1, 1000)
                win = ticket <= 3  # 0.3% шанс
                reward = 100000 if win else 0
            
            new_balance = user['coins'] - bet + reward
            conn = db.get_connection()
            if conn:
                conn.execute('UPDATE users SET coins = ? WHERE username = ?', (new_balance, current_user))
                conn.commit()
                conn.close()
            
            if reward > 1000: grant_achievement(current_user, 'casino_lucky')
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🎰 Казино v2</title></head><body>
<div class="container">
    <header><h1>🎰 КАЗИНО v2 <span class="premium-badge">НОВЫЕ ИГРЫ</span></h1></header>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:40px;">
        <div class="game-card">
            <h3>🎡 РУЛЕТКА (только зеро)</h3>
            <form method="POST">
                <input type="hidden" name="game" value="roulette">
                <input name="bet" type="number" min="100" max="{user['coins']}" placeholder="Ставка">
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#e74c3c,#c0392b);">🎡 x35</button>
            </form>
        </div>
        <div class="game-card">
            <h3>🎟️ ЛОТЕРЕЯ (0.3% шанс)</h3>
            <form method="POST">
                <input type="hidden" name="game" value="lottery">
                <input name="bet" type="number" min="1000" max="{user['coins']}" placeholder="Билет (1000+)">
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#f39c12,#e67e22);">🎟️ 100K💰</button>
            </form>
        </div>
    </div>
    <div class="game-card" style="text-align:center;margin:60px 0;">
        <h2>💰 {user['coins']:,}</h2>
        <div class="rank-display">{user['tank_rank']}</div>
    </div>
</div></body></html>'''

# ✅ СУПЕР-АДМИНКА v2 (Дашборд + Массовые действия)
@app.route('/admin', methods=['GET', 'POST'])
@require_auth
def admin_v2():
    if not is_moderator(session['user']): return redirect('/')
    
    if request.method == 'POST':
        action = request.form.get('action')
        conn = db.get_connection()
        
        if action == 'mass_mute':
            duration = int(request.form.get('duration', 300))
            reason = request.form.get('reason', 'Массовый мут')
            targets = request.form.getlist('targets[]')  # Чекбоксы
            for target in targets:
                conn.execute('INSERT INTO mutes VALUES (NULL, ?, ?, ?, "mass", ?, ?, ?)',
                           (target, session['user'], reason, duration, time.time() + duration, time.time()))
            conn.commit()
        
        elif action == 'mass_coins':
            amount = int(request.form.get('amount'))
            targets = request.form.getlist('targets[]')
            for target in targets:
                conn.execute('UPDATE users SET coins = coins + ? WHERE username = ?', (amount, target))
            conn.commit()
        conn.close()
    
    # ✅ Статистика
    conn = db.get_connection()
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'today_messages': conn.execute('SELECT COUNT(*) FROM chat WHERE timestamp > ?', (time.time()-86400,)).fetchone()[0],
        'active_mutes': conn.execute('SELECT COUNT(*) FROM mutes WHERE expires > ?', (time.time(),)).fetchone()[0]
    }
    recent_users = conn.execute('SELECT username, coins FROM users ORDER BY last_seen DESC LIMIT 10').fetchall()
    conn.close()
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>⚙️ Супер-Админка v2</title></head><body>
<div class="container">
    <header><h1 style="color:var(--danger);">⚙️ АДМИН v2 — ДАШБОРД</h1></header>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px;margin-bottom:40px;">
        <div class="role-card role-admin">👥 {stats['total_users']} игроков</div>
        <div class="role-card role-premium">💬 {stats['today_messages']:,} сообщений сегодня</div>
        <div class="role-card role-mod">🚫 {stats['active_mutes']} активных мутов</div>
    </div>
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
        <div class="game-card admin-panel">
            <h3>🚫 МАССОВЫЙ МУТ</h3>
            <form method="POST">
                <select name="duration" style="margin-bottom:15px;">
                    <option value="600">10 мин (мат)</option><option value="900">15 мин (спам)</option><option value="1800">30 мин (флуд)</option>
                </select>
                <input name="reason" placeholder="Причина" required>
                <input type="hidden" name="action" value="mass_mute">
                <button type="submit" class="nav-btn admin-btn">🔇 МУТАТЬ ВЫБРАННЫХ</button>
            </form>
        </div>
        <div class="game-card admin-panel">
            <h3>💰 МАССОВЫЕ МОНЕТЫ</h3>
            <form method="POST">
                <input name="amount" type="number" placeholder="Количество монет" required>
                <input type="hidden" name="action" value="mass_coins">
                <button type="submit" class="nav-btn admin-btn">💰 ВЫДАТЬ ВЫБРАННЫМ</button>
            </form>
        </div>
    </div>
</div></body></html>'''

# ✅ РЕГИСТРАЦИЯ v43
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 4: return "❌ Ник 3+ символа, пароль 4+"
        if not get_user(username):
            conn = db.get_connection()
            if conn:
                conn.execute('INSERT INTO users (username, password_hash, created) VALUES (?, ?, ?)',
                           (username, generate_password_hash(password), time.time()))
                conn.commit()
                conn.close()
            return redirect('/login')
    return f'''{PREMIUM_CSS_V43}<div class="container"><div class="game-card" style="max-width:500px;margin:100px auto;">
<h1>📝 РЕГИСТРАЦИЯ v43</h1><form method="POST"><input name="username" placeholder="👤 Ник (3+)" required>
<input name="password" type="password" placeholder="🔒 Пароль (4+)" required><button type="submit" class="nav-btn">🚀 ЗАРЕГИСТРИРОВАТЬСЯ</button></form></div></div>'''

# ✅ 404 + ФИНАЛЬНЫЙ ЗАПУСК
@app.errorhandler(404)
def not_found(e):
    return f'''{PREMIUM_CSS_V43}<div class="container" style="text-align:center;padding:100px;">
<h1 style="font-size:8em;color:var(--danger);">❓ 404</h1><a href="/" class="nav-btn">🏠 Главная</a></div></body></html>''', 404

if __name__ == '__main__':
    print("🚀" * 60)
    print("🎉 УЗНАВАЙКИН v43.0 — ЛУЧШИЙ ИГРОВОЙ ХАБ 2026!")
    print("✅ 23 МЕГА-ФИЧИ: Кланы • Банк 5% • Рулетка x35 • Лотерея 0.3%")
    print("✅ Socket.IO • PWA • Темная тема • Супер-Админка v2")
    print("👑 CatNap/Назар (120187) — Ветераны (100k💰 + 500 стрик!)")
    print("🎮 /casino 🎰 /bank 🏦 /clans 👥 /leaderboard 🏆 /admin ⚙️")
    print("🚀" * 60)
    
    socketio.run(app, host='0.0.0.0', port=10000, debug=False, allow_unsafe_werkzeug=True)
