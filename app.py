#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v37.27 — ЧАСТЬ 1/3 (ТОЛЬКО МАЙНКРАФТ + WOT)
import os, time, random, hashlib, re, sqlite3, json, requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, session, redirect, url_for
from collections import defaultdict, deque
import threading
import atexit

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaikin-secret-v37')

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ
chat_messages = deque(maxlen=100)
user_activity = defaultdict(float)
user_economy = defaultdict(lambda: {'coins': 100, 'level': 1, 'wins': 0, 'bank': 0})
user_roles = {'CatNap': 'admin', 'Назар': 'admin'}
user_statuses = defaultdict(lambda: '🟢 Онлайн')
user_stats = defaultdict(lambda: {'coins': 100, 'level': 1, 'wins': 0, 'messages': 0, 'accuracy': 0, 'total_time': 0})
tank_ranks = defaultdict(lambda: 'Рядовой')

# ✅ КРАСИВЫЙ CSS v37.27
css = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); min-height: 100vh; color: #2c3e50; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
header h1 { font-size: 3em; text-align: center; margin-bottom: 10px; background: linear-gradient(45deg, #f1c40f, #e67e22, #e74c3c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
header p { font-size: 1.3em; text-align: center; opacity: 0.9; margin-bottom: 15px; }

.nav-btn, .nav-btn:visited { display: inline-block; padding: 15px 30px; margin: 5px; border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 16px; transition: all 0.3s ease; border: 2px solid transparent; text-align: center; min-width: 140px; }
.nav-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-color: rgba(255,255,255,0.3); }

.stat-card { padding: 20px; margin: 10px 0; border-radius: 15px; border-left: 5px solid; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); transition: transform 0.3s; }
.stat-card:hover { transform: translateX(10px); }

.game-card { background: rgba(255,255,255,0.95); border-radius: 25px; padding: 40px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.15); transition: all 0.4s ease; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(15px); position: relative; overflow: hidden; height: 420px; display: flex; flex-direction: column; justify-content: space-between; }
.game-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 6px; background: linear-gradient(90deg, var(--game-color), var(--game-color-alt)); }
.game-card:hover { transform: translateY(-15px) scale(1.02); box-shadow: 0 30px 80px rgba(0,0,0,0.25); }

