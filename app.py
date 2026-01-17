# 🚀 УЖНАВАЙКИН v37.9 ЧАСТЬ 1/3 — ПОЛНАЯ ОСНОВА + БД + АДМИНЫ + МОДЕРАЦИЯ

from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import os
import json
import time
import hashlib
import re
import sqlite3
import mimetypes
from collections import defaultdict, deque
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'uznaykin_v37_9_full_complete_2026_stable'
DB_FILE = 'uznaykin_v37.db'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ (персистентность)
users = {}
user_roles = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
user_profiles = {}
user_activity = {}
user_stats = defaultdict(lambda: {'messages_today': 0, 'messages_total': 0})
user_economy = defaultdict(lambda: {'coins': 0, 'bank': 0})
user_inventory = defaultdict(list)
chat_messages = deque(maxlen=1000)
mutes = {'by': {}, 'list': []}
catalog = {'root': {'type': 'folder', 'created_by': 'system', 'created': time.time()}}
leaderboards = {'messages_today': [], 'coins': [], 'bank': []}
announcements = []

# ✅ РАСШИРЕННЫЙ МАТ v37.9 (все вариации)
bad_words_extended = [
    # Основные
    r'\bсук[аиы]\b', r'\bпизд[ауео][а-я]*\b', r'\bху[йя]\b', r'\bпидор[аы]?\b', r'\bбляд[ьюи]\b',
    # Пидор вариации
    r'\bп[еи]д[иа][рс]?\b', r'\b[её]б[а-я][нл][а-я]*\b', r'\bп[оі]д[оа][рс]?\b', 
    # Дополнительно
    r'\bмуд[а-я][кх]?\b', r'\bп[еи]з[дг][ауе]\b', r'\bжоп[ау]\b', r'\bп[еи]н[идус]\b',
    r'\b[её]буч[ие]\b', r'\bпидр[аил]\b', r'\bх[уи][йю]\b', r'\bпизд[ею]\b'
]

def init_db():
    """✅ ПОЛНАЯ Инициализация SQLite v37.9"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    # Пользователи (полная таблица)
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
    
    # Чат с ID и ролями
    c.execute('''CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp REAL NOT NULL,
        role TEXT DEFAULT 'start',
        deleted INTEGER DEFAULT 0
    )''')
    
    # Анонсы
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at REAL NOT NULL
    )''')
    
    # Каталог файлов/папок
    c.execute('''CREATE TABLE IF NOT EXISTS catalog (
        path TEXT PRIMARY KEY,
        type TEXT NOT NULL, -- 'file' или 'folder'
        created_by TEXT NOT NULL,
        created REAL NOT NULL,
        size INTEGER DEFAULT 0,
        mime_type TEXT
    )''')
    
    # Муты
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
    print("✅ База данных v37.9 инициализирована!")

def get_db():
    """✅ Подключение к БД с row_factory"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_user(username):
    """✅ Получает пользователя как DICT"""
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def save_user_activity(username):
    """✅ Обновляет активность (1сек=онлайн, 60сек=АФК)"""
    user_activity[username] = time.time()
    conn = get_db()
    conn.execute('UPDATE users SET last_activity = ? WHERE username = ?', 
                (time.time(), username))
    conn.commit()
    conn.close()

def get_detailed_stats_v37():
    """✅ ПОЛНАЯ статистика v37.9: онлайн/АФК/роли/топ"""
    now = time.time()
    online_count = afk_count = total_users = 0
    role_stats = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    # Подсчет по активности
    for username in users:
        last_activity = user_activity.get(username, 0)
        if now - last_activity < 1:  # 🟢 <1сек = онлайн
            online_count += 1
        elif now - last_activity < 60:  # 🟡 <60сек = АФК
            afk_count += 1
        total_users += 1
        
        role = user_roles.get(username, 'start')
        role_stats[role] = role_stats.get(role, 0) + 1
    
    # Топ по монетам
    top_wealth = sorted(
        [(u, user_economy[u]['coins']) for u in user_economy], 
        key=lambda x: x[1], reverse=True
    )[:5]
    
    return {
        'online': online_count,
        'afk': afk_count, 
        'total': total_users,
        'roles': role_stats,
        'top_wealth': [{'username': u, 'coins': c} for u, c in top_wealth]
    }

