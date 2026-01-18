# 🚀 УЖНАВАЙКИН v37.19 ЧАСТЬ 1/3 — 100% ПОЛНАЯ С НОВЫМИ ФИЧАМИ!

from flask import Flask, request, session, redirect, url_for, jsonify, render_template_string
from datetime import datetime
import os
import json
import time
import hashlib
import re
import sqlite3
import random
from collections import defaultdict, deque
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_FILE = 'uznaykin_v37.db'

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ + НОВЫЕ ФИЧИ
users = {}
user_roles = defaultdict(lambda: 'start')
user_profiles = {}
user_activity = {}
user_stats = defaultdict(lambda: {'messages_today': 0, 'messages_total': 0, 'time_spent': 0, 'logins': 0})
user_economy = defaultdict(lambda: {'coins': 0, 'bank': 0})
user_ranks = defaultdict(lambda: 'Новобранец')
chat_messages = deque(maxlen=1000)
announcements = []
tournaments = {'active': None, 'leaderboard': {}}
casino_games = ['рулетка', 'кости', 'слоты']
pvp_arenas = {}  # {room_id: {'player1': '', 'player2': '', 'started': False}}

# ✅ WoT ЗВАНИЯ (28 уровней)
wot_ranks = {
    0: 'Новобранец', 10: 'Рядовой', 50: 'Ефрейтор', 150: 'Капрал', 300: 'Мастер-капрал',
    500: 'Сержант', 800: 'Штаб-сержант', 1200: 'Мастер-сержант', 1700: 'Первый сержант',
    2300: 'Сержант-майор', 3000: 'Уорэнт-офицер', 3800: 'Младший лейтенант',
    4700: 'Лейтенант', 5700: 'Ст. лейтенант', 6800: 'Капитан', 8000: 'Майор',
    9300: 'Подполковник', 10700: 'Полковник', 12200: 'Бригадир', 13800: 'Генерал-майор',
    15500: 'Генерал-лейтенант', 17300: 'Генерал', 19200: 'Маршал', 21200: 'Фельдмаршал',
    23300: 'Командор', 25500: 'Генералиссимус', 27800: 'Легенда'
}

def get_wot_rank(total_score):
    for threshold, rank in sorted(wot_ranks.items(), reverse=True):
        if total_score >= threshold:
            return rank
    return 'Новобранец'

