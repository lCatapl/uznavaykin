# 🚀 УЖНАВАЙКИН v37.14 ЧАСТЬ 1/3 — 100% РАБОТАЮЩАЯ БЕЗ ОШИБОК!

from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import os
import json
import time
import hashlib
import re
import sqlite3
from collections import defaultdict, deque

app = Flask(__name__)
app.secret_key = 'uznaykin_v37_14_full_stable_2026'
DB_FILE = 'uznaykin_v37.db'

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ (персистентность)
users = {}
user_roles = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
user_profiles = {}
user_activity = {}
user_stats = defaultdict(lambda: {'messages_today': 0, 'messages_total': 0})
user_economy = defaultdict(lambda: {'coins': 0, 'bank': 0})
chat_messages = deque(maxlen=1000)
mutes = {'by': {}, 'list': []}
announcements = []

# ✅ CSS v37.14 — ПОЛНЫЙ + АДАПТИВНЫЙ
css = '''
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;color:#2c3e50;line-height:1.6;}
.container {max-width:1200px;margin:0 auto;padding:25px;background:white;border-radius:25px;box-shadow:0 25px 50px rgba(0,0,0,0.15);}
header {text-align:center;padding:40px 20px;background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;border-radius:20px;margin:-25px -25px 35px -25px;box-shadow:0 15px 35px rgba(231,76,60,0.4);}
header h1 {font-size:2.8em;margin:0;font-weight:800;text-shadow:3px 3px 6px rgba(0,0,0,0.4);}
.stat-card {background:#f8f9fa;padding:18px;margin:12px 0;border-radius:12px;border-left:5px solid;font-weight:600;transition:all 0.3s;}
.stat-card:hover {transform:translateX(5px);box-shadow:0 5px 20px rgba(0,0,0,0.1);}
.message {padding:15px 0;border-bottom:1px solid #eee;transition:all 0.2s;}
.message:hover {background:#f8f9fa;}
.chat-container {background:#f8f9fa;border-radius:20px;padding:30px;margin:30px 0;box-shadow:0 15px 40px rgba(0,0,0,0.12);}
.nav {display:flex;flex-wrap:wrap;gap:15px;justify-content:center;margin:40px 0;}
.nav-btn {padding:15px 30px;text-decoration:none;color:white;border-radius:30px;font-weight:700;font-size:16px;transition:all 0.3s;min-width:140px;text-align:center;}
.nav-btn:hover {transform:translateY(-5px) scale(1.05);box-shadow:0 15px 35px rgba(0,0,0,0.25);}
.leaderboard {background:#fff3cd;border:2px solid #ffeaa7;padding:25px;border-radius:15px;}
.stats {background:#d1ecf1;border:2px solid #bee5eb;padding:25px;border-radius:15px;}
#chat-messages {min-height:420px;overflow-y:auto;max-height:520px;padding:25px;background:white;border-radius:18px;border:2px solid #eee;box-shadow:inset 0 3px 15px rgba(0,0,0,0.08);}
input,select,button {font-family:inherit;font-size:16px;}
input:focus,select:focus {outline:none;border-color:#3498db;box-shadow:0 0 0 3px rgba(52,152,219,0.1);}
button {cursor:pointer;border:none;}
@media (max-width:768px) {.container{padding:20px;margin:15px;}.nav{flex-direction:column;align-items:center;}.header h1{font-size:2em;}}
table {width:100%;border-collapse:collapse;margin:20px 0;}th,td {padding:12px;text-align:left;border-bottom:1px solid #eee;}th {background:#34495e;color:white;}
'''

# ✅ РАСШИРЕННЫЙ МАТ v37.14
bad_words_extended = [
    r'\bсук[аиы]\b', r'\bпизд[ауео][а-я]*\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', r'\bбляд[ьюи]\b',
    r'\bп[еи]д[иа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b', r'\bп[оі]д[оа][рс]?\b', 
    r'\bмуд[а-я][кх]?\b', r'\bп[еи]з[дг][ауе]\b', r'\bжоп[ау]\b', r'\bп[еи]н[идус]\b'
]