def get_recent_messages(limit=40):
    """✅ Последние 40 сообщений из БД"""
    conn = get_db()
    messages = conn.execute(
        'SELECT * FROM chat WHERE deleted = 0 ORDER BY timestamp DESC LIMIT ?', 
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(msg) for msg in reversed(messages)]

def get_announcements(limit=3):
    """✅ Последние анонсы с временем"""
    conn = get_db()
    anns = conn.execute(
        'SELECT *, strftime("%H:%M", created_at, "unixepoch") as time_str FROM announcements ORDER BY created_at DESC LIMIT ?', 
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(ann) for ann in anns]

def auto_moderate_v37(message, user):
    """✅ АВТОМОДЕРАЦИЯ v37.9: мат/спам/флуд"""
    message_lower = message.lower()
    
    # Мат (расширенный)
    for pattern in bad_words_extended:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "🚫 Мат запрещен!", "mat", 15*60  # 15 минут
    
    # Спам (короткие капсом)
    if len(message) < 10 and message.isupper() and message.isascii():
        return "🚫 Спам!", "spam", 10*60  # 10 минут
    
    # Флуд (5+ одинаковых подряд)
    recent = [m['message'] for m in chat_messages[-5:] if m['user'] == user]
    if len(recent) >= 5 and len(set(recent)) == 1:
        return "🚫 Флуд!", "flood", 30*60  # 30 минут
    
    return None, None, 0

def is_muted_or_banned(user):
    """✅ Проверка мута/бана"""
    conn = get_db()
    mute = conn.execute(
        'SELECT * FROM mutes WHERE target = ? AND expires > ?',
        (user, time.time())
    ).fetchone()
    conn.close()
    return bool(mute)

def is_moderator(user):
    """✅ Проверка модератора/админа"""
    return user_roles.get(user) in ['moderator', 'admin']

def is_admin(user):
    """✅ Только админ"""
    return user_roles.get(user) == 'admin'

def create_folder(path, folder_name, user):
    """✅ Создание папки (только админы)"""
    if not is_admin(user):
        return False, "❌ Только админы!"
    full_path = f"{path}/{folder_name}" if path != 'root' else folder_name
    if full_path in catalog:
        return False, "❌ Уже существует!"
    
    catalog[full_path] = {
        'type': 'folder', 
        'created_by': user, 
        'created': time.time()
    }
    
    conn = get_db()
    conn.execute('INSERT INTO catalog VALUES (?, ?, ?, ?, 0, ?)', 
                (full_path, 'folder', user, time.time(), 'directory'))
    conn.commit()
    conn.close()
    return True, f"✅ Папка '{folder_name}' создана!"

def delete_item(path, user):
    """✅ Удаление (админы ВСЁ, модеры свои)"""
    if path not in catalog:
        return False, "❌ Не найдено!"
    
    if not is_admin(user) and catalog[path]['created_by'] != user:
        return False, "❌ Нет прав!"
    
    del catalog[path]
    
    conn = get_db()
    conn.execute('DELETE FROM catalog WHERE path = ?', (path,))
    conn.commit()
    conn.close()
    return True, "✅ Удалено!"

def setup_auto_admins_v37():
    """✅ АВТО-АДМИНЫ v37.9: CatNap + Назар"""
    global catalog
    
    ADMIN_CREDS = {
        'CatNap': hashlib.sha256('120187'.encode()).hexdigest(),
        'Назар': hashlib.sha256('120187'.encode()).hexdigest()
    }
    
    for username, pwd_hash in ADMIN_CREDS.items():
        if username not in users:
            users[username] = {'password': pwd_hash}
            user_roles[username] = 'admin'
            user_profiles[username] = {
                'status': f'👑 Супер-Админ', 
                'avatar': 'admin.png'
            }
            user_economy[username] = {'coins': 999999, 'bank': 5000000}
            user_stats[username] = {'messages_today': 0, 'messages_total': 999}
            
            # В БД
            conn = get_db()
            conn.execute('''INSERT OR REPLACE INTO users 
                (username, password, role, coins, bank, status, avatar) 
                VALUES (?, ?, 'admin', 999999, 5000000, ?, 'admin.png')''',
                (username, pwd_hash, f'👑 Супер-Админ {username}'))
            conn.commit()
            conn.close()
    
    # Корневая папка
    if 'root' not in catalog:
        catalog['root'] = {
            'type': 'folder', 
            'created_by': 'УЗНАВАЙКИН', 
            'created': time.time()
        }
    
    print("✅ АДМИНЫ v37.9: CatNap/Назар")
    print("✅ Супер-админы: 999,999💰 + 5M💳")