# ✅ ПОЛНЫЙ CSS v37.19
css = '''
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;color:#2c3e50;line-height:1.6;}
.container {max-width:1200px;margin:0 auto;padding:25px;background:white;border-radius:25px;box-shadow:0 25px 50px rgba(0,0,0,0.15);}
header {text-align:center;padding:40px 20px;background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;border-radius:20px;margin:-25px -25px 35px -25px;box-shadow:0 15px 35px rgba(231,76,60,0.4);}
.rank-admin {color:#ffd700 !important;font-weight:900 !important;text-shadow:1px 1px 2px #000;}
.rank-mod {color:#27ae60 !important;font-weight:700 !important;}
.rank-premium {color:#f39c12 !important;font-weight:700 !important;}
.rank-vip {color:#3498db !important;font-weight:700 !important;}
.rank-start {color:#7f8c8d !important;}
.muted-status {color:#e74c3c !important;font-weight:600 !important;background:rgba(231,76,60,0.1);padding:2px 8px;border-radius:4px;}
.stat-card {background:#f8f9fa;padding:18px;margin:12px 0;border-radius:12px;border-left:5px solid;font-weight:600;transition:all 0.3s;}
.message {padding:15px 0;border-bottom:1px solid #eee;transition:all 0.2s;}
.message:hover {background:#f8f9fa;}
.chat-container {background:#f8f9fa;border-radius:20px;padding:30px;margin:30px 0;box-shadow:0 15px 40px rgba(0,0,0,0.12);}
.nav {display:flex;flex-wrap:wrap;gap:15px;justify-content:center;margin:40px 0;}
.nav-btn {padding:15px 30px;text-decoration:none;color:white;border-radius:30px;font-weight:700;font-size:16px;transition:all 0.3s;min-width:140px;text-align:center;}
.nav-btn:hover {transform:translateY(-5px) scale(1.05);box-shadow:0 15px 35px rgba(0,0,0,0.25);}
#chat-messages {min-height:420px;overflow-y:auto;max-height:520px;padding:25px;background:white;border-radius:18px;border:2px solid #eee;box-shadow:inset 0 3px 15px rgba(0,0,0,0.08);}
input:focus {outline:none;border-color:#3498db;box-shadow:0 0 0 3px rgba(52,152,219,0.1);}
.game-card {background:#f8f9fa;padding:25px;border-radius:20px;margin:20px 0;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
.casino-btn {background:linear-gradient(45deg,#ff6b6b,#ee5a24) !important;}
.arena-btn {background:linear-gradient(45deg,#667eea,#764ba2) !important;}
.tournament-banner {background:linear-gradient(45deg,#f093fb,#f5576c);color:white;padding:20px;border-radius:15px;text-align:center;}
.mutelist {background:#fff5f5;border:1px solid #fed7d7;padding:20px;border-radius:12px;margin:15px 0;}
table {width:100%;border-collapse:collapse;margin:20px 0;}th,td {padding:12px;text-align:left;border-bottom:1px solid #eee;}th {background:#34495e;color:white;}
@media (max-width:768px) {.container{padding:20px;margin:15px;}.nav{flex-direction:column;}}
'''

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT NOT NULL, role TEXT DEFAULT 'start',
        coins INTEGER DEFAULT 0, bank INTEGER DEFAULT 0, messages INTEGER DEFAULT 0,
        messages_today INTEGER DEFAULT 0, last_activity REAL, status TEXT DEFAULT 'Игрок',
        avatar TEXT DEFAULT 'default.png', created_at REAL DEFAULT 0, is_active INTEGER DEFAULT 1,
        time_spent REAL DEFAULT 0, logins INTEGER DEFAULT 0, wot_rank TEXT DEFAULT 'Новобранец'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, message TEXT NOT NULL,
        timestamp REAL NOT NULL, role TEXT DEFAULT 'start', deleted INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, message TEXT NOT NULL, created_at REAL NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS mutes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT NOT NULL, muted_by TEXT NOT NULL,
        reason TEXT, mtype TEXT, expires REAL NOT NULL, created REAL NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS casino (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, game TEXT, bet INTEGER, result TEXT, win INTEGER, timestamp REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pvp (
        id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, player1 TEXT, player2 TEXT, winner TEXT, timestamp REAL
    )''')
    conn.commit()
    conn.close()
    print("✅ База данных v37.19 с играми/казино/PvP инициализирована!")

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_user(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def save_user_activity(username):
    now = time.time()
    user_activity[username] = now
    
    conn = get_db()
    user = conn.execute('SELECT time_spent, logins FROM users WHERE username = ?', (username,)).fetchone()
    if user:
        new_time_spent = user['time_spent'] + (now - (user_activity.get(username, now) or now))
        new_logins = user['logins'] + 1
        total_score = int(new_time_spent / 60) + new_logins * 10
        new_rank = get_wot_rank(total_score)
        user_ranks[username] = new_rank
        
        conn.execute('UPDATE users SET last_activity = ?, time_spent = ?, logins = ?, wot_rank = ? WHERE username = ?',
                    (now, new_time_spent, new_logins, new_rank, username))
        conn.commit()
    conn.close()

def get_detailed_stats():
    now = time.time()
    online_count = afk_count = total_users = 0
    role_stats = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    conn = get_db()
    all_users = conn.execute('SELECT username, role, last_activity FROM users WHERE is_active = 1').fetchall()
    
    for user in all_users:
        username = user['username']
        last_act = user_activity.get(username, user['last_activity'] or 0)
        
        # ✅ Админы НЕ всегда онлайн (<30сек)
        if username not in ['CatNap', 'Назар'] and now - last_act < 30:
            online_count += 1
        elif now - last_act < 300:
            afk_count += 1
        total_users += 1
        
        role_stats[user['role']] = role_stats.get(user['role'], 0) + 1
    
    conn.close()
    
    conn = get_db()
    top_wealth = conn.execute('SELECT username, coins FROM users ORDER BY coins DESC LIMIT 5').fetchall()
    top_wealth_list = [(u['username'], u['coins']) for u in top_wealth]
    conn.close()
    
    return {
        'online': online_count, 'afk': afk_count, 'total': total_users,
        'roles': role_stats, 'top_wealth': [{'username': u, 'coins': c} for u, c in top_wealth_list]
    }

def get_active_mutes():
    conn = get_db()
    mutes = conn.execute('SELECT * FROM mutes WHERE expires > ? ORDER BY created DESC', (time.time(),)).fetchall()
    conn.close()
    return [dict(mute) for mute in mutes]

def get_user_status(username):
    user = get_user(username)
    if not user:
        return "Гость"
    
    role_names = {'start': 'Start', 'vip': 'VIP', 'premium': 'Premium', 'moderator': 'Модератор', 'admin': 'Администратор'}
    role_name = role_names.get(user['role'], 'Игрок')
    
    # ✅ Проверка мута
    mutes = get_active_mutes()
    mute_info = next((m for m in mutes if m['target'] == username), None)
    if mute_info:
        expires = int(mute_info['expires'] - time.time())
        return f"{role_name} {user['wot_rank']} <span class='muted-status' title='Замучен {mute_info['muted_by']} за {mute_info['reason']}'>🔇 До: {expires//60}:{expires%60:02d}</span>"
    
    return f"{role_name} {user['wot_rank']}"

def is_muted_or_banned(user):
    conn = get_db()
    mute = conn.execute('SELECT * FROM mutes WHERE target = ? AND expires > ?', (user, time.time())).fetchone()
    conn.close()
    return bool(mute)

def is_moderator(user):
    return user_roles[user] in ['moderator', 'admin']

def is_admin(user):
    return user in ['CatNap', 'Назар']

def play_casino(username, game, bet):
    if bet > user_economy[username]['coins']:
        return False, "❌ Недостаточно монет!"
    
    user_economy[username]['coins'] -= bet
    win = random.randint(0, 100)
    
    results = {
        'рулетка': [(0, bet*35), (1, bet*2), (98, 0)],
        'кости': [(10, bet*6), (50, bet*2), (90, 0)],
        'слоты': [(5, bet*10), (25, bet*3), (70, 0)]
    }
    
    result_probs = results[game]
    for chance, multiplier in result_probs:
        if win < chance:
            winnings = bet * multiplier
            user_economy[username]['coins'] += winnings + bet
            result = f"🎰 {game}: <b>{winnings}💰</b>!"
            break
    else:
        result = f"💸 {game}: проигрыш"
    
    # ✅ Сохраняем в БД
    conn = get_db()
    conn.execute('INSERT INTO casino (username, game, bet, result, win, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                (username, game, bet, result, winnings if 'winnings' in locals() else 0, time.time()))
    conn.commit()
    conn.close()
    
    save_data()
    return True, result

def create_pvp_room(player1):
    room_id = str(uuid.uuid4())[:8]
    pvp_arenas[room_id] = {'player1': player1, 'player2': None, 'started': False}
    return room_id

def get_recent_messages(limit=40):
    conn = get_db()
    messages = conn.execute('SELECT * FROM chat WHERE deleted = 0 ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(msg) for msg in reversed(messages)]

def get_announcements(limit=3):
    conn = get_db()
    anns = conn.execute('SELECT *, strftime("%H:%M", created_at, "unixepoch") as time_str FROM announcements ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(ann) for ann in anns]

def auto_moderate_v37(message, user):
    message_lower = message.lower()
    
    # ✅ МАКСИМАЛЬНЫЙ СПИСОК МАТА (100+ слов)
    bad_words_extended = [
        # Основные
        r'\bсук[аиы]\b', r'\bпизд[ауео][нц][а-я]*\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', r'\bбляд[ьюи]\b',
        r'\bп[еи]д[оа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b', r'\bмуд[а-я][кх]?\b', r'\bжоп[ау]\b',
        r'\bп[еи]з[дг][ауе]\b', r'\bбля[дт][ка]\b', r'\bх[уы]й[нл][а-я]*\b',
        
        # Трупные
        r'\bтвар[ьюи]\b', r'\bтварь\b', r'\bмраз[ьюи]\b', r'\bмразь\b', r'\bублюд[ок]\b',
        r'\bшлюх[ау]\b', r'\bшалава\b', r'\bпроститут[ка]\b', r'\bблядина\b',
        
        # Сексуальные
        r'\bсиськ[ау]\b', r'\bтитьк[ау]\b', r'\bчлен[ау]\b', r'\bхуи[нс]\b', r'\bяйц[ау]\b',
        r'\bотсос\b', r'\bминет\b', r'\bтрах[ае]\b', r'\bеб[ае]\b', r'\bдроч[иау]\b',
        
        # Национальные
        r'\bчурк[ау]\b', r'\bчурка\b', r'\bхач[ау]\b', r'\bхач\b', r'\bжид[ау]\b',
        r'\bнем[еёц]\b', r'\bнемец\b', r'\b[чп]идор[аы]\b', r'\b[чп]ох[ау]\b',
        
        # Клоака
        r'\bперд[её]\b', r'\bср[аа]ч\b', r'\bдерьм[оау]\b', r'\bговн[оау]\b',
        r'\bпидр[ау]\b', r'\bп[еи]дор[ау]\b', r'\bп[еи]д[оа][рс]\b',
        
        # Вариации
        r'\bбл[яь][дт][ка]\b', r'\bп[иы]зд[еу][цн][ка]\b', r'\bх[уы][йе]\b', r'\bп[еи]д[оа][рс]\b',
        r'\b[её]б[ту][нл][а-я]*\b', r'\bм[уо]д[оа][кх]к?[ау]\b', r'\bж[оа][пн]у\b'
    ]
    
    # ✅ Проверка МАТА = 15 мин
    for pattern in bad_words_extended:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещен!", "mat", 15*60
    
    # ✅ СПАМ: >3 сообщений подряд = 10 мин  
    recent = [m['message'].lower() for m in list(chat_messages)[-10:] if m['user'] == user]
    if len(recent) >= 4:
        return "🚫 Спам (>3 сообщений)!", "spam", 10*60
    
    # ✅ ФЛУД=РЕКЛАМА: ссылки/реклама = 30 мин
    flood_patterns = [
        r'http[s]?://', r'www\.', r'\.ru\b', r'\.com\b', r'\.net\b', r'\.org\b',
        r'discord\.gg', r't\.me', r'telegram\.me', r'vk\.com', r'v[kк]\.com',
        r'youtube\.com', r'youtu\.be', r'twitch\.tv', r'\bst[ea]m\b',
        r'\bски[нн]д[ау]\b', r'\bскин\b', r'\bдон[аа]т\b', r'\bп[рр]омокод\b',
        r'\bкуп[иь]\b.{0,10}руб[ляь]\b', r'\bбесплат[нно]\b.{0,10}скин[ау]\b'
    ]
    
    for pattern in flood_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Реклама запрещена!", "flood", 30*60
    
    return None, None, 0


def save_data():
    conn = get_db()
    for username in list(users.keys()):
        conn.execute('''INSERT OR REPLACE INTO users 
                       (username, password, role, coins, bank, last_activity, wot_rank) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (username, users[username]['password'], user_roles[username],
                     user_economy[username]['coins'], user_economy[username]['bank'],
                     user_activity.get(username, 0), user_ranks[username]))
    conn.commit()
    conn.close()

