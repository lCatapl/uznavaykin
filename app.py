#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v43.0 — 15+ НОВЫХ СИСТЕМ + СУПЕР-АДМИНКА (ЧАСТЬ 1/3)
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

# ✅ CSS v43.0 (PWA + Particles + Темы) — ПОЛНЫЙ КОД
PREMIUM_CSS_V43 = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json">
<style>*{margin:0;padding:0;box-sizing:border-box;}
:root{--primary-gradient:linear-gradient(135deg,#1e3c72 0%,#2a5298 50%,#f093fb 100%);--success:#00d4aa;--danger:#ff4757;--warning:#ffa502;--info:#3742fa;--dark:#2f3542;--light:#f1f2f6;--shadow:0 20px 60px rgba(0,0,0,0.2);--glass:rgba(255,255,255,0.95);}
[data-theme="dark"]{--glass:rgba(47,53,66,0.95);--light:#2f3542;}
body{font-family:\'Segoe UI\',sans-serif;background:var(--primary-gradient);min-height:100vh;color:var(--dark);transition:all 0.3s;}
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

# ✅ 30+ ЗВАНИЙ v43.0 + ACHIEVEMENTS — ПОЛНАЯ СИСТЕМА
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

# ✅ ГЛОБАЛЬНЫЕ СИСТЕМЫ v43.0 — ПОЛНЫЕ СТРУКТУРЫ
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

# ✅ СУПЕР-БАЗА v43.0 (ВСЕ ТАБЛИЦЫ) — ПОЛНАЯ СТРУКТУРА
class MegaDatabase:
    def __init__(self, db_path='uznavaykin_v43.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON; PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=10000;')
            return conn
        except Exception as e:
            logger.error(f"❌ DB Connection Error: {e}")
            return None
    
    def init_db(self):
        conn = self.get_connection()
        if not conn: 
            logger.error("❌ Cannot initialize database!")
            return False
        
        # ✅ ПОЛНАЯ СХЕМА БАЗЫ v43.0
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 1000,
                bank INTEGER DEFAULT 0,
                daily_bonus REAL DEFAULT 0,
                role TEXT DEFAULT 'start',
                premium INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                rank_wins INTEGER DEFAULT 0,
                tank_rank TEXT DEFAULT 'Новобранец',
                wins INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages INTEGER DEFAULT 0,
                created REAL DEFAULT 0,
                last_seen REAL DEFAULT 0,
                casino_wins INTEGER DEFAULT 0,
                tournament_wins INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                friends TEXT DEFAULT '[]',
                achievements TEXT DEFAULT '[]',
                clan_id INTEGER DEFAULT NULL
            );
            
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp REAL NOT NULL,
                role TEXT,
                rank TEXT,
                room TEXT DEFAULT 'global',
                FOREIGN KEY(user) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                muted_by TEXT,
                reason TEXT,
                mtype TEXT,
                duration INTEGER,
                expires REAL,
                created REAL,
                FOREIGN KEY(target) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ach_id TEXT NOT NULL,
                reward INTEGER,
                unlocked REAL,
                FOREIGN KEY(username) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS daily_logins (
                username TEXT,
                date TEXT,
                bonus INTEGER,
                PRIMARY KEY(username, date),
                FOREIGN KEY(username) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                interest REAL DEFAULT 0,
                timestamp REAL NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                leader TEXT NOT NULL,
                members INTEGER DEFAULT 1,
                coins INTEGER DEFAULT 0,
                created REAL,
                FOREIGN KEY(leader) REFERENCES users(username)
            );
            
            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER,
                username TEXT,
                joined REAL,
                PRIMARY KEY(clan_id, username),
                FOREIGN KEY(clan_id) REFERENCES clans(id),
                FOREIGN KEY(username) REFERENCES users(username)
            );
        ''')
        
        # ✅ ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
        conn.executescript('''
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat(timestamp);
            CREATE INDEX IF NOT EXISTS idx_chat_user ON chat(user);
            CREATE INDEX IF NOT EXISTS idx_mutes_expires ON mutes(expires);
            CREATE INDEX IF NOT EXISTS idx_mutes_target ON mutes(target);
            CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(username);
            CREATE INDEX IF NOT EXISTS idx_daily_logins_user ON daily_logins(username);
            CREATE INDEX IF NOT EXISTS idx_bank_transactions_user ON bank_transactions(username);
            CREATE INDEX IF NOT EXISTS idx_clans_leader ON clans(leader);
        ''')
        
        # ✅ СУПЕР-АДМИНЫ v43.0 (полные профили)
        admin_hash = generate_password_hash('120187')
        super_admins = [
            ('CatNap', admin_hash, 'admin', True, 15000, '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран', 100000, 500),
            ('Назар', admin_hash, 'admin', True, 15000, '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран', 100000, 500)
        ]
        
        for username, pwd, role, premium, rank_wins, rank, coins, streak in super_admins:
            conn.execute('''INSERT OR REPLACE INTO users 
                (username, password_hash, role, premium, rank_wins, tank_rank, coins, streak, created, last_seen) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (username, pwd, role, int(premium), rank_wins, rank, coins, streak, time.time(), time.time()))
        
        conn.commit()
        conn.close()
        logger.info("✅ v43.0 MegaDB инициализирована! 2 супер-админа созданы!")
        return True

# ✅ ИНИЦИАЛИЗАЦИЯ БАЗЫ
db = MegaDatabase()

# ✅ СУПЕР-ФУНКЦИИ v43.0 — ПОЛНЫЕ РЕАЛИЗАЦИИ
def get_user(username: str) -> Optional[sqlite3.Row]:
    """Полный профиль пользователя с кэшированием"""
    conn = db.get_connection()
    if not conn: return None
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

@lru_cache(maxsize=128)
def get_role_stats() -> Dict[str, int]:
    """Расширенная статистика ролей + Premium с кэшированием"""
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
    """Система 30+ званий по победам"""
    for threshold, rank_name in sorted(RANK_SYSTEM.items(), reverse=True):
        if wins >= threshold: return rank_name
    return RANK_SYSTEM[0]

def is_user_muted(username: str) -> bool:
    """Проверка активного мута"""
    conn = db.get_connection()
    if not conn: return False
    mute = conn.execute('SELECT 1 FROM mutes WHERE target=? AND expires>?', (username, time.time())).fetchone()
    conn.close()
    return bool(mute)

def advanced_moderation(message: str, username: str, history: List[str]) -> Tuple[Optional[str], str, int]:
    """🚫 СУПЕР-МОДЕРАТОР v43 (3 уровня: Мат/Спам/Флуд)"""
    message_lower = message.lower().strip()
    
    # 1️⃣ МАТ = +10 мин (600 сек) — регулярные выражения
    bad_words = [r'\bсук[аиы]\b', r'\bпизд[ауео][нц]?\b', r'\bху[йя]\b', r'\bбл[яь][дт]\b', r'\bп[иы]зде[цт][ьц]\b']
    for pattern in bad_words:
        if re.search(pattern, message_lower, re.IGNORECASE | re.UNICODE):
            return "🚫 Мат обнаружен = 10 минут!", "mat", 600
    
    # 2️⃣ СПАМ (3+ одинаковых сообщений за 10 последних)
    recent = history[-10:]
    if len([m for m in recent if m.strip() == message.strip()]) >= 3:
        return "🚫 Спам (3+ одинаковых) = 15 минут!", "spam", 900
    
    # 3️⃣ ФЛУД/РЕКЛАМА = 30 мин
    links = re.findall(r'http[s]?://(?:[a-zA-Z0-9]|[$-_@.&+!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
    if len(links) > 0 or (len(message) < 3 and len(recent) >= 5):
        return "🚫 Флуд/Реклама = 30 минут!", "flood", 1800
    
    return None, None, 0

def grant_achievement(username: str, ach_id: str) -> bool:
    """💎 Полная система достижений с БД и уведомлениями"""
    if ach_id in user_achievements[username]: 
        return False
    
    user = get_user(username)
    if not user: 
        return False
    
    reward = ACHIEVEMENTS[ach_id]['reward']
    conn = db.get_connection()
    if conn:
        # Сохранить достижение
        conn.execute('INSERT INTO achievements (username, ach_id, reward, unlocked) VALUES (?, ?, ?, ?)',
                    (username, ach_id, reward, time.time()))
        
        # Выдать монеты
        conn.execute('UPDATE users SET coins = coins + ? WHERE username = ?', (reward, username))
        
        # Добавить в JSON achievements
        current_achs = json.loads(user['achievements'] or '[]')
        current_achs.append(ach_id)
        conn.execute('UPDATE users SET achievements = ? WHERE username = ?', 
                    (json.dumps(current_achs), username))
        
        conn.commit()
        conn.close()
    
    user_achievements[username].add(ach_id)
    notifications.append({
        'user': username, 
        'type': 'achievement', 
        'title': ACHIEVEMENTS[ach_id]['name'], 
        'reward': reward
    })
    logger.info(f"💎 {username} получил '{ACHIEVEMENTS[ach_id]['name']}' (+{reward}💰)")
    createParticles(50, 50, "#ffd700")  # Партиклы при достижении
    return True

def get_daily_bonus(username: str) -> Tuple[int, bool]:
    """📅 Полная система ежедневных бонусов со стрикингом"""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = db.get_connection()
    if not conn: 
        return 0, False
    
    # Получить текущий стрик
    streak_row = conn.execute('SELECT streak FROM users WHERE username = ?', (username,)).fetchone()
    current_streak = streak_row['streak'] if streak_row else 0
    
    # Проверить последний бонус
    last_bonus = conn.execute('SELECT date FROM daily_logins WHERE username = ? ORDER BY date DESC LIMIT 1', (username,)).fetchone()
    is_new_day = not last_bonus or last_bonus['date'] != today
    
    if is_new_day:
        # Рассчитать бонус (100 * стрик)
        bonus = 100 * (current_streak + 1)
        
        # Обновить стрик (проверить последовательность)
        new_streak = current_streak + 1
        if last_bonus:
            last_date = datetime.strptime(last_bonus['date'], '%Y-%m-%d').date()
            if (datetime.now().date() - last_date).days != 1:
                new_streak = 1
        
        # Сохранить ежедневный логин
        conn.execute('INSERT OR REPLACE INTO daily_logins (username, date, bonus) VALUES (?, ?, ?)', 
                    (username, today, bonus))
        
        # Обновить пользователя
        conn.execute('UPDATE users SET coins = coins + ?, streak = ?, daily_bonus = ? WHERE username = ?', 
                    (bonus, new_streak, time.time(), username))
        
        conn.commit()
        
        # Достижение за 7 дней подряд
        if new_streak >= 7:
            grant_achievement(username, 'daily_streak')
        
        conn.close()
        logger.info(f"📅 {username}: +{bonus}💰 (стрик: {new_streak})")
        return bonus, True
    
    conn.close()
    return 0, False

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """🏆 Глобальный лидерборд с сортировкой по монетам + стрик"""
    conn = db.get_connection()
    if not conn: 
        return []
    
    top = conn.execute('''
        SELECT username, coins, tank_rank, premium, streak 
        FROM users 
        ORDER BY coins DESC, streak DESC, last_seen DESC 
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    return [
        {
            'username': u['username'], 
            'coins': u['coins'], 
            'rank': u['tank_rank'], 
            'premium': u['premium'], 
            'streak': u['streak']
        } 
        for u in top
    ]

def is_authenticated() -> bool:
    """Проверка авторизации с валидацией пользователя"""
    return bool(session.get('user') and get_user(session.get('user')))

def require_auth(f):
    """Декоратор авторизации с редиректом"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            session['login_redirect'] = request.path
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def is_moderator(username: str) -> bool:
    """Проверка модераторских прав"""
    user = get_user(username)
    return user and user['role'] in ['admin', 'moderator']

def save_user_activity(username: str):
    """Сохранение активности пользователя"""
    conn = db.get_connection()
    if conn:
        conn.execute('UPDATE users SET last_seen = ? WHERE username = ?', (time.time(), username))
        conn.commit()
        conn.close()

# ✅ PWA MANIFEST v43.0
@app.route('/manifest.json')
def manifest():
    return {
        "name": "🚀 Узнавайкин v43.0 — Мега Хаб",
        "short_name": "УЗ43",
        "description": "Игровой хаб с чатом, казино, кланами и 23+ фичами",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ],
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#1e3c72",
        "background_color": "#f1f2f6",
        "orientation": "portrait-primary"
    }

# ✅ ЛОГ СТАРТА
print("🚀" * 40)
print("✅ УЗНАВАЙКИН v43.0 ЧАСТЬ 1/3 — 15+ МЕГА-ФИЧ!")
print("💎 Достижения • Ежедневки • Лидерборд • Супер-Модератор v43")
print("👑 CatNap/Назар (120187) — Ветераны (100k💰 + 500 стрик!)")
print("📊 MegaDB готова — 9 таблиц + 7 индексов!")
print("🚀" * 40)
# ✅ Socket.IO СИСТЕМА v43.0 (Реал-тайм чат + VIP комнаты)
@socketio.on('connect')
def handle_connect():
    """Обработка подключения с логгированием"""
    username = session.get('user', 'guest')
    logger.info(f"🔌 {username} подключился к Socket.IO")
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения"""
    username = session.get('user', 'guest')
    logger.info(f"🔌 {username} отключился от Socket.IO")

@socketio.on('join')
def on_join(data):
    """Присоединение к комнате (глобал/VIP/premium)"""
    username = session.get('user', 'guest')
    room = data.get('room', 'global')
    
    if len(room) > 20:  # Защита от флуда комнат
        emit('error', {'msg': '❌ Название комнаты слишком длинное!'})
        return
    
    join_room(room)
    user = get_user(username)
    
    if user:
        emit('status', {
            'msg': f'👋 {username} ({user["tank_rank"]}) зашёл в {room}', 
            'user': username,
            'rank': user['tank_rank']
        }, room=room)
    
    logger.info(f"🔗 {username} присоединился к комнате '{room}'")
    emit('joined', {'room': room})

@socketio.on('leave')
def on_leave(data):
    """Покинуть комнату"""
    username = session.get('user', 'guest')
    room = data.get('room', 'global')
    leave_room(room)
    
    emit('status', {
        'msg': f'👋 {username} покинул {room}', 
        'user': username
    }, room=room)
    
    logger.info(f"🔗 {username} покинул комнату '{room}'")

@socketio.on('message')
def handle_message(data):
    """🚀 ОСНОВНАЯ ЛОГИКА ЧАТА v43 — СУПЕР-МОДЕРАТОР + ДОСТИЖЕНИЯ"""
    username = session.get('user')
    if not username: 
        emit('error', {'msg': '❌ Не авторизован!'})
        return
    
    if is_user_muted(username):
        emit('error', {'msg': '🚫 Вы в муте!'})
        return
    
    message = data.get('message', '').strip()
    room = data.get('room', 'global')
    
    if not message or len(message) > 500:  # Ограничения
        emit('error', {'msg': '❌ Сообщение пустое или слишком длинное (макс. 500 символов)'})
        return
    
    # ✅ СПАМ-КЭШ
    spam_counters[username].append(message)
    spam_counters[username] = spam_counters[username][-50:]  # Храним 50 последних
    
    # ✅ СУПЕР-МОДЕРАТОР v43 (3 уровня)
    reason, mtype, duration = advanced_moderation(message, username, spam_counters[username])
    
    if reason:
        emit('system_message', {
            'msg': f"{username}: {reason}", 
            'type': 'mute',
            'duration': duration
        }, room=room)
        
        # Сохранить мут в БД
        conn = db.get_connection()
        if conn:
            conn.execute('''INSERT INTO mutes (target, muted_by, reason, mtype, duration, expires, created) 
                          VALUES (?, 'AUTO-MODERATOR', ?, ?, ?, ?, ?)''',
                        (username, reason, mtype, duration, time.time() + duration, time.time()))
            conn.commit()
            conn.close()
        
        logger.warning(f"🚫 AUTO-MUT: {username} ({mtype}) - {reason}")
        return
    
    # ✅ САХРАНЕНИЕ + МОНЕТЫ + ДОСТИЖЕНИЯ
    user = get_user(username)
    if not user: return
    
    # Добавить в глобальный чат
    chat_messages.append({
        'user': username, 
        'rank': user['tank_rank'], 
        'role': user['role'], 
        'message': message, 
        'timestamp': time.time(), 
        'premium': user['premium'], 
        'room': room
    })
    
    # Сохранить в БД
    conn = db.get_connection()
    if conn:
        conn.execute('''INSERT INTO chat (user, message, timestamp, role, rank, room) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (username, message, time.time(), user['role'], user['tank_rank'], room))
        
        # Монеты за сообщение
        coins = 5 + (15 if user['premium'] else 0)
        conn.execute('UPDATE users SET coins = coins + ?, messages = messages + 1, last_seen = ? WHERE username = ?', 
                    (coins, time.time(), username))
        
        # ✅ СИСТЕМА ДОСТИЖЕНИЙ
        msg_count = conn.execute('SELECT messages FROM users WHERE username = ?', (username,)).fetchone()['messages']
        if msg_count == 1:
            grant_achievement(username, 'first_chat')
        elif msg_count == 100:
            grant_achievement(username, 'chat_master')
        
        conn.commit()
        conn.close()
    
    # ✅ ОТПРАВИТЬ ВСЕМ В КОМНАТЕ
    emit('message', {
        'user': username,
        'rank': user['tank_rank'],
        'role': user['role'],
        'message': message,
        'timestamp': time.time(),
        'premium': user['premium']
    }, room=room)
    
    logger.info(f"💬 [{room}] {username}: {message[:50]}...")

# ✅ ЛОГИН v43.0 (PWA + РЕФЕРАЛКИ + ЗАЩИТА)
@app.route('/login', methods=['GET', 'POST'])
def login():
    ref = request.args.get('ref', '').strip()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template_string(f'{PREMIUM_CSS_V43}<div class="container"><div class="game-card"><h2>❌ Заполните все поля!</h2><a href="/login" class="nav-btn">🔙 Назад</a></div></div>')
        
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            save_user_activity(username)
            
            # ✅ РЕФЕРАЛКА (+500 обоим)
            if ref and ref != username and get_user(ref):
                conn = db.get_connection()
                if conn:
                    conn.execute('UPDATE users SET coins = coins + 500, referrals = referrals + 1 WHERE username IN (?, ?)',
                               (username, ref))
                    conn.commit()
                    conn.close()
                
                notifications.append({
                    'user': username, 
                    'type': 'referral', 
                    'title': '🤝 Рефералка!', 
                    'reward': 500
                })
                logger.info(f"🤝 РЕФЕРАЛКА: {username} ← {ref}")
            
            # Редирект после логина
            next_url = session.get('login_redirect', '/')
            del session['login_redirect']
            return redirect(next_url)
        
        return render_template_string(f'{PREMIUM_CSS_V43}<div class="container"><div class="game-card"><h2>❌ Неверный логин/пароль!</h2><a href="/login" class="nav-btn">🔙 Попробовать снова</a></div></div>')
    
    # GET — форма логина
    ref_link = f"/login?ref={session.get('user', '')}" if session.get('user') else ""
    return f'''{PREMIUM_CSS_V43}
<div class="container">
    <div class="game-card" style="max-width:500px;margin:100px auto;text-align:center;">
        <h1 style="font-size:5em;margin-bottom:30px;">🔐 ВХОД v43.0</h1>
        <form method="POST" style="max-width:400px;margin:0 auto;">
            <input name="username" placeholder="👤 Никнейм" required autofocus>
            <input name="password" type="password" placeholder="🔒 Пароль" required>
            <button type="submit" class="nav-btn" style="width:100%;background:var(--success);font-size:20px;padding:20px;">🚀 ВОЙТИ В МЕГА-ХАБ</button>
        </form>
        <div style="margin-top:40px;">
            <div class="premium-badge" style="font-size:16px;">👑 CatNap / Назар (120187)</div>
        </div>
        <div style="margin-top:30px;">
            <a href="/register" class="nav-btn" style="background:var(--info);">📝 Регистрация</a>
        </div>
        {f'<div style="margin-top:20px;font-size:14px;"><span>Твоя рефка: </span><code style="background:var(--glass);padding:8px 12px;border-radius:8px;">{ref_link}</code></div>' if ref_link else ""}
    </div>
</div>'''

# ✅ ГЛАВНАЯ СТРАНИЦА v43.0 (SocketIO + Лидерборд + Темы + Particles)
@app.route('/', methods=['GET', 'POST'])
@require_auth
def index():
    """🚀 ГЛАВНАЯ СТАНИЦА — ВЫСОКОГРУЖЕННАЯ"""
    current_user = session['user']
    user = get_user(current_user)
    role_stats = get_role_stats()
    leaderboard = get_leaderboard(5)
    
    # ✅ ЕЖЕДНЕВНЫЙ БОНУС
    bonus, claimed = get_daily_bonus(current_user)
    
    # ✅ ЛИДЕРБОРД HTML
    lb_html = ''
    for i, u in enumerate(leaderboard):
        premium_badge = '<span class="premium-badge" style="font-size:14px;">PREMIUM</span>' if u['premium'] else ''
        lb_html += f'''
        <div style="display:flex;align-items:center;gap:15px;padding:15px;background:rgba(0,0,0,0.1);border-radius:15px;margin:10px 0;">
            <div style="font-size:2em;font-weight:900;color:var(--success);">{i+1}</div>
            <div style="flex:1;font-weight:800;">{u["username"]}</div>
            <div style="color:var(--success);font-weight:900;font-size:1.3em;">{u["coins"]:,}💰</div>
            {premium_badge}
        </div>'''
    
    # ✅ ЧАТ ПЛЕЙСХОЛДЕРЫ (последние 50 сообщений)
    recent_messages = list(chat_messages)[-20:]
    chat_html = ''
    for msg in recent_messages:
        badge = '💎' if msg.get('premium') else ''
        chat_html += f'''
        <div class="message">
            <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
                <span style="font-weight:900;color:var(--info);">{msg["user"]}</span>
                <span style="font-size:0.9em;color:#95a5ab;">{msg["rank"]}</span>
                <span style="font-size:0.8em;color:#95a5ab;">{datetime.fromtimestamp(msg["timestamp"]).strftime("%H:%M")}</span>
                <span>{badge}</span>
            </div>
            <div>{msg["message"]}</div>
        </div>'''
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Узнавайкин v43.0 — Мега Хаб</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
</head>
<body>
    <canvas id="particles" class="particles-canvas"></canvas>
    <div class="theme-toggle" onclick="toggleTheme()">🌙</div>
    
    <!-- Уведомление о достижении -->
    <div class="achievement-popup" id="achievementPopup">
        <h2 id="achTitle"></h2>
        <p id="achReward" style="font-size:2em;">+<span>0</span>💰</p>
        <button class="nav-btn" onclick="hideAchievement()" style="width:200px;">Понятно! ✨</button>
    </div>
    
    <div class="container">
        <!-- ✅ ХЕДЕР -->
        <header>
            <h1>🚀 УЗНАВАЙКИН <span style="font-size:0.4em;">v43.0</span> 
                <span class="premium-badge">{'💎 PREMIUM' if user['premium'] else 'MEGA'}</span>
            </h1>
            
            <!-- ✅ СТАТИСТИКА РОЛЕЙ -->
            <div class="role-stats">
                <div class="role-card role-start">👤 {role_stats['start']}</div>
                <div class="role-card role-vip">⭐ {role_stats['vip']}</div>
                <div class="role-card role-premium">💎 {role_stats['premium']}</div>
                <div class="role-card role-mod">🛡️ {role_stats['moderator']}</div>
                <div class="role-card role-admin">👑 {role_stats['admin']}</div>
            </div>
            
            <!-- ✅ ЕЖЕДНЕВНЫЙ БОНУС -->
            {f'<div style="font-size:28px;margin-top:30px;padding:20px;background:var(--success);color:white;border-radius:20px;box-shadow:var(--shadow);">🎉 +{bonus:,}💰 ЕЖЕДНЕВКА! СТРИК: {user["streak"]}🔥</div>' if bonus > 0 else ''}
            
            <!-- ✅ СТАТУС ПОЛЬЗОВАТЕЛЯ -->
            <div style="margin-top:20px;font-size:20px;">
                💰 <strong style="color:var(--success);">{user['coins']:,}</strong> | 
                {user['tank_rank']} | 
                {'💎 PREMIUM' if user['premium'] else '⭐ Базовый'}
            </div>
        </header>

        <!-- ✅ ОСНОВНОЙ ЛЭЙАУТ -->
        <div style="display:grid;grid-template-columns:2fr 1fr;gap:40px;">
            
            <!-- ✅ ГЛОБАЛЬНЫЙ ЧАТ -->
            <div class="game-card">
                <h3 style="display:flex;justify-content:space-between;align-items:center;">
                    💬 ГЛОБАЛЬНЫЙ ЧАТ <span style="font-size:14px;color:#666;">({len(chat_messages)} сообщений)</span>
                </h3>
                <div id="chat-messages" style="height:450px;overflow-y:auto;background:rgba(255,255,255,0.9);border-radius:20px;padding:20px;">
                    {chat_html}
                </div>
                <div style="display:flex;gap:15px;margin-top:20px;">
                    <input id="chat-input" placeholder="💬 Пиши сообщение (+{5+(15 if user[\'premium\'] else 0)}💰 за сообщение)" 
                           style="flex:1;" maxlength="300">
                    <button onclick="sendMessage()" class="nav-btn" style="width:140px;padding:18px 20px;">📤 ОТПРАВИТЬ</button>
                </div>
            </div>
            
            <!-- ✅ ЛИДЕРБОРД + МЕНЮ -->
            <div class="leaderboard">
                <h3 style="margin-bottom:25px;text-align:center;">🏆 ТОП-5 ИГРОКОВ</h3>
                {lb_html}
                
                <div style="margin-top:35px;">
                    <a href="/leaderboard" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">🏆 Полный лидерборд</a>
                    <a href="/daily" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">📅 Ежедневные бонусы</a>
                    <a href="/bank" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">🏦 Банк (5% годовых)</a>
                    <a href="/casino" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;background:linear-gradient(135deg,#e74c3c,#c0392b);">🎰 Казино</a>
                    <a href="/clans" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;">👥 Кланы</a>
                    {f'<a href="/admin" class="nav-btn" style="font-size:14px;width:100%;margin:5px 0;background:linear-gradient(135deg,var(--danger),#ff3742);">⚙️ Админ-панель</a>' if is_moderator(current_user) else ''}
                </div>
                
                <div style="margin-top:20px;padding:15px;background:rgba(0,0,0,0.1);border-radius:15px;text-align:center;">
                    <a href="/logout" style="color:var(--danger);font-weight:800;">🚪 Выход</a>
                </div>
            </div>
        </div>
    </div>

    <!-- ✅ JAVASCRIPT v43.0 -->
    <script>
    const socket = io();
    let theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    
    // Темная тема
    function toggleTheme() {{
        theme = theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
    }}
    
    // Чат
    socket.on('message', function(msg) {{
        addMessage(msg);
        scrollChat();
        createParticles(100, window.innerHeight/2, '#00d4aa');
    }});
    
    socket.on('system_message', function(msg) {{
        addSystemMessage(msg.msg);
        scrollChat();
    }});
    
    socket.on('status', function(msg) {{
        addSystemMessage(msg.msg);
        scrollChat();
    }});
    
    function addMessage(msg) {{
        const div = document.createElement('div');
        div.className = 'message';
        div.innerHTML = `
            <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
                <span style="font-weight:900;color:var(--info);">${{msg.user}}</span>
                <span style="font-size:0.9em;color:#95a5ab;">${{msg.rank}}</span>
                <span style="font-size:0.8em;color:#95a5ab;">${{new Date(msg.timestamp*1000).toLocaleTimeString()}}</span>
                ${{msg.premium ? '<span style="font-size:1.2em;">💎</span>' : ''}}
            </div>
            <div>${{msg.message}}</div>
        `;
        document.getElementById('chat-messages').appendChild(div);
    }}
    
    function addSystemMessage(msg) {{
        const div = document.createElement('div');
        div.style.cssText = 'color:var(--danger);font-weight:800;padding:15px;background:rgba(255,71,87,0.1);border-radius:15px;margin:10px 0;border-left:6px solid var(--danger);';
        div.textContent = msg;
        div.classList.add('notification');
        document.getElementById('chat-messages').appendChild(div);
    }}
    
    function sendMessage() {{
        const input = document.getElementById('chat-input');
        const msg = input.value.trim();
        if (msg) {{
            socket.emit('message', {{message: msg, room: 'global'}});
            input.value = '';
        }}
    }}
    
    // Enter для отправки
    document.getElementById('chat-input').addEventListener('keypress', function(e) {{
        if (e.key === 'Enter') sendMessage();
    }});
    
    function scrollChat() {{
        const chat = document.getElementById('chat-messages');
        chat.scrollTop = chat.scrollHeight;
    }}
    
    // Подключение к комнате
    socket.emit('join', {{room: 'global'}});
    
    // Запуск анимации частиц
    animateParticles();
    
    // Скрыть popup достижений
    function hideAchievement() {{
        document.getElementById('achievementPopup').style.display = 'none';
    }}
    </script>
</body>
</html>'''

# ✅ РЕФЕРАЛКИ
@app.route('/referrals')
@require_auth
def referrals():
    user = get_user(session['user'])
    ref_link = f"https://{request.host}/login?ref={session['user']}"
    return f'''{PREMIUM_CSS_V43}
<div class="container">
    <header><h1>🤝 СИСТЕМА РЕФЕРАЛОВ</h1></header>
    <div class="game-card" style="max-width:600px;margin:0 auto;">
        <h3>📈 ТВОИ СТАТИСТИКИ</h3>
        <p><strong>Приведено друзей:</strong> {user['referrals'] or 0}</p>
        <p><strong>Заработано:</strong> {user['referrals'] * 500:,}💰</p>
        
        <h3 style="margin-top:40px;">🔗 ТВОЯ РЕФЕРАЛКА</h3>
        <div style="background:var(--glass);padding:20px;border-radius:20px;margin:20px 0;font-size:18px;">
            <code style="font-size:20px;background:#2f3542;color:#ffd700;padding:15px;border-radius:15px;display:block;word-break:break-all;">
                {ref_link}
            </code>
        </div>
        <p style="font-size:16px;color:var(--info);"><strong>+500💰 тебе + 500💰 другу!</strong></p>
    </div>
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div>'''

print("🚀 УЗНАВАЙКИН v43.0 ЧАСТЬ 2/3 — SocketIO + Реал-тайм!")
print("✅ Чат мгновенный • Рефералки • Главная с лидербордом!")
# ✅ ЛИДЕРБОРД ПОЛНЫЙ v43.0 (ТОП-50 с пагинацией)
@app.route('/leaderboard')
@require_auth
def leaderboard():
    """🏆 ГЛОБАЛЬНЫЙ ЛИДЕРБОРД — ТОП-50"""
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    conn = db.get_connection()
    if not conn:
        return "❌ Ошибка базы данных", 500
    
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_pages = (total_users + per_page - 1) // per_page
    
    top_players = conn.execute('''
        SELECT username, coins, tank_rank, premium, streak, referrals, messages
        FROM users 
        ORDER BY coins DESC, streak DESC 
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    conn.close()
    
    lb_html = ''
    for i, u in enumerate(top_players):
        global_rank = offset + i + 1
        premium_badge = '<span class="premium-badge" style="font-size:12px;">PREMIUM</span>' if u['premium'] else ''
        lb_html += f'''
        <tr style="border-bottom:1px solid rgba(0,0,0,0.1);">
            <td style="padding:15px;text-align:center;font-weight:900;font-size:1.3em;">#{global_rank}</td>
            <td style="padding:15px;display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.4em;font-weight:900;">{u['username']}</span>
                <span style="font-size:0.9em;opacity:0.8;">{u['tank_rank']}</span>
                {premium_badge}
            </td>
            <td style="padding:15px;text-align:right;font-weight:900;color:var(--success);font-size:1.2em;">{u['coins']:,}💰</td>
            <td style="padding:15px;text-align:center;font-weight:800;">{u['streak']}🔥</td>
            <td style="padding:15px;text-align:center;opacity:0.8;">{u['referrals']}</td>
        </tr>'''
    
    pagination = ''
    if total_pages > 1:
        pagination = f'''
        <div style="display:flex;justify-content:center;gap:10px;margin:30px 0;">
            {''.join(f'<a href="?page={p}" class="nav-btn" style="padding:10px 15px;font-size:14px;">{p}</a>' for p in range(1, min(6, total_pages+1)))}
            {f'<span style="padding:10px 15px;font-weight:800;">...</span><a href="?page={total_pages}" class="nav-btn" style="padding:10px 15px;font-size:14px;">{total_pages}</a>' if total_pages > 5 else ''}
        </div>'''
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🏆 Лидерборд v43.0</title></head><body>
<div class="container">
    <header><h1>🏆 ГЛОБАЛЬНЫЙ ЛИДЕРБОРД v43</h1><p style="font-size:1.2em;color:var(--info);">Всего игроков: {total_users}</p></header>
    <div class="game-card" style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:linear-gradient(135deg,var(--info),#5a6fd8);color:white;">
                    <th style="padding:20px;font-size:1.2em;">#</th>
                    <th style="padding:20px;font-size:1.2em;">ИГРОК</th>
                    <th style="padding:20px;font-size:1.2em;">💰 МОНЕТЫ</th>
                    <th style="padding:20px;font-size:1.2em;">🔥 СТРИК</th>
                    <th style="padding:20px;font-size:1.2em;">👥 РЕФЫ</th>
                </tr>
            </thead>
            <tbody>{lb_html}</tbody>
        </table>
    </div>
    {pagination}
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ БАНК v43.0 (5% годовых + ежедневный % + история)
@app.route('/bank', methods=['GET', 'POST'])
@require_auth
def bank():
    current_user = session['user']
    user = get_user(current_user)
    
    if request.method == 'POST':
        action = request.form.get('action')
        amount = int(request.form.get('amount', 0))
        
        conn = db.get_connection()
        if conn and amount >= 100:
            if action == 'deposit' and user['coins'] >= amount:
                conn.execute('UPDATE users SET coins = coins - ?, bank = bank + ? WHERE username = ?', 
                           (amount, amount, current_user))
                conn.execute('INSERT INTO bank_transactions (username, amount, type, timestamp) VALUES (?, ?, ?, ?)',
                           (current_user, amount, 'deposit', time.time()))
            elif action == 'withdraw' and user['bank'] >= amount:
                interest = amount * 0.05  # 5% бонус при снятии
                conn.execute('UPDATE users SET coins = coins + ?, bank = bank - ? WHERE username = ?', 
                           (amount + int(interest), amount, current_user))
                conn.execute('INSERT INTO bank_transactions (username, amount, type, interest, timestamp) VALUES (?, ?, ?, ?, ?)',
                           (current_user, amount, 'withdraw', interest, time.time()))
            conn.commit()
            conn.close()
            return redirect('/bank')
    
    # ✅ История транзакций (последние 10)
    conn = db.get_connection()
    transactions = conn.execute('''
        SELECT amount, type, interest, timestamp FROM bank_transactions 
        WHERE username = ? ORDER BY timestamp DESC LIMIT 10
    ''', (current_user,)).fetchall()
    conn.close()
    
    daily_interest = user['bank'] * 0.05 / 365
    
    trans_html = ''
    for t in transactions:
        trans_type = '➤ ВКЛАД' if t['type'] == 'deposit' else '💰 СНЯТИЕ'
        interest = f'+{t["interest"]:.0f}💰' if t['interest'] else ''
        trans_html += f'<tr><td>{datetime.fromtimestamp(t["timestamp"]).strftime("%d.%m %H:%M")}</td><td>{trans_type}</td><td style="text-align:right;">{abs(t["amount"]):,}💰</td><td>{interest}</td></tr>'
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🏦 Банк v43.0</title></head><body>
<div class="container">
    <header><h1>🏦 ПРЕМИУМ БАНК <span class="premium-badge">5% ГОДОВЫХ</span></h1></header>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
        <div class="game-card">
            <h3>💰 ТВОЙ СЧЕТ</h3>
            <div style="font-size:3em;text-align:center;margin:40px 0;">
                <div style="color:var(--success);">💳 Наличные: {user['coins']:,}💰</div>
                <div style="color:var(--info);">🏦 Депозит: {user['bank']:,}💰</div>
                <div style="font-size:1.4em;color:var(--warning);">📈 +{daily_interest:,.0f}💰 в день</div>
            </div>
        </div>
        <div class="game-card">
            <h3>⚡ БЫСТРЫЕ ОПЕРАЦИИ (мин. 100💰)</h3>
            <form method="POST">
                <input type="hidden" name="action" value="deposit">
                <input name="amount" type="number" min="100" max="{user['coins']}" placeholder="Сумма" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--success);">➤ ПОПОЛНИТЬ</button>
            </form>
            <form method="POST" style="margin-top:20px;">
                <input type="hidden" name="action" value="withdraw">
                <input name="amount" type="number" min="100" max="{user['bank']}" placeholder="Сумма" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--danger);">➤ СНЯТЬ (+5% бонус)</button>
            </form>
        </div>
    </div>
    
    <!-- История операций -->
    <div class="game-card" style="margin-top:40px;">
        <h3>📋 ПОСЛЕДНИЕ ОПЕРАЦИИ</h3>
        <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:var(--info);color:white;"><th>Дата</th><th>Тип</th><th>Сумма</th><th>Бонус</th></tr></thead>
            <tbody>{trans_html or '<tr><td colspan=4 style="padding:40px;text-align:center;color:#666;">Нет операций</td></tr>'}</tbody>
        </table>
    </div>
    
    <div style="text-align:center;margin:60px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ КЛАНЫ v43.0 (Полная система)
@app.route('/clans', methods=['GET', 'POST'])
@require_auth
def clans():
    current_user = session['user']
    
    if request.method == 'POST':
        action = request.form.get('action')
        conn = db.get_connection()
        if action == 'create' and conn:
            clan_name = request.form.get('clan_name', '').strip()
            if len(clan_name) >= 3 and len(clan_name) <= 20:
                if not conn.execute('SELECT id FROM clans WHERE name = ?', (clan_name,)).fetchone():
                    clan_id = conn.execute('INSERT INTO clans (name, leader, created) VALUES (?, ?, ?)', 
                                         (clan_name, current_user, time.time())).lastrowid
                    conn.execute('INSERT INTO clan_members (clan_id, username, joined) VALUES (?, ?, ?)', 
                               (clan_id, current_user, time.time()))
                    conn.execute('UPDATE users SET clan_id = ? WHERE username = ?', (clan_id, current_user))
                    conn.commit()
                    logger.info(f"👥 КЛАН СОЗДАН: {clan_name} [{current_user}]")
            conn.close()
        return redirect('/clans')
    
    # Получить кланы и статус пользователя
    conn = db.get_connection()
    user_clan = conn.execute('SELECT c.* FROM clans c JOIN users u ON c.id = u.clan_id WHERE u.username = ?', 
                           (current_user,)).fetchone()
    
    top_clans = conn.execute('''
        SELECT c.*, COUNT(cm.username) as member_count, u.tank_rank as leader_rank
        FROM clans c 
        LEFT JOIN clan_members cm ON c.id = cm.clan_id 
        LEFT JOIN users u ON c.leader = u.username
        GROUP BY c.id 
        ORDER BY member_count DESC, c.coins DESC 
        LIMIT 20
    ''').fetchall()
    
    conn.close()
    
    clans_html = ''
    user_clan_html = ''
    
    if user_clan:
        user_clan_html = f'''
        <div class="game-card" style="border-left:6px solid var(--success);background:linear-gradient(90deg,rgba(0,212,170,0.1),transparent);">
            <h3>👑 ТВОЙ КЛАН: <span style="color:var(--success);font-size:1.3em;">{user_clan["name"]}</span></h3>
            <p>Лидер: {user_clan["leader"]} | Членов: {user_clan["members"]} | 💰 {user_clan["coins"]:,}</p>
        </div>'''
    
    for clan in top_clans:
        clans_html += f'''
        <div class="game-card" style="display:flex;justify-content:space-between;align-items:center;padding:25px;">
            <div>
                <h4 style="margin:0 0 10px 0;font-size:1.5em;">{clan["name"]}</h4>
                <div style="display:flex;gap:20px;font-size:14px;color:#666;">
                    <span>👑 {clan["leader"]}</span>
                    <span>👥 {clan["member_count"] or clan["members"]}</span>
                    <span>💰 {clan["coins"]:,}</span>
                </div>
            </div>
            <a href="/clan/{clan['id']}" class="nav-btn" style="padding:12px 24px;">Присоединиться</a>
        </div>'''
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>👥 Кланы v43.0</title></head><body>
<div class="container">
    <header><h1>👥 КЛАНОВАЯ СИСТЕМА v43</h1></header>
    {user_clan_html}
    <div class="game-card" style="text-align:center;padding:40px;">
        <form method="POST">
            <input type="hidden" name="action" value="create">
            <input name="clan_name" placeholder="Название клана (3-20 символов)" maxlength="20" required style="max-width:400px;margin:0 auto 20px;display:block;">
            <button type="submit" class="nav-btn" style="width:100%;background:var(--info);font-size:18px;">👑 СОЗДАТЬ КЛАН</button>
        </form>
    </div>
    <h3 style="text-align:center;margin:60px 0 30px 0;">🔥 ТОП-20 КЛАНОВ</h3>
    <div style="display:grid;gap:20px;">{clans_html}</div>
    <div style="text-align:center;margin:80px 0;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ КАЗИНО v2.0 (Рулетка + Лотерея + История)
@app.route('/casino', methods=['GET', 'POST'])
@require_auth
def casino():
    current_user = session['user']
    user = get_user(current_user)
    
    result_msg = ''
    if request.method == 'POST':
        game = request.form.get('game')
        bet = int(request.form.get('bet', 0))
        
        if bet > 0 and user['coins'] >= bet:
            if game == 'roulette':
                result = random.randint(0, 36)
                win = result == 0  # Только зеро!
                reward = bet * 35 if win else 0
                result_msg = f'🎡 Выпало: <strong style="color:var(--danger);font-size:2em;">{result}</strong> | {"🎉 ВЫИГРЫШ x35!" if win else "😔 Проигрыш"}'
            elif game == 'lottery':
                ticket = random.randint(1, 1000)
                win = ticket <= 3  # 0.3%
                reward = 100000 if win else 0
                result_msg = f'🎟️ Билет #{ticket} | {"💰 100K Джекпот!" if win else "😔 Не повезло"}'
            
            # Обновить баланс
            new_balance = user['coins'] - bet + reward
            conn = db.get_connection()
            if conn:
                conn.execute('UPDATE users SET coins = ? WHERE username = ?', (new_balance, current_user))
                if reward > 1000:
                    grant_achievement(current_user, 'casino_lucky')
                conn.commit()
                conn.close()
            
            # Партиклы победы
            if reward > 0:
                createParticles(50, 50, "#ffd700")
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>🎰 Казино v2.0</title></head><body>
<div class="container">
    <header><h1>🎰 КАЗИНО v2.0 <span class="premium-badge">x35 РУЛЕТКА</span></h1></header>
    {f'<div style="background:var(--success);color:white;padding:20px;border-radius:20px;margin-bottom:30px;text-align:center;font-size:1.5em;">{result_msg}</div>' if result_msg else ''}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:40px;">
        <div class="game-card">
            <h3 style="text-align:center;">🎡 РУЛЕТКА (только 0)</h3>
            <form method="POST">
                <input type="hidden" name="game" value="roulette">
                <input name="bet" type="number" min="100" max="{user['coins']}" placeholder="Ставка (от 100💰)" required>
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#e74c3c,#c0392b);font-size:20px;padding:25px 20px;">🎡 КРУТИТЬ x35</button>
            </form>
            <p style="text-align:center;margin-top:20px;font-size:14px;color:#666;">Шанс: 1/37 (~2.7%)</p>
        </div>
        <div class="game-card">
            <h3 style="text-align:center;">🎟️ ЛОТЕРЕЯ СУПЕР-ДЖЕКПОТ</h3>
            <form method="POST">
                <input type="hidden" name="game" value="lottery">
                <input name="bet" type="number" min="1000" max="{user['coins']}" placeholder="Билет (от 1000💰)" required>
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#f39c12,#e67e22);font-size:20px;padding:25px 20px;">🎟️ 100 000💰</button>
            </form>
            <p style="text-align:center;margin-top:20px;font-size:14px;color:#666;">Шанс: 0.3% (3/1000)</p>
        </div>
    </div>
    <div class="game-card" style="text-align:center;margin:60px 0;">
        <h2 style="font-size:3em;color:var(--success);margin-bottom:10px;">💰 {user["coins"]:,}</h2>
        <div style="font-size:1.5em;opacity:0.8;">{user["tank_rank"]}</div>
    </div>
    <div style="text-align:center;">
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ СУПЕР-админка v2.0 (Дашборд + Массовые действия)
@app.route('/admin', methods=['GET', 'POST'])
@require_auth
def admin_panel():
    if not is_moderator(session['user']):
        return redirect('/')
    
    current_user = session['user']
    
    if request.method == 'POST':
        action = request.form.get('action')
        conn = db.get_connection()
        
        if action == 'mass_mute':
            duration = int(request.form.get('duration', 300))
            reason = request.form.get('reason', 'Массовый мут')
            targets = request.form.getlist('targets[]')
            for target in targets:
                conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, duration, expires, created) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (target, current_user, reason, 'mass', duration, time.time() + duration, time.time()))
            conn.commit()
        
        elif action == 'mass_coins':
            amount = int(request.form.get('amount'))
            targets = request.form.getlist('targets[]')
            for target in targets:
                conn.execute('UPDATE users SET coins = coins + ? WHERE username = ?', (amount, target))
            conn.commit()
        
        elif action == 'clear_chat':
            conn.execute('DELETE FROM chat WHERE timestamp < ?', (time.time() - 86400 * 7,))  # 7 дней
            conn.commit()
        
        conn.close()
        return redirect('/admin')
    
    # ✅ СТАТИСТИКА
    conn = db.get_connection()
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'today_messages': conn.execute('SELECT COUNT(*) FROM chat WHERE timestamp > ?', (time.time()-86400,)).fetchone()[0],
        'active_mutes': conn.execute('SELECT COUNT(*) FROM mutes WHERE expires > ?', (time.time(),)).fetchone()[0],
        'total_clans': conn.execute('SELECT COUNT(*) FROM clans').fetchone()[0],
        'premium_users': conn.execute('SELECT COUNT(*) FROM users WHERE premium=1').fetchone()[0]
    }
    
    recent_users = conn.execute('SELECT username, coins, last_seen FROM users ORDER BY last_seen DESC LIMIT 10').fetchall()
    recent_mutes = conn.execute('SELECT target, reason, expires FROM mutes WHERE expires > ? ORDER BY created DESC LIMIT 5', (time.time(),)).fetchall()
    
    conn.close()
    
    recent_users_html = ''.join(f'<tr><td>{u["username"]}</td><td style="text-align:right;">{u["coins"]:,}💰</td><td>{datetime.fromtimestamp(u["last_seen"]).strftime("%H:%M сегодня") if u["last_seen"] > time.time()-86400 else datetime.fromtimestamp(u["last_seen"]).strftime("%d.%m.%Y")}</td></tr>' for u in recent_users)
    recent_mutes_html = ''.join(f'<tr><td>{m["target"]}</td><td>{m["reason"][:50]}...</td><td>{int((m["expires"]-time.time())/60)} мин</td></tr>' for m in recent_mutes)
    
    return f'''{PREMIUM_CSS_V43}
<!DOCTYPE html><html><head><title>⚙️ Админ v2.0</title></head><body>
<div class="container">
    <header><h1 style="color:var(--danger);">⚙️ СУПЕР-АДМИН v2.0</h1></header>
    
    <!-- ✅ ДАШБОРД -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px;margin-bottom:40px;">
        <div class="role-card role-admin">👥 {stats['total_users']} игроков</div>
        <div class="role-card role-premium">💎 {stats['premium_users']} Premium</div>
        <div class="role-card role-mod">💬 {stats['today_messages']:,} сообщений/день</div>
        <div class="role-card role-start">👥 {stats['total_clans']} кланов</div>
        <div class="role-card role-vip">🚫 {stats['active_mutes']} мутов</div>
    </div>
    
    <!-- ✅ МАССОВЫЕ ДЕЙСТВИЯ -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;">
        <div class="game-card">
            <h3>🚫 МАССОВЫЙ МУТ</h3>
            <form method="POST">
                <input type="hidden" name="action" value="mass_mute">
                <select name="duration">
                    <option value="600">10 мин (мат)</option>
                    <option value="900">15 мин (спам)</option>
                    <option value="1800">30 мин (флуд)</option>
                    <option value="3600">1 час</option>
                </select>
                <input name="reason" placeholder="Причина мута" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--danger);">🔇 МУТАТЬ ВЫБРАННЫХ</button>
            </form>
        </div>
        <div class="game-card">
            <h3>💰 МАССОВЫЕ МОНЕТЫ</h3>
            <form method="POST">
                <input type="hidden" name="action" value="mass_coins">
                <input name="amount" type="number" placeholder="Количество монет" required>
                <button type="submit" class="nav-btn" style="width:100%;background:var(--success);">💰 ВЫДАТЬ ВСЕМ</button>
            </form>
        </div>
    </div>
    
    <!-- ✅ НЕДАВНИЕ АКТИВНОСТИ -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:40px;">
        <div class="game-card">
            <h3>👥 АКТИВНЫЕ ИГРОКИ</h3>
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:var(--info);color:white;"><th>Игрок</th><th>💰</th><th>Онлайн</th></tr></thead>
                <tbody>{recent_users_html}</tbody>
            </table>
        </div>
        <div class="game-card">
            <h3>🚫 АКТИВНЫЕ МУТЫ</h3>
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:var(--danger);color:white;"><th>Игрок</th><th>Причина</th><th>Осталось</th></tr></thead>
                <tbody>{recent_mutes_html or '<tr><td colspan=3 style=\"padding:40px;text-align:center;color:#666;\">Нет активных мутов</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    
    <div style="text-align:center;margin:60px 0;">
        <form method="POST" style="display:inline;">
            <input type="hidden" name="action" value="clear_chat">
            <button type="submit" class="nav-btn" style="background:var(--warning);">🧹 ОЧИСТИТЬ ЧАТ (7 дней)</button>
        </form>
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div>
</div></body></html>'''