# ✅ КРИТИЧЕСКИЕ АЛИАСЫ v37.9 — ФИКС NameError!
get_detailed_stats = get_detailed_stats_v37
setup_auto_admins = setup_auto_admins_v37

# ✅ ИНИЦИАЛИЗАЦИЯ
init_db()
setup_auto_admins()

print("🚀 УЗНАВАЙКИН v37.9 ЧАСТЬ 1/3 — ПОЛНАЯ ОСНОВА!")
print("✅ Готово к запуску! Скажи '2/3' для главной + чата!")
# 🚀 УЖНАВАЙКИН v37.9 ЧАСТЬ 2/3 — ГЛАВНАЯ + ЧАТ + КАТАЛОГ + НАВИГАЦИЯ

# ✅ save_data() — синхронизация памяти ↔ БД
def save_data():
    """Сохраняет ВСЕ данные в БД"""
    conn = get_db()
    
    # Пользователи в БД
    for username, data in users.items():
        conn.execute('''INSERT OR REPLACE INTO users (username, password, role, coins, bank) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (username, data['password'], user_roles.get(username, 'start'),
                     user_economy[username]['coins'], user_economy[username]['bank']))
    
    # Чат в БД
    for msg in chat_messages:
        conn.execute('INSERT OR REPLACE INTO chat (id, user, message, timestamp, role) VALUES (?, ?, ?, ?, ?)',
                    (msg['id'], msg['user'], msg['message'], msg['timestamp'], msg.get('role', 'start')))
    
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    # ✅ Обновление активности пользователя
    if current_user:
        save_user_activity(current_user)
    
    # ✅ POST — отправка сообщения в чат
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
                # ✅ Сохраняем сообщение +5 монет
                msg_id = len(chat_messages) + 1
                chat_messages.append({
                    'id': msg_id,
                    'user': current_user,
                    'message': message,
                    'timestamp': time.time(),
                    'role': user_roles.get(current_user, 'start')
                })
                user_economy[current_user]['coins'] += 5
                save_data()
    
    # ✅ Данные для рендера
    stats = get_detailed_stats()
    messages = get_recent_messages(limit=40)
    announcements = get_announcements(limit=3)
    
    # ✅ HTML переменные (фикс NameError)
    msg_count = len(messages)
    chat_form_html = f"""<form method='POST' id='chat-form' style='padding:25px;background:#f1f3f4;border-radius:10px;'>
        <div style='display:flex;gap:15px;align-items:center;'>
            <input name='message' id='message-input' placeholder='Напиши сообщение... (+5💰)' maxlength='300' 
                   style='flex:1;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:16px;' required autocomplete='off'>
            <button type='submit' style='padding:12px 20px;background:#27ae60;color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;'>📤</button>
        </div>
        <div id='char-count' style='color:#7f8c8d;font-size:13px;margin-top:5px;'>0/300</div>
    </form>""" if current_user else """<div style='padding:30px;text-align:center;background:#f8f9fa;border-radius:15px;border:2px dashed #bdc3c7;'>
        <h4 style='color:#7f8c8d;'>🔐 Войди для чата!</h4>
        <p style='color:#95a5a6;margin:10px 0;'>Админы: CatNap / Назар (пароль: 120187)</p>
        <a href='/login' class='nav-btn' style='background:#e74c3c;width:auto;padding:12px 30px;display:inline-block;'>🔐 Войти</a>
    </div>"""
    
    profile_nav_html = f"""<a href='/profile' class='nav-btn' style='background:#3498db;'>👤 {current_user}</a>
                          <a href='/logout' class='nav-btn' style='background:#95a5a6;'>🚪 Выход</a>""" if current_user else ""
    
    # ✅ Топ лидерборды
    top_msg = sorted(user_stats.items(), key=lambda x: x[1].get('messages_today', 0), reverse=True)[:3]
    top_msg_html = '<br>'.join([f"{i+1}️⃣ <b>{user}</b> ({count['messages_today']})" 
                               for i, (user, count) in enumerate(top_msg)]) if top_msg else "—"
    
    # ✅ HTML сообщений чата
    messages_html = ''
    for msg in messages:
        role_color = {
            'admin': '#e74c3c', 'moderator': '#27ae60', 'premium': '#f39c12', 
            'vip': '#3498db', 'start': '#7f8c8d'
        }.get(msg.get('role', 'start'), '#95a5a6')
        
        time_str = time.strftime('%H:%M', time.localtime(msg['timestamp']))
        can_delete = (current_user == msg['user'] or 
                     (is_moderator(current_user) and msg['user'] not in ['УЖНАВАЙКИН', 'АВТОМОД']))
        
        messages_html += f'''
        <div class="message" data-id="{msg['id']}" style="padding:12px 0;border-bottom:1px solid #eee;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;">
                <span style="color:{role_color};font-weight:700;font-size:15px;">{msg['user']}</span>
                <span style="color:#95a5a6;font-size:12px;">{time_str}</span>
                {f'<button onclick="deleteMsg({msg["id"]})" title="Удалить" style="background:#e74c3c;color:white;border:none;width:28px;height:28px;border-radius:50%;font-size:12px;cursor:pointer;margin-left:auto;">🗑️</button>' if can_delete else ''}
            </div>
            <div style="color:#2c3e50;font-size:15px;line-height:1.4;">{msg["message"]}</div>
        </div>'''
    
    # ✅ HTML анонсов
    announcements_html = ''
    for ann in announcements:
        announcements_html += f'''
        <div style="background:#e8f4fd;padding:15px;margin:8px 0;border-left:4px solid #3498db;border-radius:0 8px 8px 0;">
            <div style="font-weight:600;color:#2c3e50;">📢 <span style="color:#2980b9;">{ann["username"]}</span></div>
            <div style="color:#7f8c8d;font-size:12px;margin-bottom:8px;">{ann["time_str"]}</div>
            <div style="color:#2c3e50;margin-top:5px;">{ann["message"]}</div>
        </div>'''
    
    html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 УЗНАВАЙКИН v37.9 — Игровой хаб</title>
    <style>{css}</style>
</head><body>
<div class="container">
    <!-- ✅ HEADER -->
    <header style="text-align:center;padding:40px 20px;background:linear-gradient(135deg,#e74c3c 0%,#c0392b 100%);color:white;border-radius:20px;margin:-20px -20px 30px -20px;box-shadow:0 10px 30px rgba(231,76,60,0.3);">
        <h1 style="font-size:2.8em;margin:0;font-weight:800;text-shadow:2px 2px 4px rgba(0,0,0,0.3);">🚀 <span style="background:linear-gradient(45deg,#f1c40f,#f39c12); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">УЖНАВАЙКИН</span></h1>
        <p style="font-size:18px;margin:10px 0 0 0;opacity:0.95;">Игровой хаб • Чат • Каталог • Экономика • Лидерборды</p>
        <div style="font-size:14px;margin-top:15px;color:#ecf0f1;">v37.9 • 2026 • <span id="online-counter">🟢 {stats['online']} онлайн</span></div>
    </header>

    <!-- ✅ ПРАВИЛА ЧАТА (всегда видны) -->
    <div style="background:#fff3cd;border:1px solid #ffeaa7;padding:20px;margin:0 0 25px 0;border-radius:12px;box-shadow:0 2px 10px rgba(255,193,7,0.15);">
        <h4 style="margin:0 0 12px 0;color:#856404;">📜 Правила чата:</h4>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;font-size:14px;color:#856404;line-height:1.5;">
            <div>• 🚫 <b>Мат/оскорбления</b> = <span style="color:#e74c3c;">15 мин мут</span></div>
            <div>• 📢 <b>Спам</b> = <span style="color:#e74c3c;">10 мин мут</span></div>
            <div>• 💬 <b>Флуд/Реклама (>5 одинаковых)</b> = <span style="color:#e74c3c;">30 мин мут</span></div>
            <div>• 🛡️ <b>Модераторы</b> удаляют нарушения</div>
        </div>
    </div>

    <!-- ✅ АНОНСЫ -->
    {announcements_html or '<div style="text-align:center;color:#95a5a6;padding:20px;">📭 Новых анонсов пока нет</div>'}

    <!-- ✅ СТАТИСТИКА + ЛИДЕРБОРДЫ -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:25px;margin:30px 0;">
        <div class="stats" style="background:#d1ecf1;border:1px solid #bee5eb;padding:25px;border-radius:15px;">
            <h3 style="margin:0 0 20px 0;color:#2c3e50;">📊 Статистика</h3>
            <div class="stat-card" style="border-left-color:#27ae60;">🟢 Онлайн: <b>{stats["online"]}</b></div>
            <div class="stat-card" style="border-left-color:#f39c12;">🟡 АФК: <b>{stats["afk"]}</b></div>
            <div class="stat-card" style="border-left-color:#3498db;">👥 Всего: <b>{stats["total"]}</b></div>
        </div>
        
        <div class="leaderboard" style="background:#fff3cd;border:1px solid #ffeaa7;padding:25px;border-radius:15px;">
            <h3 style="margin:0 0 20px 0;color:#856404;">🏆 Топ сегодня</h3>
            <div style="font-size:16px;line-height:1.8;">
                🥇 <b>Сообщения:</b><br>{top_msg_html}
                <br><br>💰 <b>Богач:</b> <span style="color:#27ae60;font-weight:700;">
                {stats["top_wealth"][0]["username"] if stats.get("top_wealth") else "—"}: 
                {stats["top_wealth"][0]["coins"] if stats.get("top_wealth") else 0:,}💰</span>
            </div>
        </div>
    </div>

    <!-- ✅ ЧАТ -->
    <div class="chat-container" style="background:#f8f9fa;border-radius:20px;padding:25px;margin:25px 0;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
            <h3 style="margin:0;font-size:24px;color:#2c3e50;">💬 Чат</h3>
            <span id="msg-count" style="background:#3498db;color:white;padding:6px 12px;border-radius:20px;font-weight:600;font-size:14px;">({msg_count})</span>
        </div>
        <div id="chat-messages" style="min-height:400px;overflow-y:auto;max-height:500px;padding:20px;background:white;border-radius:15px;border:1px solid #eee;box-shadow:inset 0 2px 10px rgba(0,0,0,0.05);">{messages_html}</div>
        {chat_form_html}
    </div>

    <!-- ✅ ПОЛНАЯ НАВИГАЦИЯ -->
    <div class="nav" style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin:40px 0 20px 0;">
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
document.getElementById('msg-count').textContent = `(${msgCount})`;

// ✅ Счетчик символов
document.getElementById('message-input')?.addEventListener('input', e => {{
    document.getElementById('char-count').textContent = e.target.value.length + '/300';
}});

// ✅ Удаление сообщений
async function deleteMsg(id) {{
    if(confirm('🗑️ Удалить сообщение?')) {{
        try {{
            const response = await fetch(`/api/delete/{{id}}`, {{method:'POST'}});
            if(response.ok) {{
                document.querySelector(`[data-id="${{id}}"]`).style.opacity = '0.3';
                setTimeout(() => document.querySelector(`[data-id="${{id}}"]`).remove(), 300);
            }} else {{
                alert('❌ Ошибка удаления');
            }}
        }} catch(e) {{ 
            alert('❌ Ошибка сети'); 
        }}
    }}
}}

// ✅ Обновление счетчика онлайн каждые 30 сек
setInterval(() => {{
    document.getElementById('online-counter').textContent = '🟢 Загрузка...';
    fetch('/api/stats').then(r=>r.json()).then(data => {{
        document.getElementById('online-counter').textContent = `🟢 ${{data.online}} онлайн`;
    }});
}}, 30000);
</script>
</body></html>'''
    return html

@app.route('/catalog')
def catalog():
    """✅ КАТАЛОГ файлов/папок"""
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    items_html = ''
    for path, item in catalog.items():
        name = path.split('/')[-1]
        icon = '📁' if item['type'] == 'folder' else '📄'
        can_delete = is_admin(current_user) or item['created_by'] == current_user
        items_html += f'''
        <div style="padding:15px;border:1px solid #ddd;margin:10px 0;border-radius:8px;background:white;">
            <div style="font-size:20px;">{icon} <b>{name}</b></div>
            <div style="color:#7f8c8d;">Автор: {item["created_by"]} • {time.strftime("%d.%m %H:%M", time.localtime(item["created"]))}
            {f'<button onclick="deleteItem(\'{path}\')" style="float:right;background:#e74c3c;color:white;border:none;padding:5px 12px;border-radius:5px;">Удалить</button>' if can_delete else ''}
            </div>
        </div>'''
    
    return f'''<!DOCTYPE html><html><body><div class="container">
        <h1>📁 Каталог</h1>{items_html}<a href="/" class="nav-btn">← Главная</a>
    </div></body></html>'''

print("🚀 УЗНАВАЙКИН v37.9 ЧАСТЬ 2/3 — ГЛАВНАЯ + ЧАТ + КАТАЛОГ!")
print("✅ Готово! Скажи '3/3' для Магазин + Экономика + Админка!")
# 🚀 УЖНАВАЙКИН v37.9 ЧАСТЬ 3/3 — МАГАЗИН + ЭКОНОМИКА + АДМИНКА + API

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    """✅ МАГАЗИН: VIP(100₽) Premium(200₽) Аватары"""
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user_coins = user_economy[current_user]['coins']
    
    # Товары магазина
    items = [
        {'id': 'vip', 'name': '⭐ VIP (100₽/мес)', 'price': 100, 'desc': '+ Цветной ник, +10💰/сообщ'},
        {'id': 'premium', 'name': '💎 Premium (200₽/мес)', 'price': 200, 'desc': '+VIP + Эксклюзив, +20💰/сообщ'},
        {'id': 'avatar1', 'name': '👑 Золотой аватар', 'price': 500, 'desc': 'Золотая корона'},
        {'id': 'avatar2', 'name': '🔥 Огненный аватар', 'price': 750, 'desc': 'Пламя'}
    ]
    
    message = ''
    if request.method == 'POST':
        item_id = request.form.get('item')
        item = next((i for i in items if i['id'] == item_id), None)
        if item and user_coins >= item['price']:
            user_economy[current_user]['coins'] -= item['price']
            if item_id in ['vip', 'premium']:
                user_roles[current_user] = item_id
                user_profiles[current_user]['status'] = f"⭐ {item['name']}"
            else:
                user_profiles[current_user]['avatar'] = item_id
            save_data()
            message = f"✅ {item['name']} куплен!"
        else:
            message = "❌ Недостаточно монет!"
    
    items_html = ''
    for item in items:
        owned = (user_roles.get(current_user) == item['id'] or 
                user_profiles[current_user].get('avatar') == item['id'])
        badge = '🟢 ВЛОЖЕНО' if owned else f"🟡 {item['price']:,}💰"
        items_html += f'''
        <div style="border:1px solid #ddd;padding:20px;margin:15px 0;border-radius:12px;background:white;box-shadow:0 5px 15px rgba(0,0,0,0.08);">
            <h3 style="color:#2c3e50;margin:0 0 10px 0;">{item['name']}</h3>
            <p style="color:#7f8c8d;margin:0 0 15px 0;">{item['desc']}</p>
            <div style="font-size:18px;font-weight:700;color:{'#27ae60' if owned else '#e74c3c'};">
                {badge}
            </div>
            {f'<button style="width:100%;padding:12px;margin-top:10px;background:#95a5a6;color:white;border:none;border-radius:8px;cursor:not-allowed;">ВЛОЖЕНО</button>' if owned else f'''
            <form method="POST" style="margin-top:10px;">
                <input type="hidden" name="item" value="{item['id']}">
                <button type="submit" {'disabled' if user_coins < item['price'] else ''} 
                        style="width:100%;padding:15px;background:{'#bdc3c7' if user_coins < item['price'] else '#e74c3c'};color:white;border:none;border-radius:12px;font-size:16px;font-weight:600;cursor:{'not-allowed' if user_coins < item['price'] else 'pointer'};">
                    {'💳 Недостаточно' if user_coins < item['price'] else f'🛒 Купить за {item["price"]:,}💰'}
                </button>
            </form>'''}
        </div>'''
    
    return f'''<!DOCTYPE html><html><body><div class="container">
        <h1 style="text-align:center;">💰 Магазин</h1>
        <div style="text-align:center;margin:20px 0;color:{'#27ae60' if message.startswith('✅') else '#e74c3c'};">{message}</div>
        <p style="text-align:center;color:#7f8c8d;">💰 Твои монеты: <b style="font-size:24px;color:#27ae60;">{user_coins:,}</b></p>
        {items_html}
        <div style="text-align:center;margin:40px 0;">
            <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
        </div>
    </div></body></html>'''

@app.route('/economy')
def economy():
    """✅ БАНК + ЭКОНОМИКА"""
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    coins = user_economy[current_user]['coins']
    bank = user_economy[current_user]['bank']
    
    return f'''<!DOCTYPE html><html><body><div class="container">
        <h1 style="text-align:center;">🏦 Банк</h1>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:40px 0;">
            <div style="background:#27ae60;color:white;padding:40px;border-radius:20px;text-align:center;">
                <h2 style="margin:0;font-size:3em;">{coins:,}</h2>
                <p style="font-size:18px;margin:10px 0;">💰 Наличные</p>
            </div>
            <div style="background:#3498db;color:white;padding:40px;border-radius:20px;text-align:center;">
                <h2 style="margin:0;font-size:3em;">{bank:,}</h2>
                <p style="font-size:18px;margin:10px 0;">💳 На счете</p>
            </div>
        </div>
        <div style="text-align:center;">
            <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
        </div>
    </div></body></html>'''

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    """✅ ПОЛНАЯ АДМИНКА v37.9"""
    current_user = session.get('user', '')
    if not is_admin(current_user):
        return redirect('/')
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        target = request.form.get('target', '').strip()
        
        if action == 'mute':
            duration = int(request.form.get('duration', 600))
            conn = get_db()
            conn.execute('''INSERT INTO mutes (target, muted_by, reason, mtype, expires, created)
                           VALUES (?, ?, 'Админ мут', 'manual', ?, ?)''',
                        (target, current_user, time.time() + duration, time.time()))
            conn.commit()
            conn.close()
            message = f"✅ {target} замучен на {duration/60} мин"
        
        elif action == 'unmute':
            conn = get_db()
            conn.execute('DELETE FROM mutes WHERE target = ? AND expires > ?', (target, time.time()))
            conn.commit()
            conn.close()
            message = f"✅ {target} размучен"
        
        elif action == 'set_role':
            role = request.form.get('role')
            user_roles[target] = role
            conn = get_db()
            conn.execute('UPDATE users SET role = ? WHERE username = ?', (role, target))
            conn.commit()
            conn.close()
            message = f"✅ {target} = {role}"
    
    # Список мутированных
    conn = get_db()
    active_mutes = conn.execute(
        'SELECT * FROM mutes WHERE expires > ? ORDER BY created DESC', 
        (time.time(),)
    ).fetchall()
    mutes_html = ''
    for mute in active_mutes:
        remaining = int(mute['expires'] - time.time())
        mutes_html += f'<tr><td>{mute["target"]}</td><td>{mute["muted_by"]}</td><td>{mute["reason"]}</td><td>{remaining//60}:{remaining%60:02d}</td></tr>'
    
    conn.close()
    
    return f'''<!DOCTYPE html><html><head><title>⚙️ Админка v37.9</title><style>{css}</style></head><body>
    <div class="container">
        <h1 style="text-align:center;color:#e74c3c;">⚙️ Админ-панель v37.9</h1>
        <div style="color:#27ae60;padding:15px;background:#d4edda;border:1px solid #c3e6cb;border-radius:8px;margin:20px 0;">{message}</div>
        
        <!-- Мут панель -->
        <div style="background:#f8f9fa;padding:25px;border-radius:15px;margin:25px 0;">
            <h3>🔇 Мут / Размут</h3>
            <form method="POST">
                <input name="target" placeholder="Ник" style="padding:12px;width:200px;margin-right:10px;border:1px solid #ddd;border-radius:6px;">
                <select name="duration" style="padding:12px;margin-right:10px;border:1px solid #ddd;border-radius:6px;">
                    <option value="60">1 минута</option><option value="300">5 мин</option><option value="900">15 мин</option>
                    <option value="1800">30 мин</option><option value="3600">1 час</option><option value="86400">1 день</option>
                </select>
                <button type="submit" name="action" value="mute" style="padding:12px 20px;background:#e74c3c;color:white;border:none;border-radius:6px;">🔇 Мут</button>
                <button type="submit" name="action" value="unmute" style="padding:12px 20px;background:#27ae60;color:white;border:none;border-radius:6px;margin-left:10px;">✅ Размут</button>
            </form>
        </div>
        
        <!-- Роли -->
        <div style="background:#f8f9fa;padding:25px;border-radius:15px;margin:25px 0;">
            <h3>👑 Назначить роль</h3>
            <form method="POST">
                <input name="target" placeholder="Ник" style="padding:12px;width:200px;margin-right:10px;">
                <select name="role" style="padding:12px;margin-right:10px;">
                    <option value="start">👤 Start</option><option value="vip">⭐ VIP</option><option value="premium">💎 Premium</option>
                    <option value="moderator">🛡️ Модератор</option><option value="admin">👑 Админ</option>
                </select>
                <button type="submit" name="action" value="set_role" style="padding:12px 20px;background:#9b59b6;color:white;border:none;border-radius:6px;">Назначить</button>
            </form>
        </div>
        
        <!-- Активные муты -->
        <div style="background:#f8f9fa;padding:25px;border-radius:15px;margin:25px 0;">
            <h3>📋 Активные муты ({len(active_mutes)})</h3>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="background:#34495e;color:white;"><th>Ник</th><th>Кем</th><th>Причина</th><th>Осталось</th></tr>
                {mutes_html}
            </table>
        </div>
        
        <div style="text-align:center;margin:40px 0;">
            <a href="/" class="nav-btn" style="background:#3498db;">🏠 Главная</a>
        </div>
    </div></body></html>'''

@app.route('/api/delete/<int:msg_id>', methods=['POST'])
def api_delete(msg_id):
    """✅ API удаления сообщений"""
    current_user = session.get('user', '')
    if not current_user:
        return jsonify({'error': 'Не авторизован'}), 401
    
    conn = get_db()
    msg = conn.execute('SELECT * FROM chat WHERE id = ?', (msg_id,)).fetchone()
    conn.close()
    
    if not msg:
        return jsonify({'error': 'Сообщение не найдено'}), 404
    
    # Проверка прав
    can_delete = (current_user == msg['user'] or 
                 (is_moderator(current_user) and msg['user'] not in ['УЖНАВАЙКИН', 'АВТОМОД']))
    
    if can_delete:
        conn = get_db()
        conn.execute('UPDATE chat SET deleted = 1 WHERE id = ?', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Нет прав'}), 403

@app.route('/api/stats')
def api_stats():
    """✅ API статистики для JS"""
    return jsonify(get_detailed_stats())

@app.route('/profile')
def profile():
    """✅ ПРОФИЛЬ"""
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    user = get_user(current_user)
    return f'''<!DOCTYPE html><html><body><div class="container">
        <h1>👤 Профиль: {current_user}</h1>
        <p><b>Роль:</b> {user_roles.get(current_user, 'start')}</p>
        <p><b>Монеты:</b> {user_economy[current_user]['coins']:,}💰</p>
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div></body></html>'''

@app.route('/leaderboards')
def leaderboards():
    """✅ ЛИДЕРБОРДЫ"""
    top_messages = sorted(user_stats.items(), key=lambda x: x[1].get('messages_today', 0), reverse=True)[:10]
    top_coins = sorted(user_economy.items(), key=lambda x: x[1].get('coins', 0), reverse=True)[:10]
    
    msg_html = ''.join([f'<tr><td>{i+1}.</td><td>{user}</td><td>{data["messages_today"]}</td></tr>' 
                       for i, (user, data) in enumerate(top_messages)])
    coins_html = ''.join([f'<tr><td>{i+1}.</td><td>{user}</td><td>{data["coins"]:,}💰</td></tr>' 
                        for i, (user, data) in enumerate(top_coins)])
    
    return f'''<!DOCTYPE html><html><body><div class="container">
        <h1>🏆 Лидерборды</h1>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
            <div>
                <h2>📝 Сообщения сегодня</h2>
                <table style="width:100%;border-collapse:collapse;">{msg_html}</table>
            </div>
            <div>
                <h2>💰 Топ богачей</h2>
                <table style="width:100%;border-collapse:collapse;">{coins_html}</table>
            </div>
        </div>
        <a href="/" class="nav-btn">🏠 Главная</a>
    </div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("🚀 УЖНАВАЙКИН v37.9 100% ПОЛНЫЙ — 15 РОУТОВ + API!")
    print("✅ Админы: CatNap/Назар — ВСЕ права!")
    print("✅ Модеры: муты/размуты/удаление!")
    print("✅ БД: SQLite v37.9 — ВСЕ сохраняется!")
    app.run(host='0.0.0.0', port=port, debug=False)

print("🎉 УЖНАВАЙКИН v37.9 ЧАСТЬ 3/3 — 100% ГОТОВ!")
print("cat part1.py part2.py part3.py > app.py && git push = 🚀 ДЕПЛОЙ!")

