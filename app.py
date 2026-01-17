from flask import Flask, request, session, redirect, url_for, jsonify
from datetime import datetime
import os
import json
import time
import hashlib
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'uznaykin_v36_4_full_rights_admins_moderators_2026'

# ✅ ГЛОБАЛЬНЫЕ ДАННЫЕ v36.4
data_file = 'uznaykin_v36_4_data.json'
upload_folder = 'static/uploads'
os.makedirs(upload_folder, exist_ok=True)

# Инициализация ВСЕХ данных
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

# ✅ АВТО-АДМИНЫ v36.4
AUTO_ADMINS = ['CatNap', 'Назар']

# АВТО-МОДЕРАЦИЯ
bad_words = ['сука', 'пизда', 'хуй', 'пидор', 'блять', 'нахуй', 'ебать', 'пидорас']
spam_patterns = [r'http[s]?://[^\s]*', r'@\w+\.\w+', r'\b(тг|tg|vk|discord)\b']

# МАГАЗИН v36.4
shop_items = {
    'avatar1': {'name': '👑 Золотой аватар', 'price': 500, 'type': 'avatar'},
    'color_gold': {'name': '🌟 Золотой ник', 'price': 1000, 'type': 'color'},
    'status_vip': {'name': '⭐ VIP статус', 'price': 2000, 'type': 'status'}
}

def get_timestamp():
    return time.time()

# ✅ КРИТИЧЕСКИЕ ФУНКЦИИ СОХРАНЕНИЯ/ЗАГРУЗКИ v36.4
def load_data():
    global users, user_roles, user_profiles, user_activity, user_stats, user_economy
    global user_inventory, chat_messages, mutes, catalog, announcements, notifications
    global bans, friends, blocked, leaderboards, pinned_messages, moderation_logs
    
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, value in data.items():
                    globals()[key] = value
    except Exception as e:
        print(f"Ошибка загрузки: {e}")

def save_data():
    """Сохранение ВСЕХ данных с оптимизацией"""
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

# ✅ Загрузка при старте
load_data()

# ✅ АВТО-АДМИНЫ v36.5 + ФИКС КАТАЛОГА
def setup_auto_admins():
    """Создает авто-админов и инициализирует каталог"""
    global catalog
    
    # ✅ АВТО-АДМИНЫ v36.5
    AUTO_ADMINS = ['CatNap', 'admin', '120187', 'moderator']
    
    for admin_name in AUTO_ADMINS:
        if admin_name not in user_roles:
            # Создаем аккаунт админа
            users[admin_name] = {
                'password': hashlib.sha256(admin_name.encode()).hexdigest()
            }
            user_roles[admin_name] = 'admin'
            user_profiles[admin_name] = {
                'status': '👑 Супер-Админ v36.5', 
                'info': '🚀 Полные права: CRUD + роли + модерация',
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
                'message': '🎉 Авто-админ создан! Бесконечные монеты + все права'
            })
            print(f"✅ СОЗДАН АВТО-АДМИН: {admin_name}")
        else:
            # Обновляем права существующих
            user_roles[admin_name] = 'admin'
            user_economy.setdefault(admin_name, {'coins': 999999, 'bank': 5000000})
            print(f"✅ ОБНОВЛЕН АДМИН: {admin_name}")
    
    # ✅ ФИКС КАТАЛОГА v36.5
    if not catalog or 'root' not in catalog:
        catalog = {
            'root': {
                'type': 'folder',
                'created_by': 'system',
                'created': time.time(),
                'items_count': 0
            }
        }
        print("✅ КАТАЛОГ ИНИЦИАЛИЗИРОВАН")
    
    # ✅ Инициализация других данных
    if not leaderboards:
        leaderboards = {
            'messages_today': {},
            'messages_week': {},
            'online_time': {},
            'wealth': {}
        }
    
    if not chat_messages:
        chat_messages.append({
            'user': '🚀 СИСТЕМА', 
            'text': 'УЖНАВКИН v36.5 запущен! Добро пожаловать! 🎉', 
            'time': time.time()
        })
    
    save_data()
    print("✅ SETUP_AUTO_ADMINS() ЗАВЕРШЕН — все данные готовы!")


