from flask import Flask, request, session, redirect, url_for, jsonify, send_file
from datetime import datetime, timedelta
import os
import json
import time
import hashlib
import re
import base64
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.secret_key = 'uznaykin_v36_full_features_2026_xyz987_secure_fixed'

# ✅ НОВЫЕ ГЛОБАЛЬНЫЕ ДАННЫЕ v36 — ВСЕ ФИЧИ
users = {}
user_roles = {}
user_profiles = {
    # avatar, status, info, color, custom_status, background_music
}
user_activity = {}
user_stats = {}  # Лидерборды: messages, online_time
user_economy = {}  # Монеты, банк
user_inventory = {}  # Аватары, цвета, статусы
chat_messages = []
mutes = {
    'by': {}, 'reason': {}, 'muted_by': {}, 'duration': {}, 
    'expires': {}  # Время окончания
}
catalog = {'root': {}}  # ✅ CRUD папки/файлы
announcements = []  # Анонсы админа
notifications = {}  # 🔔 Уведомления
bans = {}  # IP баны
friends = {}  # Друзья
blocked = {}  # Блокировка
leaderboards = {
    'messages_today': {},      # {дата: {ник: количество}}
    'messages_week': {},       # {неделя: {ник: количество}}
    'online_time': {},         # {ник: секунды}
    'wealth': {}               # {ник: монеты}
}
pinned_messages = []  # 📌 Закреплённые
moderation_logs = []  # Логи модерации
settings = {
    'dark_mode': False, 'music': False, 'sound_notifications': True,
    'maintenance': False  # Тех. работы
}
upload_folder = 'static/uploads'
os.makedirs(upload_folder, exist_ok=True)

data_file = 'uznaykin_v36_full.json'

# ✅ СЛОВА ДЛЯ АВТО-МОДЕРАЦИИ
bad_words = [
    'сука', 'пизда', 'хуй', 'пидор', 'блять', 'нахуй', 'ебать', 'пидорас',
    'хуесос', 'пиздец', 'мудак', 'пидор', 'охуеть', 'заебало'
]
spam_patterns = [
    r'http[s]?://[^\s]*', r'@\w+\.\w+', r'\b(тг|tg|vk|discord|youtube)\b',
    r'[wW]+[WwWw]+[WwWw]*\.[a-zA-Z0-9]+'
]

# ✅ МАГАЗИН v36
shop_items = {
    'avatar1': {'name': '👑 Золотой аватар', 'price': 500, 'type': 'avatar'},
    'color_gold': {'name': '🌟 Золотой ник', 'price': 1000, 'type': 'color'},
    'status_vip': {'name': '⭐ VIP статус', 'price': 2000, 'type': 'status'},
    'background_neon': {'name': '🌈 Неоновый фон', 'price': 1500, 'type': 'background'},
    'custom_status': {'name': '✨ Кастом статус', 'price': 3000, 'type': 'custom_status'}
}

def get_timestamp():
    return time.time()

def load_data():
    """Загрузка ВСЕХ данных"""
    global users, user_roles, user_profiles, user_activity, user_stats, user_economy
    global user_inventory, chat_messages, mutes, catalog, announcements, notifications
    global bans, friends, blocked, leaderboards, pinned_messages, moderation_logs, settings
    
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = data.get('users', {})
                user_roles = data.get('user_roles', {})
                user_profiles = data.get('user_profiles', {})
                user_activity = data.get('user_activity', {})
                user_stats = data.get('user_stats', {})
                user_economy = data.get('user_economy', {})
                user_inventory = data.get('user_inventory', {})
                chat_messages = data.get('chat_messages', [])
                mutes = data.get('mutes', {'by': {}, 'reason': {}, 'muted_by': {}, 'duration': {}, 'expires': {}})
                catalog = data.get('catalog', {'root': {}})
                announcements = data.get('announcements', [])
                notifications = data.get('notifications', {})
                bans = data.get('bans', {})
                friends = data.get('friends', {})
                blocked = data.get('blocked', {})
                leaderboards = data.get('leaderboards', {'messages_today': {}, 'messages_week': {}, 'online_time': {}, 'wealth': {}})
                pinned_messages = data.get('pinned_messages', [])
                moderation_logs = data.get('moderation_logs', [])
                settings = data.get('settings', settings)
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
    
    # ✅ АВТО-АДМИНЫ v36
    auto_admins = ['CatNap', 'Назар']
    for username in auto_admins:
        if username not in users:
            users[username] = {'password': hashlib.sha256('120187'.encode()).hexdigest(), 'role': 'admin', 'registered': get_timestamp()}
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': '👑 Авто-администратор', 'avatar': None, 'color': '#e74c3c', 'background': None}
            user_economy[username] = {'coins': 999999, 'bank': 0}
            user_stats[username] = {'messages': 0, 'online_time': 0}
            user_activity[username] = get_timestamp()
        user_roles[username] = 'admin'
    
    save_data()

# В ЧАСТИ 1 заменить инициализацию leaderboards:
leaderboards = {
    'messages_today': {},      # {дата: {ник: количество}}
    'messages_week': {},       # {неделя: {ник: количество}}
    'online_time': {},         # {ник: секунды}
    'wealth': {}               # {ник: монеты}
}

# ✅ УЛУЧШЕННАЯ ФУНКЦИЯ СОХРАНЕНИЯ (каждые 10 сек)
last_save = 0
def save_data(force=False):
    global last_save
    now = get_timestamp()
    if force or now - last_save > 10:  # Каждые 10 сек
        last_save = now
        data = {
            'users': users, 
            'user_roles': user_roles, 
            'user_profiles': user_profiles,
            'user_activity': {k: v for k, v in user_activity.items() if now - v < 3600},  # Только активные
            'user_stats': user_stats,
            'user_economy': user_economy,
            'user_inventory': user_inventory,
            'chat_messages': chat_messages[-1000:],  # Последние 1000
            'mutes': mutes,
            'catalog': catalog,
            'announcements': announcements[-50:],
            'notifications': {k: [n for n in v if now - n['time'] < 86400] for k, v in notifications.items()},
            'bans': bans,
            'friends': friends,
            'blocked': blocked,
            'leaderboards': leaderboards,
            'pinned_messages': pinned_messages,
            'moderation_logs': moderation_logs[-500:]
        }
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")


# ✅ ИНИЦИАЛИЗАЦИЯ
load_data()
# ✅ ФУНКЦИИ РОЛЕЙ v36 (цветные + стили)
def get_role_display(username):
    role = user_roles.get(username, 'start')
    role_styles = {
        'start': {'icon': '👤', 'color': '#95a5a6', 'label': 'Обычный'},
        'vip': {'icon': '⭐', 'color': '#f39c12', 'label': 'VIP'},
        'premium': {'icon': '💎', 'color': '#9b59b6', 'label': 'Premium'},
        'moderator': {'icon': '🛡️', 'color': '#27ae60', 'label': 'Модератор'},
        'admin': {'icon': '👑', 'color': '#e74c3c', 'label': 'Администратор'}
    }
    role_data = role_styles.get(role, role_styles['start'])
    profile_color = user_profiles.get(username, {}).get('color', role_data['color'])
    return f'<span style="color:{profile_color} !important;">{role_data["icon"]} {role_data["label"]}</span>'

