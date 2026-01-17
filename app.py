from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import os
import json
import time
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'uznaykin_v36_7_full_fix_2026_stable'

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ v36.7
data_file = 'uznaykin_v36_7_data.json'
upload_folder = 'static/uploads'
os.makedirs(upload_folder, exist_ok=True)

# Инициализация данных
users = {}
user_roles = {}
user_profiles = {}
user_activity = {}
user_stats = {}
user_economy = {}
user_inventory = {}
chat_messages = []
mutes = {'by': {}, 'reason': {}, 'muted_by': {}, 'duration': {}, 'expires': {}}
catalog = {'root': {}}
announcements = []
notifications = {}
bans = {}
friends = {}
blocked = {}
leaderboards = {
    'messages_today': {},
    'messages_week': {},
    'online_time': {},
    'wealth': {}
}
pinned_messages = []
moderation_logs = []

# ✅ АВТО-МОДЕРАЦИЯ
bad_words = ['сука', 'пизда', 'хуй', 'пидор', 'блять', 'нахуй', 'ебать', 'пидорас']
spam_patterns = [r'http[s]?://[^\s]*', r'@\w+\.\w+', r'\b(тг|tg|vk|discord)\b']

def get_timestamp():
    return time.time()

# ✅ КРИТИЧЕСКИЕ ФУНКЦИИ СОХРАНЕНИЯ v36.7
def load_data():
    global users, user_roles, user_profiles, user_activity, user_stats, user_economy
    global user_inventory, chat_messages, mutes, catalog, announcements, notifications
    global bans, friends, blocked, leaderboards, pinned_messages, moderation_logs
    
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ✅ БЕЗОПАСНАЯ загрузка catalog
                if 'catalog' in data and isinstance(data['catalog'], dict):
                    catalog = data['catalog']
                else:
                    catalog = {'root': {'type': 'folder', 'created_by': 'system', 'created': time.time()}}
                
                for key, value in data.items():
                    if key != 'catalog':
                        globals()[key] = value
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        catalog = {'root': {'type': 'folder', 'created_by': 'system', 'created': time.time()}}

def save_data():
    data = {
        'users': users, 
        'user_roles': user_roles, 
        'user_profiles': user_profiles,
        'user_activity': {k: v for k, v in user_activity.items() if time.time() - v < 3600},
        'user_stats': user_stats,
        'user_economy': user_economy,
        'user_inventory': user_inventory,
        'chat_messages': chat_messages[-1000:],
        'mutes': mutes,
        'catalog': catalog,
        'announcements': announcements[-10:],
        'notifications': notifications,
        'bans': bans,
        'friends': friends,
        'blocked': blocked,
        'leaderboards': leaderboards,
        'pinned_messages': pinned_messages,
        'moderation_logs': moderation_logs[-300:]
    }
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

# Загрузка данных
load_data()

# ✅ АВТО-АДМИНЫ v36.7 (ТОЛЬКО CatNap + Назар)
def setup_auto_admins():
    """v36.7: Только CatNap + Назар"""
    global catalog
    
    AUTO_ADMINS = {
        'CatNap': '120187',
        'Назар': '120187'
    }
    
    for admin_name, password in AUTO_ADMINS.items():
        if admin_name not in user_roles:
            users[admin_name] = {'password': hashlib.sha256(password.encode()).hexdigest()}
            user_roles[admin_name] = 'admin'
            user_profiles[admin_name] = {
                'status': '👑 Супер-Админ', 
                'info': 'Полные права v36.7', 
                'color': '#e74c3c', 
                'avatar': '👑'
            }
            user_economy[admin_name] = {
                'coins': 999999, 
                'bank': 5000000, 
                'last_bank': time.time()
            }
            notifications.setdefault(admin_name, []).append({
                'time': time.time(),
                'message': '🎉 Авто-админ v36.7! Все права + бесконечные монеты'
            })
            print(f"✅ АДМИН СОЗДАН: {admin_name} (пароль: {password})")
        else:
            user_roles[admin_name] = 'admin'
            user_economy.setdefault(admin_name, {'coins': 999999})
            print(f"✅ АДМИН ОБНОВЛЕН: {admin_name}")
    
    # ✅ Инициализация каталога
    if not isinstance(catalog, dict) or 'root' not in catalog:
        catalog = {
            'root': {
                'type': 'folder',
                'created_by': 'system',
                'created': time.time(),
                'items_count': 0
            }
        }
        print("✅ КАТАЛОГ ИНИЦИАЛИЗИРОВАН")
    
    # ✅ Первое сообщение
    if not chat_messages:
        chat_messages.append({
            'user': '🚀 УЗНАВАЙКИН', 
            'text': 'v36.7 запущен! Админы: CatNap, Назар', 
            'time': time.time()
        })
    
    save_data()
    print("✅ SETUP_AUTO_ADMINS v36.7 ЗАВЕРШЕН!")