# ✅ ОСНОВНЫЕ ФУНКЦИИ v36.4
def get_role_display(username):
    role = user_roles.get(username, 'start')
    role_styles = {
        'start': {'icon': '👤', 'color': '#95a5a6', 'label': 'Обычный'},
        'vip': {'icon': '⭐', 'color': '#f39c12', 'label': 'VIP'},
        'premium': {'icon': '💎', 'color': '#9b59b6', 'label': 'Premium'},
        'moderator': {'icon': '🛡️', 'color': '#27ae60', 'label': 'Модератор'},
        'admin': {'icon': '👑', 'color': '#e74c3c', 'label': 'Администратор'}
    }
    style = role_styles.get(role, role_styles['start'])
    profile_color = user_profiles.get(username, {}).get('color', style['color'])
    return f'<span style="color:{profile_color} !important;">{style["icon"]} {style["label"]}</span>'

def is_admin(username):
    return user_roles.get(username) == 'admin'

def is_moderator(username):
    return user_roles.get(username) in ['admin', 'moderator']

def is_online(username):
    return username in user_activity and time.time() - user_activity[username] < 60

def is_muted(username):
    if username not in mutes['by']:
        return False
    expires = mutes['expires'].get(username, 0)
    if expires == 0 or time.time() < expires:
        return True
    # Авто-очистка истекших мутов
    for key in mutes:
        mutes[key].pop(username, None)
    save_data()
    return False

def auto_moderate(message, username):
    """Авто-модерация: мат + спам + флуд"""
    message_lower = message.lower()
    
    # Мат
    for word in bad_words:
        if word in message_lower:
            return f'🚫 Мат ({word}) — авто-мут 10 мин', 600
    
    # Спам/реклама
    for pattern in spam_patterns:
        if re.search(pattern, message):
            return f'🚫 Спам/реклама — авто-мут 30 мин', 1800
    
    # Флуд (3 одинаковых сообщения подряд)
    recent_msgs = [m['text'].lower() for m in chat_messages[-10:] if m['user'] == username]
    if len(recent_msgs) >= 3 and len(set(recent_msgs[-3:])) <= 1:
        return f'🚫 Флуд — авто-мут 1 час', 3600
    
    return None, 0

def add_coins(username, amount, reason=''):
    """Экономика: начисление монет"""
    user_economy.setdefault(username, {'coins': 0, 'bank': 0, 'last_bank': time.time()})
    user_economy[username]['coins'] += amount
    leaderboards.setdefault('wealth', {})[username] = leaderboards['wealth'].get(username, 0) + amount
    user_stats.setdefault(username, {})['coins_earned'] = user_stats[username].get('coins_earned', 0) + amount
    save_data()
    return user_economy[username]['coins']

def get_top_leaderboard(category='wealth', limit=10):
    """Лидерборды"""
    now = datetime.now()
    today_key = now.strftime('%Y-%m-%d')
    
    if category == 'messages_today':
        data = leaderboards.setdefault('messages_today', {}).get(today_key, {})
    elif category == 'wealth':
        data = leaderboards.setdefault('wealth', {})
    else:
        data = {}
    
    return sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit]

def calculate_stats():
    """Статистика сервера"""
    stats = {'online': 0, 'total_users': len(users)}
    for user in users:
        if is_online(user):
            stats['online'] += 1
    return stats

# ✅ CRUD КАТАЛОГА v36.4 (ТОЛЬКО АДМИНЫ)
def create_folder(parent_path, folder_name, admin_username):
    """Создание папки"""
    if len(folder_name) > 50 or not folder_name.strip():
        return False, "❌ Название: 1-50 символов"
    
    full_path = f"{parent_path}/{folder_name}".strip('/') if parent_path != 'root' else folder_name
    if full_path in catalog:
        return False, "❌ Уже существует"
    
    catalog[full_path] = {
        'type': 'folder',
        'created_by': admin_username,
        'created': time.time(),
        'items_count': 0
    }
    moderation_logs.append({'time': time.time(), 'action': f'create_folder:{full_path}', 'admin': admin_username})
    save_data()
    return True, f"✅ Папка '{folder_name}' создана"