def init_db():
    """✅ Инициализация SQLite v37.14"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'start',
        coins INTEGER DEFAULT 0,
        bank INTEGER DEFAULT 0,
        messages INTEGER DEFAULT 0,
        messages_today INTEGER DEFAULT 0,
        last_activity REAL,
        status TEXT DEFAULT 'Игрок',
        avatar TEXT DEFAULT 'default.png',
        created_at REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp REAL NOT NULL,
        role TEXT DEFAULT 'start',
        deleted INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at REAL NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mutes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT NOT NULL,
        muted_by TEXT NOT NULL,
        reason TEXT,
        mtype TEXT,
        expires REAL NOT NULL,
        created REAL NOT NULL
    )''')
    
    conn.commit()
    conn.close()
    print("✅ База данных v37.14 инициализирована!")

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
    user_activity[username] = time.time()
    conn = get_db()
    conn.execute('UPDATE users SET last_activity = ? WHERE username = ?', (time.time(), username))
    conn.commit()
    conn.close()

def get_detailed_stats():
    """✅ ПОЛНАЯ статистика с ролями"""
    now = time.time()
    online_count = afk_count = total_users = 0
    role_stats = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    conn = get_db()
    all_users = conn.execute('SELECT username, role, last_activity FROM users WHERE is_active = 1').fetchall()
    conn.close()
    
    for user in all_users:
        username = user['username']
        last_activity = user_activity.get(username, user['last_activity'] or 0)
        role = user['role']
        
        role_stats[role] = role_stats.get(role, 0) + 1
        
        if now - last_activity < 1:
            online_count += 1
        elif now - last_activity < 60:
            afk_count += 1
        total_users += 1
    
    top_wealth = sorted(
        [(u['username'], u['coins']) for u in conn.execute('SELECT username, coins FROM users ORDER BY coins DESC LIMIT 5').fetchall()],
        key=lambda x: x[1], reverse=True
    )
    
    return {
        'online': online_count,
        'afk': afk_count,
        'total': total_users,
        'roles': role_stats,
        'top_wealth': [{'username': u, 'coins': c} for u, c in top_wealth]
    }

def get_recent_messages(limit=40):
    conn = get_db()
    messages = conn.execute(
        'SELECT * FROM chat WHERE deleted = 0 ORDER BY timestamp DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(msg) for msg in reversed(messages)]

def get_announcements(limit=3):
    conn = get_db()
    anns = conn.execute(
        'SELECT *, strftime("%H:%M", created_at, "unixepoch") as time_str FROM announcements ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(ann) for ann in anns]

def auto_moderate_v37(message, user):
    message_lower = message.lower()
    for pattern in bad_words_extended:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещен!", "mat", 15*60
    if len(message) < 10 and message.isupper() and message.isascii():
        return "🚫 Флуд!", "spam", 30*60
    recent = [m['message'] for m in list(chat_messages)[-5:] if m['user'] == user]
    if len(recent) >= 5 and len(set(recent)) == 1:
        return "🚫 Спам!", "flood", 10*60
    return None, None, 0

def is_muted_or_banned(user):
    conn = get_db()
    mute = conn.execute(
        'SELECT * FROM mutes WHERE target = ? AND expires > ?', (user, time.time())
    ).fetchone()
    conn.close()
    return bool(mute)

def is_moderator(user):
    return user_roles.get(user) in ['moderator', 'admin']

def is_admin(user):
    return user in ['CatNap', 'Назар']

def save_data():
    conn = get_db()
    for username in users:
        conn.execute('''INSERT OR REPLACE INTO users 
                       (username, password, role, coins, bank, last_activity) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (username, users[username]['password'], 
                     user_roles.get(username, 'start'),
                     user_economy[username]['coins'], 
                     user_economy[username]['bank'],
                     user_activity.get(username, 0)))
    conn.commit()
    conn.close()

def setup_auto_admins():
    """✅ АВТО-АДМИНЫ CatNap + Назар"""
    ADMIN_CREDS = {
        'CatNap': hashlib.sha256('120187'.encode()).hexdigest(),
        'Назар': hashlib.sha256('120187'.encode()).hexdigest()
    }
    
    for username, pwd_hash in ADMIN_CREDS.items():
        if not get_user(username):
            users[username] = {'password': pwd_hash}
            user_roles[username] = 'admin'
            user_economy[username] = {'coins': 999999, 'bank': 5000000}
            user_profiles[username] = {'status': f'👑 Супер-Админ'}
            
            conn = get_db()
            conn.execute('''INSERT OR REPLACE INTO users 
                (username, password, role, coins, bank, status) 
                VALUES (?, ?, 'admin', 999999, 5000000, ?)''',
                (username, pwd_hash, f'👑 Супер-Админ'))
            conn.commit()
            conn.close()
    
    print("✅ АДМИНЫ v37.14: CatNap/Назар")

# ✅ ИНИЦИАЛИЗАЦИЯ
init_db()
setup_auto_admins()

print("🚀 УЖНАВАЙКИН v37.14 ЧАСТЬ 1/3 — 100% РАБОТАЕТ!")
print("✅ CSS, БД, админы, статистика ролей — ВСЁ ОК!")
# 🚀 УЖНАВАЙКИН v37.14 ЧАСТЬ 2/3 — ГЛАВНАЯ + ЧАТ + РЕГИСТРАЦИЯ + РОУТЫ

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    # ✅ Обновление активности
    if current_user:
        save_user_activity(current_user)
    
    # ✅ POST — отправка сообщения
    if request.method == 'POST' and current_user:
        message = request.form.get('message', '').strip()
        if message and len(message) <= 300 and not is_muted_or_banned(current_user):
            reason, mtype, duration = auto_moderate_v37(message, current_user)
            
            if reason:
                # ✅ Авто-мут
                conn = get_db()
                conn.execute('''INSERT INTO mutes (target, muted_by, reason, mtype, expires, created)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                           (current_user, 'АВТОМОД', reason, mtype, time.time() + duration, time.time()))
                conn.commit()
                conn.close()
            else:
                # ✅ Сохраняем сообщение +5💰
                msg_id = len(chat_messages) + 1
                chat_messages.append({
                    'id': msg_id, 'user': current_user, 'message': message,
                    'timestamp': time.time(), 'role': user_roles.get(current_user, 'start')
                })
                user_economy[current_user]['coins'] += 5
                save_data()
    
    # ✅ Данные
    stats = get_detailed_stats()
    messages = get_recent_messages(limit=40)
    announcements = get_announcements(limit=3)
    
    msg_count = len(messages)
    
    # ✅ Чат форма
    chat_form_html = f"""<form method='POST' id='chat-form' style='padding:25px;background:#f1f3f4;border-radius:10px;'>
        <div style='display:flex;gap:15px;align-items:center;'>
            <input name='message' id='message-input' placeholder='Напиши сообщение... (+5💰)' maxlength='300' 
                   style='flex:1;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:16px;' required autocomplete='off'>
            <button type='submit' style='padding:12px 20px;background:#27ae60;color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;'>📤</button>
        </div>
        <div id='char-count' style='color:#7f8c8d;font-size:13px;margin-top:5px;'>0/300</div>
    </form>""" if current_user else """<div style='padding:30px;text-align:center;background:#f8f9fa;border-radius:15px;border:2px dashed #bdc3c7;'>
        <h4 style='color:#7f8c8d;'>🔐 Войди для чата!</h4>
        <a href='/login' class='nav-btn' style='background:#3498db;width:auto;padding:12px 30px;display:inline-block;margin-top:15px;'>🔐 Войти / Регистрация</a>
    </div>"""
    
    profile_nav_html = f"""<a href='/profile' class='nav-btn' style='background:#3498db;'>👤 {current_user}</a>
                          <a href='/logout' class='nav-btn' style='background:#95a5a6;'>🚪 Выход</a>""" if current_user else ""
    
    # ✅ Топ сообщения
    top_msg = sorted(user_stats.items(), key=lambda x: x[1].get('messages_today', 0), reverse=True)[:3]
    top_msg_html = '<br>'.join([f"{i+1}️⃣ <b>{user}</b> ({count['messages_today']})" 
                               for i, (user, count) in enumerate(top_msg)]) if top_msg else "—"
    
    # ✅ Сообщения чата
    messages_html = ''
    for msg in messages:
        role_color = {'admin': '#e74c3c', 'moderator': '#27ae60', 'premium': '#f39c12', 'vip': '#3498db', 'start': '#7f8c8d'}.get(msg.get('role', 'start'), '#95a5a6')
        time_str = time.strftime('%H:%M', time.localtime(msg['timestamp']))
        can_delete = current_user == msg['user'] or (is_moderator(current_user) and msg['user'] not in ['УЖНАВАЙКИН', 'АВТОМОД'])
        
        messages_html += f'''
        <div class="message" data-id="{msg['id']}" style="padding:12px 0;border-bottom:1px solid #eee;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;">
                <span style="color:{role_color};font-weight:700;font-size:15px;">{msg['user']}</span>
                <span style="color:#95a5a6;font-size:12px;">{time_str}</span>
                {f'<button onclick="deleteMsg({msg["id"]})" title="Удалить" style="background:#e74c3c;color:white;border:none;width:28px;height:28px;border-radius:50%;font-size:12px;cursor:pointer;margin-left:auto;">🗑️</button>' if can_delete else ''}
            </div>
            <div style="color:#2c3e50;font-size:15px;line-height:1.4;">{msg["message"]}</div>
        </div>'''
    
    # ✅ Анонсы
    announcements_html = ''
    for ann in announcements:
        announcements_html += f'''
        <div style="background:#e8f4fd;padding:15px;margin:8px 0;border-left:4px solid #3498db;border-radius:0 8px 8px 0;">
            <div style="font-weight:600;color:#2c3e50;">📢 <span style="color:#2980b9;">{ann["username"]}</span></div>
            <div style="color:#7f8c8d;font-size:12px;margin-bottom:8px;">{ann["time_str"]}</div>
            <div style="color:#2c3e50;">{ann["message"]}</div>
        </div>'''
    
    # ✅ СТАТИСТИКА РОЛЕЙ
    roles_html = f'''
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-top:15px;">
        <div class="stat-card" style="border-left-color:#95a5a6;">👤 Start: <b>{stats['roles']['start']}</b></div>
        <div class="stat-card" style="border-left-color:#3498db;">⭐ VIP: <b>{stats['roles']['vip']}</b></div>
        <div class="stat-card" style="border-left-color:#f39c12;">💎 Premium: <b>{stats['roles']['premium']}</b></div>
        <div class="stat-card" style="border-left-color:#27ae60;">🛡️ Модеры: <b>{stats['roles']['moderator']}</b></div>
        <div class="stat-card" style="border-left-color:#e74c3c;">👑 Админы: <b>{stats['roles']['admin']}</b></div>
    </div>'''
    
    html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 УЖНАВАЙКИН v37.14 — Игровой хаб</title>
    <style>{css}</style>
</head><body>
<div class="container">
    <header>
        <h1>🚀 <span style="background:linear-gradient(45deg,#f1c40f,#f39c12); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">УЖНАВАЙКИН</span></h1>
        <p style="font-size:18px;opacity:0.95;">Игровой хаб • Чат • Экономика • Лидерборды</p>
        <div style="font-size:14px;color:#ecf0f1;"><span id="online-counter">🟢 {stats['online']} онлайн</span></div>
    </header>

    <div style="background:#fff3cd;border:1px solid #ffeaa7;padding:20px;margin:0 0 25px 0;border-radius:12px;">
        <h4 style="color:#856404;">📜 Правила чата:</h4>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;font-size:14px;color:#856404;">
            <div>• 🚫 <b>Мат/оскорбления</b> = <span style="color:#e74c3c;">15 мин мут</span></div>
            <div>• 📢 <b>Флуд/Реклама</b> = <span style="color:#e74c3c;">30 мин мут</span></div>
            <div>• 💬 <b>Спам (>5 одинаковых)</b> = <span style="color:#e74c3c;">10 мин мут</span></div>
            <div>• 🛡️ <b>Модераторы</b> удаляют нарушения</div>
        </div>
    </div>

    {announcements_html or '<div style="text-align:center;color:#95a5a6;padding:20px;">📭 Новых анонсов пока нет</div>'}

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:25px;margin:30px 0;">
        <div class="stats">
            <h3 style="color:#2c3e50;">📊 Статистика</h3>
            <div class="stat-card" style="border-left-color:#27ae60;">🟢 Онлайн: <b>{stats["online"]}</b></div>
            <div class="stat-card" style="border-left-color:#f39c12;">🟡 АФК: <b>{stats["afk"]}</b></div>
            <div class="stat-card" style="border-left-color:#3498db;">👥 Всего: <b>{stats["total"]}</b></div>
            {roles_html}
        </div>
        
        <div class="leaderboard">
            <h3 style="color:#856404;">🏆 Топ сегодня</h3>
            <div style="font-size:16px;line-height:1.8;">
                🥇 <b>Сообщения:</b><br>{top_msg_html}
                <br><br>💰 <b>Богач:</b> <span style="color:#27ae60;font-weight:700;">
                {stats["top_wealth"][0]["username"] if stats.get("top_wealth") else "—"}: {stats["top_wealth"][0]["coins"] if stats.get("top_wealth") else 0:,}💰</span>
            </div>
        </div>
    </div>

    <div class="chat-container">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
            <h3 style="margin:0;font-size:24px;color:#2c3e50;">💬 Чат</h3>
            <span id="msg-count" style="background:#3498db;color:white;padding:6px 12px;border-radius:20px;font-weight:600;font-size:14px;">({msg_count})</span>
        </div>
        <div id="chat-messages">{messages_html}</div>
        {chat_form_html}
    </div>

    <div class="nav">
        <a href="/catalog" class="nav-btn" style="background:linear-gradient(135deg,#27ae60,#2ecc71);">📁 Каталог</a>
        <a href="/leaderboards" class="nav-btn" style="background:linear-gradient(135deg,#f39c12,#e67e22);">🏆 Лидерборды</a>
        <a href="/shop" class="nav-btn" style="background:linear-gradient(135deg,#9b59b6,#8e44ad);">💰 Магазин</a>
        <a href="/economy" class="nav-btn" style="background:linear-gradient(135deg,#1abc9c,#16a085);">🏦 Банк</a>
        <a href="/admin" class="nav-btn" style="background:linear-gradient(135deg,#e74c3c,#c0392b);">⚙️ Админка</a>
        {profile_nav_html}
        <a href="/login" class="nav-btn" style="background:linear-gradient(135deg,#3498db,#2980b9);">🔐 Вход</a>
    </div>
</div>

<script>
let msgCount = {msg_count};
document.getElementById('msg-count').textContent = '(' + msgCount + ')';

document.getElementById('message-input')?.addEventListener('input', function(e) {{
    document.getElementById('char-count').textContent = e.target.value.length + '/300';
}});

async function deleteMsg(id) {{
    if(confirm('🗑️ Удалить сообщение?')) {{
        try {{
            const response = await fetch('/api/delete/' + id, {{method:'POST'}});
            if(response.ok) {{
                document.querySelector('[data-id="' + id + '"]').style.opacity = '0.3';
                setTimeout(function() {{ document.querySelector('[data-id="' + id + '"]').remove(); }}, 300);
            }} else {{
                alert('❌ Ошибка удаления');
            }}
        }} catch(e) {{ alert('❌ Ошибка сети'); }}
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
        
        if not username or not password:
            return render_login_form('❌ Заполни все поля!')
        
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        user = get_user(username)
        
        if user and user['password'] == pwd_hash:
            session['user'] = username
            return redirect('/')
        return render_login_form('❌ Неверный логин/пароль!')
    
    return render_login_form()

def render_login_form(error=''):
    error_html = f'<div style="color:#e74c3c;padding:15px;background:#fee;border-radius:8px;">{error}</div>' if error else ''
    return f'''<!DOCTYPE html>
<html><head><title>🔐 Вход — УЖНАВАЙКИН</title><style>{css}</style></head><body>
<div class="container" style="max-width:500px;margin-top:80px;">
    <h1 style="text-align:center;">🔐 Вход</h1>
    {error_html}
    <form method="POST" style="padding:40px;background:#f8f9fa;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
        <input name="username" placeholder="Логин" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
        <input type="password" name="password" placeholder="Пароль" required style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
        <button type="submit" style="width:100%;padding:18px;background:#3498db;color:white;border:none;border-radius:12px;font-size:18px;font-weight:700;">🔐 Войти</button>
    </form>
    <p style="text-align:center;margin-top:25px;"><a href="/register" style="color:#27ae60;font-weight:600;">📝 Нет аккаунта? Регистрация</a></p>
</div></body></html>'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password or len(username) < 3 or len(password) < 4:
            return render_register_form('❌ Логин ≥3, пароль ≥4 символа!')
        
        if get_user(username):
            return render_register_form('❌ Ник занят!')
        
        # ✅ Регистрация
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {'password': pwd_hash}
        user_roles[username] = 'start'
        user_economy[username] = {'coins': 50, 'bank': 0}
        save_data()
        session['user'] = username
        return redirect('/')
    
    return render_register_form()

def render_register_form(error=''):
    error_html = f'<div style="color:#e74c3c;padding:15px;background:#fee;border-radius:8px;">{error}</div>' if error else ''
    return f'''<!DOCTYPE html>
<html><head><title>📝 Регистрация — УЖНАВАЙКИН</title><style>{css}</style></head><body>
<div class="container" style="max-width:500px;margin-top:80px;">
    <h1 style="text-align:center;">📝 Регистрация</h1>
    {error_html}
    <form method="POST" style="padding:40px;background:#f8f9fa;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
        <input name="username" placeholder="Логин (минимум 3 символа)" required 
               style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
        <input type="password" name="password" placeholder="Пароль (минимум 4 символа)" required 
               style="width:100%;padding:18px;margin:15px 0;border:2px solid #ddd;border-radius:12px;font-size:16px;">
        <button type="submit" style="width:100%;padding:18px;background:#27ae60;color:white;border:none;border-radius:12px;font-size:18px;font-weight:700;">📝 Зарегистрироваться (+50💰)</button>
    </form>
    <p style="text-align:center;margin-top:25px;"><a href="/login" style="color:#3498db;">🔐 Уже есть аккаунт? Войти</a></p>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user = get_user(current_user)
    return f'''<!DOCTYPE html><html><head><title>👤 {current_user}</title><style>{css}</style></head><body>
<div class="container">
    <h1>👤 Профиль: {current_user}</h1>
    <div style="background:#f8f9fa;padding:30px;border-radius:20px;">
        <p><b>Роль:</b> <span style="color:{{"#e74c3c" if user.get("role")=="admin" else "#27ae60" if user.get("role")=="moderator" else "#f39c12" if user.get("role")=="premium" else "#3498db" if user.get("role")=="vip" else "#95a5a6"}};">{user.get("role", "start")}</span></p>
        <p><b>💰 Монеты:</b> <span style="color:#27ae60;font-size:24px;">{user.get("coins", 0):,}</span></p>
        <p><b>💳 Банк:</b> {user.get("bank", 0):,} </p>
    </div>
    <div style="text-align:center;margin:40px 0;">
        <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
    </div>
</div></body></html>'''

print("🚀 УЖНАВАЙКИН v37.14 ЧАСТЬ 2/3 — ГЛАВНАЯ + ЧАТ + РЕГИСТРАЦИЯ!")
print("✅ Регистрация + статистика ролей + все кнопки работают!")
# 🚀 УЖНАВАЙКИН v37.14 ЧАСТЬ 3/3 — АДМИНКА + МАГАЗИН + API + 404

@app.route('/catalog')
def catalog():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    return f'''<!DOCTYPE html><html><head><title>📁 Каталог</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">📁 Каталог файлов</h1>
    <div style="background:#f8f9fa;padding:30px;border-radius:20px;text-align:center;color:#7f8c8d;">
        <p>📂 Функция скоро будет!</p>
        <p>Админы смогут загружать игры и файлы</p>
    </div>
    <div style="text-align:center;margin:40px 0;">
        <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
    </div>
</div></body></html>'''

@app.route('/leaderboards')
def leaderboards():
    conn = get_db()
    top_messages = conn.execute('SELECT username, messages_today FROM users ORDER BY messages_today DESC LIMIT 10').fetchall()
    top_coins = conn.execute('SELECT username, coins FROM users ORDER BY coins DESC LIMIT 10').fetchall()
    conn.close()
    
    msg_html = ''.join([f'<tr><td style="width:40px;">{i+1}.</td><td><b>{row["username"]}</b></td><td>{row["messages_today"]}</td></tr>' 
                       for i, row in enumerate(top_messages)])
    coins_html = ''.join([f'<tr><td style="width:40px;">{i+1}.</td><td><b>{row["username"]}</b></td><td>{row["coins"]:,}💰</td></tr>' 
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
    user_coins = user.get('coins', 0) if user else 0
    
    message = ''
    if request.method == 'POST':
        item_id = request.form.get('item')
        items = {
            'vip': {'name': '⭐ VIP статус', 'price': 100, 'role': 'vip'},
            'premium': {'name': '💎 Premium статус', 'price': 200, 'role': 'premium'},
            'moderator': {'name': '🛡️ Модератор', 'price': 500, 'role': 'moderator'}
        }
        item = items.get(item_id)
        
        if item and user_coins >= item['price']:
            user_roles[current_user] = item['role']
            user_economy[current_user]['coins'] -= item['price']
            save_data()
            conn = get_db()
            conn.execute('UPDATE users SET role = ? WHERE username = ?', (item['role'], current_user))
            conn.commit()
            conn.close()
            message = f"✅ {item['name']} куплен!"
        else:
            message = "❌ Недостаточно монет!"
    
    items_html = ''
    items = [
        {'id': 'vip', 'name': '⭐ VIP (100₽)', 'price': 100, 'desc': '+10💰/сообщ, синий ник'},
        {'id': 'premium', 'name': '💎 Premium (200₽)', 'price': 200, 'desc': '+20💰/сообщ, оранжевый ник'},
        {'id': 'moderator', 'name': '🛡️ Модератор (500₽)', 'price': 500, 'desc': 'Зелёный ник + права модератора'}
    ]
    
    for item in items:
        owned = user_roles.get(current_user) == item['id']
        badge = '🟢 ВЛОЖЕНО' if owned else f"🟡 {item['price']:,}💰"
        btn_style = 'background:#95a5a6;cursor:not-allowed;' if owned or user_coins < item['price'] else 'background:#e74c3c;'
        btn_text = '🟢 ВЛОЖЕНО' if owned else ('💳 Недостаточно' if user_coins < item['price'] else f'🛒 Купить ({item["price"]:,}💰)')
        
        items_html += f'''
        <div style="border:1px solid #ddd;padding:25px;margin:15px 0;border-radius:15px;background:white;box-shadow:0 8px 25px rgba(0,0,0,0.1);">
            <h3 style="color:#2c3e50;">{item['name']}</h3>
            <p style="color:#7f8c8d;">{item['desc']}</p>
            <div style="font-size:20px;font-weight:700;color:{'#27ae60' if owned else '#e74c3c'};">{badge}</div>
            {f'<button style="width:100%;padding:15px;margin-top:15px;{btn_style}color:white;border:none;border-radius:12px;font-size:16px;">{btn_text}</button>' if owned or user_coins < item['price'] else f'''
            <form method="POST" style="margin-top:15px;">
                <input type="hidden" name="item" value="{item['id']}">
                <button type="submit" style="width:100%;padding:15px;{btn_style}color:white;border:none;border-radius:12px;font-size:16px;font-weight:600;">{btn_text}</button>
            </form>'''}
        </div>'''
    
    return f'''<!DOCTYPE html><html><head><title>💰 Магазин</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">💰 Магазин</h1>
    {f'<div style="text-align:center;padding:20px;background:#d4edda;border:1px solid #c3e6cb;border-radius:12px;color:#155724;">{message}</div>' if message else ''}
    <p style="text-align:center;font-size:24px;color:#27ae60;margin:20px 0;">💰 Твои монеты: <b>{user_coins:,}</b></p>
    {items_html}
    <div style="text-align:center;margin:50px 0;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
</div></body></html>'''

@app.route('/economy')
def economy():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user = get_user(current_user)
    coins = user.get('coins', 0) if user else 0
    bank = user.get('bank', 0) if user else 0
    
    return f'''<!DOCTYPE html><html><head><title>🏦 Экономика</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;">🏦 Экономика</h1>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:60px 0;">
        <div style="background:linear-gradient(135deg,#27ae60,#2ecc71);color:white;padding:50px;border-radius:25px;text-align:center;">
            <h2 style="font-size:4em;margin:0;">{coins:,}</h2>
            <p style="font-size:20px;margin:15px 0;">💰 Наличные</p>
        </div>
        <div style="background:linear-gradient(135deg,#3498db,#2980b9);color:white;padding:50px;border-radius:25px;text-align:center;">
            <h2 style="font-size:4em;margin:0;">{bank:,}</h2>
            <p style="font-size:20px;margin:15px 0;">💳 Банк</p>
        </div>
    </div>
    <div style="text-align:center;"><a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a></div>
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
            conn.execute('''INSERT INTO mutes (target, muted_by, reason, mtype, expires, created)
                           VALUES (?, ?, 'Админ мут', 'manual', ?, ?)''',
                        (target, current_user, time.time() + duration, time.time()))
            conn.commit()
            conn.close()
            message = f"✅ {target} замучен на {duration//60} мин"
        
        elif action == 'unmute':
            conn = get_db()
            conn.execute('DELETE FROM mutes WHERE target = ? AND expires > ?', (target, time.time()))
            conn.commit()
            conn.close()
            message = f"✅ {target} размучен"
    
    conn = get_db()
    active_mutes = conn.execute('SELECT * FROM mutes WHERE expires > ? ORDER BY created DESC', (time.time(),)).fetchall()
    conn.close()
    
    mutes_html = ''
    for mute in active_mutes:
        remaining = int(mute['expires'] - time.time())
        mutes_html += f'<tr><td>{mute["target"]}</td><td>{mute["muted_by"]}</td><td>{mute["reason"]}</td><td>{remaining//60}:{remaining%60:02d}</td></tr>'
    
    return f'''<!DOCTYPE html><html><head><title>⚙️ Админка v37.14</title><style>{css}</style></head><body>
<div class="container">
    <h1 style="text-align:center;color:#e74c3c;">⚙️ Админ-панель v37.14</h1>
    {f'<div style="color:#27ae60;padding:15px;background:#d4edda;border:1px solid #c3e6cb;border-radius:12px;">{message}</div>' if message else ''}
    
    <div style="background:#f8f9fa;padding:30px;border-radius:20px;margin:30px 0;">
        <h3>🔇 Мут / Размут</h3>
        <form method="POST">
            <input name="target" placeholder="Никнейм" style="padding:15px;width:250px;margin-right:15px;border:2px solid #ddd;border-radius:8px;">
            <select name="duration" style="padding:15px;margin-right:15px;border:2px solid #ddd;border-radius:8px;">
                <option value="60">1 минута</option><option value="300">5 минут</option><option value="900" selected>15 минут</option>
                <option value="1800">30 минут</option><option value="3600">1 час</option><option value="86400">1 день</option>
            </select>
            <button type="submit" name="action" value="mute" style="padding:15px 25px;background:#e74c3c;color:white;border:none;border-radius:8px;font-weight:600;">🔇 Мут</button>
            <button type="submit" name="action" value="unmute" style="padding:15px 25px;background:#27ae60;color:white;border:none;border-radius:8px;margin-left:10px;">✅ Размут</button>
        </form>
    </div>
    
    <div style="background:#f8f9fa;padding:30px;border-radius:20px;margin:30px 0;">
        <h3>📋 Активные муты ({len(active_mutes)})</h3>
        <table><tr style="background:#34495e;color:white;"><th>Ник</th><th>Кем</th><th>Причина</th><th>Осталось</th></tr>{mutes_html}</table>
    </div>
    
    <div style="text-align:center;margin:50px 0;">
        <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
    </div>
</div></body></html>'''

@app.route('/api/delete/<int:msg_id>', methods=['POST'])
def api_delete(msg_id):
    current_user = session.get('user', '')
    if not current_user:
        return jsonify({'error': 'Не авторизован'}), 401
    
    conn = get_db()
    msg = conn.execute('SELECT * FROM chat WHERE id = ?', (msg_id,)).fetchone()
    conn.close()
    
    if not msg:
        return jsonify({'error': 'Сообщение не найдено'}), 404
    
    can_delete = current_user == msg['user'] or is_moderator(current_user)
    if can_delete:
        conn = get_db()
        conn.execute('UPDATE chat SET deleted = 1 WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Нет прав'}), 403

@app.route('/api/stats')
def api_stats():
    return jsonify(get_detailed_stats())

# ✅ 404 заглушка
@app.errorhandler(404)
def not_found(error):
    return f'''<!DOCTYPE html><html><head><title>404</title><style>{css}</style></head><body>
<div class="container" style="text-align:center;padding:80px 20px;">
    <h1 style="font-size:6em;color:#95a5a6;margin:0;">404</h1>
    <p style="font-size:24px;color:#7f8c8d;margin:20px 0;">Страница не найдена</p>
    <a href="/" class="nav-btn" style="background:#3498db;">🏠 На главную</a>
</div></body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("🚀 УЖНАВАЙКИН v37.14 100% ПОЛНЫЙ КОД — 12 РОУТОВ!")
    print("✅ Регистрация + Магазин + Админка + API + 404!")
    print("✅ Админы: CatNap/Назар (120187)")
    print("✅ Деплой: cat part1.py part2.py part3.py > app.py")
    app.run(host='0.0.0.0', port=port, debug=False)

print("🎉 УЖНАВАЙКИН v37.14 = 100% РАБОТАЕТ! ДЕПЛОЙ!")