def is_admin(username): 
    return user_roles.get(username) == 'admin'

def is_moderator(username): 
    return user_roles.get(username) == 'moderator'

# ✅ НОВЫЙ ОНЛАЙН (1 мин = оффлайн, 30 сек = АФК)
def is_online(username):
    if username not in user_activity:
        return False
    return get_timestamp() - user_activity[username] < 60

def is_afk(username):
    if not is_online(username):
        return False
    return get_timestamp() - user_activity[username] > 30

def calculate_stats():
    stats = {'online': 0, 'afk': 0, 'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    for user in users:
        if is_online(user):
            stats['online'] += 1
            if is_afk(user):
                stats['afk'] += 1
            role = user_roles.get(user, 'start')
            stats[role] += 1
    return stats

# ✅ АВТО-МОДЕРАЦИЯ v36
def auto_moderate(message, username):
    message_lower = message.lower()
    
    for word in bad_words:
        if word in message_lower:
            return f'🚫 Мат ({word}) — авто-мут 10 мин', 600
    
    for pattern in spam_patterns:
        if re.search(pattern, message):
            return f'🚫 Спам/реклама — авто-мут 30 мин', 1800
    
    recent_msgs = [m['text'].lower() for m in chat_messages[-5:] if m['user'] == username]
    if len(recent_msgs) >= 3 and len(set(recent_msgs)) == 1:
        return f'🚫 Флуд — авто-мут 1 час', 3600
    
    return None, 0

# ✅ ЭКОНОМИКА v36
def add_coins(username, amount, reason=''):
    if username not in user_economy:
        user_economy[username] = {'coins': 0, 'bank': 0, 'last_bank': get_timestamp()}
    
    user_economy[username]['coins'] += amount
    user_stats.setdefault(username, {})['coins_earned'] = user_stats.get(username, {}).get('coins_earned', 0) + amount
    
    save_data()
    return user_economy[username]['coins']

def deposit_bank(username, amount):
    if username in user_economy and user_economy[username]['coins'] >= amount:
        user_economy[username]['coins'] -= amount
        user_economy[username]['bank'] += amount
        user_economy[username]['last_bank'] = get_timestamp()
        save_data()
        return True
    return False

def collect_bank_interest():
    now = get_timestamp()
    for username in user_economy:
        if now - user_economy[username].get('last_bank', 0) > 3600:
            interest = int(user_economy[username]['bank'] * 0.03)
            if interest > 0:
                user_economy[username]['coins'] += interest
                user_economy[username]['last_bank'] = now
    save_data()

# ✅ ЛИДЕРБОРДЫ v36 (ИСПРАВЛЕНО!)
def update_leaderboards(username):
    now = datetime.now()
    today_key = now.strftime('%Y-%m-%d')
    week_key = now.strftime('%Y-%W')
    
    # ✅ ИСПРАВЛЕНО: Используем .setdefault()
    leaderboards['messages_today'].setdefault(today_key, {})
    leaderboards['messages_today'][today_key].setdefault(username, 0)
    leaderboards['messages_today'][today_key][username] += 1
    
    leaderboards['messages_week'].setdefault(week_key, {})
    leaderboards['messages_week'][week_key].setdefault(username, 0)
    leaderboards['messages_week'][week_key][username] += 1
    
    user_stats.setdefault(username, {})['online_time'] = user_stats.get(username, {}).get('online_time', 0) + 1
    leaderboards['online_time'][username] = user_stats[username]['online_time']
    
    save_data()

def get_top_leaderboard(category='messages_today', limit=10):
    now = datetime.now()
    today_key = now.strftime('%Y-%m-%d')
    week_key = now.strftime('%Y-%W')
    
    if category == 'messages_today':
        data = leaderboards['messages_today'].get(today_key, {})
    elif category == 'messages_week':
        data = leaderboards['messages_week'].get(week_key, {})
    elif category == 'online_time':
        data = leaderboards.get('online_time', {})
    elif category == 'wealth':
        data = leaderboards.get('wealth', {})
    else:
        data = {}
    
    return sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit]

# ✅ МУТЫ v36 (с проверкой истечения)
def is_muted(username):
    if username not in mutes['by']:
        return False
    
    expires = mutes['expires'].get(username, 0)
    if expires == 0 or get_timestamp() < expires:
        return True
    else:
        remove_mute(username)
        return False

def remove_mute(username):
    for key in ['by', 'reason', 'muted_by', 'duration', 'expires']:
        mutes[key].pop(username, None)
    save_data()

def add_mute(username, admin, duration, reason):
    expires = 0 if duration == 0 else get_timestamp() + duration
    mutes['by'][username] = get_timestamp()
    mutes['reason'][username] = reason
    mutes['muted_by'][username] = admin
    mutes['duration'][username] = duration
    mutes['expires'][username] = expires
    
    moderation_logs.append({
        'time': get_timestamp(),
        'action': 'mute',
        'admin': admin,
        'target': username,
        'duration': duration,
        'reason': reason
    })
    save_data()

# ✅ КАТАЛОГ CRUD v36 (создание/удаление папок + файлов)
def get_catalog_content(path='root'):
    """Получить содержимое папки с рекурсивной проверкой"""
    if path not in catalog:
        catalog[path] = {}
    
    current = catalog[path]
    folders = []
    files = []
    
    for name, item in current.items():
        if item.get('type') == 'folder':
            folders.append({'name': name, **item})
        elif item.get('type') == 'file':
            files.append({'name': name, **item})
    
    return {
        'folders': sorted(folders, key=lambda x: x['name']),
        'files': sorted(files, key=lambda x: x['name']),
        'path': path
    }

def catalog_path_join(parent, name):
    """Создать полный путь папки"""
    if parent == 'root':
        return name
    return f"{parent}/{name}"

def create_catalog_folder(parent_path, folder_name, admin_username):
    """✅ СОЗДАНИЕ ПАПКИ"""
    if not folder_name or len(folder_name) > 50:
        return False, "Название слишком длинное (макс 50 символов)"
    
    full_path = catalog_path_join(parent_path, folder_name)
    if full_path in catalog:
        return False, "Папка уже существует"
    
    catalog[full_path] = {
        'type': 'folder',
        'created': get_timestamp(),
        'created_by': admin_username,
        'items_count': 0
    }
    
    # Обновляем счетчик родителя
    if parent_path != 'root':
        parent = catalog[parent_path]
        parent.setdefault('items_count', 0)
        parent['items_count'] += 1
    
    moderation_logs.append({
        'time': get_timestamp(),
        'action': 'create_folder',
        'admin': admin_username,
        'path': full_path
    })
    save_data()
    return True, "✅ Папка создана!"