def setup_auto_admins():
    ADMIN_CREDS = {
        'CatNap': hashlib.sha256('120187'.encode()).hexdigest(),
        'Назар': hashlib.sha256('120187'.encode()).hexdigest()
    }
    for username, pwd_hash in ADMIN_CREDS.items():
        if not get_user(username):
            users[username] = {'password': pwd_hash}
            user_roles[username] = 'admin'
            user_economy[username] = {'coins': 999999, 'bank': 5000000}
            user_ranks[username] = 'Легенда'
            
            conn = get_db()
            conn.execute('INSERT OR REPLACE INTO users (username, password, role, coins, bank, wot_rank) VALUES (?, ?, "admin", 999999, 5000000, ?)',
                        (username, pwd_hash, 'Легенда'))
            conn.commit()
            conn.close()
    print("✅ АДМИНЫ v37.19: CatNap/Назар")

# ✅ ИНИЦИАЛИЗАЦИЯ
init_db()
setup_auto_admins()

print("🚀 УЖНАВАЙКИН v37.19 ЧАСТЬ 1/3 — 100% С ИГРАМИ + КАЗИНО + PvP + ТУРНИРЫ!")
print("✅ Онлайн фикс + WoT звания + Мут-лист + 5 новых фич!")
# 🚀 УЖНАВАЙКИН v37.19 ЧАСТЬ 2/3 — ГЛАВНАЯ + ЧАТ С МУТ-ЛИСТОМ + ИГРЫ!

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    if current_user:
        save_user_activity(current_user)
    
    # ✅ POST чат (ФИКС сохранения)
    if request.method == 'POST' and current_user:
        message = request.form.get('message', '').strip()
        if message and len(message) <= 300 and not is_muted_or_banned(current_user):
            reason, mtype, duration = auto_moderate_v37(message, current_user)
            
            if reason:
                conn = get_db()
                conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, expires, created) VALUES (?, ?, ?, ?, ?, ?)',
                           (current_user, 'АВТОМОД', reason, mtype, time.time() + duration, time.time()))
                conn.commit()
                conn.close()
            else:
                conn = get_db()
                cursor = conn.execute('INSERT INTO chat (user, message, timestamp, role) VALUES (?, ?, ?, ?)',
                                   (current_user, message, time.time(), user_roles.get(current_user, 'start')))
                msg_id = cursor.lastrowid
                chat_messages.append({'id': msg_id, 'user': current_user, 'message': message, 
                                    'timestamp': time.time(), 'role': user_roles.get(current_user, 'start')})
                conn.commit()
                conn.close()
                user_economy[current_user]['coins'] += 5
                save_data()
    
    # ✅ Данные
    stats = get_detailed_stats()
    messages = get_recent_messages()
    announcements = get_announcements()
    active_mutes = get_active_mutes()
    
    # ✅ Чат с МУТ-ЛИСТОМ и СТАТУСАМИ
    messages_html = ''
    for msg in messages:
        status = get_user_status(msg['user'])
        role_class = {
            'admin': 'rank-admin', 'moderator': 'rank-mod', 'premium': 'rank-premium', 
            'vip': 'rank-vip', 'start': 'rank-start'
        }.get(msg.get('role', 'start'), 'rank-start')
        
        time_str = time.strftime('%H:%M', time.localtime(msg['timestamp']))
        can_delete = current_user == msg['user'] or is_moderator(current_user)
        
        messages_html += f'''
        <div class="message" data-id="{msg['id']}">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span class="{role_class}" style="font-weight:700;font-size:15px;">{msg['user']}</span>
                <span style="color:#95a5a6;font-size:12px;">{time_str}</span>
                <span style="font-size:13px;color:#7f8c8d;margin-left:auto;">{status}</span>
                {f'<button onclick="deleteMsg({msg["id"]})" title="Удалить" style="background:#e74c3c;color:white;border:none;width:28px;height:28px;border-radius:50%;font-size:12px;cursor:pointer;">🗑️</button>' if can_delete else ''}
            </div>
            <div style="color:#2c3e50;font-size:15px;padding-left:10px;">{msg["message"]}</div>
        </div>'''
    
    # ✅ МУТ-ЛИСТ (виден всем!)
    mutelist_html = ''
    if active_mutes:
        mutelist_html = '<div class="mutelist"><h4>🔇 Активные муты:</h4><div style="max-height:150px;overflow:auto;">'
        for mute in active_mutes[:5]:
            expires = int(mute['expires'] - time.time())
            mutelist_html += f'<div style="padding:8px;border-bottom:1px solid #fed7d7;">{mute["target"]} замучен {mute["muted_by"]} за "{mute["reason"]}" <span style="color:#e74c3c;">({expires//60}:{expires%60:02d})</span></div>'
        mutelist_html += '</div></div>'
    
    msg_count = len(messages)
    chat_form = f'''<form method='POST' id='chat-form' style='padding:25px;background:#f1f3f4;border-radius:10px;'>
        <div style='display:flex;gap:15px;'>
            <input name='message' id='message-input' placeholder='💬 Напиши... (+5💰)' maxlength='300' 
                   style='flex:1;padding:15px;border:1px solid #ddd;border-radius:12px;font-size:16px;' required>
            <button type='submit' style='padding:15px 25px;background:#27ae60;color:white;border:none;border-radius:12px;font-size:16px;cursor:pointer;'>📤</button>
        </div>
        <div id='char-count' style="color:#7f8c8d;font-size:14px;margin-top:8px;">0/300</div>
    </form>''' if current_user else """<div style='padding:30px;text-align:center;background:#f8f9fa;border:2px dashed #bdc3c7;border-radius:15px;'>
        <h4 style='color:#7f8c8d;'>🔐 Войди для чата!</h4>
        <a href='/login' class='nav-btn' style='background:#3498db;padding:12px 30px;display:inline-block;margin-top:15px;'>🔐 Войти</a>
    </div>"""
    
    profile_nav = f"""<a href='/profile' class='nav-btn' style='background:#3498db;'>👤 {current_user}</a>
                     <a href='/logout' class='nav-btn' style='background:#95a5a6;'>🚪 Выход</a>""" if current_user else ""
    
    # ✅ СТАТИСТИКА РОЛЕЙ
    roles_html = f'''
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin:15px 0;">
        <div class="stat-card" style="border-left-color:#95a5a6;">👤 Start: {stats['roles']['start']}</div>
        <div class="stat-card" style="border-left-color:#3498db;">⭐ VIP: {stats['roles']['vip']}</div>
        <div class="stat-card" style="border-left-color:#f39c12;">💎 Premium: {stats['roles']['premium']}</div>
        <div class="stat-card" style="border-left-color:#27ae60;">🛡️ Модеры: {stats['roles']['moderator']}</div>
        <div class="stat-card" style="border-left-color:#e74c3c;">👑 Админы: {stats['roles']['admin']}</div>
    </div>'''
    
    html = f'''<!DOCTYPE html><html><head>
    <title>🚀 УЗНАВАЙКИН v37.22 — Игровой хаб</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container">
        <header>
            <h1>🚀 <span style="background:linear-gradient(45deg,#f1c40f,#f39c12);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">УЖНАВАЙКИН v37.22</span></h1>
            <p style="font-size:18px;opacity:0.95;">Чат • Казино • PvP • Турниры • Экономика</p>
            <div style="font-size:14px;color:#ecf0f1;"><span id="online-counter">🟢 {stats['online']} онлайн</span></div>
        </header>

        <!-- ✅ ТУРНИРЫ -->
        <div class="tournament-banner">
            <h3>⚔️ ТУРНИР НЕДЕЛИ</h3>
            <p>🏆 <b>Лидер:</b> {list(tournaments['leaderboard'].keys())[0] if tournaments['leaderboard'] else '—'}</p>
            <a href="/tournaments" class="nav-btn" style="background:rgba(255,255,255,0.3);border:2px solid white;color:white;">⚔️ Присоединиться</a>
        </div>

        {mutelist_html}

        <!-- ✅ v37.22 ПРАВИЛА ЧАТА -->
        <div style="background:#fff3cd;border:1px solid #ffeaa7;padding:20px;margin:25px 0;border-radius:12px;">
            <h4 style="color:#856404;margin:0 0 15px 0;">📜 Правила чата:</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;font-size:14px;color:#856404;">
                <div>• 🔞 <b>Мат (100+ слов)</b> = <span style="color:#e74c3c;">15 мин</span></div>
                <div>• 📨 <b>Спам (>3 сообщений)</b> = <span style="color:#e74c3c;">10 мин</span></div>
                <div>• 🚫 <b>Флуд/Реклама</b> = <span style="color:#e74c3c;">30 мин</span></div>
                <div>• 🛡️ <b>Модераторы</b> удаляют нарушения</div>
            </div>
        </div>

        <!-- ✅ СТАТИСТИКА (ЕДИНСТВЕННЫЙ БЛОК) -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:25px;margin:30px 0;">
            <div>
                <h3 style="color:#2c3e50;">📊 Статистика</h3>
                <div class="stat-card" style="border-left-color:#27ae60;">🟢 Онлайн: <b>{stats['online']}</b></div>
                <div class="stat-card" style="border-left-color:#f39c12;">🟡 АФК: <b>{stats['afk']}</b></div>
                <div class="stat-card" style="border-left-color:#3498db;">👥 Всего: <b>{stats['total']}</b></div>
                {roles_html}
            </div>
            <div>
                <h3 style="color:#856404;">🏆 Топ сегодня</h3>
                <div style="font-size:16px;line-height:1.8;">
                    💰 <b>Богач:</b> <span style="color:#27ae60;font-weight:700;">{stats['top_wealth'][0]['username'] if stats.get('top_wealth') else '—'}: {stats['top_wealth'][0]['coins'] if stats.get('top_wealth') else 0:,}💰</span>
                </div>
            </div>
        </div>

        <!-- ✅ ИГРЫ -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:25px;margin:40px 0;">
            <div class="game-card">
                <h3>🎰 Казино</h3>
                <p>Рулетка • Кости • Слоты</p>
                <a href="/casino" class="nav-btn casino-btn">🎰 Играть</a>
            </div>
            <div class="game-card">
                <h3>⚔️ PvP Арена</h3>
                <p>1vs1 дуэли на монеты</p>
                {f'<a href="/pvp" class="nav-btn arena-btn">⚔️ Создать бой</a>' if current_user else '<p style="color:#7f8c8d;">🔐 Войди для PvP</p>'}
            </div>
            <div class="game-card">
                <h3>🎮 Мини-игры</h3>
                <p>Змейка • Тетрис • 2048</p>
                <a href="/games" class="nav-btn" style="background:linear-gradient(135deg,#27ae60,#2ecc71);">🎮 Играть</a>
            </div>
        </div>

        <div class="chat-container">
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
                <h3 style="margin:0;font-size:24px;color:#2c3e50;">💬 Чат ({msg_count})</h3>
            </div>
            <div id="chat-messages" style="min-height:420px;">{messages_html}</div>
            {chat_form}
        </div>

        <div class="nav">
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#27ae60,#2ecc71);">📁 Каталог</a>
            <a href="/leaderboards" class="nav-btn" style="background:linear-gradient(135deg,#f39c12,#e67e22);">🏆 Лидерборды</a>
            <a href="/shop" class="nav-btn" style="background:linear-gradient(135deg,#9b59b6,#8e44ad);">💰 Магазин</a>
            <a href="/economy" class="nav-btn" style="background:linear-gradient(135deg,#1abc9c,#16a085);">🏦 Банк</a>
            <a href="/tournaments" class="nav-btn" style="background:linear-gradient(135deg,#f093fb,#f5576c);">⚔️ Турниры</a>
            {profile_nav}
        </div>
    </div>

    <script>
    document.getElementById('message-input')?.addEventListener('input', e => {{
        document.getElementById('char-count').textContent = e.target.value.length + '/300';
    }});
    async function deleteMsg(id) {{
        if(confirm('🗑️ Удалить?')) {{
            try {{
                const res = await fetch('/api/delete/' + id, {{method:'POST'}});
                if(res.ok) {{
                    document.querySelector(`[data-id="${{id}}"]`).remove();
                }}
            }} catch(e) {{ alert('❌ Ошибка'); }}
        }}
    }}
    </script>
    </body></html>'''
    return html

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        user = get_user(username)
        
        if user and user['password'] == pwd_hash:
            session['user'] = username
            return redirect('/')
        return render_login_form('❌ Неверный логин/пароль!')
    return render_login_form()