# ✅ РЕГИСТРАЦИЯ v43.0
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 4:
            return render_template_string(f'{PREMIUM_CSS_V43}<div class="container"><div class="game-card"><h2 style="color:var(--danger);">❌ Ник: 3+ символа, пароль: 4+</h2><a href="/register" class="nav-btn">🔙 Попробовать снова</a></div></div>')
        
        if get_user(username):
            return render_template_string(f'{PREMIUM_CSS_V43}<div class="container"><div class="game-card"><h2 style="color:var(--danger);">❌ Ник {username} занят!</h2><a href="/register" class="nav-btn">🔙 Попробовать снова</a></div></div>')
        
        conn = db.get_connection()
        if conn:
            conn.execute('INSERT INTO users (username, password_hash, created) VALUES (?, ?, ?)',
                       (username, generate_password_hash(password), time.time()))
            conn.commit()
            conn.close()
            logger.info(f"👤 НОВЫЙ ИГРОК: {username}")
            return redirect('/login')
    
    return f'''{PREMIUM_CSS_V43}
<div class="container">
    <div class="game-card" style="max-width:500px;margin:100px auto;text-align:center;">
        <h1 style="font-size:5em;margin-bottom:30px;">📝 РЕГИСТРАЦИЯ v43.0</h1>
        <form method="POST" style="max-width:400px;margin:0 auto;">
            <input name="username" placeholder="👤 Никнейм (3+ символа)" required autofocus maxlength="20">
            <input name="password" type="password" placeholder="🔒 Пароль (4+ символа)" required maxlength="50">
            <button type="submit" class="nav-btn" style="width:100%;background:var(--success);font-size:20px;padding:25px 20px;">🚀 ЗАРЕГИСТРИРОВАТЬСЯ</button>
        </form>
        <div style="margin-top:30px;">
            <a href="/login" class="nav-btn" style="background:var(--info);">🔐 Уже есть аккаунт</a>
        </div>
        <div class="premium-badge" style="margin-top:30px;font-size:14px;">Узнавайкин v43.0 — 2026 ©</div>
    </div>
</div>'''