def create_catalog_file(parent_path, file_name, content, admin_username):
    """✅ СОЗДАНИЕ ФАЙЛА"""
    if not file_name or len(file_name) > 50:
        return False, "Название слишком длинное"
    
    full_path = catalog_path_join(parent_path, file_name)
    if full_path in catalog:
        return False, "Файл уже существует"
    
    catalog[full_path] = {
        'type': 'file',
        'name': file_name,
        'content': content[:5000],  # Лимит 5KB
        'created': get_timestamp(),
        'created_by': admin_username,
        'size': len(content)
    }
    
    if parent_path != 'root':
        parent = catalog[parent_path]
        parent.setdefault('items_count', 0)
        parent['items_count'] += 1
    
    moderation_logs.append({
        'time': get_timestamp(),
        'action': 'create_file',
        'admin': admin_username,
        'path': full_path
    })
    save_data()
    return True, "✅ Файл создан!"

def delete_catalog_item(path, admin_username):
    """✅ УДАЛЕНИЕ папки/файла"""
    if path not in catalog:
        return False, "Элемент не найден"
    
    item = catalog[path]
    item_type = item['type']
    
    # Рекурсивное удаление папки
    if item_type == 'folder':
        for subitem_path in list(catalog.keys()):
            if subitem_path.startswith(path + '/'):
                del catalog[subitem_path]
    
    # Удаляем сам элемент
    del catalog[path]
    
    # Обновляем счетчик родителя
    parent_path = path.rsplit('/', 1)[0] if '/' in path else 'root'
    if parent_path != 'root' and parent_path in catalog:
        parent = catalog[parent_path]
        if parent.get('items_count', 0) > 0:
            parent['items_count'] -= 1
    
    moderation_logs.append({
        'time': get_timestamp(),
        'action': f'delete_{item_type}',
        'admin': admin_username,
        'path': path
    })
    save_data()
    return True, f"✅ {item_type.title()} удален!"

# ✅ МАГАЗИН v36
def buy_item(username, item_id):
    """Покупка предмета из магазина"""
    if item_id not in shop_items:
        return False, "Товар не найден"
    
    item = shop_items[item_id]
    price = item['price']
    
    if username not in user_economy or user_economy[username]['coins'] < price:
        return False, f"Недостаточно монет! Нужно: {price}"
    
    user_economy[username]['coins'] -= price
    if username not in user_inventory:
        user_inventory[username] = []
    
    user_inventory[username].append(item_id)
    
    # Применяем эффекты
    if item['type'] == 'avatar':
        user_profiles[username]['avatar'] = f"avatars/{item_id}.png"
    elif item['type'] == 'color':
        user_profiles[username]['color'] = item.get('color', '#ffd700')
    elif item['type'] == 'status':
        user_profiles[username]['custom_status'] = item['name']
    
    notifications.setdefault(username, []).append({
        'time': get_timestamp(),
        'message': f"✅ Куплено: {item['name']} за {price} монет!",
        'type': 'purchase'
    })
    
    save_data()
    return True, f"✅ Куплено: {item['name']}"

def get_user_inventory(username):
    """Инвентарь пользователя"""
    inventory = user_inventory.get(username, [])
    owned_items = []
    
    for item_id in inventory:
        if item_id in shop_items:
            owned_items.append(shop_items[item_id])
    
    return owned_items

# ✅ УВЕДОМЛЕНИЯ v36
def add_notification(username, message, notification_type='info'):
    """Добавить уведомление"""
    notifications.setdefault(username, []).append({
        'time': get_timestamp(),
        'message': message,
        'type': notification_type
    })
    
    # Ограничиваем 50 уведомлений
    if len(notifications[username]) > 50:
        notifications[username] = notifications[username][-50:]
    
    save_data()

# ✅ ДРУЗЬЯ + БЛОКИРОВКА
def add_friend(username, friend_username):
    """Добавить в друзья"""
    friends.setdefault(username, []).append(friend_username)
    friends.setdefault(friend_username, []).append(username)
    save_data()
    return True

def block_user(username, blocked_username):
    """Заблокировать пользователя"""
    blocked.setdefault(username, []).append(blocked_username)
    # Удаляем из друзей
    if blocked_username in friends.get(username, []):
        friends[username].remove(blocked_username)
    save_data()
    return True

def is_blocked(username, target_username):
    """Проверить блокировку"""
    return target_username in blocked.get(username, [])

# ✅ АНОНСЫ v36
def add_announcement(admin_username, message):
    """Добавить анонс (только админ)"""
    announcements.insert(0, {
        'time': get_timestamp(),
        'admin': admin_username,
        'message': message[:500]
    })
    if len(announcements) > 10:
        announcements = announcements[:10]
    save_data()
    return True

# ✅ ЗАКРЕПЛЁННЫЕ СООБЩЕНИЯ
def pin_message(msg_id, admin_username):
    """Закрепить сообщение"""
    for msg in chat_messages:
        if msg['id'] == msg_id:
            pinned_messages.insert(0, msg.copy())
            pinned_messages[0]['pinned_by'] = admin_username
            if len(pinned_messages) > 3:
                pinned_messages = pinned_messages[:3]
            save_data()
            return True
    return False