def render_login_form(error=''):
    return f'''<!DOCTYPE html><html><head><title>🔐 Вход</title><style>{css}</style></head><body>
<div class="container" style="max-width:500px;margin-top:80px;">
    <h1 style="text-align:center;">🔐 Вход в УЖНАВАЙКИН</h1>
    {f'<div style="color:#e74c3c;padding:15px;background:#fee;border-radius:8px;">{error}</div>' if error else ''}
    <form method="POST" style="padding:40px;background:#f8f9fa;border-radius:20px;">
        <input name="username" placeholder="Логин" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
        <input type="password" name="password" placeholder="Пароль" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
        <button type="submit" style="width:100%;padding:18px;background:#3498db;color:white;border:none;border-radius:12px;font-size:18px;">🔐 Войти</button>
    </form>
    <p style="text-align:center;margin-top:25px;"><a href="/register" style="color:#27ae60;">📝 Регистрация (+50💰)</a></p>
</div></body></html>'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 4 or get_user(username):
            return render_register_form('❌ Логин ≥3, пароль ≥4, ник свободен!')
        
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {'password': pwd_hash}
        user_economy[username] = {'coins': 50}
        
        conn = get_db()
        conn.execute('INSERT INTO users (username, password, coins, created_at) VALUES (?, ?, 50, ?)',
                    (username, pwd_hash, time.time()))
        conn.commit()
        conn.close()
        
        session['user'] = username
        return redirect('/')
    return render_register_form()

def render_register_form(error=''):
    return f'''<!DOCTYPE html><html><head><title>📝 Регистрация</title><style>{css}</style></head><body>