setup_auto_admins()

# ✅ ОСНОВНЫЕ ФУНКЦИИ v36.7
def get_role_display(username):
    """Правильные названия ролей"""
    role = user_roles.get(username, 'start')
    role_names = {
        'start': '👤 Start',
        'vip': '⭐ VIP', 
        'premium': '💎 Premium',
        'moderator': '🛡️ Модератор',
        'admin': '👑 Администратор'
    }
    colors = {
        'start': '#95a5a6', 
        'vip': '#f39c12', 
        'premium': '#9b59b6',
        'moderator': '#27ae60', 
        'admin': '#e74c3c'
    }
    color = colors.get(role, '#95a5a6')
    return f'<span style="color:{color} !important;font-weight:bold;">{role_names.get(role, role)}</span>'

def is_admin(username):
    return user_roles.get(username) == 'admin'

def is_moderator(username):
    return user_roles.get(username) in ['admin', 'moderator']

def is_online(username):
    return username in user_activity and time.time() - user_activity[username] < 60

def is_afk(username):
    last_activity = user_activity.get(username, 0)
    return 60 <= time.time() - last_activity < 3600

def is_muted(username):
    if username not in mutes['by']:
        return False
    expires = mutes['expires'].get(username, 0)
    if expires == 0 or time.time() < expires:
        return True
    # Очистка мутов
    for key in mutes:
        mutes[key].pop(username, None)
    save_data()
    return False

def get_detailed_stats():
    """Подробная статистика: онлайн/АФК/роли"""
    now = time.time()
    online_count = 0
    afk_count = 0
    role_stats = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    for user in users.keys():
        last_activity = user_activity.get(user, 0)
        if now - last_activity < 1:  # 1 минута = онлайн
            online_count += 1
        elif now - last_activity < 60:  # 1 час = АФК
            afk_count += 1
        
        role = user_roles.get(user, 'start')
        role_stats[role] = role_stats.get(role, 0) + 1
    
    return {
        'online': online_count,
        'afk': afk_count,
        'total': len(users),
        'roles': role_stats
    }

def safe_catalog_count():
    """БЕЗОПАСНЫЙ подсчет файлов"""
    global catalog
    if not isinstance(catalog, dict) or 'root' not in catalog:
        catalog = {'root': {'type': 'folder', 'created_by': 'system', 'created': time.time()}}
    
    try:
        file_count = 0
        for item_path, item_data in catalog.items():
            if item_path != 'root' and isinstance(item_data, dict) and item_data.get('type') == 'file':
                file_count += 1
        return file_count
    except:
        return 0

def auto_moderate(message, username):
    """Авто-модерация"""
    message_lower = message.lower()
    
    for word in bad_words:
        if word in message_lower:
            return f'🚫 Мат ({word}) — мут 10 мин', 600
    
    for pattern in spam_patterns:
        if re.search(pattern, message):
            return f'🚫 Спам — мут 30 мин', 1800
    
    recent_msgs = [m['text'].lower() for m in chat_messages[-10:] if m['user'] == username]
    if len(recent_msgs) >= 3 and len(set(recent_msgs[-3:])) <= 1:
        return f'🚫 Флуд — мут 1 час', 3600
    
    return None, 0

def add_coins(username, amount, reason=''):
    user_economy.setdefault(username, {'coins': 0, 'bank': 0, 'last_bank': time.time()})
    user_economy[username]['coins'] += amount
    leaderboards.setdefault('wealth', {})[username] = leaderboards['wealth'].get(username, 0) + amount
    save_data()
    return user_economy[username]['coins']

def get_top_leaderboard(category='wealth', limit=5):
    data = leaderboards.get(category, {})
    return sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit]