# ✅ CSS v36 (темная тема + PWA)
css_v36 = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Inter',sans-serif;background:#f8f9fa;color:#2c3e50;transition:all 0.3s;}
body.dark {background:#1a1a1a;color:#e0e0e0;}
.container {max-width:1400px;margin:0 auto;background:#fff;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
.dark .container {background:#2d2d2d;}
.header {padding:30px;text-align:center;background:linear-gradient(45deg,#ff9a9e,#fecfef);}
.dark .header {background:linear-gradient(45deg,#4a5568,#2d3748);}
.stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:15px;padding:25px;background:#f8f9fa;border-radius:20px;margin:20px 0;}
.dark .stats {background:#4a5568;}
.stats div {text-align:center;padding:20px;background:#fff;border-radius:15px;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
.leaderboard {background:#e3f2fd;padding:25px;border-radius:20px;margin:20px 0;}
.leaderboard h3 {color:#1976d2;margin-bottom:15px;}
.lb-item {display:flex;justify-content:space-between;padding:10px;background:#fff;border-radius:10px;margin:5px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.nav {display:flex;flex-wrap:wrap;gap:12px;padding:25px;background:#ecf0f1;border-radius:20px;justify-content:center;}
.dark .nav {background:#4a5568;}
.nav-btn {padding:15px 25px;color:white;text-decoration:none;border-radius:15px;font-weight:bold;transition:all 0.3s;}
#chat-container {max-width:1000px;margin:25px auto;background:#f8f9fa;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
#chat-messages {max-height:450px;overflow-y:auto;padding:25px;background:#fff;}
.dark #chat-messages {background:#2d2d2d;}
.chat-msg {margin-bottom:15px;padding:20px;background:#f1f3f4;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.dark .chat-msg {background:#4a5568;}
.mute-timer {background:#ff6b6b;color:white;padding:25px;border-radius:20px;margin:20px;text-align:center;}
.economy {display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:20px 0;}
.economy-card {background:#fff;padding:25px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);text-align:center;}
.notification {background:#d4edda;color:#155724;padding:15px;border-radius:10px;margin:10px 0;border-left:4px solid #28a745;}
.announcement {background:#fff3cd;color:#856404;padding:20px;border-radius:15px;margin:20px 0;border-left:5px solid #ffc107;font-weight:bold;}
.shop-grid {display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}
.shop-item {background:#fff;padding:25px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.1);text-align:center;border-top:5px solid #3498db;}
@media (max-width:768px) {.container{padding:20px;margin:10px;border-radius:20px;}}'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """✅ ГЛАВНАЯ СТРАНИЦА v36"""
    current_user = session.get('user', '')
    collect_bank_interest()  # Начисляем %
    
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form['message'].strip()
        if message and len(message) <= 300:
            # ✅ АВТО-МОДЕРАЦИЯ
            auto_result, duration = auto_moderate(message, current_user)
            if auto_result:
                add_mute(current_user, 'СИСТЕМА', duration, auto_result)
                chat_messages.append({
                    'id': len(chat_messages), 'user': '🚫 АВТОМОД', 
                    'text': f'{auto_result}: {current_user}',
                    'time': get_timestamp(), 'role': 'Система', 'pinned': False
                })
            else:
                # ✅ НОРМАЛЬНОЕ СООБЩЕНИЕ
                if message.startswith('/profile '):
                    target = message[9:].strip().lstrip('@')
                    message = f'👤 /profile/{target}'
                
                chat_messages.append({
                    'id': len(chat_messages), 'user': current_user, 
                    'text': message, 'time': get_timestamp(),
                    'role': get_role_display(current_user)
                })
                
                # ✅ НАГРАДА ЗА СООБЩЕНИЕ
                coins = add_coins(current_user, 5, 'сообщение')
                update_leaderboards(current_user)
                user_activity[current_user] = get_timestamp()
            
            save_data()
    
    if current_user:
        user_activity[current_user] = get_timestamp()
    
    stats = calculate_stats()
    top_messages = get_top_leaderboard('messages_today', 5)
    top_wealth = get_top_leaderboard('wealth', 5)
    
    # HTML структура
    html = f'''<!DOCTYPE html>
<html><head><title>🚀 Узнавайкин v36</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#667eea">
<style>{css_v36}</style></head><body>'''
    
    if session.get('dark_mode', False):
        html += '<script>document.body.classList.add("dark");</script>'
    
    html += f'<div class="container">'
    
    # ✅ ХЕДЕР + ТЕМНАЯ ТЕМА
    theme_btn = '☀️ Светлая' if session.get('dark_mode', False) else '🌙 Тёмная'
    html += f'''
    <div class="header">
        <h1>🚀 Узнавайкин v36</h1>
        <p>👤 <b>{current_user or "Гость"}</b> | {get_role_display(current_user) if current_user else ""} 
        | <button onclick="toggleTheme()" style="background:none;border:1px solid;color:#666;padding:5px 10px;border-radius:5px;cursor:pointer;font-size:14px;">{theme_btn}</button>
        </p>
    </div>'''
    
    # ✅ СТАТИСТИКА + ЛИДЕРБОРДЫ
    html += f'''
    <div class="stats">
        <div><b>{stats["online"]}</b><br>👥 Онлайн</div>
        <div><b>{stats["afk"]}</b><br>😴 АФК</div>
        <div><b>{len(user_economy)}</b><br>💰 Игроков</div>
    </div>
    
    <div class="leaderboard">
        <h3>🥇 Актив сегодня</h3>
        {' '.join([f'<div class="lb-item"><span>{i+1}.</span><span>{user}</span><span>{count}</span></div>' for i,(user,count) in enumerate(top_messages)]) or 'Пусто'}
    </div>'''
    
    # ✅ АНОНСЫ
    for ann in announcements[:3]:
        html += f'<div class="announcement">📢 {ann["message"]} <small>от {ann["admin"]} {datetime.fromtimestamp(ann["time"]).strftime("%H:%M")}</small></div>'
    
    # ✅ ЭКОНОМИКА
    if current_user:
        economy = user_economy.get(current_user, {'coins': 0, 'bank': 0})
        html += f'''
        <div class="economy">
            <div class="economy-card">
                <h3>💰 {economy["coins"]}</h3>
                <p>Монеты в кармане</p>
                <a href="/economy" class="nav-btn" style="background:#f39c12;padding:10px 20px;font-size:14px;">💳 Банк</a>
            </div>
            <div class="economy-card">
                <h3>🏦 {economy["bank"]}</h3>
                <p>В банке (3%/час)</p>
                <a href="/shop" class="nav-btn" style="background:#9b59b6;padding:10px 20px;font-size:14px;">🛒 Магазин</a>
            </div>
        </div>'''
    
    # ✅ ЧАТ (с закреплёнными)
    html += '''
    <div id="chat-container">
        <div id="pinned-messages" style="background:#e8f5e8;padding:15px;border-bottom:1px solid #ddd;">📌 Закреплённые:'''
    for msg in pinned_messages:
        html += f' <span style="background:#d4edda;padding:5px 10px;border-radius:5px;">{msg["user"]}: {msg["text"][:50]}...</span>'
    html += '</div><div id="chat-messages">'
    
    for msg in reversed(chat_messages[-30:]):
        delete_btn = '<button class="delete-btn" onclick="deleteMessage({})">×</button>'.format(msg['id']) if current_user and (is_admin(current_user) or is_moderator(current_user)) else ''
        html += f'''
        <div class="chat-msg">
            {delete_btn}
            <div class="chat-header">{msg["user"]} <span style="color:#666;">{msg["role"]} {datetime.fromtimestamp(msg["time"]).strftime("%H:%M")}</span></div>
            <div>{msg["text"]}</div>
        </div>'''
    
    html += '</div>'
    
    # ✅ ИНПУТ ЧАТА
    if current_user and not is_muted(current_user):
        html += '<form method="post" id="chatForm"><div id="chat-input" style="padding:20px;background:#ecf0f1;border-top:1px solid #ddd;display:flex;gap:10px;"><input type="text" name="message" id="messageInput" placeholder="/profile @ник, команды, чат... (макс. 300)" maxlength="300" style="flex:1;padding:15px;border:1px solid #ddd;border-radius:10px;font-size:16px;"><button type="submit" style="padding:15px 25px;background:#27ae60;color:white;border:none;border-radius:10px;cursor:pointer;font-size:16px;font-weight:bold;">📤</button></div></form>'
    else:
        html += '<div id="chat-input" style="padding:20px;text-align:center;color:#666;font-size:18px;">🔐 Войдите для чата или вы в муте</div>'
    
    html += '</div>'
    
    # ✅ МУТ ТАЙМЕР
    if current_user and is_muted(current_user):
        end_time = mutes['expires'].get(current_user, 0)
        reason = mutes['reason'].get(current_user, 'Причина не указана')
        html += f'''
        <div class="mute-timer">
            <h3>🔇 Вы замучены!</h3>
            <div id="mute-timer" data-end="{end_time}">Загрузка...</div>
            <p>{reason}</p>
        </div>'''
    
    # ✅ Навигация v36
    nav_items = [
        ('/catalog', '📁 Каталог', '#667eea'),
        ('/profiles', '👥 Профили', '#764ba2'),
        ('/leaderboards', '🏆 Лидерборды', '#f39c12'),
        ('/economy', '💰 Экономика', '#27ae60')
    ]
    
    if current_user:
        nav_items.extend([
            (f'/profile/{current_user}', '👤 Профиль', '#9b59b6'),
            ('/friends', '👫 Друзья', '#e74c3c')
        ])
        if is_admin(current_user):
            nav_items.append(('/admin', '🔧 Админ', '#e74c3c'))
        nav_items.append(('/logout', '🚪 Выход', '#95a5a6'))
    else:
        nav_items.append(('/login', '🔐 Войти', '#f39c12'))
    
    html += '<div class="nav">'
    for url, label, color in nav_items:
        html += f'<a href="{url}" class="nav-btn" style="background:{color};">{label}</a>'
    html += '</div></div>'
    
    # ✅ JAVASCRIPT v36 (PWA + реалтайм)
    html += f'''
    <script>
    let lastMsgCount = {len(chat_messages)};
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoAAAAA');
    
    // 🔄 РЕАЛТАЙМ 2 сек
    function updateChat() {{
        fetch('/api/chat').then(r=>r.json()).then(data => {{
            if(data.messages.length > lastMsgCount) {{
                lastMsgCount = data.messages.length;
                document.getElementById('chat-messages').innerHTML = data.html;
                window.scrollTo(0, document.body.scrollHeight);
                if(data.sound) audio.play();
            }}
        }});
    }}
    setInterval(updateChat, 2000);
    
    // 💰 БАНК % каждые 5 мин
    setInterval(() => fetch('/api/bank_interest'), 300000);
    
    // 🔔 МУТ ТАЙМЕР
    const muteTimer = document.getElementById('mute-timer');
    if(muteTimer) {{
        let endTime = parseFloat(muteTimer.dataset.end) * 1000;
        setInterval(() => {{
            let diff = endTime - Date.now();
            if(diff > 0) {{
                let s = Math.floor(diff/1000);
                muteTimer.textContent = `${{Math.floor(s/3600)}}ч ${{Math.floor((s%3600)/60)}}м ${{s%60}}с`;
            }} else {{
                muteTimer.textContent = '✅ Мут снят!';
                setTimeout(() => location.reload(), 1500);
            }}
        }}, 1000);
    }}
    
    // 🖱️ ПING онлайн
    setInterval(() => fetch('/api/ping', {{method: 'POST'}}), 25000);
    
    // 🗑️ УДАЛЕНИЕ
    function deleteMessage(msgId) {{
        if(confirm('Удалить сообщение?')) {{
            fetch(`/api/delete_message/${{msgId}}`, {{method: 'DELETE'}})
            .then(r=>r.json()).then(data => {{
                if(data.success) document.querySelector(`[onclick="deleteMessage(${msgId})"]`).closest('.chat-msg').remove();
            }});
        }}
    }}
    
    // 🌙 ТЕМНАЯ ТЕМА
    function toggleTheme() {{
        document.body.classList.toggle('dark');
        fetch('/api/theme', {{method: 'POST', headers:{{"Content-Type":"application/json"}}, body:JSON.stringify({{dark: document.body.classList.contains('dark')}})}});
    }}
    </script></body></html>'''
    
    return html

# ✅ API ENDPOINTS v36
@app.route('/api/chat')
def api_chat():
    current_user = session.get('user', '')
    html = ''
    for msg in reversed(chat_messages[-30:]):
        delete_btn = ''
        if current_user and (is_admin(current_user) or is_moderator(current_user)):
            delete_btn = f'<button class="delete-btn" onclick="deleteMessage({msg["id"]})" style="float:right;background:#e74c3c;color:white;border:none;border-radius:50%;width:25px;height:25px;cursor:pointer;font-size:14px;">×</button>'
        html += f'''
        <div class="chat-msg">
            {delete_btn}
            <div class="chat-header">{msg["user"]} <span style="color:#666;">{msg["role"]} {datetime.fromtimestamp(msg["time"]).strftime("%H:%M")}</span></div>
            <div>{msg["text"]}</div>
        </div>'''
    return jsonify({'messages': chat_messages[-30:], 'html': html, 'sound': True})

@app.route('/api/ping', methods=['POST'])
def api_ping():
    current_user = session.get('user', '')
    if current_user:
        user_activity[current_user] = get_timestamp()
        save_data()
    return jsonify({'ok': True})

@app.route('/api/theme', methods=['POST'])
def api_theme():
    data = request.json
    session['dark_mode'] = data.get('dark', False)
    return jsonify({'success': True})

@app.route('/api/bank_interest')
def api_bank_interest():
    collect_bank_interest()
    return jsonify({'collected': True})

@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def api_delete_message(msg_id):
    current_user = session.get('user', '')
    if not current_user or not (is_admin(current_user) or is_moderator(current_user)):
        return jsonify({'error': 'Нет доступа'}), 403
    
    for i, msg in enumerate(chat_messages):
        if msg['id'] == msg_id:
            del chat_messages[i]
            moderation_logs.append({
                'time': get_timestamp(),
                'action': 'delete_message',
                'moderator': current_user,
                'msg_id': msg_id
            })
            save_data()
            return jsonify({'success': True})
    return jsonify({'error': 'Сообщение не найдено'}), 404
# ✅ ПРОФИЛИ v36 (аватарки + кастомизация)
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    current_user = session.get('user', '')
    if username not in users:
        return redirect(url_for('index'))
    
    profile_data = user_profiles.get(username, {'status': '🟢 Онлайн', 'info': '', 'avatar': None, 'color': '#2c3e50'})
    is_own = current_user == username
    
    if request.method == 'POST' and is_own:
        profile_data['status'] = request.form.get('status', '🟢 Онлайн')
        profile_data['info'] = request.form['info'][:500]
        if 'avatar_file' in request.files:
            file = request.files['avatar_file']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, f"{current_user}_{int(time.time())}.{filename.rsplit('.',1)[1]}")
                file.save(filepath)
                profile_data['avatar'] = f"/static/uploads/{os.path.basename(filepath)}"
        user_profiles[username] = profile_data
        save_data()
    
    avatar_html = f'<img src="{profile_data.get("avatar", "/static/default_avatar.png")}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;box-shadow:0 10px 30px rgba(0,0,0,0.2);">'
    
    notifications_count = len(notifications.get(username, []))
    
    edit_form = ''
    if is_own:
        edit_form = f'''
        <form method="post" enctype="multipart/form-data">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:30px 0;">
                <select name="status" style="padding:20px;border:2px solid #ddd;border-radius:15px;font-size:18px;">
                    <option selected>🟢 Онлайн</option><option>🟡 Занят</option><option>🔴 Не беспокоить</option><option>😴 Отошел</option>
                </select>
                <input type="file" name="avatar_file" accept="image/*" style="padding:20px;border:2px solid #ddd;border-radius:15px;">
            </div>
            <textarea name="info" maxlength="500" placeholder="О себе...">{profile_data.get("info", "")}</textarea>
            <button type="submit" style="background:#27ae60;color:white;padding:18px 35px;border:none;border-radius:12px;font-size:18px;font-weight:bold;">💾 Сохранить</button>
        </form>'''
    
    return f'''<!DOCTYPE html><html><head><title>{username}</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);}}
.profile-container{{max-width:900px;margin:auto;background:#fff;border-radius:30px;padding:50px;box-shadow:0 30px 100px rgba(0,0,0,0.15);}}</style></head>
<body><div class="profile-container">
<h1 style="font-size:3em;text-align:center;color:#2c3e50;margin-bottom:30px;">👤 {username}</h1>
<div style="text-align:center;margin-bottom:40px;">{avatar_html}</div>
<div style="padding:20px 40px;color:white;border-radius:25px;font-size:1.8em;font-weight:bold;display:inline-block;margin:20px 0;">{get_role_display(username)}</div>
<div style="padding:30px;background:#f8f9fa;border-radius:20px;margin:30px 0;font-size:1.2em;">{profile_data.get("info", "Информация не указана")}</div>
{edit_form}
<a href="/notifications/{username}" style="background:#3498db;color:white;padding:15px 30px;border-radius:15px;font-size:18px;font-weight:bold;text-decoration:none;display:inline-block;">🔔 Уведомления ({notifications_count})</a>
<a href="/" style="background:#2c3e50;color:white;padding:20px 40px;border-radius:20px;font-size:18px;font-weight:bold;text-decoration:none;display:inline-block;margin-left:20px;">🏠 Главная</a>
</div></body></html>'''

# ✅ МАГАЗИН v36
@app.route('/shop')
def shop():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    inventory_items = get_user_inventory(current_user)
    coins = user_economy.get(current_user, {}).get('coins', 0)
    
    shop_html = '<div class="shop-grid">'
    for item_id, item in shop_items.items():
        owned = item_id in user_inventory.get(current_user, [])
        btn_text = '✅ Куплено' if owned else f'💰 Купить ({item["price"]})'
        btn_disabled = 'disabled' if owned else ''
        shop_html += f'''
        <div class="shop-item">
            <h3>{item["name"]}</h3>
            <p>💰 {item["price"]} монет</p>
            <button onclick="buyItem('{item_id}')" {btn_disabled} style="padding:15px 30px;background:{'#27ae60' if not owned else '#95a5a6'};color:white;border:none;border-radius:12px;font-weight:bold;cursor:{'pointer' if not owned else 'default'};">{btn_text}</button>
            {f'<p style="color:#27ae60;">В инвентаре</p>' if owned else ''}
        </div>'''
    shop_html += '</div>'
    
    return f'''<!DOCTYPE html><html><head><title>🛒 Магазин</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3em;margin-bottom:40px;">🛒 Магазин</h1>
<div style="background:#fff;padding:30px;border-radius:20px;margin-bottom:30px;text-align:center;">
    <h2>💰 {coins} монет</h2>
    <a href="/economy" class="nav-btn" style="background:#f39c12;">💳 Экономика</a>
</div>
{shop_html}
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
<script>
function buyItem(itemId) {{
    fetch('/api/buy_item', {{method:'POST', headers:{{"Content-Type":"application/json"}}, body:JSON.stringify({{item:itemId}})}})
    .then(r=>r.json()).then(data => {{
        if(data.success) {{
            alert(data.message);
            location.reload();
        }} else {{
            alert('❌ ' + data.error);
        }}
    }});
}}
</script></body></html>'''

@app.route('/api/buy_item', methods=['POST'])
def api_buy_item():
    current_user = session.get('user', '')
    if not current_user:
        return jsonify({'error': 'Не авторизован'}), 401
    
    data = request.json
    success, message = buy_item(current_user, data.get('item'))
    return jsonify({'success': success, 'message': message})

# ✅ ЭКОНОМИКА v36
@app.route('/economy')
def economy():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    economy_data = user_economy.get(current_user, {'coins': 0, 'bank': 0})
    top_wealth = get_top_leaderboard('wealth', 10)
    
    return f'''<!DOCTYPE html><html><head><title>💰 Экономика</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3em;margin-bottom:40px;">💰 Экономика</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:40px;">
    <div style="background:#fff;padding:40px;border-radius:25px;box-shadow:0 20px 60px rgba(0,0,0,0.1);">
        <h2 style="color:#27ae60;">💰 {economy_data["coins"]}</h2>
        <p style="font-size:1.5em;color:#666;">Монеты в кармане</p>
        <a href="/shop" class="nav-btn" style="background:#9b59b6;">🛒 Магазин</a>
    </div>
    <div style="background:#fff;padding:40px;border-radius:25px;box-shadow:0 20px 60px rgba(0,0,0,0.1);">
        <h2 style="color:#3498db;">🏦 {economy_data["bank"]}</h2>
        <p style="font-size:1.5em;color:#666;">В банке (3% в час)</p>
        <button onclick="collectInterest()" class="nav-btn" style="background:#f39c12;">📈 Собрать %</button>
    </div>
</div>
<h3 style="margin:30px 0 20px 0;">🥇 Топ богачей</h3>
<div style="background:#fff;padding:30px;border-radius:20px;">'''
    
    for i, (user, amount) in enumerate(top_wealth):
        html_icon = '🥇🥈🥉'[i] if i < 3 else f'{i+1}️⃣'
        html += f'<div style="display:flex;justify-content:space-between;padding:15px;border-bottom:1px solid #eee;"><span>{html_icon} {user}</span><span>{amount}</span></div>'
    
    html = f'''
    </div><a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
    <script>
    function collectInterest() {{
        fetch('/api/collect_interest', {{method:'POST'}}).then(r=>r.json()).then(data => {{
            if(data.success) alert('✅ Проценты собраны!');
            location.reload();
        }});
    }}
    </script></body></html>'''
    
    return html

@app.route('/api/collect_interest', methods=['POST'])
def api_collect_interest():
    current_user = session.get('user', '')
    if current_user:
        collect_bank_interest()
    return jsonify({'success': True})

# ✅ ЛИДЕРБОРДЫ
@app.route('/leaderboards')
def leaderboards():
    current_user = session.get('user', '')
    if not current_user:
        return redirect('/login')
    
    today_top = get_top_leaderboard('messages_today', 10)
    week_top = get_top_leaderboard('messages_week', 10)
    online_top = get_top_leaderboard('online_time', 10)
    
    return f'''<!DOCTYPE html><html><head><title>🏆 Лидерборды</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3em;margin-bottom:40px;">🏆 Лидерборды</h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
    <div>
        <h2 style="color:#f39c12;">📩 Сегодня</h2>
        <div style="background:#fff;padding:25px;border-radius:20px;">'''
    
    for i, (user, count) in enumerate(today_top):
        medal = '🥇🥈🥉'[i] if i < 3 else f'{i+1}️⃣'
        html += f'<div style="display:flex;justify-content:space-between;padding:12px;"><span>{medal} {user}</span><span>{count}</span></div>'
    
    html = f'''
        </div></div><div>
        <h2 style="color:#27ae60;">⏱️ Время онлайн</h2>
        <div style="background:#fff;padding:25px;border-radius:20px;">'''
    
    for i, (user, time) in enumerate(online_top):
        medal = '🥇🥈🥉'[i] if i < 3 else f'{i+1}️⃣'
        html += f'<div style="display:flex;justify-content:space-between;padding:12px;"><span>{medal} {user}</span><span>{time//60}м</span></div>'
    
    html = f'''
        </div></div></div><a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a></body></html>'''
    
    return html
# ✅ КАТАЛОГ CRUD v36 (админ только)
@app.route('/catalog/<path:path>', methods=['GET', 'POST'])
@app.route('/catalog', methods=['GET', 'POST'])
def catalog_view(path='root'):
    current_user = session.get('user', '')
    if not current_user or not is_admin(current_user):
        # Обычное отображение для всех
        content = get_catalog_content(path)
        breadcrumbs = '<a href="/catalog">📁 Каталог</a>'
        parts = [p.strip() for p in path.split('/') if p.strip()]
        temp_path = []
        for part in parts:
            temp_path.append(part)
            path_str = '/'.join(temp_path)
            breadcrumbs += f' → <a href="/catalog/{path_str}">{part}</a>'
        
        content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:30px;">'
        
        for folder in content['folders']:
            content_html += f'''
            <a href="/catalog/{path}/{folder['name']}" style="text-decoration:none;">
                <div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:40px;border-radius:25px;border-left:8px solid #2196f3;text-align:center;">
                    <div style="font-size:4em;">📁</div>
                    <h3 style="font-size:2.2em;color:#2196f3;">{folder['name']}</h3>
                </div>
            </a>'''
        
        for file_item in content['files']:
            content_html += f'''
            <div style="background:linear-gradient(135deg,#f3e5f5,#e1bee7);padding:40px;border-radius:25px;border-left:8px solid #9c27b0;">
                <h3 style="font-size:2.4em;color:#2c3e50;">{file_item['name']}</h3>
                <div style="background:#f9f9f9;padding:25px;border-radius:20px;font-size:1.2em;">{file_item.get('content', '—')[:200]}...</div>
            </div>'''
        
        content_html += '</div>'
        
        return f'''<!DOCTYPE html><html><head><title>📁 Каталог</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3.5em;margin-bottom:50px;">📁 Каталог</h1>
<div style="padding:30px;background:#ecf0f1;border-radius:25px;margin-bottom:40px;font-size:1.3em;">{breadcrumbs}</div>
{content_html}
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''
    
    # ✅ АДМИН CRUD
    content = get_catalog_content(path)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_folder':
            success, msg = create_catalog_folder(path, request.form['folder_name'], current_user)
            add_notification(current_user, msg)
        elif action == 'create_file':
            success, msg = create_catalog_file(path, request.form['file_name'], request.form['file_content'], current_user)
            add_notification(current_user, msg)
        elif action == 'delete':
            success, msg = delete_catalog_item(request.form['item_path'], current_user)
            add_notification(current_user, msg)
        save_data()
    
    # Админ панель каталога
    create_forms = '''
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:40px 0;">
        <div style="background:#d4edda;padding:30px;border-radius:20px;">
            <h3>📁 Создать папку</h3>
            <form method="post">
                <input type="hidden" name="action" value="create_folder">
                <input name="folder_name" placeholder="Название папки" required maxlength="50" style="width:100%;padding:15px;margin:10px 0;border:1px solid #ddd;border-radius:10px;">
                <button type="submit" style="width:100%;padding:15px;background:#28a745;color:white;border:none;border-radius:10px;font-weight:bold;">📁 Создать</button>
            </form>
        </div>
        <div style="background:#e3f2fd;padding:30px;border-radius:20px;">
            <h3>📄 Создать файл</h3>
            <form method="post">
                <input type="hidden" name="action" value="create_file">
                <input name="file_name" placeholder="Имя файла" required maxlength="50" style="width:100%;padding:15px;margin:10px 0;border:1px solid #ddd;border-radius:10px;">
                <textarea name="file_content" placeholder="Содержимое..." maxlength="5000" style="width:100%;height:100px;padding:15px;margin:10px 0;border:1px solid #ddd;border-radius:10px;"></textarea>
                <button type="submit" style="width:100%;padding:15px;background:#2196f3;color:white;border:none;border-radius:10px;font-weight:bold;">📄 Создать</button>
            </form>
        </div>
    </div>'''
    
    items_list = ''
    for folder in content['folders']:
        items_list += f'''
        <div style="display:flex;justify-content:space-between;background:#e3f2fd;padding:20px;border-radius:15px;margin:10px 0;">
            <a href="/catalog/{path}/{folder['name']}" style="font-size:1.5em;color:#2196f3;">📁 {folder['name']}</a>
            <form method="post" style="display:inline;" onsubmit="return confirm('Удалить папку {folder['name']}?')">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="item_path" value="{path}/{folder['name']}">
                <button type="submit" style="background:#e74c3c;color:white;border:none;border-radius:8px;padding:8px 15px;font-weight:bold;">🗑️</button>
            </form>
        </div>'''
    
    for file_item in content['files']:
        items_list += f'''
        <div style="display:flex;justify-content:space-between;background:#f3e5f5;padding:20px;border-radius:15px;margin:10px 0;">
            <div style="flex:1;">
                <div style="font-size:1.5em;color:#9c27b0;">📄 {file_item['name']}</div>
                <div style="color:#666;margin-top:5px;">{file_item.get('content', '')[:100]}...</div>
            </div>
            <form method="post" style="display:inline;" onsubmit="return confirm('Удалить файл {file_item['name']}?')">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="item_path" value="{path}/{file_item['name']}">
                <button type="submit" style="background:#e74c3c;color:white;border:none;border-radius:8px;padding:8px 15px;font-weight:bold;">🗑️</button>
            </form>
        </div>'''
    
    return f'''<!DOCTYPE html><html><head><title>📁 Каталог (Админ)</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1>📁 Каталог — {path}</h1>
{create_forms}
<div style="background:#f8f9fa;padding:30px;border-radius:20px;">
    <h3>📋 Содержимое ({len(content["folders"])} папок, {len(content["files"])} файлов)</h3>
    {items_list or '<p style="text-align:center;color:#666;font-size:1.2em;padding:40px;">Пусто</p>'}
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# ✅ СУПЕР АДМИНКА v36
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    current_user = session.get('user', '')
    if not is_admin(current_user):
        return redirect(url_for('index'))
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'mute':
            target = request.form['target'].strip()
            duration = int(request.form.get('duration', 600))
            reason = request.form['reason'].strip()[:100]
            add_mute(target, current_user, duration, reason)
            message = f'✅ {target} замучен на {duration}s: {reason}'
        
        elif action == 'announce':
            add_announcement(current_user, request.form['message'])
            message = '✅ Анонс отправлен!'
        
        elif action == 'ban':
            target = request.form['target'].strip()
            bans[target] = {'by': current_user, 'time': get_timestamp()}
            message = f'✅ {target} забанен!'
        
        save_data()
    
    # Статистика
    stats = calculate_stats()
    mutelist = [(u, mutes['expires'].get(u, 0)) for u in mutes['by'] if get_timestamp() < mutes['expires'].get(u, 0)]
    
    return f'''<!DOCTYPE html><html><head><title>🔧 Админка v36</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3em;">🔧 Админ-панель v36</h1>
{message and f'<div style="background:#d4edda;padding:20px;border-radius:15px;margin:20px 0;">{message}</div>' or ''}
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;">
    <div style="background:#f8d7da;padding:30px;border-radius:20px;">
        <h3>🔇 Мут</h3>
        <form method="post">
            <input type="hidden" name="action" value="mute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;">
            <input name="duration" type="number" value="600" style="width:100%;padding:12px;margin:8px 0;">
            <input name="reason" placeholder="Причина" style="width:100%;padding:12px;margin:8px 0;">
            <button style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:10px;">🔇 Замутить</button>
        </form>
    </div>
    <div style="background:#e3f2fd;padding:30px;border-radius:20px;">
        <h3>📢 Анонс</h3>
        <form method="post">
            <input type="hidden" name="action" value="announce">
            <textarea name="message" placeholder="Текст анонса" style="width:100%;height:80px;padding:12px;margin:8px 0;"></textarea>
            <button style="width:100%;padding:12px;background:#2196f3;color:white;border:none;border-radius:10px;">📢 Отправить</button>
        </form>
    </div>
    <div style="background:#ffeaa7;padding:30px;border-radius:20px;">
        <h3>🚫 Бан</h3>
        <form method="post">
            <input type="hidden" name="action" value="ban">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;">
            <button style="width:100%;padding:12px;background:#e74c3c;color:white;border:none;border-radius:10px;">🚫 Забанить</button>
        </form>
    </div>
</div>
<div style="margin-top:40px;">
    <h3>📊 Статистика: {stats["online"]} онлайн</h3>
    <h4>🔇 Мутлист ({len(mutelist)}):</h4>
    <div style="background:#f8f9fa;padding:20px;border-radius:15px;max-height:200px;overflow:auto;">{''.join([f'<div>{user} (до {datetime.fromtimestamp(time)})</div>' for user,time in mutelist]) or 'Пусто'}</div>
</div>
<a href="/" class="nav-btn" style="background:#2c3e50;">🏠 Главная</a>
</div></body></html>'''

# ✅ ОСТАЛЬНЫЕ РОУТЫ
@app.route('/profiles')
def profiles():
    stats = calculate_stats()
    profiles_html = ''
    for user in sorted(users.keys()):
        status = '🟢 Онлайн' if is_online(user) else '⚫ Оффлайн'
        profiles_html += f'''
        <div style="background:#fff;padding:30px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;margin:20px;">
            <h3 style="font-size:2em;">👤 {user}</h3>
            <div style="padding:15px 30px;color:white;border-radius:15px;font-size:1.3em;">{get_role_display(user)}</div>
            <div style="padding:12px 25px;border-radius:12px;font-size:1.2em;font-weight:bold;background:{'#d4edda' if is_online(user) else '#e2e3e5'};">{status}</div>
            <a href="/profile/{user}" style="display:inline-block;padding:15px 35px;background:#3498db;color:white;border-radius:15px;font-weight:bold;">👁️ Профиль</a>
        </div>'''
    
    return f'''<!DOCTYPE html><html><head><title>👥 Профили</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>{css_v36}</style></head><body><div class="container">
<h1 style="text-align:center;font-size:3em;">👥 Профили ({stats["online"]} онлайн)</h1>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:30px;">{profiles_html}</div>
<a href="/" style="background:#2c3e50;color:white;padding:25px 50px;border-radius:20px;font-size:22px;font-weight:bold;text-decoration:none;display:block;margin:60px auto;">🏠 Главная</a>
</div></body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        session['user'] = username
        
        if username not in user_roles:
            user_roles[username] = 'start'
        if username not in users:
            users[username] = {'password': password, 'role': 'start', 'registered': get_timestamp()}
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': '', 'avatar': None}
            user_economy[username] = {'coins': 100, 'bank': 0}  # Стартовые монеты
            user_stats[username] = {'messages': 0, 'online_time': 0}
            user_activity[username] = get_timestamp()
            add_notification(username, '🎉 Добро пожаловать! Получено 100 монет.')
        save_data()
        return redirect(url_for('index'))
    
    return f'''<!DOCTYPE html><html><head><title>🔐 Вход</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;min-height:100vh;}}
.login-box{{background:#fff;padding:60px;border-radius:30px;box-shadow:0 35px 120px rgba(0,0,0,0.25);width:100%;max-width:450px;}}</style></head>
<body><div class="login-box">
<h1 style="text-align:center;font-size:2.8em;color:#2c3e50;margin-bottom:30px;">🔐 Узнавайкин v36</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required maxlength="20" style="width:100%;padding:25px;margin:15px 0;border:2px solid #ddd;border-radius:15px;font-size:18px;">
<input name="password" type="password" placeholder="🔑 Пароль" required style="width:100%;padding:25px;margin:15px 0;border:2px solid #ddd;border-radius:15px;font-size:18px;">
<button style="width:100%;padding:25px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:15px;font-size:20px;font-weight:bold;">🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form></div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# ✅ PWA
@app.route('/manifest.json')
def manifest():
    return jsonify({
        'name': 'Узнавайкин v36',
        'short_name': 'Узнавайкин',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#f8f9fa',
        'theme_color': '#667eea',
        'icons': [{
            'src': '/static/icon-192.png',
            'sizes': '192x192',
            'type': 'image/png'
        }]
    })

@app.errorhandler(404)
def not_found(e):
    return f'''<!DOCTYPE html><html><head><title>404</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:100px;background:linear-gradient(135deg,#667eea,#764ba2);color:#e74c3c;text-align:center;}}</style></head>
<body><h1 style="font-size:8em;">404</h1><p style="font-size:2em;">Страница не найдена</p><a href="/" style="background:#2c3e50;color:white;padding:20px 50px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;">🏠 Главная</a></body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