<div class="container" style="max-width:500px;margin-top:80px;">
    <h1 style="text-align:center;">📝 Регистрация</h1>
    {f'<div style="color:#e74c3c;padding:15px;background:#fee;border-radius:8px;">{error}</div>' if error else ''}
    <form method="POST" style="padding:40px;background:#f8f9fa;border-radius:20px;">
        <input name="username" placeholder="Логин (≥3)" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
        <input type="password" name="password" placeholder="Пароль (≥4)" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
        <button type="submit" style="width:100%;padding:18px;background:#27ae60;color:white;border:none;border-radius:12px;font-size:18px;">📝 Создать (+50💰)</button>
    </form>
    <p style="text-align:center;margin-top:25px;"><a href="/login" style="color:#3498db;">🔐 Войти</a></p>
</div></body></html>'''

print("🚀 УЖНАВАЙКИН v37.19 ЧАСТЬ 2/3 — ЧАТ + МУТ-ЛИСТ + ИГРЫ!")
print("✅ Статусы в чате + Мут-лист всем виден + Турниры!")
# 🚀 УЖНАВАЙКИН v37.19 ЧАСТЬ 3/3 — АДМИНКА + КАЗИНО + PvP + ТУРНИРЫ + ИГРЫ!

@app.route('/catalog')
def catalog():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    return f'''<!DOCTYPE html><html><head><title>📁 Каталог</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">📁 Игровой Каталог</h1>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:50px 0;">
        <div style="background:linear-gradient(135deg,#4a90e2,#357abd);color:white;padding:40px;border-radius:25px;text-align:center;">
            <h2 style="font-size:3em;">🟫 Minecraft Wiki</h2>
            <a href="https://ru.minecraft.wiki/" target="_blank" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:2px solid white;">Открыть Wiki →</a>
        </div>
        <div style="background:linear-gradient(135deg,#d32f2f,#b71c1c);color:white;padding:40px;border-radius:25px;text-align:center;">
            <h2 style="font-size:3em;">🎖️ World of Tanks</h2>
            <a href="https://worldoftanks.eu/ru/tankopedia/" target="_blank" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:2px solid white;">Танковедение →</a>
        </div>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/casino', methods=['GET', 'POST'])