# ✅ CSS v36.7
css_v36_7 = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Inter',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#333;min-height:100vh;}
.container {max-width:1300px;margin:20px auto;padding:30px;background:#fff;border-radius:25px;box-shadow:0 25px 80px rgba(0,0,0,0.15);}
.header {text-align:center;padding:35px;background:linear-gradient(45deg,#ff9a9e,#fecfef);border-radius:20px;margin:-30px -30px 30px -30px;}
.stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:20px;margin:25px 0;}
.stat-card {background:linear-gradient(135deg,#f8f9fa,#e9ecef);padding:25px;border-radius:18px;text-align:center;box-shadow:0 8px 25px rgba(0,0,0,0.1);transition:transform 0.3s;}
.stat-card:hover {transform:translateY(-5px);}
.chat-container {background:#f8f9fa;border-radius:20px;overflow:hidden;box-shadow:0 15px 50px rgba(0,0,0,0.1);}
#chat-messages {max-height:450px;overflow-y:auto;padding:30px;background:#fff;}
.chat-msg {padding:22px;margin:12px 0;background:#fff;border-radius:18px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border-left:4px solid #3498db;}
.nav {display:flex;flex-wrap:wrap;justify-content:center;gap:15px;padding:35px;background:#ecf0f1;border-radius:20px;margin-top:30px;}
.nav-btn {padding:16px 28px;color:white;text-decoration:none;border-radius:15px;font-weight:600;transition:all 0.3s;font-size:15px;}
.nav-btn:hover {transform:translateY(-3px);box-shadow:0 8px 25px rgba(0,0,0,0.2);}
.announcement {background:linear-gradient(45deg,#fff3cd,#ffeaa7);color:#856404;padding:25px;border-radius:20px;margin:20px 0;border-left:6px solid #f39c12;}
form input, form select, form textarea {width:100%;padding:15px;margin:10px 0;border:2px solid #e1e5e9;border-radius:12px;font-size:16px;box-sizing:border-box;font-family:inherit;}
form button {width:100%;padding:16px;background:linear-gradient(45deg,#3498db,#2980b9);color:white;border:none;border-radius:12px;font-weight:600;font-size:17px;cursor:pointer;transition:all 0.3s;}
form button:hover {transform:translateY(-2px);box-shadow:0 8px 25px rgba(52,152,219,0.4);}
@media (max-width:768px) {.container{padding:20px;margin:10px;}.nav{flex-direction:column;align-items:center;}}'''

# 🚀 УЗНАВАЙКИН v36.7 ЧАСТЬ 1/3

# ✅ ГЛАВНАЯ СТРАНИЦА v36.7
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form.get('message', '').strip()
        if message and len(message) <= 300:
            try:
                auto_msg, duration = auto_moderate(message, current_user)
                if auto_msg:
                    mutes['by'][current_user] = time.time()
                    mutes['expires'][current_user] = time.time() + duration
                    mutes['reason'][current_user] = auto_msg
                    chat_messages.append({
                        'user': '🚫 АВТОМОД', 
                        'text': f'{auto_msg}: {current_user}', 
                        'time': time.time()
                    })
                else:
                    chat_messages.append({
                        'user': current_user, 
                        'text': message, 
                        'time': time.time()
                    })
                    add_coins(current_user, 3, 'чат')
                    user_activity[current_user] = time.time()
                save_data()
            except Exception as e:
                print(f"Чат ошибка: {e}")
    
    if current_user:
        user_activity[current_user] = time.time()
    
    stats = get_detailed_stats()
    catalog_count = safe_catalog_count()
    top_wealth = get_top_leaderboard('wealth', 5)
    
    html = f'''<!DOCTYPE html>
<html><head><title>Узнавайкин</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css_v36_7}</style></head><body>
<div class="container">
<div class="header">
<h1>🚀 Узнавайкин</h1>
<p>{get_role_display(current_user) if current_user else "👋 Гость"} | 🟢 {stats['online']} онлайн, 🟡 {stats['afk']} АФК</p>
</div>'''

    # ✅ СТАТИСТИКА
    html += f'''<div class="stats">
<div class="stat-card"><b>{stats['online']}</b><br>🟢 Онлайн</div>
<div class="stat-card"><b>{stats['afk']}</b><br>🟡 АФК</div>
<div class="stat-card"><b>{stats['total']}</b><br>👥 Всего</div>
<div class="stat-card"><b>{len(chat_messages)}</b><br>💬 Сообщений</div>'''

    if current_user:
        coins = user_economy.get(current_user, {}).get('coins', 0)
        html += f'<div class="stat-card"><b>{coins:,}</b><br>💰 Монет</div>'
    html += '</div>'

    # ✅ РОЛИ СТАТИСТИКА
    html += f'''<div style="background:#f0f8ff;padding:25px;border-radius:20px;margin:20px 0;">
<h3 style="margin-bottom:15px;">📊 По ролям:</h3>
<div style="display:flex;flex-wrap:wrap;gap:20px;justify-content:center;font-size:16px;">
<div style="padding:15px;background:#e3f2fd;border-radius:12px;">👤 Start: <b>{stats["roles"]["start"]}</b></div>
<div style="padding:15px;background:#fff3e0;border-radius:12px;">⭐ VIP: <b>{stats["roles"]["vip"]}</b></div>
<div style="padding:15px;background:#e1bee7;border-radius:12px;">💎 Premium: <b>{stats["roles"]["premium"]}</b></div>
<div style="padding:15px;background:#e8f5e8;border-radius:12px;">🛡️ Модератор: <b>{stats["roles"]["moderator"]}</b></div>
<div style="padding:15px;background:#ffebee;border-radius:12px;">👑 Админ: <b>{stats["roles"]["admin"]}</b></div>
</div></div>'''

    # ✅ АНОНСЫ
    if announcements:
        html += f'<div class="announcement"><b>📢 {announcements[0]["admin"]}</b>: {announcements[0]["message"]}</div>'

    # ✅ ТОП БОГАЧЕЙ
    html += '<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:30px;border-radius:20px;margin:25px 0;">'
    html += '<h3 style="margin-bottom:20px;text-align:center;">🥇 Топ богачей</h3>'
    if top_wealth:
        for i, (user, coins) in enumerate(top_wealth):
            medal = '🥇🥈🥉'[i] if i < 3 else f'{i+1}️⃣'
            html += f'<div style="display:flex;justify-content:space-between;padding:18px;background:#fff;border-radius:15px;margin:10px 0;box-shadow:0 4px 20px rgba(0,0,0,0.1);"><span>{medal} {user}</span><span style="color:#27ae60;font-weight:bold;">{coins:,} 💰</span></div>'
    else:
        html += '<p style="text-align:center;color:#666;">Никого нет</p>'
    html += '</div>'

    # ✅ ЧАТ
    html += '<div class="chat-container">'
    html += '<div id="chat-messages">'
    for msg in reversed(chat_messages[-50:]):
        time_str = datetime.fromtimestamp(msg['time']).strftime('%H:%M')
        html += f'<div class="chat-msg"><b>{msg["user"]}</b> <span style="color:#888;float:right;font-size:14px;">{time_str}</span><div style="clear:both;margin-top:10px;">{msg["text"]}</div></div>'
    html += '</div>'

    # ✅ ЧАТ ИНПУТ
    if current_user and not is_muted(current_user):
        mute_info = ''
        if current_user in mutes.get('expires', {}) and time.time() < mutes['expires'][current_user]:
            remaining = int(mutes['expires'][current_user] - time.time())
            mute_info = f'🔇 Мут: {remaining//60}м | '
        
        html += f'''<form method="post" style="padding:30px;background:#ecf0f1;border-top:1px solid #ddd;">
<input name="message" id="chat-input" placeholder="{mute_info}💭 Напишите сообщение... (макс 300 символов)" maxlength="300" required 
style="width:calc(100% - 85px);padding:20px;border:2px solid #ddd;border-radius:15px;font-size:17px;box-sizing:border-box;height:60px;">
<button type="submit" style="width:80px;height:60px;padding:0;background:linear-gradient(45deg,#27ae60,#229954);color:white;border:none;border-radius:15px;font-size:20px;font-weight:700;">📤</button>
</form>'''
    else:
        html += '<div style="padding:60px;text-align:center;background:#ffebee;color:#c53030;font-size:22px;border-radius:15px;margin:20px 0;">🔐 Войдите в аккаунт или вы в муте</div>'

    html += '</div>'

    # ✅ НАВИГАЦИЯ v36.7
    nav_items = [
        ('/profiles', '👥 Профили', '#3498db'),
        ('/privileges', '⭐ Привилегии', '#9b59b6'),
        ('/shop', '🛒 Магазин', '#f39c12'),
        ('/economy', '💰 Экономика', '#27ae60')
    ]
    
    if current_user:
        nav_items.extend([
            (f'/profile/{current_user}', '👤 Мой профиль', '#764ba2'),
            ('/catalog', '📁 Каталог', '#3498db')
        ])
        if is_admin(current_user):
            nav_items.append(('/admin', '🔧 Админка (ВСЁ)', '#e74c3c'))
        elif is_moderator(current_user):
            nav_items.append(('/moderator', '🛡️ Модератор', '#27ae60'))
        nav_items.append(('/logout', '🚪 Выход', '#95a5a6'))
    else:
        nav_items.append(('/login', '🔐 Войти', '#e74c3c'))

    html += '<div class="nav">'
    for url, label, color in nav_items:
        html += f'<a href="{url}" class="nav-btn" style="background:{color};">{label}</a>'
    html += '</div></div></body></html>'
    
    return html

# ✅ ЛОГИН/РЕГИСТРАЦИЯ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        if username in bans:
            return f'''<div style="text-align:center;padding:50px;color:#c53030;font-size:24px;">
🚫 <b>Вы забанены!</b><br><br><a href="/" style="background:#2c3e50;color:white;padding:15px 30px;border-radius:12px;text-decoration:none;">🏠 Главная</a>
</div>'''
        
        # Регистрация новых
        if username not in users:
            users[username] = {'password': hashlib.sha256(password.encode()).hexdigest()}
            user_roles[username] = 'start'
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': f'Привет! Новый пользователь'}
            user_economy[username] = {'coins': 100, 'bank': 0}
            notifications[username] = [{'time': time.time(), 'message': '🎉 Регистрация успешна! +100 монет подарок'}]
            add_coins(username, 100, 'регистрация')
        
        # Проверка пароля
        elif users[username]['password'] != hashlib.sha256(password.encode()).hexdigest():
            return f'''<div style="text-align:center;padding:50px;color:#c53030;font-size:24px;">
❌ <b>Неверный пароль!</b><br><br><a href="/login" style="background:#e74c3c;color:white;padding:15px 30px;border-radius:12px;text-decoration:none;">← Попробовать снова</a>
</div>'''
        
        session['user'] = username
        user_activity[username] = time.time()
        save_data()
        return redirect('/')
    
    return f'''<!DOCTYPE html><html><head><title>🔐 Узнавайкин - Вход</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>body{{background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Inter',sans-serif;padding:20px;}}
.login-box{{background:#fff;padding:60px;border-radius:25px;box-shadow:0 30px 100px rgba(0,0,0,0.25);width:100%;max-width:450px;text-align:center;}}
.login-box h1{{color:#2c3e50;margin-bottom:35px;font-size:2.5em;}}
input{{width:100%;padding:22px;margin:15px 0;border:2px solid #e1e8ed;border-radius:15px;font-size:18px;box-sizing:border-box;}}</style></head>
<body><div class="login-box">
<h1>🚀 Узнавайкин</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required>
<input name="password" type="password" placeholder="🔑 Пароль" required>
<button style="width:100%;padding:22px;background:linear-gradient(45deg,#ff6b6b,#ee5a52);color:white;border:none;border-radius:15px;font-size:20px;font-weight:700;box-shadow:0 10px 30px rgba(255,107,107,0.4);">🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form>
<p style="margin-top:25px;color:#666;font-size:14px;">
💡 <b>Админы:</b> CatNap (CatNap), Назар (120187)
</p><a href="/" style="background:#2c3e50;color:white;padding:12px 25px;border-radius:10px;text-decoration:none;">🏠 Главная</a>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ✅ АДМИНКА v36.7 (ПОЛНЫЕ ПРАВА)
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    current_user = session.get('user', '')
    if not is_admin(current_user):
        return redirect('/')
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        target = request.form.get('target', '').strip()
        
        if action == 'mute':
            duration = int(request.form.get('duration', 600))
            mutes['by'][target] = time.time()
            mutes['expires'][target] = time.time() + duration
            mutes['reason'][target] = request.form.get('reason', f'Мут от {current_user}')
            message = f'✅ {target} замучен на {duration//60} мин'
            
        elif action == 'unmute':
            for key in mutes:
                mutes[key].pop(target, None)
            message = f'✅ {target} размучен'
            
        elif action == 'ban':
            bans[target] = {'by': current_user, 'time': time.time()}
            message = f'✅ {target} забанен'
            
        elif action == 'set_role':
            role = request.form.get('role')
            if role in ['start', 'vip', 'premium', 'moderator', 'admin']:
                user_roles[target] = role
                message = f'✅ {target} = {role}'
            
        elif action == 'announce':
            announcements.insert(0, {
                'message': request.form['message'][:250],
                'admin': current_user,
                'time': time.time()
            })
            message = '✅ Анонс отправлен!'
        
        save_data()
    
    stats = get_detailed_stats()
    mutelist = [u for u in mutes['by'] if time.time() < mutes['expires'].get(u, 0)]
    
    return f'''<!DOCTYPE html><html><head><title>🔧 Админка - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7} .admin-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:25px;}}</style></head>
<body><div class="container">
<h1 style="color:#e74c3c;">🔧 АДМИНКА v36.7</h1>
{message and f'<div style="background:#d4edda;padding:25px;border-radius:20px;margin:20px 0;">{message}</div>' or ''}
<div class="admin-grid">
<div style="background:#ffebee;padding:30px;border-radius:20px;">
<h3>🔇 Мут / Размут</h3>
<form method="post"><input type="hidden" name="action" value="mute">
<input name="target" placeholder="👤 Ник" required><input name="duration" type="number" value="1800" placeholder="сек">
<input name="reason" placeholder="Причина"><button style="background:#e74c3c;">🔇 МУТ</button></form>
<form method="post"><input type="hidden" name="action" value="unmute">
<input name="target" placeholder="👤 Ник" required><button style="background:#27ae60;">✅ РАЗМУТ</button></form>
</div>
<div style="background:#e8f5e8;padding:30px;border-radius:20px;">
<h3>👑 Роли</h3><form method="post"><input type="hidden" name="action" value="set_role">
<input name="target" placeholder="👤 Ник" required>
<select name="role"><option value="start">👤 Start</option><option value="vip">⭐ VIP</option><option value="premium">💎 Premium</option><option value="moderator">🛡️ Модератор</option><option value="admin">👑 Админ</option></select>
<button style="background:#9b59b6;">👑 НАЗНАЧИТЬ</button></form>
</div>
<div style="background:#fff3cd;padding:30px;border-radius:20px;">
<h3>📢 Анонс</h3><form method="post"><input type="hidden" name="action" value="announce">
<textarea name="message" placeholder="Сообщение всем" style="height:80px;"></textarea><button style="background:#f39c12;">📢 ОТПРАВИТЬ</button></form>
</div>
</div>
<div style="margin-top:30px;background:#f8f9fa;padding:25px;border-radius:20px;">
<h3>📊 СТАТИСТИКА</h3>
<p>🟢 {stats['online']} онлайн | 🟡 {stats['afk']} АФК | 👥 {stats['total']} всего</p>
<p>🔇 Мутов: {len(mutelist)} | 💬 Сообщений: {len(chat_messages)}</p>
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# 🚀 УЗНАВАЙКИН v36.7 ЧАСТЬ 2/3

# ✅ МОДЕРАТОРСКАЯ ПАНЕЛЬ
@app.route('/moderator', methods=['GET', 'POST'])
def moderator_panel():
    current_user = session.get('user', '')
    if not is_moderator(current_user):
        return redirect('/')
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        target = request.form.get('target', '').strip()
        
        if action == 'mute':
            duration = int(request.form.get('duration', 600))
            mutes['by'][target] = time.time()
            mutes['expires'][target] = time.time() + duration
            mutes['reason'][target] = f"Модератор {current_user}: {request.form.get('reason', '')}"
            message = f'✅ {target} замучен на {duration//60} мин'
            save_data()
        elif action == 'unmute':
            for key in mutes:
                mutes[key].pop(target, None)
            message = f'✅ {target} размучен'
            save_data()
    
    mutelist = [u for u in mutes['by'] if time.time() < mutes['expires'].get(u, 0)]
    
    return f'''<!DOCTYPE html><html><head><title>🛡️ Модератор - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1 style="color:#27ae60;">🛡️ ПАНЕЛЬ МОДЕРАТОРА</h1>
{get_role_display(current_user)} | Активных мутов: {len(mutelist)}
{message and f'<div style="background:#d4edda;padding:25px;border-radius:20px;margin:25px 0;">{message}</div>' or ''}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
<div style="background:#e8f5e8;padding:40px;border-radius:25px;">
<h3>🔇 МУТИТЬ</h3><form method="post"><input type="hidden" name="action" value="mute">
<input name="target" placeholder="👤 Ник" required style="width:100%;padding:18px;margin:12px 0;">
<input name="duration" type="number" value="1200" placeholder="секунды">
<input name="reason" placeholder="Причина"><button style="width:100%;padding:18px;background:#e74c3c;color:white;border:none;border-radius:15px;">🔇 МУТИТЬ</button></form>
</div>
<div style="background:#fff3cd;padding:40px;border-radius:25px;">
<h3>✅ РАЗМУТИТЬ</h3><form method="post"><input type="hidden" name="action" value="unmute">
<input name="target" placeholder="👤 Ник" required style="width:100%;padding:18px;margin:12px 0;">
<button style="width:100%;padding:25px;background:#27ae60;color:white;border:none;border-radius:15px;font-weight:700;">✅ РАЗМУТИТЬ</button></form>
</div>
</div>
<h3>🔇 АКТИВНЫЕ МУТЫ ({len(mutelist)}):</h3>
<div style="background:#f8f9fa;padding:30px;border-radius:20px;max-height:350px;overflow:auto;">
{''.join([f'<div style="padding:15px;margin:8px 0;background:#ffebee;border-radius:12px;">🔇 {user}</div>' for user in mutelist]) or '<p style="text-align:center;color:#666;padding:40px;">Мутов нет ✅</p>'}
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# ✅ МАГАЗИН
@app.route('/shop', methods=['GET', 'POST'])
def shop():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    coins = user_economy.get(current_user, {}).get('coins', 0)
    
    shop_items = {
        'vip': {'name': '⭐ VIP статус', 'price': 500, 'desc': 'Золотой ник + бонусы'},
        'premium': {'name': '💎 Premium', 'price': 1000, 'desc': 'Все VIP + эксклюзив'},
        'avatar_gold': {'name': '👑 Золотой аватар', 'price': 200, 'desc': 'Крутой аватар'}
    }
    
    html = f'<h2 style="text-align:center;">🛒 Магазин | 💰 {coins:,} монет</h2>'
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:25px;">'
    
    for item_id, item in shop_items.items():
        owned = item_id in user_inventory.get(current_user, [])
        html += f'''
        <div style="background:#fff;padding:35px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;border-top:6px solid #3498db;">
            <h3>{item["name"]}</h3>
            <div style="font-size:2.5em;margin:20px 0;color:#27ae60;">💰 {item["price"]:,}</div>
            <p style="color:#666;margin-bottom:20px;">{item["desc"]}</p>
            <button onclick="buyItem(\'{item_id}\')" style="padding:20px 40px;background:{{\'#27ae60\' if not owned else \'#95a5a6\'}};color:white;border:none;border-radius:15px;font-weight:700;font-size:18px;cursor:{{\'pointer\' if not owned else \'default\'}};">
                {{\'\u2705 Куплено\' if owned else \'💸 Купить\'}}
            </button>
        </div>'''
    
    html += '''</div>
<script>
function buyItem(itemId) {
    fetch("/api/buy", {
        method:"POST", 
        headers:{"Content-Type":"application/json"}, 
        body:JSON.stringify({item:itemId})
    })
    .then(r=>r.json()).then(data => {
        if(data.success) {
            alert("✅ " + data.message);
            location.reload();
        } else {
            alert("❌ " + data.error);
        }
    });
}
</script>'''
    
    return f'<!DOCTYPE html><html><head><title>🛒 Магазин - Узнавайкин</title><meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">{html}<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a></div></body></html>'

@app.route('/api/buy', methods=['POST'])
def api_buy():
    current_user = session.get('user', '')
    if not current_user:
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    data = request.get_json()
    item_id = data.get('item')
    
    shop_items = {
        'vip': 500, 'premium': 1000, 'avatar_gold': 200
    }
    
    if item_id not in shop_items:
        return jsonify({'success': False, 'error': 'Товар не найден'})
    
    price = shop_items[item_id]
    coins = user_economy.get(current_user, {}).get('coins', 0)
    
    if coins < price:
        return jsonify({'success': False, 'error': f'Нужно {price:,} монет'})
    
    user_economy[current_user]['coins'] -= price
    user_inventory.setdefault(current_user, []).append(item_id)
    
    if item_id == 'vip':
        user_roles[current_user] = 'vip'
    elif item_id == 'premium':
        user_roles[current_user] = 'premium'
    
    save_data()
    return jsonify({'success': True, 'message': f'Куплено: {item_id} за {price} монет'})

# ✅ ПРИВИЛЕГИИ
@app.route('/privileges')
def privileges():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    current_role = user_roles.get(current_user, 'start')
    
    return f'''<!DOCTYPE html><html><head><title>⭐ Привилегии - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1 style="text-align:center;">⭐ Привилегии</h1>
{get_role_display(current_user)} | Текущая роль
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:30px;margin:40px 0;">
<div style="padding:40px;border-radius:25px;background:#f0f8ff;border:4px solid {'#27ae60' if current_role in ['start','vip','premium','moderator','admin'] else '#ddd'};text-align:center;">
<h3>👤 Start</h3><div style="font-size:3em;margin:25px 0;color:#27ae60;">0 ₽/мес</div><p>Базовые права для всех</p>
<span style="background:#e8f5e8;padding:10px 20px;border-radius:10px;">{'' if current_role != 'start' else '✅ АКТИВНА'}</span>
</div>
<div style="padding:40px;border-radius:25px;background:#fff3e0;border:4px solid {'#f39c12' if current_role == 'vip' else '#ddd'};text-align:center;">
<h3>⭐ VIP</h3><div style="font-size:3em;margin:25px 0;color:#f39c12;">100 ₽/мес</div><p>Золотой ник + бонусы</p>
<span style="background:#fff176;padding:10px 20px;border-radius:10px;">{'' if current_role != 'vip' else '✅ АКТИВНА'}</span>
</div>
<div style="padding:40px;border-radius:25px;background:#e8f5e8;border:4px solid {'#9b59b6' if current_role == 'premium' else '#ddd'};text-align:center;">
<h3>💎 Premium</h3><div style="font-size:3em;margin:25px 0;color:#9b59b6;">200 ₽/мес</div><p>Всё VIP + эксклюзив</p>
<span style="background:#e1bee7;padding:10px 20px;border-radius:10px;">{'' if current_role != 'premium' else '✅ АКТИВНА'}</span>
</div>
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
<a href="/shop" class="nav-btn" style="background:#f39c12;">🛒 Купить в магазине</a>
</div></body></html>'''

# ✅ ЭКОНОМИКА
@app.route('/economy')
def economy():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    data = user_economy.get(current_user, {'coins': 0, 'bank': 0})
    coins = data.get('coins', 0)
    bank = data.get('bank', 0)
    
    return f'''<!DOCTYPE html><html><head><title>💰 Экономика - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1>💰 Экономика {get_role_display(current_user)}</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:40px 0;">
<div style="background:#e8f5e8;padding:50px;border-radius:25px;text-align:center;">
<h2>💰 Наличные</h2><div style="font-size:4em;color:#27ae60;margin:30px 0;">{coins:,}</div>
<p style="color:#666;">Монеты на руках</p>
</div>
<div style="background:#e3f2fd;padding:50px;border-radius:25px;text-align:center;">
<h2>🏦 Банк</h2><div style="font-size:4em;color:#2196f3;margin:30px 0;">{bank:,}</div>
<p style="color:#666;">Монеты в банке</p>
</div>
</div>
<div style="text-align:center;margin:40px 0;padding:30px;background:#f8f9fa;border-radius:20px;">
<h3>📊 Ваш топ</h3>
<p>Вы на #{sorted([v for v in leaderboards.get("wealth", {}).values()], reverse=True).index(coins)+1 if coins in leaderboards.get("wealth", {}).values() else "N/A"} месте</p>
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# ✅ ПРОФИЛИ
@app.route('/profiles')
def profiles():
    online_users = [u for u in users if is_online(u)]
    afk_users = [u for u in users if is_afk(u)]
    
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px;margin:40px 0;">'
    for user in sorted(users.keys()):
        status = '🟢' if is_online(user) else '🟡' if is_afk(user) else '⚫'
        coins = user_economy.get(user, {}).get('coins', 0)
        html += f'''
        <div style="background:#fff;padding:30px;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.1);text-align:center;">
            <div style="font-size:2.5em;margin-bottom:15px;">{user_profiles.get(user, {}).get('avatar', '👤')}</div>
            <h3 style="margin:10px 0;">{user}</h3>
            <div style="color:#27ae60;font-size:1.3em;">{status}</div>
            <div style="color:#666;margin:10px 0;">💰 {coins:,}</div>
            {get_role_display(user)}
            <a href="/profile/{user}" style="display:inline-block;background:#3498db;color:white;padding:12px 25px;border-radius:12px;text-decoration:none;margin-top:15px;font-weight:600;">👁️ Профиль</a>
        </div>'''
    html += '</div>'
    
    return f'''<!DOCTYPE html><html><head><title>👥 Профили - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1 style="text-align:center;margin-bottom:20px;">👥 Все профили</h1>
<p style="text-align:center;color:#666;margin-bottom:40px;">🟢 {len(online_users)} онлайн | 🟡 {len(afk_users)} АФК | 👥 {len(users)} всего</p>
{html}
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

@app.route('/profile/<username>')
def profile(username):
    current_user = session.get('user', '')
    profile_data = user_profiles.get(username, {})
    coins = user_economy.get(username, {}).get('coins', 0)
    role = user_roles.get(username, 'start')
    
    is_own = current_user == username
    status = '🟢 Онлайн' if is_online(username) else '🟡 АФК' if is_afk(username) else '⚫ Оффлайн'
    
    return f'''<!DOCTYPE html><html><head><title>{username} - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1 style="text-align:center;">👤 {username}</h1>
<div style="text-align:center;margin:40px 0;">
<div style="font-size:5em;padding:30px;background:#f8f9fa;border-radius:50%;display:inline-block;box-shadow:0 20px 60px rgba(0,0,0,0.2);">{profile_data.get('avatar', '👤')}</div>
</div>
<div style="background:#e3f2fd;padding:40px;border-radius:25px;margin:30px 0;text-align:center;">
<h2>{get_role_display(username)}</h2>
<div style="font-size:2.5em;margin:25px 0;color:#27ae60;">{status}</div>
<div style="font-size:2em;color:#f39c12;">💰 {coins:,} монет</div>
</div>
{profile_data.get('info', '<p style="text-align:center;color:#666;margin:40px 0;">Информация не заполнена</p>')}
<div style="text-align:center;margin:50px 0;">
<a href="/profiles" class="nav-btn" style="background:#3498db;">👥 Все профили</a>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
{is_own and '<a href="/economy" class="nav-btn" style="background:#27ae60;">💰 Экономика</a>' or ''}
</div>
</div></body></html>'''

@app.route('/catalog')
def catalog():
    return f'''<!DOCTYPE html><html><head><title>📁 Каталог - Узнавайкин</title>
<meta charset="utf-8"><style>{css_v36_7}</style></head><body><div class="container">
<h1>📁 Каталог файлов</h1>
<div style="background:#f8f9fa;padding:40px;border-radius:20px;text-align:center;color:#666;">
🔧 Каталог доступен только администраторам<br>
<a href="/admin" class="nav-btn" style="background:#e74c3c;">🔧 Админка</a>
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# ✅ ЗАПУСК
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # 🚀 УЖНАВКИН v36.7 ПОЛНЫЙ КОД ЗАГРУЖЕН!
    # ✅ Админы: CatNap(120187), Назар(120187)
    # ✅ Все роуты: /, /login, /shop, /economy, /privileges, /profiles, /admin
    app.run(host='0.0.0.0', port=port, debug=False)