def create_file(parent_path, file_name, content, admin_username):
    """Создание файла"""
    if len(file_name) > 50 or len(content) > 5000:
        return False, "❌ Имя: 1-50 симв. | Контент: макс 5KB"
    
    full_path = f"{parent_path}/{file_name}".strip('/') if parent_path != 'root' else file_name
    if full_path in catalog:
        return False, "❌ Уже существует"
    
    catalog[full_path] = {
        'type': 'file',
        'name': file_name,
        'content': content,
        'created_by': admin_username,
        'created': time.time(),
        'size': len(content)
    }
    moderation_logs.append({'time': time.time(), 'action': f'create_file:{full_path}', 'admin': admin_username})
    save_data()
    return True, f"✅ Файл '{file_name}' ({len(content)} симв.) создан"

def delete_catalog_item(path, admin_username):
    """Удаление папки/файла рекурсивно"""
    if path not in catalog:
        return False, "❌ Элемент не найден"
    
    # Рекурсивное удаление содержимого папки
    if catalog[path].get('type') == 'folder':
        for item_path in list(catalog.keys()):
            if item_path.startswith(path + '/'):
                del catalog[item_path]
    
    del catalog[path]
    moderation_logs.append({'time': time.time(), 'action': f'delete:{path}', 'admin': admin_username})
    save_data()
    return True, f"✅ '{path}' удалён"

def get_catalog_content(path='root'):
    """Получить содержимое каталога"""
    if path not in catalog:
        catalog[path] = {'type': 'folder', 'created_by': 'system', 'created': time.time()}
    
    folders = []
    files = []
    for name, item in catalog.items():
        if name.startswith(path + '/') and name.count('/') == path.count('/') + 1:
            if item['type'] == 'folder':
                folders.append(name.split('/')[-1])
            else:
                files.append({'name': name.split('/')[-1], 'content': item.get('content', '')[:100]})
    
    return sorted(folders), sorted(files, key=lambda x: x['name'])

# ✅ УПРАВЛЕНИЕ РОЛЯМИ v36.4 (ТОЛЬКО АДМИНЫ)
def set_user_role(target_user, new_role, admin_username):
    """Назначение/снятие ролей"""
    valid_roles = ['start', 'vip', 'moderator', 'admin']
    if new_role not in valid_roles:
        return False, "❌ Роль: start/vip/moderator/admin"
    
    if target_user not in users:
        return False, "❌ Пользователь не найден"
    
    old_role = user_roles.get(target_user, 'start')
    user_roles[target_user] = new_role
    
    moderation_logs.append({
        'time': time.time(),
        'action': f'role:{target_user} {old_role}→{new_role}',
        'admin': admin_username
    })
    
    # Специальные бонусы для ролей
    if new_role == 'vip':
        add_coins(target_user, 1000, 'VIP бонус')
    elif new_role == 'moderator':
        user_profiles.setdefault(target_user, {})['status'] = '🛡️ Модератор'
    elif new_role == 'admin':
        user_profiles.setdefault(target_user, {})['status'] = '👑 Администратор'
        user_economy.setdefault(target_user, {'coins': 999999})
    
    save_data()
    return True, f"✅ {target_user}: {old_role} → {new_role}"

def buy_item(username, item_id):
    """Покупка из магазина"""
    if item_id not in shop_items:
        return False, "❌ Товар не найден"
    
    item = shop_items[item_id]
    price = item['price']
    coins = user_economy.get(username, {}).get('coins', 0)
    
    if coins < price:
        return False, f"❌ Нужно {price:,} монет (у вас {coins:,})"
    
    user_economy[username]['coins'] -= price
    user_inventory.setdefault(username, []).append(item_id)
    
    # Применение эффекта
    if item['type'] == 'avatar':
        user_profiles.setdefault(username, {})['avatar'] = item['name']
    elif item['type'] == 'color':
        user_profiles.setdefault(username, {})['color'] = '#ffd700'
    
    notifications.setdefault(username, []).append({
        'time': time.time(),
        'message': f"✅ Куплено: {item['name']} за {price:,} монет!",
        'type': 'purchase'
    })
    
    save_data()
    return True, f"✅ Куплено: {item['name']}"