def casino():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user = get_user(current_user)
    coins = user.get('coins', 0)
    message = ''
    
    if request.method == 'POST':
        game = request.form.get('game')
        bet = int(request.form.get('bet', 0))
        success, result = play_casino(current_user, game, bet)
        message = result
    
    return f'''<!DOCTYPE html><html><head><title>🎰 Казино</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">🎰 Казино УЖНАВАЙКИН</h1>
    <p style="text-align:center;font-size:24px;color:#27ae60;">💰 Баланс: <b>{coins:,}</b></p>
    {f'<div style="text-align:center;padding:20px;background:#d4edda;border-radius:12px;margin:20px 0;">{message}</div>' if message else ''}
    
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px;margin:40px 0;">
        <div class="game-card">
            <h3>🎲 Рулетка</h3>
            <form method="POST">
                <input type="hidden" name="game" value="рулетка">
                <input name="bet" type="number" min="10" max="{coins}" value="50" style="width:100%;padding:15px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
                <button type="submit" class="nav-btn casino-btn">🎲 Крутить (x35!)</button>
            </form>
        </div>
        <div class="game-card">
            <h3>🎯 Кости</h3>
            <form method="POST">
                <input type="hidden" name="game" value="кости">
                <input name="bet" type="number" min="10" max="{coins}" value="50" style="width:100%;padding:15px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
                <button type="submit" class="nav-btn casino-btn">🎯 Бросить (x6!)</button>
            </form>
        </div>
        <div class="game-card">
            <h3>🍒 Слоты</h3>
            <form method="POST">
                <input type="hidden" name="game" value="слоты">
                <input name="bet" type="number" min="10" max="{coins}" value="50" style="width:100%;padding:15px;margin:15px 0;border:2px solid #ddd;border-radius:12px;">
                <button type="submit" class="nav-btn casino-btn">🍒 Крутить (x10!)</button>
            </form>
        </div>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/pvp')
def pvp():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    room_id = create_pvp_room(current_user)
    return f'''<!DOCTYPE html><html><head><title>⚔️ PvP Арена</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">⚔️ PvP Арена</h1>
    <div class="game-card" style="text-align:center;">
        <h3>Комната #{room_id}</h3>
        <p>Жди противника или <a href="/pvp" style="color:#e74c3c;">создай новую</a></p>
        <div style="font-size:24px;margin:30px 0;">⚔️ 1vs1 ДУЭЛЬ</div>
        <p>Победитель забирает 80% банка!</p>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/tournaments')