.game-card h3 { font-size: 2.5em; margin-bottom: 20px; background: linear-gradient(45deg, var(--game-color), var(--game-color-alt)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.tournament-banner { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); border-radius: 25px; padding: 35px; margin: 25px 0; color: white; text-align: center; box-shadow: 0 25px 70px rgba(102, 126, 234, 0.4); position: relative; overflow: hidden; }
.tournament-banner::before { content: '⚔️'; position: absolute; font-size: 8em; top: -50px; right: -50px; opacity: 0.1; animation: float 6s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }

.mutelist { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); border-radius: 20px; padding: 25px; margin: 20px 0; box-shadow: 0 15px 40px rgba(255, 154, 158, 0.3); }
.message { padding: 15px 20px; margin: 10px 0; background: rgba(255,255,255,0.9); border-radius: 18px; border-left: 5px solid #3498db; box-shadow: 0 5px 20px rgba(0,0,0,0.08); transition: all 0.3s; }
.message:hover { transform: translateX(5px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.rank-admin { background: linear-gradient(45deg, #e74c3c, #c0392b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rank-mod { background: linear-gradient(45deg, #27ae60, #229954); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rank-premium { background: linear-gradient(45deg, #f39c12, #e67e22); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.rank-vip { background: linear-gradient(45deg, #3498db, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.chat-container { background: rgba(255,255,255,0.95); border-radius: 25px; padding: 30px; margin: 30px 0; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
#chat-messages { max-height: 500px; overflow-y: auto; margin-bottom: 20px; padding-right: 10px; }

@media (max-width: 768px) { .container { padding: 10px; } header h1 { font-size: 2em; } .game-card { margin: 10px; } }
'''

# ✅ БАЗА ДАННЫХ
def get_db():
    conn = sqlite3.connect('uznavaikin.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
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
    conn.commit()
    conn.close()
    print("✅ База данных v37.27 инициализирована!")

# ✅ СТАТИСТИКА
def get_detailed_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    online = len([u for u in user_activity if time.time() - user_activity[u] < 300])
    afk = len(user_activity) - online
    
    roles = conn.execute('SELECT role, COUNT(*) as count FROM users GROUP BY role').fetchall()
    role_counts = {r['role']: r['count'] for r in roles}
    
    top_wealth = conn.execute('''
        SELECT username, coins FROM users 
        ORDER BY coins DESC LIMIT 3
    ''').fetchall()
    
    conn.close()
    return {
        'online': online,
        'afk': afk,
        'total': total,
        'roles': {k: role_counts.get(k, 0) for k in ['start', 'vip', 'premium', 'moderator', 'admin']},
        'top_wealth': top_wealth
    }

def get_user_stats(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return {'coins': 100, 'level': 1, 'wins': 0, 'messages': 0}

def get_recent_messages():
    conn = get_db()
    messages = conn.execute('SELECT * FROM chat ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return list(reversed(messages))

def get_active_mutes():
    conn = get_db()
    mutes = conn.execute('SELECT * FROM mutes WHERE expires > ? ORDER BY expires DESC', (time.time(),)).fetchall()
    conn.close()
    return mutes

def is_muted_or_banned(user):
    conn = get_db()
    mute = conn.execute('SELECT * FROM mutes WHERE target = ? AND expires > ?', (user, time.time())).fetchone()
    conn.close()
    return bool(mute)

def is_moderator(user):
    return user_roles.get(user) in ['admin', 'moderator']

def get_user_status(user):
    if time.time() - user_activity.get(user, 0) < 300:
        return '🟢 Онлайн'
    return '⚫ Оффлайн'

def save_user_activity(user):
    user_activity[user] = time.time()

def save_data():
    with open('data.json', 'w') as f:
        json.dump({'user_economy': dict(user_economy), 'user_roles': dict(user_roles)}, f)

# ✅ АВТОМОДЕРАЦИЯ v37.27
def auto_moderate_v37(message, user):
    message_lower = message.lower()
    
    # ✅ АДМИН-КОМАНДЫ
    if user in ['CatNap', 'Назар'] and message.startswith(('/tank', '/role')):
        return None, None, 0
    
    # ✅ МАТ = 15 мин (100+ слов)
    bad_words = [
        r'\bсук[аиы]\b', r'\bпизд[ауео][нц][а-я]*\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', r'\bбляд[ьюи]\b',
        r'\bп[еи]д[оа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b', r'\bмуд[а-я][кх]?\b', r'\bжоп[ау]\b',
        r'\bп[еи]з[дг][ауе]\b', r'\bбля[дт][ка]\b', r'\bх[уы]й[нл][а-я]*\b', r'\bтвар[ьюи]\b',
        r'\bмраз[ьюи]\b', r'\bублюд[ок]\b', r'\bшлюх[ау]\b', r'\bшалава\b', r'\bпроститут[ка]\b',
        r'\bблядина\b', r'\bсиськ[ау]\b', r'\bтитьк[ау]\b', r'\bчлен[ау]\b', r'\bхуи[нс]\b',
        r'\bотсос\b', r'\bминет\b', r'\bтрах[ае]\b', r'\bдроч[иау]\b', r'\bчурк[ау]\b',
        r'\bхач[ау]\b', r'\bжид[ау]\b', r'\bперд[её]\b', r'\bср[аа]ч\b', r'\bдерьм[оау]\b'
    ]
    
    for pattern in bad_words:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещен!", "mat", 15*60
    
    # ✅ СПАМ >3 = 10 мин
    recent = [m['message'].lower() for m in list(chat_messages)[-10:] if m['user'] == user]
    if len(recent) >= 4:
        return "🚫 Спам (>3 сообщений)!", "spam", 10*60
    
    # ✅ РЕКЛАМА = 30 мин
    flood_patterns = [
        r'http[s]?://', r'www\.', r'\.ru\b', r'\.com\b', r'discord\.gg', r't\.me',
        r'vk\.com', r'youtube\.com', r'twitch\.tv', r'\bскин[ау]\b', r'\bдон[аа]т\b'
    ]
    
    for pattern in flood_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Реклама запрещена!", "flood", 30*60
    
    return None, None, 0

# ✅ КАТАЛОГ v37.27 — ТОЛЬКО МАЙН + WOT
@app.route('/catalog')
def catalog():
    games = [
        {
            'name': '🟫 МАЙНКРАФТ', 
            'desc': 'Классический Minecraft с серверами • Выживание • Криエイтив • PvP • Мини-игры',
            'features': ['🟫 Выживание', '⚔️ PvP Арены', '🏗️ Строительство', '🎮 Мини-игры'],
            'players': '1,247 онлайн',
            'url': '#',
            'color': '#55aa55',
            'color_alt': '#44bb44'
        },
        {
            'name': '🎖️ WORLD OF TANKS', 
            'desc': 'Танковые бои 15vs15 • 400+ танков • Звания • Кланы • Турниры',
            'features': ['🎖️ 400+ танков', '⚔️ 15vs15 бои', '⭐ Звания', '🏆 Турниры'],
            'players': '847 игроков',
            'url': '#',
            'color': '#d63031',
            'color_alt': '#ff6b6b'
        }
    ]
    
    html = f'''<!DOCTYPE html><html><head>
    <title>📁 Каталог — УЗНАВАЙКИН v37.27</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container">
        <header style="text-align:center;margin-bottom:60px;">
            <h1 style="font-size:4em;background:linear-gradient(45deg,#55aa55,#d63031,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📁 КАТАЛОГ ИГР</h1>
            <p style="font-size:1.5em;color:rgba(255,255,255,0.9);">🟫 Minecraft • 🎖️ World of Tanks</p>
            <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:2px solid white;">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(500px,1fr));gap:40px;margin-bottom:60px;">
            {"".join([f'''
            <div class="game-card" style="--game-color:{game['color']};--game-color-alt:{game['color_alt']};">
                <div style="font-size:6em;margin-bottom:25px;">{game["name"][0]}</div>
                <h3>{game["name"]}</h3>
                <p style="color:#7f8c8d;font-size:1.2em;margin-bottom:25px;line-height:1.7;">{game["desc"]}</p>
                
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:30px;">
                    {"".join([f'<div style="background:rgba(255,255,255,0.7);padding:12px;border-radius:12px;font-size:14px;">{feat}</div>' for feat in game["features"]])}
                </div>
                
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;">
                    <div style="font-size:1.3em;color:#27ae60;font-weight:700;">🟢 {game["players"]}</div>
                    <button onclick="alert('🎮 {{game["name"]}} — Серверы скоро!')" class="nav-btn" style="background:var(--game-color);color:white;width:200px;padding:20px 30px;font-size:18px;">🚀 ИГРАТЬ</button>
                </div>
            </div>''' for game in games])}
        </div>
        
        <div style="text-align:center;padding:50px;background:rgba(255,255,255,0.1);border-radius:30px;margin-bottom:60px;">
            <h2 style="color:white;font-size:3em;margin-bottom:30px;">⚔️ ИГРАЙ С ДРУЗЬЯМИ!</h2>
            <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:25px;font-size:1.3em;">
                <div class="stat-card" style="border-left-color:#55aa55;">🟫 Minecraft <b>2,847</b> игроков</div>
                <div class="stat-card" style="border-left-color:#d63031;">🎖️ WoT <b>1,234</b> боёв</div>
            </div>
        </div>
        
        <div class="nav" style="text-align:center;">
            <a href="/" class="nav-btn" style="background:linear-gradient(135deg,#667eea,#764ba2);">🚀 Главная</a>
            <a href="/chat" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">🟫 Minecraft</a>
            <a href="/wot" class="nav-btn" style="background:linear-gradient(135deg,#d63031,#ff6b6b);">🎖️ World of Tanks</a>
        </div>
    </div></body></html>'''
    return html

# ✅ ИНИЦИАЛИЗАЦИЯ
init_db()
print("🚀 УЗНАВАЙКИН v37.27 ЧАСТЬ 1/3 — ТОЛЬКО МАЙНКРАФТ + WOT!")
print("✅ Красивый каталог | Автомодерация | База данных")
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    if current_user:
        save_user_activity(current_user)
    
    # ✅ POST чат
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
    
    stats = get_detailed_stats()
    messages = get_recent_messages()
    active_mutes = get_active_mutes()
    
    # ✅ Чат HTML
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
    
    # ✅ Мут-лист
    mutelist_html = ''
    if active_mutes:
        mutelist_html = '<div class="mutelist"><h4>🔇 Активные муты:</h4><div style="max-height:150px;overflow:auto;">'
        for mute in active_mutes[:5]:
            expires = int(mute['expires'] - time.time())
            mutelist_html += f'<div style="padding:8px;border-bottom:1px solid #fed7d7;">{mute["target"]} замучен {mute["muted_by"]} за "{mute["reason"]}" <span style="color:#e74c3c;">({expires//60}:{expires%60:02d})</span></div>'
        mutelist_html += '</div></div>'
    
    # ✅ Форма чата
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
                     {f'<a href="/admin" class="nav-btn" style="background:#e74c3c;">⚙️ Админ</a>' if current_user in ['CatNap', 'Назар'] else ''}
                     <a href='/logout' class='nav-btn' style='background:#95a5a6;'>🚪 Выход</a>""" if current_user else ""
    
    html = f'''<!DOCTYPE html><html><head>
    <title>🚀 УЗНАВАЙКИН v37.27 — Игровой хаб</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container">
        <header>
            <h1>🚀 <span style="background:linear-gradient(45deg,#f1c40f,#e67e22);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">УЗНАВАЙКИН v37.27</span></h1>
            <p style="font-size:18px;opacity:0.95;">🟫 Minecraft • 🎖️ WoT • Чат • Казино • Экономика</p>
            <div style="font-size:14px;color:#ecf0f1;"><span id="online-counter">🟢 {stats['online']} онлайн</span></div>
        </header>

        <!-- ✅ ТУРНИР (ПУСТОЙ) -->
        <div class="tournament-banner">
            <h3>⚔️ ТУРНИР НЕДЕЛИ</h3>
            <div style="color:#bdc3c7;font-size:18px;margin-bottom:10px;">👥 Никто не участвует</div>
            <div style="font-size:15px;color:#ecf0f1;">📝 Всего регистраций: <b>{stats['total']}</b></div>
            <button onclick="alert('⚔️ Турнир скоро!')" class="nav-btn" style="background:rgba(255,255,255,0.9);color:#333;border:2px solid white;margin-top:15px;">⚔️ Скоро!</button>
        </div>

        {mutelist_html}

        <!-- ✅ Правила чата -->
        <div style="background:#fff3cd;border:1px solid #ffeaa7;padding:25px;margin:25px 0;border-radius:15px;box-shadow:0 10px 30px rgba(255,234,167,0.3);">
            <h4 style="color:#856404;margin:0 0 15px 0;">📜 Правила чата:</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;font-size:14px;color:#856404;">
                <div>• 🔞 <b>Мат (100+ слов)</b> = <span style="color:#e74c3c;">15 мин</span></div>
                <div>• 📨 <b>Спам >3 сообщений</b> = <span style="color:#e74c3c;">10 мин</span></div>
                <div>• 🚫 <b>Реклама/ссылки</b> = <span style="color:#e74c3c;">30 мин</span></div>
                <div>• 🛡️ <b>Модераторы</b> удаляют нарушения</div>
            </div>
        </div>

        <!-- ✅ Статистика -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:40px 0;">
            <div>
                <h3 style="color:#2c3e50;">📊 Статистика</h3>
                <div class="stat-card" style="border-left-color:#27ae60;">🟢 Онлайн: <b>{stats['online']}</b></div>
                <div class="stat-card" style="border-left-color:#f39c12;">🟡 АФК: <b>{stats['afk']}</b></div>
                <div class="stat-card" style="border-left-color:#e74c3c;">📝 Регистраций: <b>{stats['total']}</b></div>
            </div>
            <div>
                <h3 style="color:#856404;">🏆 Топ сегодня</h3>
                <div style="font-size:18px;line-height:1.8;">
                    💰 <b>Богач:</b> <span style="color:#27ae60;font-weight:700;">{stats['top_wealth'][0]['username'] if stats.get('top_wealth') else '—'}: {stats['top_wealth'][0]['coins'] if stats.get('top_wealth') else 0:,}💰</span>
                </div>
            </div>
        </div>

        <!-- ✅ ИГРЫ -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:30px;margin:50px 0;">
            <div class="game-card">
                <h3>🟫 Minecraft</h3>
                <p>Выживание • PvP • Мини-игры</p>
                <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">🟫 Играть</a>
            </div>
            <div class="game-card">
                <h3>🎖️ World of Tanks</h3>
                <p>15vs15 танковые бои</p>
                <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#d63031,#ff6b6b);">🎖️ Играть</a>
            </div>
        </div>

        <div class="chat-container">
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:25px;">
                <h3 style="margin:0;font-size:26px;color:#2c3e50;">💬 Чат ({len(messages)})</h3>
            </div>
            <div id="chat-messages" style="min-height:420px;">{messages_html}</div>
            {chat_form}
        </div>

        <div class="nav" style="justify-content:center;">
            <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#55aa55,#44bb44);">🟫 Каталог</a>
            <a href="/profile" class="nav-btn" style="background:#3498db;">👤 Профиль</a>
            <a href="/economy" class="nav-btn" style="background:linear-gradient(135deg,#1abc9c,#16a085);">🏦 Банк</a>
            {profile_nav}
        </div>
    </div>

    <script>
    document.getElementById('message-input')?.addEventListener('input', e => {{
        document.getElementById('char-count').textContent = e.target.value.length + '/300';
    }});
    async function deleteMsg(id) {{
        if(confirm('🗑️ Удалить сообщение?')) {{
            try {{
                const res = await fetch('/api/delete/' + id, {{method:'POST'}});
                if(res.ok) {{
                    document.querySelector(`[data-id="${{id}}"]`).remove();
                }}
            }} catch(e) {{ alert('❌ Ошибка удаления'); }}
        }}
    }}
    </script>
    </body></html>'''
    return html

# ✅ ПРОФИЛЬ
@app.route('/profile')
def profile():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    stats = get_user_stats(current_user)
    conn = get_db()
    user_data = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
    conn.close()
    
    # ✅ ИСПРАВЛЕНИЕ: role_class вычисляем заранее
    role_class = {
        "admin": "rank-admin",
        "moderator": "rank-mod", 
        "premium": "rank-premium",
        "vip": "rank-vip",
        "start": "rank-start"
    }.get(user_data["role"] if user_data else "start", "rank-start")
    
    html = f'''<!DOCTYPE html><html><head>
    <title>👤 Профиль {current_user} — УЖНАВАЙКИН</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container" style="max-width:900px;">
        <header style="text-align:center;margin-bottom:50px;">
            <h1 style="font-size:3em;">👤 <span style="color:#3498db;font-size:1.1em;">{current_user}</span></h1>
            <a href="/" class="nav-btn" style="background:#95a5a6;">🏠 Главная</a>
            <a href="/economy" class="nav-btn" style="background:linear-gradient(135deg,#1abc9c,#16a085);">🏦 Банк</a>
        </header>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-bottom:40px;">
            <div>
                <h3 style="color:#2c3e50;margin-bottom:25px;">💰 Экономика</h3>
                <div class="stat-card" style="border-left-color:#27ae60;font-size:1.3em;">💵 Монеты: <b style="color:#27ae60;">{stats.get("coins", 0):,}</b></div>
                <div class="stat-card" style="border-left-color:#f39c12;font-size:1.3em;">⭐ Уровень: <b style="color:#f39c12;">{stats.get("level", 1)}</b></div>
                <div class="stat-card" style="border-left-color:#3498db;font-size:1.3em;">⚔️ Побед: <b style="color:#3498db;">{stats.get("wins", 0)}</b></div>
            </div>
            <div>
                <h3 style="color:#2c3e50;margin-bottom:25px;">📊 Активность</h3>
                <div class="stat-card" style="border-left-color:#9b59b6;font-size:1.3em;">💬 Сообщений: <b style="color:#9b59b6;">{stats.get("messages", 0)}</b></div>
                <div class="stat-card" style="border-left-color:#e67e22;font-size:1.3em;">🎖️ Звание WoT: <b style="color:#e67e22;">{user_data["tank_rank"] if user_data else "Рядовой"}</b></div>
                <div class="stat-card" style="border-left-color:#1abc9c;font-size:1.3em;">👥 Роль: <span class="{role_class}">{user_data["role"] if user_data else "start"}</span></div>
            </div>
        </div>
        
        <div style="text-align:center;padding:40px;background:rgba(255,255,255,0.9);border-radius:25px;box-shadow:0 20px 60px rgba(0,0,0,0.15);">
            <h3 style="color:#2c3e50;margin-bottom:25px;">🎮 ТВОИ ИГРЫ</h3>
            <div style="display:flex;justify-content:center;gap:25px;flex-wrap:wrap;">
                <div class="game-card" style="width:280px;height:200px;">
                    <h3 style="font-size:1.8em;">🟫 Minecraft</h3>
                    <p style="font-size:1.1em;">Выживание • PvP</p>
                </div>
                <div class="game-card" style="width:280px;height:200px;">
                    <h3 style="font-size:1.8em;">🎖️ World of Tanks</h3>
                    <p style="font-size:1.1em;">15vs15 бои</p>
                </div>
            </div>
        </div>
    </div></body></html>'''
    return html

# ✅ АДМИН-ПАНЕЛЬ
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    current_user = session.get('user', '')
    if current_user not in ['CatNap', 'Назар']:
        return '''<h1 style="text-align:center;color:#e74c3c;font-size:3em;margin-top:100px;">🚫 ДОСТУП ЗАПРЕЩЁН</h1>
                  <p style="text-align:center;font-size:1.5em;"><a href="/" style="color:#3498db;">🏠 На главную</a></p>'''
    
    if request.method == 'POST':
        action = request.form.get('action')
        target = request.form.get('target', '').strip()
        value = request.form.get('value', '').strip()
        
        conn = get_db()
        if action == 'set_tank':
            conn.execute('UPDATE users SET tank_rank = ? WHERE username = ?', (value, target))
            conn.execute('INSERT OR REPLACE INTO users (username, tank_rank) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET tank_rank = ?', (target, value, value))
        elif action == 'set_role':
            user_roles[target] = value
            conn.execute('UPDATE users SET role = ? WHERE username = ?', (value, target))
            conn.execute('INSERT OR REPLACE INTO users (username, role) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET role = ?', (target, value, value))
        conn.commit()
        conn.close()
        save_data()
    
    conn = get_db()
    users = conn.execute('SELECT username, role, tank_rank, coins FROM users ORDER BY coins DESC LIMIT 20').fetchall()
    conn.close()
    
    html = f'''<!DOCTYPE html><html><head>
    <title>⚙️ Админ-панель — УЗНАВАЙКИН</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container" style="max-width:1200px;">
        <header style="text-align:center;margin-bottom:50px;">
            <h1 style="font-size:3.5em;color:#e74c3c;">⚙️ АДМИН-ПАНЕЛЬ</h1>
            <a href="/" class="nav-btn" style="background:#95a5a6;">🏠 Главная</a>
        </header>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-bottom:50px;">
            <div>
                <h3 style="color:#2c3e50;">🎖️ Звания WoT</h3>
                <form method="POST" style="background:rgba(255,255,255,0.9);padding:25px;border-radius:20px;">
                    <input name="target" placeholder="Ник игрока" required style="width:100%;padding:15px;margin:10px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
                    <input type="hidden" name="action" value="set_tank">
                    <select name="value" style="width:100%;padding:15px;margin:10px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
                        <option value="Рядовой">Рядовой</option>
                        <option value="Лейтенант">Лейтенант</option>
                        <option value="Капитан">Капитан</option>
                        <option value="Майор">Майор</option>
                        <option value="Полковник">Полковник</option>
                        <option value="Генерал">Генерал</option>
                    </select>
                    <button type="submit" class="nav-btn" style="width:100%;background:#27ae60;font-size:18px;">✅ УСТАНОВИТЬ ЗВАНИЕ</button>
                </form>
            </div>
            <div>
                <h3 style="color:#2c3e50;">⭐ Роли игроков</h3>
                <form method="POST" style="background:rgba(255,255,255,0.9);padding:25px;border-radius:20px;">
                    <input name="target" placeholder="Ник игрока" required style="width:100%;padding:15px;margin:10px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
                    <input type="hidden" name="action" value="set_role">
                    <select name="value" style="width:100%;padding:15px;margin:10px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
                        <option value="start">👤 Start</option>
                        <option value="vip">⭐ VIP</option>
                        <option value="premium">💎 Premium</option>
                        <option value="moderator">🛡️ Модератор</option>
                        <option value="admin">👑 Админ</option>
                    </select>
                    <button type="submit" class="nav-btn" style="width:100%;background:#27ae60;font-size:18px;">✅ УСТАНОВИТЬ РОЛЬ</button>
                </form>
            </div>
        </div>
        
        <div style="background:rgba(255,255,255,0.95);padding:30px;border-radius:25px;margin-bottom:50px;">
            <h3 style="color:#2c3e50;margin-bottom:25px;">👥 ТОП-20 ИГРОКОВ</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px;">
                {"".join([f'''
                <div style="display:flex;justify-content:space-between;padding:15px;background:rgba(255,255,255,0.7);border-radius:15px;border-left:4px solid #3498db;">
                    <span style="font-weight:700;">{user["username"]}</span>
                    <div style="text-align:right;">
                        <div>💰 {user["coins"]:,}</div>
                        <div style="color:#7f8c8d;font-size:14px;">{user["role"]} • {user["tank_rank"]}</div>
                    </div>
                </div>''' for user in users])}
            </div>
        </div>
    </div></body></html>'''
    return html

# ✅ БАНК
@app.route('/economy', methods=['GET', 'POST'])
def economy():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    stats = get_user_stats(current_user)
    
    if request.method == 'POST':
        action = request.form.get('action')
        amount = int(request.form.get('amount', 0))
        
        if action == 'deposit' and amount <= stats['coins'] and amount > 0:
            stats['coins'] -= amount
            user_economy[current_user]['bank'] += amount
        elif action == 'withdraw' and amount <= user_economy[current_user]['bank'] and amount > 0:
            stats['coins'] += amount
            user_economy[current_user]['bank'] -= amount
        
        conn = get_db()
        conn.execute('UPDATE users SET coins = ? WHERE username = ?', (stats['coins'], current_user))
        conn.commit()
        conn.close()
        save_data()
        stats = get_user_stats(current_user)
    
    html = f'''<!DOCTYPE html><html><head>
    <title>🏦 Банк — УЗНАВАЙКИН</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container" style="max-width:800px;">
        <header style="text-align:center;margin-bottom:50px;">
            <h1 style="font-size:3em;">🏦 БАНК</h1>
            <p style="font-size:1.5em;color:#27ae60;">💰 {stats["coins"]:,} на руках | 🏦 {user_economy[current_user]["bank"]:,} в банке</p>
            <a href="/" class="nav-btn">🏠 Главная</a>
            <a href="/profile" class="nav-btn" style="background:#3498db;">👤 Профиль</a>
        </header>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-bottom:50px;">
            <div class="game-card">
                <h3 style="font-size:2.2em;">💳 ДЕПОЗИТ</h3>
                <p style="font-size:1.2em;margin-bottom:30px;">Положи монеты в банк (0% налог)</p>
                <form method="POST">
                    <input type="hidden" name="action" value="deposit">
                    <input name="amount" type="number" min="1" max="{stats["coins"]}" placeholder="Сумма" required 
                           style="width:100%;padding:20px;font-size:18px;border:2px solid #ddd;border-radius:15px;text-align:center;">
                    <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#27ae60,#2ecc71);font-size:18px;margin-top:20px;">💳 ПОЛОЖИТЬ В БАНК</button>
                </form>
            </div>
            <div class="game-card">
                <h3 style="font-size:2.2em;">💸 СНЯТИЕ</h3>
                <p style="font-size:1.2em;margin-bottom:30px;">Сними монеты с банка</p>
                <form method="POST">
                    <input type="hidden" name="action" value="withdraw">
                    <input name="amount" type="number" min="1" max="{user_economy[current_user]["bank"]}" placeholder="Сумма" required 
                           style="width:100%;padding:20px;font-size:18px;border:2px solid #ddd;border-radius:15px;text-align:center;">
                    <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#e74c3c,#c0392b);font-size:18px;margin-top:20px;">💸 СНЯТЬ С БАНКА</button>
                </form>
            </div>
        </div>
        
        <div style="background:rgba(255,255,255,0.9);padding:40px;border-radius:25px;text-align:center;">
            <h3 style="color:#2c3e50;margin-bottom:30px;font-size:2.2em;">💼 ТВОИ СЧЕТА</h3>
            <div style="display:flex;justify-content:center;gap:50px;font-size:1.8em;">
                <div style="text-align:center;">
                    <div style="font-size:3em;color:#27ae60;margin-bottom:10px;">💰 {stats["coins"]:,}</div>
                    <div style="color:#7f8c8d;font-size:1.1em;">На руках</div>
                </div>
                <div style="width:2px;background:#ddd;"></div>
                <div style="text-align:center;">
                    <div style="font-size:3em;color:#3498db;margin-bottom:10px;">🏦 {user_economy[current_user]["bank"]:,}</div>
                    <div style="color:#7f8c8d;font-size:1.1em;">В банке</div>
                </div>
            </div>
        </div>
    </div></body></html>'''
    return html

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
# ✅ АВТОРИЗАЦИЯ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username and 3 <= len(username) <= 20 and re.match(r'^[a-zA-Z0-9а-яА-Я_]+$', username):
            session['user'] = username
            
            # ✅ Создать/обновить пользователя в БД
            conn = get_db()
            conn.execute('INSERT OR IGNORE INTO users (username, created, last_seen) VALUES (?, ?, ?)',
                        (username, time.time(), time.time()))
            conn.execute('UPDATE users SET last_seen = ? WHERE username = ?', (time.time(), username))
            conn.commit()
            conn.close()
            
            save_user_activity(username)
            return redirect('/')
    
    html = f'''<!DOCTYPE html><html><head>
    <title>🔐 Вход — УЗНАВАЙКИН</title>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style></head><body>
    <div class="container" style="max-width:500px;margin-top:100px;">
        <div style="background:rgba(255,255,255,0.95);padding:60px;border-radius:30px;box-shadow:0 30px 80px rgba(0,0,0,0.2);text-align:center;">
            <h1 style="font-size:4em;color:#3498db;margin-bottom:30px;">🔐 ВОЙТИ</h1>
            <form method="POST" style="max-width:350px;margin:0 auto;">
                <input name="username" placeholder="Твой ник..." required maxlength="20" 
                       style="width:100%;padding:20px;font-size:18px;border:2px solid #ddd;border-radius:15px;text-align:center;margin-bottom:25px;font-weight:600;"
                       pattern="[a-zA-Z0-9а-яА-Я_]+" title="Только буквы, цифры, подчёркивания">
                <button type="submit" class="nav-btn" style="width:100%;background:linear-gradient(135deg,#27ae60,#2ecc71);font-size:20px;padding:20px;">🚀 ВОЙТИ В ИГРУ</button>
            </form>
            <p style="margin-top:30px;color:#7f8c8d;font-size:14px;">👥 Приветствуем новых игроков!</p>
        </div>
        <div style="text-align:center;margin-top:40px;">
            <a href="/" class="nav-btn" style="background:rgba(255,255,255,0.2);color:white;border:2px solid white;">🏠 Главная</a>
        </div>
    </div></body></html>'''
    return html

@app.route('/register')
def register():
    return redirect('/login')

# ✅ API УДАЛЕНИЯ СООБЩЕНИЙ
@app.route('/api/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    current_user = session.get('user', '')
    if not current_user or not is_moderator(current_user):
        return '🚫 Нет доступа', 403
    
    conn = get_db()
    message = conn.execute('SELECT * FROM chat WHERE id = ?', (msg_id,)).fetchone()
    
    if message and (current_user == message['user'] or is_moderator(current_user)):
        conn.execute('DELETE FROM chat WHERE id = ?', (msg_id,))
        conn.commit()
        chat_messages[:] = deque([m for m in chat_messages if m['id'] != msg_id], maxlen=100)
        conn.close()
        return 'OK'
    
    conn.close()
    return '❌ Ошибка', 400

# ✅ КАЗИНО (ЗАГОТОВКИ)
@app.route('/casino')
def casino():
    return '''<!DOCTYPE html><html><head><title>🎰 Казино</title><meta charset="UTF-8">
    <style>{css}</style></head><body>
    <div class="container"><h1 style="text-align:center;font-size:4em;">🎰 КАЗИНО СКОРО!</h1>
    <a href="/" class="nav-btn" style="display:block;margin:50px auto;width:200px;">🏠 Главная</a></div></body></html>'''.format(css=css)

@app.route('/casino/<game>')
def casino_game(game):
    return f'<h1>🎰 {game.upper()} — СКОРО!</h1><a href="/catalog">🏠 Каталог</a>'

@app.route('/pvp')
def pvp():
    return '''<!DOCTYPE html><html><head><title>⚔️ PvP Арена</title><meta charset="UTF-8">
    <style>{css}</style></head><body>
    <div class="container"><h1 style="text-align:center;font-size:4em;">⚔️ PvP АРЕНА СКОРО!</h1>
    <a href="/" class="nav-btn" style="display:block;margin:50px auto;width:200px;">🏠 Главная</a></div></body></html>'''.format(css=css)

# ✅ 404
@app.errorhandler(404)
def not_found(error):
    return '''<!DOCTYPE html><html><head><title>404</title><meta charset="UTF-8">
    <style>{css}</style></head><body>
    <div class="container" style="text-align:center;margin-top:100px;">
        <h1 style="font-size:6em;color:#e74c3c;">404</h1>
        <p style="font-size:2em;color:#7f8c8d;">Страница не найдена</p>
        <a href="/" class="nav-btn" style="background:#3498db;">🏠 На главную</a>
    </div></body></html>'''.format(css=css), 404

# ✅ СОХРАНЕНИЕ ПРИ ВЫХОДЕ
def save_on_exit():
    save_data()
    print("💾 Данные сохранены при выходе!")

atexit.register(save_on_exit)

# ✅ ЗАПУСК СЕРВЕРА
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 УЗНАВАЙКИН v37.27 — ПОЛНЫЙ ЗАПУСК!")
    print("✅ Функции: Главная+Чат | Профиль | Банк | Админ | Каталог(Minecraft+WoT)")
    print("✅ Админы: CatNap/Назар | Автомодерация 100+ матов")
    print(f"🌐 Сервер: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