# ✅ CSS v36.4 (современный + адаптивный)
css_v36_4 = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
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
.admin-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:25px;}
.nav {display:flex;flex-wrap:wrap;justify-content:center;gap:15px;padding:35px;background:#ecf0f1;border-radius:20px;margin-top:30px;}
.nav-btn {padding:16px 28px;color:white;text-decoration:none;border-radius:15px;font-weight:600;transition:all 0.3s;font-size:15px;}
.nav-btn:hover {transform:translateY(-3px);box-shadow:0 8px 25px rgba(0,0,0,0.2);}
.mute-timer {background:linear-gradient(45deg,#ff6b6b,#ee5a52);color:white;padding:35px;border-radius:20px;text-align:center;margin:25px 0;font-size:18px;}
.announcement {background:linear-gradient(45deg,#fff3cd,#ffeaa7);color:#856404;padding:25px;border-radius:20px;margin:20px 0;border-left:6px solid #f39c12;}
form input, form select, form textarea {width:100%;padding:15px;margin:10px 0;border:2px solid #e1e5e9;border-radius:12px;font-size:16px;box-sizing:border-box;font-family:inherit;}
form button {width:100%;padding:16px;background:linear-gradient(45deg,#3498db,#2980b9);color:white;border:none;border-radius:12px;font-weight:600;font-size:17px;cursor:pointer;transition:all 0.3s;}
form button:hover {transform:translateY(-2px);box-shadow:0 8px 25px rgba(52,152,219,0.4);}
@media (max-width:768px) {.container{padding:20px;margin:10px;border-radius:20px;}.nav{flex-direction:column;align-items:center;}}'''

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    
    # ✅ Обработка сообщений
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form['message'].strip()
        if message and len(message) <= 300:
            
            if message.startswith('/admin ') and is_admin(current_user):
                cmd = message[6:].strip().lower()
                if cmd == 'stats':
                    stats = calculate_stats()
                    chat_messages.append({
                        'user': f'👑 {current_user}', 
                        'text': f'📊 Онлайн: {stats["online"]}/{stats["total_users"]} | Сообщений: {len(chat_messages)}', 
                        'time': time.time()
                    })
                save_data()
            else:
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
                        'user': current_user, 'text': message, 'time': time.time()
                    })
                    add_coins(current_user, 3, 'чат')
                    user_activity[current_user] = time.time()
                save_data()
    
    if current_user:
        user_activity[current_user] = time.time()
    
    stats = calculate_stats()
    top_wealth = get_top_leaderboard('wealth', 5)
    
    # ✅ ФИКС: Правильный подсчет каталога
    catalog_count = len([item for item in catalog if item != 'root' and catalog[item].get('type') == 'file'])
    
    html = f'''<!DOCTYPE html>
<html><head><title>🚀 Узнавайкин v36.5 ✅</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css_v36_4}</style></head><body>
<div class="container">
<div class="header">
<h1>🚀 УЖНАВКИН v36.5 ✅ ФИКС</h1>
<p>{get_role_display(current_user) if current_user else "👋 Гость"} | 🟢 {stats['online']}/{stats['total_users']} онлайн</p>
</div>'''

    # ✅ ИСПРАВЛЕННАЯ СТАТИСТИКА
    html += f'''<div class="stats">
<div class="stat-card"><b>{stats['online']}</b><br>🟢 Онлайн</div>
<div class="stat-card"><b>{len(chat_messages)}</b><br>💬 Сообщений</div>
<div class="stat-card"><b>{catalog_count}</b><br>📁 Файлов</div>'''

    if current_user:
        coins = user_economy.get(current_user, {}).get('coins', 0)
        html += f'<div class="stat-card"><b>{coins:,}</b><br>💰 Монет</div>'
    
    html += '</div>'

    # Остальной код index() без изменений...
    if announcements:
        html += f'<div class="announcement"><b>📢 {announcements[0]["admin"]}</b><br>{announcements[0]["message"]}</div>'

    html += '<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:30px;border-radius:20px;margin:25px 0;">'
    html += '<h3 style="margin-bottom:20px;">🥇 Топ богачей</h3>'
    if top_wealth:
        for i, (user, coins) in enumerate(top_wealth):
            medal = '🥇🥈🥉'[i] if i < 3 else f'{i+1}️⃣'
            html += f'<div style="display:flex;justify-content:space-between;padding:15px;background:#fff;border-radius:12px;margin:8px 0;box-shadow:0 3px 15px rgba(0,0,0,0.1);"><span>{medal} {user}</span><span>{coins:,} 💰</span></div>'
    html += '</div>'

    html += '<div class="chat-container"><div id="chat-messages">'
    for msg in reversed(chat_messages[-40:]):
        time_str = datetime.fromtimestamp(msg['time']).strftime('%H:%M')
        html += f'<div class="chat-msg"><b>{msg["user"]}</b> <span style="color:#888;float:right;">{time_str}</span><div style="clear:both;margin-top:8px;">{msg["text"]}</div></div>'
    html += '</div>'

    if current_user and not is_muted(current_user):
        html += f'''<form method="post" style="padding:30px;background:#ecf0f1;">
<div style="display:flex;gap:15px;align-items:end;">
<input name="message" placeholder="💭 Напиши... /admin stats" maxlength="300" required 
style="flex:1;padding:20px;border:2px solid #ddd;border-radius:15px;font-size:17px;">
<button type="submit" style="padding:20px 35px;background:linear-gradient(45deg,#27ae60,#229954);color:white;border:none;border-radius:15px;font-weight:700;font-size:17px;">📤</button>
</div></form>'''
    else:
        html += '<div style="padding:50px;text-align:center;background:#ffebee;color:#c53030;font-size:20px;border-radius:15px;margin:20px;">🔐 Войдите или вы в муте</div>'

    html += '</div>'

    nav_items = [
        ('/profiles', '👥 Профили', '#3498db'),
        ('/shop', '🛒 Магазин', '#9b59b6'),
        ('/catalog', '📁 Каталог', '#f39c12')
    ]
    
    if current_user:
        nav_items.extend([
            (f'/profile/{current_user}', '👤 Мой профиль', '#764ba2'),
            ('/economy', '💰 Экономика', '#27ae60')
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
            return '<h1 style="color:red;text-align:center;">🚫 Вы забанены!</h1><a href="/">← Назад</a>'
        
        # ✅ Регистрация новых
        if username not in users:
            users[username] = {'password': hashlib.sha256(password.encode()).hexdigest()}
            user_roles[username] = 'start'
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': f'Привет! Я {username}'}
            user_economy[username] = {'coins': 150, 'bank': 0}
            notifications[username] = [{'time': time.time(), 'message': '🎉 Регистрация! +150 монет подарок!'}]
            add_coins(username, 150, 'регистрация')
        
        # ✅ Проверка пароля
        elif users[username]['password'] != hashlib.sha256(password.encode()).hexdigest():
            return f'''<h1 style="color:red;text-align:center;margin:50px;">❌ Неверный пароль!</h1>
            <div style="text-align:center;"><a href="/login" style="background:#e74c3c;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;font-weight:bold;">← Попробовать снова</a></div>'''
        
        session['user'] = username
        user_activity[username] = time.time()
        save_data()
        return redirect('/')
    
    return f'''<!DOCTYPE html><html><head><title>🔐 Узнавайкин v36.4</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>body{{background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Inter',sans-serif;padding:20px;}}
.login-box{{background:#fff;padding:60px;border-radius:25px;box-shadow:0 30px 100px rgba(0,0,0,0.25);width:100%;max-width:450px;text-align:center;}}
.login-box h1{{color:#2c3e50;margin-bottom:35px;font-size:2.5em;}}</style></head>
<body><div class="login-box">
<h1>🚀 УЖНАВКИН v36.4</h1>
<form method="post">
<input name="username" placeholder="👤 Логин (CatNap/admin = АДМИН)" required 
style="width:100%;padding:22px;margin:15px 0;border:2px solid #e1e8ed;border-radius:15px;font-size:18px;box-sizing:border-box;">
<input name="password" type="password" placeholder="🔑 Пароль (любой)" required 
style="width:100%;padding:22px;margin:15px 0;border:2px solid #e1e8ed;border-radius:15px;font-size:18px;box-sizing:border-box;">
<button style="width:100%;padding:22px;background:linear-gradient(45deg,#ff6b6b,#ee5a52);color:white;border:none;border-radius:15px;font-size:20px;font-weight:700;box-shadow:0 10px 30px rgba(255,107,107,0.4);">🚀 ВОЙТИ / ЗАРЕГИСТРИРОВАТЬСЯ</button>
</form>
<p style="margin-top:25px;color:#666;font-size:14px;">💡 Авто-админы: CatNap, 120187, admin, moderator</p>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ✅ АДМИНКА v36.4 (ПОЛНЫЕ ПРАВА)
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
            message = f'✅ {target} забанен навсегда'
            
        elif action == 'set_role':
            role = request.form.get('role')
            success, msg = set_user_role(target, role, current_user)
            message = msg
            
        elif action == 'create_folder':
            success, msg = create_folder('root', request.form['folder_name'], current_user)
            message = msg
            
        elif action == 'create_file':
            success, msg = create_file('root', request.form['file_name'], 
                                     request.form['file_content'], current_user)
            message = msg
            
        elif action == 'delete_item':
            success, msg = delete_catalog_item(request.form['item_path'], current_user)
            message = msg
            
        elif action == 'announce':
            announcements.insert(0, {
                'message': request.form['message'][:250],
                'admin': current_user,
                'time': time.time()
            })
            message = '✅ Анонс отправлен ВСЕМ!'
        
        save_data()
    
    stats = calculate_stats()
    mutelist = [u for u in mutes['by'] if time.time() < mutes['expires'].get(u, 0)]
    
    return f'''<!DOCTYPE html><html><head><title>🔧 Админка v36.4</title>
<meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container">
<h1 style="color:#e74c3c;text-align:center;font-size:2.5em;">🔧 АДМИНКА v36.4 — ПОЛНЫЕ ПРАВА</h1>
{message and f'<div style="background:linear-gradient(135deg,#d4edda,#c3e6cb);padding:25px;border-radius:20px;margin:20px 0;text-align:center;font-size:18px;border-left:6px solid #28a745;">{message}</div>' or ''}
<div class="admin-grid">
<div style="background:linear-gradient(135deg,#ffebee,#ffcdd2);padding:30px;border-radius:20px;">
<h3>🔇 Мут / Размут</h3><form method="post">
<input type="hidden" name="action" value="mute"><input name="target" placeholder="👤 Ник" required style="width:100%;padding:15px;margin:10px 0;">
<input name="duration" type="number" value="1800" placeholder="секунды" style="width:100%;padding:15px;margin:10px 0;">
<input name="reason" placeholder="Причина" style="width:100%;padding:15px;margin:10px 0;">
<button style="width:100%;padding:15px;background:#e74c3c;color:white;border:none;border-radius:12px;font-weight:700;">🔇 ЗАМУТИТЬ</button></form>
<form method="post" style="margin-top:15px;"><input type="hidden" name="action" value="unmute">
<input name="target" placeholder="👤 Ник" required style="width:100%;padding:15px;margin:10px 0;">
<button style="width:100%;padding:15px;background:#27ae60;color:white;border:none;border-radius:12px;font-weight:700;">✅ РАЗМУТИТЬ</button></form>
</div>

<div style="background:linear-gradient(135deg,#e8f5e8,#c8e6c9);padding:30px;border-radius:20px;">
<h3>👑 Управление ролями</h3><form method="post"><input type="hidden" name="action" value="set_role">
<input name="target" placeholder="👤 Ник" required style="width:100%;padding:15px;margin:10px 0;">
<select name="role" style="width:100%;padding:15px;margin:10px 0;border:2px solid #4caf50;border-radius:10px;font-size:16px;">
<option value="admin">👑 Админ (ВСЁ)</option><option value="moderator">🛡️ Модератор (муты)</option><option value="vip">⭐ VIP</option><option value="start">👤 Обычный</option></select>
<button style="width:100%;padding:15px;background:#9b59b6;color:white;border:none;border-radius:12px;font-weight:700;">👑 НАЗНАЧИТЬ РОЛЬ</button></form>
</div>

<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:30px;border-radius:20px;">
<h3>📁 Каталог CRUD</h3>
<form method="post"><input type="hidden" name="action" value="create_folder">
<input name="folder_name" placeholder="📁 Название папки" maxlength="50" required style="width:100%;padding:15px;margin:10px 0;">
<button style="width:100%;padding:15px;background:#2196f3;color:white;border:none;border-radius:12px;">📁 СОЗДАТЬ ПАПКУ</button></form>
<form method="post" style="margin-top:10px;"><input type="hidden" name="action" value="create_file">
<input name="file_name" placeholder="📄 Имя файла" maxlength="50" style="width:100%;padding:15px;margin:10px 0;">
<textarea name="file_content" placeholder="Содержимое файла (макс 5KB)..." maxlength="5000" style="width:100%;height:80px;padding:15px;margin:10px 0;"></textarea>
<button style="width:100%;padding:15px;background:#9c27b0;color:white;border:none;border-radius:12px;">📄 СОЗДАТЬ ФАЙЛ</button></form>
</div>

<div style="background:linear-gradient(135deg,#fff3cd,#ffeaa7);padding:30px;border-radius:20px;">
<h3>🚫 Баны + 📢 Анонсы</h3>
<form method="post"><input type="hidden" name="action" value="ban">
<input name="target" placeholder="👤 Ник для БАНА" required style="width:100%;padding:15px;margin:10px 0;">
<button style="width:100%;padding:18px;background:#e74c3c;color:white;border:none;border-radius:12px;font-size:16px;font-weight:700;">🚫 ПОЛНЫЙ БАН</button></form>
<form method="post" style="margin-top:15px;"><input type="hidden" name="action" value="announce">
<textarea name="message" placeholder="📢 Анонс ВСЕМ игрокам (макс 250 симв.)" maxlength="250" required style="width:100%;height:70px;padding:15px;margin:10px 0;"></textarea>
<button style="width:100%;padding:15px;background:#f39c12;color:white;border:none;border-radius:12px;">📢 ОТПРАВИТЬ АНОНС</button></form>
</div>
</div>

<div style="margin-top:30px;background:linear-gradient(135deg,#ffcdd2,#ffafbd);padding:25px;border-radius:20px;">
<h3>🗑️ УДАЛЕНИЕ каталога</h3>
<form method="post"><input type="hidden" name="action" value="delete_item">
<input name="item_path" placeholder="📁 полный/путь/к/папке или файлу" required style="width:70%;padding:15px;margin:10px;">
<button style="width:28%;padding:15px;background:#e74c3c;color:white;border:none;border-radius:12px;font-weight:700;">🗑️ УДАЛИТЬ НАВСЕГДА</button></form>
</div>

<div style="margin-top:25px;background:#f8f9fa;padding:30px;border-radius:20px;">
<h3>📊 СТАТИСТИКА v36.4</h3>
<p><b>🟢 Онлайн:</b> {stats["online"]} | <b>👥 Всего:</b> {stats["total_users"]}</p>
<p><b>🔇 Мутов:</b> {len(mutelist)} | <b>📁 Каталога:</b> {len(catalog)-1}</p>
<p><b>💰 Рекорд:</b> {get_top_leaderboard("wealth",1)[0][1] if get_top_leaderboard("wealth",1) else 0:,} монет</p>
<p><b>📝 Логов:</b> {len(moderation_logs)}</p>
</div>

<a href="/" class="nav-btn" style="background:#2c3e50;font-size:18px;">🏠 НА ГЛАВНУЮ</a>
</div></body></html>'''

# ✅ МОДЕРАТОРСКАЯ v36.4 (только муты)
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
    stats = calculate_stats()
    
    return f'''<!DOCTYPE html><html><head><title>🛡️ Модератор v36.4</title>
<meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container">
<h1 style="color:#27ae60;text-align:center;">🛡️ ПАНЕЛЬ МОДЕРАТОРА</h1>
{get_role_display(current_user)} | Онлайн: {stats['online']}
{message and f'<div style="background:#d4edda;padding:25px;border-radius:20px;margin:25px 0;">{message}</div>' or ''}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
<div style="background:linear-gradient(135deg,#e8f5e8,#c8e6c9);padding:40px;border-radius:25px;">
<h3>🔇 МУТИТЬ</h3><form method="post"><input type="hidden" name="action" value="mute">
<input name="target" placeholder="👤 Ник для мута" required style="width:100%;padding:18px;margin:12px 0;">
<input name="duration" type="number" value="1200" placeholder="секунды (20мин)" style="width:100%;padding:18px;margin:12px 0;">
<input name="reason" placeholder="Причина мута" style="width:100%;padding:18px;margin:12px 0;">
<button style="width:100%;padding:18px;background:#e74c3c;color:white;border:none;border-radius:15px;font-weight:700;font-size:16px;">🔇 ЗАМУТИТЬ</button></form>
</div>
<div style="background:linear-gradient(135deg,#fff3cd,#ffeaa7);padding:40px;border-radius:25px;">
<h3>✅ РАЗМУТИТЬ</h3><form method="post"><input type="hidden" name="action" value="unmute">
<input name="target" placeholder="👤 Ник для размута" required style="width:100%;padding:18px;margin:12px 0;">
<button style="width:100%;padding:25px;background:#27ae60;color:white;border:none;border-radius:15px;font-weight:700;font-size:18px;">✅ РАЗМУТИТЬ</button></form>
</div>
</div>
<h3 style="margin:30px 0 15px 0;">🔇 АКТИВНЫЕ МУТЫ ({len(mutelist)})</h3>
<div style="background:#f8f9fa;padding:30px;border-radius:20px;max-height:350px;overflow:auto;border:2px solid #ffebee;">
{''.join([f'<div style="padding:15px;margin:8px 0;background:#ffebee;border-radius:12px;font-size:16px;">🔇 {user} {"🕐" if time.time() < mutes["expires"].get(user,0) else "✅"}</div>' for user in mutelist]) or '<p style="text-align:center;color:#666;font-size:18px;padding:40px;">Мутов нет ✅</p>'}
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;font-size:18px;">🏠 ГЛАВНАЯ</a>
</div></body></html>'''

# ✅ МАГАЗИН + ЭКОНОМИКА + ПРОФИЛИ (упрощенно)
@app.route('/shop', methods=['GET', 'POST'])
def shop():
    current_user = session.get('user', '')
    if not current_user: return redirect('/login')
    
    html = f'<h2 style="text-align:center;">🛒 МАГАЗИН | 💰 {user_economy.get(current_user,{{}}).get("coins",0):,} монет</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:25px;">'
    
    for item_id, item in shop_items.items():
        owned = item_id in user_inventory.get(current_user, [])
        html += f'''
        <div style="background:#fff;padding:35px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;">
            <h3>{item['name']}</h3>
            <div style="font-size:3em;margin:20px 0;">💰 {item['price']:,}</div>
            <button onclick="buy('{item_id}')" style="padding:20px 40px;background:{'#27ae60' if not owned else '#95a5a6'};color:white;border:none;border-radius:15px;font-weight:700;font-size:18px;cursor:{'pointer' if not owned else 'default'};">
                {'' if owned else '💸 '}{'' if not owned else 'Купить'}{' ✅ Куплено' if owned else ''}
            </button>
        </div>'''
    
    html += '</div><script>function buy(id){fetch("/api/buy",{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{item:id}})}).then(r=>r.json()).then(d=>alert(d.success?"✅"+d.message:"❌"+d.error)).then(()=>location.reload());}</script>'
    
    return f'<!DOCTYPE html><html><head><title>🛒 Магазин</title><meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container">{html}<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a></div></body></html>'

@app.route('/api/buy', methods=['POST'])
def api_buy():
    current_user = session.get('user', '')
    data = request.json
    success, msg = buy_item(current_user, data.get('item'))
    return jsonify({'success': success, 'message': msg})

@app.route('/profiles')
@app.route('/profile/<username>')
def profiles(username=None):
    if username:
        return f'<!DOCTYPE html><html><head><title>{username}</title><meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container"><h1>👤 {username}</h1><p>{get_role_display(username)}</p><a href="/" class="nav-btn">🏠</a></div></body></html>'
    
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;">'
    for user in sorted(users):
        html += f'<div style="padding:25px;border-radius:15px;background:#f8f9fa;text-align:center;"><b>{user}</b><br>{get_role_display(user)}<br>{"🟢" if is_online(user) else "⚫"}</div>'
    html += '</div>'
    return f'<!DOCTYPE html><html><head><title>👥 Профили</title><meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container"><h1>👥 Все игроки</h1>{html}<a href="/" class="nav-btn">🏠</a></div></body></html>'

@app.route('/catalog')
def catalog():
    content = get_catalog_content('root')
    html = f'<h2>📁 Каталог ({len(catalog)-1} элементов)</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;">'
    
    for folder in content[0]:
        html += f'<div style="padding:30px;border-radius:20px;background:#e3f2fd;text-align:center;"><h3>📁 {folder}</h3></div>'
    
    for file in content[1]:
        html += f'<div style="padding:25px;border-radius:15px;background:#f3e5f5;"><b>📄 {file["name"]}</b><br><small>{file["content"]}...</small></div>'
    
    html += '</div>'
    return f'<!DOCTYPE html><html><head><title>📁 Каталог</title><meta charset="utf-8"><style>{css_v36_4}</style></head><body><div class="container">{html}<a href="/" class="nav-btn">🏠</a></div></body></html>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 УЖНАВКИН v36.4 запущен! Авто-админы: CatNap, Назар")
    app.run(host='0.0.0.0', port=port, debug=False)