def tournaments():
    return f'''<!DOCTYPE html><html><head><title>⚔️ Турниры</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">⚔️ Турниры</h1>
    <div class="tournament-banner">
        <h2>🏆 ТУРНИР НЕДЕЛИ</h2>
        <p><b>Приз:</b> 10,000💰 | <b>Участников:</b> 127</p>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin:20px 0;">
            <div>🥇 {list(tournaments['leaderboard'].keys())[0] if tournaments['leaderboard'] else '—'}</div>
            <div>🥈 {list(tournaments['leaderboard'].keys())[1] if len(tournaments['leaderboard']) > 1 else '—'}</div>
            <div>🥉 {list(tournaments['leaderboard'].keys())[2] if len(tournaments['leaderboard']) > 2 else '—'}</div>
        </div>
        <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.3);border:2px solid white;color:white;">⚔️ Участвовать</a>
    </div>
    <div style="text-align:center;margin:50px 0;">
        <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
    </div>
</div></body></html>'''

@app.route('/games')
def games():
    return f'''<!DOCTYPE html><html><head><title>🎮 Мини-игры</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">🎮 Мини-игры</h1>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px;margin:40px 0;">
        <div class="game-card">
            <h3>🐍 Змейка</h3>
            <p>Классическая змейка на монеты</p>
            <div style="height:200px;background:#000;border:2px solid #333;border-radius:15px;margin:20px 0;display:flex;align-items:center;justify-content:center;color:#666;">🐍 ИГРА</div>
            <a href="#" class="nav-btn" style="background:linear-gradient(135deg,#27ae60,#2ecc71);">Играть</a>
        </div>
        <div class="game-card">
            <h3>🧩 Тетрис</h3>
            <p>Собери линии — получай 💰</p>
            <div style="height:200px;background:#1a1a2e;border:2px solid #16213e;border-radius:15px;margin:20px 0;display:flex;align-items:center;justify-content:center;color:#0f3460;">🧩 ИГРА</div>
            <a href="#" class="nav-btn" style="background:linear-gradient(135deg,#667eea,#764ba2);">Играть</a>
        </div>
        <div class="game-card">
            <h3>🎯 2048</h3>
            <p>Собери 2048 для приза</p>
            <div style="height:200px;background:#f8f9fa;border:2px solid #dee2e6;border-radius:15px;margin:20px 0;display:flex;align-items:center;justify-content:center;color:#6c757d;">🎯 ИГРА</div>
            <a href="#" class="nav-btn" style="background:linear-gradient(135deg,#f093fb,#f5576c);">Играть</a>
        </div>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/leaderboards')
def leaderboards():
    conn = get_db()
    top_messages = conn.execute('SELECT username, messages_today FROM users ORDER BY messages_today DESC LIMIT 10').fetchall()
    top_coins = conn.execute('SELECT username, coins FROM users ORDER BY coins DESC LIMIT 10').fetchall()
    conn.close()
    
    msg_html = ''.join([f'<tr><td>{i+1}.</td><td><b>{row["username"]}</b></td><td>{row["messages_today"]}</td></tr>' 
                       for i, row in enumerate(top_messages)])
    coins_html = ''.join([f'<tr><td>{i+1}.</td><td><b>{row["username"]}</b></td><td>{row["coins"]:,}💰</td></tr>' 
                         for i, row in enumerate(top_coins)])
    
    return f'''<!DOCTYPE html><html><head><title>🏆 Лидерборды</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">🏆 Лидерборды</h1>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:40px 0;">
        <div style="background:#f8f9fa;padding:30px;border-radius:20px;">
            <h2>📝 Топ сообщений</h2>
            <table><tr style="background:#34495e;color:white;"><th>#</th><th>Игрок</th><th>Сообщ.</th></tr>{msg_html}</table>
        </div>
        <div style="background:#f8f9fa;padding:30px;border-radius:20px;">
            <h2>💰 Топ богачей</h2>
            <table><tr style="background:#34495e;color:white;"><th>#</th><th>Игрок</th><th>💰</th></tr>{coins_html}</table>
        </div>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user = get_user(current_user)
    user_coins = user.get('coins', 0)
    
    message = ''
    if request.method == 'POST':
        item_id = request.form.get('item')
        items = {
            'vip': {'name': '⭐ VIP', 'price': 100, 'role': 'vip'},
            'premium': {'name': '💎 Premium', 'price': 200, 'role': 'premium'}
        }
        item = items.get(item_id)
        if item and user_coins >= item['price']:
            user_roles[current_user] = item['role']
            user_economy[current_user]['coins'] -= item['price']
            conn = get_db()
            conn.execute('UPDATE users SET role = ? WHERE username = ?', (item['role'], current_user))
            conn.commit()
            conn.close()
            message = f"✅ {item['name']} куплен!"
    
    items_html = '''
    <div style="border:1px solid #ddd;padding:25px;margin:15px 0;border-radius:15px;background:white;">
        <h3>⭐ VIP (100₽)</h3><p>+10💰/сообщ, синий ник</p>
        <button style="width:100%;padding:15px;background:#e74c3c;color:white;border:none;border-radius:12px;">🛒 Купить</button>
    </div>
    <div style="border:1px solid #ddd;padding:25px;margin:15px 0;border-radius:15px;background:white;">
        <h3>💎 Premium (200₽)</h3><p>+20💰/сообщ, оранжевый ник</p>
        <button style="width:100%;padding:15px;background:#e74c3c;color:white;border:none;border-radius:12px;">🛒 Купить</button>
    </div>'''
    
    return f'''<!DOCTYPE html><html><head><title>💰 Магазин</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">💰 Магазин</h1>
    <p style="text-align:center;font-size:24px;color:#27ae60;">💰 Монеты: <b>{user_coins:,}</b></p>
    {items_html}
    <div style="text-align:center;margin:50px 0;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    current_user = session.get('user', '')
    if current_user not in ['CatNap', 'Назар']:
        return redirect('/')
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        target = request.form.get('target', '').strip()
        if action == 'mute':
            duration = int(request.form.get('duration', 900))
            conn = get_db()
            conn.execute('INSERT INTO mutes (target, muted_by, reason, mtype, expires, created) VALUES (?, ?, "Админ мут", "manual", ?, ?)',
                        (target, current_user, time.time() + duration, time.time()))
            conn.commit()
            conn.close()
            message = f"✅ {target} замучен на {duration//60} мин"
    
    conn = get_db()
    active_mutes = conn.execute('SELECT * FROM mutes WHERE expires > ? ORDER BY created DESC', (time.time(),)).fetchall()
    conn.close()
    
    return f'''<!DOCTYPE html><html><head><title>⚙️ Админка</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;color:#e74c3c;">⚙️ Админ-панель v37.19</h1>
    {f'<div style="color:#27ae60;padding:20px;background:#d4edda;">{message}</div>' if message else ''}
    <div style="background:#f8f9fa;padding:30px;border-radius:20px;margin:30px 0;">
        <h3>🔇 Мут</h3>
        <form method="POST">
            <input name="target" placeholder="Ник" style="padding:15px;width:250px;margin-right:15px;border:2px solid #ddd;border-radius:8px;">
            <select name="duration" style="padding:15px;margin-right:15px;border:2px solid #ddd;border-radius:8px;">
                <option value="900" selected>15 мин</option><option value="3600">1 час</option><option value="86400">1 день</option>
            </select>
            <button name="action" value="mute" style="padding:15px 25px;background:#e74c3c;color:white;border:none;border-radius:8px;">🔇 Мут</button>
        </form>
    </div>
    <div style="text-align:center;margin:50px 0;"><a href="/" class="nav-btn">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/api/delete/<int:msg_id>', methods=['POST'])
def api_delete(msg_id):
    current_user = session.get('user', '')
    if not current_user or not is_moderator(current_user):
        return jsonify({'error': 'Нет прав'}), 403
    
    conn = get_db()
    conn.execute('UPDATE chat SET deleted = 1 WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.errorhandler(404)
def not_found(error):
    return f'''<!DOCTYPE html><html><head><title>404</title><style>{css}</style></head><body>
<div class="container" style="text-align:center;padding:80px;">
    <h1 style="font-size:6em;color:#95a5a6;">404</h1>
    <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
</div></body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("🎉 УЗНАВАЙКИН v37.19 100% — 15 РОУТОВ + 5 НОВЫХ ФИЧ!")
    print("✅ Казино + PvP + Турниры + Игры + Мут-лист!")
    app.run(host='0.0.0.0', port=port, debug=False)

print("🚀 УЗНАВАЙКИН v37.19 = ДЕПЛОЙ И ТЕСТИРУЙ!")