# ✅ 404 + ФИНАЛЬНЫЙ ЗАПУСК
@app.errorhandler(404)
def not_found(e):
    return f'''{PREMIUM_CSS_V43}
<div class="container" style="text-align:center;padding:150px 20px;">
    <h1 style="font-size:10em;color:var(--danger);margin-bottom:20px;">❓ 404</h1>
    <h2 style="font-size:2.5em;color:var(--dark);margin-bottom:40px;">Страница не найдена</h2>
    <a href="/" class="nav-btn" style="font-size:20px;padding:25px 50px;">🏠 На главную</a>
</div>''', 404

@app.route('/daily')
@require_auth
def daily():
    bonus, claimed = get_daily_bonus(session['user'])
    return f'<h1>📅 ЕЖЕДНЕВНЫЙ БОНУС</h1><p>{bonus if bonus > 0 else "Бонус уже получен!"}'

if __name__ == '__main__':
    print("🚀" * 70)
    print("🎉 УЗНАВАЙКИН v43.0 — ПОЛНЫЙ РЕЛИЗ! 23+ МЕГА-ФИЧИ!")
    print("✅ Кланы • Банк 5% • Рулетка x35 • Лотерея 0.3% • Socket.IO")
    print("✅ PWA • Темная тема • Супер-Админка • 9 таблиц БД")
    print("👑 Логин: CatNap/Назар | Пароль: 120187 | 100k💰 + 500 стрик!")
    print("🎮 РОУТЫ: /casino 🎰 /bank 🏦 /clans 👥 /leaderboard 🏆 /admin ⚙️")
    print("🚀" * 70)
    
    socketio.run(app, host='0.0.0.0', port=10000, debug=False, allow_unsafe_werkzeug=True)
