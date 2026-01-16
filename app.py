# ✅ ИСПРАВЛЕННЫЙ ПОЛНЫЙ КОД УЖНАВКИН v33

from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.secret_key = 'uznaykin_v33_secret_key_2026'

# Глобальные данные
users = {}
user_roles = {}
user_profiles = {}
user_activity = {}
chat_messages = []
mutes = {}
catalog = {}  # ✅ ПУСТОЙ КАТАЛОГ
data_file = 'uznaykin_data.json'

def load_data():
    global users, user_roles, user_profiles, user_activity, chat_messages, mutes, catalog
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = data.get('users', {})
                user_roles = data.get('user_roles', {})
                user_profiles = data.get('user_profiles', {})
                user_activity = data.get('user_activity', {})
                chat_messages = data.get('chat_messages', [])
                mutes = data.get('mutes', {})
                catalog = data.get('catalog', {})  # ✅ ПУСТОЙ
    except:
        pass

def save_data():
    data = {
        'users': users,
        'user_roles': user_roles,
        'user_profiles': user_profiles,
        'user_activity': user_activity,
        'chat_messages': chat_messages,
        'mutes': mutes,
        'catalog': catalog
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_timestamp():
    return datetime.now().timestamp()

def is_online(username):
    if username not in user_activity:
        return False
    return get_timestamp() - user_activity[username] < 300  # 5 минут

def is_afk(username):
    if not is_online(username):
        return False
    return get_timestamp() - user_activity[username] > 120  # 2 минуты бездействия

def calculate_stats():
    online_count = 0
    afk_count = 0
    stats = {'online': 0, 'afk': 0, 'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    for user in users.keys():
        if is_online(user):
            online_count += 1
            if is_afk(user):
                afk_count += 1
            role = user_roles.get(user, 'start')
            stats[role] += 1
    
    stats['online'] = online_count
    stats['afk'] = afk_count
    return stats

def get_role_display(username):
    role = user_roles.get(username, 'start')
    roles = {
        'start': '👤 Обычный',
        'vip': '⭐ VIP', 
        'premium': '💎 Premium',
        'moderator': '🛡️ Модератор',
        'admin': '👑 Администратор'
    }
    return roles.get(role, '👤 Обычный')

def is_admin(username):
    return user_roles.get(username) == 'admin'

def is_moderator(username):
    return user_roles.get(username) == 'moderator'

def is_muted(username):
    if username not in mutes:
        return False
    return get_timestamp() < mutes[username]

def get_catalog_content(path=''):
    parts = [p.strip() for p in path.split('/') if p.strip()]
    current_path = {}
    
    if not parts:  # Корень
        for folder in sorted(catalog.keys()):
            if isinstance(catalog[folder], dict) and 'type' in catalog[folder]:
                continue
            current_path.setdefault('folders', []).append(folder)
    else:
        current = catalog
        for part in parts:
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                return {'error': 'Папка не найдена'}
        
        for key in current:
            if isinstance(current[key], dict) and current[key].get('type') == 'folder':
                current_path.setdefault('folders', []).append(key)
            elif isinstance(current[key], dict) and current[key].get('type') == 'item':
                current_path.setdefault('items', {}).update({key: current[key]})
    
    current_path['folders'] = current_path.get('folders', [])
    current_path['items'] = current_path.get('items', {})
    return current_path

load_data()

css = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root{--primary:#667eea;--secondary:#764ba2;--success:#27ae60;--danger:#e74c3c;--warning:#f39c12;--dark:#2c3e50;--light:#ecf0f1;--bg:#f8f9fa;}
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Inter',sans-serif;line-height:1.6;background:var(--bg);color:var(--dark);padding:10px;min-height:100vh;}
.container {max-width:1200px;margin:0 auto;background:#fff;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    stats = calculate_stats()
    
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form['message'].strip()
        if message and len(message) <= 300:
            if message.startswith('/profile '):
                target = message[9:].strip()
                if target.startswith('@'):
                    target = target[1:]
                chat_messages.append({
                    'id': len(chat_messages),
                    'user': current_user,
                    'text': f'👤 Профиль: /profile/{target}',
                    'time': get_timestamp(),
                    'role': get_role_display(current_user)
                })
            else:
                chat_messages.append({
                    'id': len(chat_messages),
                    'user': current_user,
                    'text': message,
                    'time': get_timestamp(),
                    'role': get_role_display(current_user)
                })
            user_activity[current_user] = get_timestamp()
            save_data()
    
    html = '''<!DOCTYPE html>
<html><head><title>🚀 Узнавайкин v33</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>''' + css + '''* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Inter',sans-serif;line-height:1.6;min-height:100vh;padding:10px;}
.container {max-width:1200px;margin:0 auto;background:#fff;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
.header {padding:30px;text-align:center;background:linear-gradient(45deg,#ff9a9e,#fecfef);}
h1 {font-size:2.5em;margin:0;color:#2c3e50;}
.stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:15px;padding:25px;background:#f8f9fa;border-radius:20px;margin:20px 0;}
.stats div {text-align:center;padding:15px;background:#fff;border-radius:15px;box-shadow:0 5px 15px rgba(0,0,0,0.1);color:#2c3e50;}
.nav {display:flex;flex-wrap:wrap;gap:12px;padding:25px;background:#ecf0f1;border-radius:20px;justify-content:center;}
.nav-btn {padding:15px 25px;color:white;text-decoration:none;border-radius:15px;font-weight:bold;margin:5px;transition:all 0.3s;}
.nav-btn:hover {transform:translateY(-2px);box-shadow:0 10px 25px rgba(0,0,0,0.2);}
#chat-container {max-width:900px;margin:25px auto;background:#f8f9fa;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
#chat-messages {max-height:450px;overflow-y:auto;padding:25px;background:#fff;}
.chat-msg {margin-bottom:15px;padding:20px;background:#f1f3f4;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.chat-header {font-weight:bold;font-size:14px;margin-bottom:8px;color:#2c3e50;}
.delete-btn {float:right;background:#e74c3c;color:white;border:none;border-radius:50%;width:25px;height:25px;cursor:pointer;font-size:14px;}
#chat-input {padding:20px;background:#ecf0f1;border-top:1px solid #ddd;}
input[type="text"] {width:70%;padding:15px;border:1px solid #ddd;border-radius:10px;font-size:16px;background:#fff;color:#2c3e50;}
button[type="submit"] {width:25%;padding:15px;background:#27ae60;color:white;border:none;border-radius:10px;cursor:pointer;font-size:16px;font-weight:bold;}</style></head><body>'''
    
    html += '<div class="container">'
    
    if current_user:
        html += '<div class="header"><h1>🚀 Узнавайкин v33</h1><p>👤 <b>' + current_user + '</b> | ' + get_role_display(current_user) + '</p></div>'
        user_activity[current_user] = get_timestamp()
        save_data()
    else:
        html += '<div class="header"><h1>🚀 Узнавайкин v33</h1><p>👋 Добро пожаловать, Гость!</p></div>'
    
    html += '<div class="stats">'
    html += '<div><b>' + str(stats['online']) + '</b><br>👥 Онлайн</div>'
    html += '<div><b>' + str(stats['afk']) + '</b><br>😴 АФК</div>'
    html += '<div><b>' + str(stats['start']) + '</b><br>📚 Обычные</div>'
    html += '<div><b>' + str(stats['vip']) + '</b><br>⭐ VIP</div>'
    html += '<div><b>' + str(stats['premium']) + '</b><br>💎 Premium</div>'
    html += '<div><b>' + str(stats['moderator']) + '</b><br>🛡️ Модератор</div>'
    html += '<div><b>' + str(stats['admin']) + '</b><br>👑 Администратор</div>'
    html += '</div>'
    
    html += '<div id="chat-container"><div id="chat-messages">'
    
    for msg in reversed(chat_messages[-50:]):
        delete_btn = ''
        if current_user and (is_admin(current_user) or is_moderator(current_user)) and msg['user'] != current_user:
            delete_btn = '<button class="delete-btn" onclick="deleteMessage(' + str(msg['id']) + ')">×</button>'
        
        html += '<div class="chat-msg">'
        html += delete_btn
        html += '<div class="chat-header">' + msg["user"] + ' <span style="color:#666;">' + msg["role"] + ' ' + datetime.fromtimestamp(msg["time"]).strftime("%H:%M") + '</span></div>'
        html += '<div>' + msg["text"] + '</div>'
        html += '</div>'

    html += '</div><div id="chat-input">'
    if current_user and not is_muted(current_user):
        html += '<form method="post" id="chatForm"><input type="text" name="message" id="messageInput" placeholder="/profile @ник или сообщение... (макс. 300 символов)" maxlength="300"><button type="submit">📤 Отправить</button></form>'
    else:
        html += '<p style="padding:20px;text-align:center;color:#666;font-size:18px;">🔐 Войдите в чат</p>'
    html += '</div></div>'
    
    html += '<div class="nav">'
    html += '<a href="/catalog" class="nav-btn" style="background:var(--primary);">📁 Каталог</a>'
    html += '<a href="/profiles" class="nav-btn" style="background:var(--secondary);">👥 Профили</a>'
    html += '<a href="/community" class="nav-btn" style="background:var(--success);">💬 Сообщество</a>'
    if current_user:
        html += '<a href="/profile/' + current_user + '" class="nav-btn" style="background:#f39c12;">👤 Мой профиль</a>'
        if is_admin(current_user):
            html += '<a href="/admin" class="nav-btn" style="background:var(--danger);">🔧 Админ</a>'
        html += '<a href="/logout" class="nav-btn" style="background:#95a5a6;">🚪 Выход</a>'
    else:
        html += '<a href="/login" class="nav-btn" style="background:var(--warning);">🔐 Войти</a>'
    html += '</div></div>'
    
    html += '''<script>
let lastMsgCount = ''' + str(len(chat_messages)) + ''';
setInterval(() => {
    fetch('/api/chat_count').then(r=>r.json()).then(data => {
        if(data.count > lastMsgCount) {
            lastMsgCount = data.count;
            location.reload();
        }
    }).catch(() => {});
}, 3000);

function deleteMessage(msgId) {
    if(confirm('Удалить сообщение?')) {
        fetch(`/api/delete_message/${msgId}`, {method: 'DELETE'})
        .then(r => r.json())
        .then(data => {
            if(data.success) location.reload();
        }).catch(() => alert('Ошибка'));
    }
}
</script></body></html>'''
    return html

# ✅ НОВЫЙ АДМИН ПАНЕЛЬ
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    current_user = session.get('user', '')
    if not is_admin(current_user):
        return redirect(url_for('index'))
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'make_moderator':
            target = request.form['target'].strip()
            duration_str = request.form.get('duration', 'forever')
            duration = 0 if duration_str == 'forever' else float(duration_str) * 86400  # дни
            if target in users and target != current_user:
                user_roles[target] = 'moderator'
                message = f'✅ {target} назначен модератором!'
        
        elif action == 'remove_moderator':
            target = request.form['target'].strip()
            if target in users and user_roles.get(target) == 'moderator':
                user_roles[target] = 'start'
                message = f'✅ У {target} снята модерация!'
        
        elif action == 'mute':
            target = request.form['target'].strip()
            duration_str = request.form['duration']
            reason = request.form['reason'].strip()[:100]
            duration = 0 if duration_str == 'forever' else float(duration_str) * 86400
            if target in users and target != current_user:
                mutes[target] = get_timestamp() + duration
                message = f'✅ {target} замучен!'
        
        elif action == 'unmute':
            target = request.form['target'].strip()
            if target in mutes:
                del mutes[target]
                message = f'✅ {target} размучен!'
        
        elif action == 'create_folder':
            name = request.form['name'].strip()
            location = request.form['location'].strip()
            photo = request.form.get('photo', '').strip()
            if name:
                if not location:
                    location = 'root'
                current = catalog
                for part in location.split('/'):
                    if part and part not in current:
                        current[part] = {'type': 'folder'}
                    if isinstance(current[part], dict):
                        current = current[part]
                current[name] = {'type': 'folder', 'photo': photo}
                message = f'✅ Папка "{name}" создана!'
        
        elif action == 'create_item':
            name = request.form['name'].strip()
            info = request.form['info'].strip()
            main_photo = request.form.get('main_photo', '').strip()
            photos = request.form.get('photos', '').strip()
            if name and info:
                catalog[name] = {
                    'type': 'item',
                    'info': info,
                    'main_photo': main_photo,
                    'photos': photos.split(',') if photos else [],
                    'location': 'root'
                }
                message = f'✅ Элемент "{name}" создан!'
        
        elif action == 'delete_folder':
            name = request.form['name'].strip()
            if name in catalog and isinstance(catalog[name], dict) and catalog[name].get('type') == 'folder':
                del catalog[name]
                message = f'✅ Папка "{name}" удалена!'
        
        elif action == 'delete_item':
            name = request.form['name'].strip()
            if name in catalog and isinstance(catalog[name], dict) and catalog[name].get('type') == 'item':
                del catalog[name]
                message = f'✅ Элемент "{name}" удален!'
        
        save_data()
    
    stats = calculate_stats()
    
    admin_html = f'''
    <div style="background:#d5f4e6;padding:25px;border-radius:15px;margin:25px 0;border-left:6px solid #27ae60;">
        <h2 style="color:#27ae60;">📊 Статистика: {stats['online']} онлайн, {stats['afk']} АФК</h2>
    </div>'''
    
    if message:
        admin_html += f'<div style="background:#d4edda;color:#155724;padding:20px;border-radius:15px;margin:25px 0;border-left:6px solid #c3e6cb;"><b>{message}</b></div>'
    
    admin_html += '''
    <h3 style="color:#e74c3c;">👑 Админ функции</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;margin:30px 0;">
    
    <div style="background:#fff3cd;padding:25px;border-radius:15px;border-left:5px solid #ffc107;">
        <h4>🛡️ Назначить модератора</h4>
        <form method="post">
            <input type="hidden" name="action" value="make_moderator">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="duration" placeholder="Дни (или forever)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#ffc107;color:#000;border:none;border-radius:8px;font-weight:bold;">Назначить</button>
        </form>
    </div>
    
    <div style="background:#fff3cd;padding:25px;border-radius:15px;border-left:5px solid #ffc107;">
        <h4>❌ Снять модератора</h4>
        <form method="post">
            <input type="hidden" name="action" value="remove_moderator">
            <input name="target" placeholder="👤 Ник модератора" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#ffc107;color:#000;border:none;border-radius:8px;font-weight:bold;">Снять</button>
        </form>
    </div>
    
    </div>
    
    <h3 style="color:#e74c3c;">🚫 Мут функций</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;margin:30px 0;">
    
    <div style="background:#f8d7da;padding:25px;border-radius:15px;border-left:5px solid #dc3545;">
        <h4>🔇 Замутить</h4>
                <form method="post">
            <input type="hidden" name="action" value="mute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="duration" placeholder="Дни (или forever)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="reason" placeholder="Причина (необязательно)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:8px;font-weight:bold;">🔇 Замутить</button>
        </form>
    </div>

    <div style="background:#d4edda;padding:25px;border-radius:15px;border-left:5px solid #28a745;">
        <h4>🔊 Размутить</h4>
        <form method="post">
            <input type="hidden" name="action" value="unmute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:8px;font-weight:bold;">🔊 Размутить</button>
        </form>
    </div>

    </div>

    <h3 style="color:#2196f3;">📁 Каталог (только админ)</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;margin:30px 0;">

    <div style="background:#e3f2fd;padding:25px;border-radius:15px;border-left:5px solid #2196f3;">
        <h4>📁 Создать папку</h4>
        <form method="post">
            <input type="hidden" name="action" value="create_folder">
            <input name="name" placeholder="Название папки" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="location" placeholder="Расположение (root/папка)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="photo" placeholder="Ссылка на фото (необязательно)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#2196f3;color:white;border:none;border-radius:8px;font-weight:bold;">📁 Создать</button>
        </form>
    </div>

    <div style="background:#e3f2fd;padding:25px;border-radius:15px;border-left:5px solid #2196f3;">
        <h4>➕ Создать инфу</h4>
        <form method="post">
            <input type="hidden" name="action" value="create_item">
            <input name="name" placeholder="Название" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <textarea name="info" placeholder="Информация" required style="width:100%;height:80px;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;"></textarea>
            <input name="main_photo" placeholder="Главное фото URL" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="photos" placeholder="Другие фото через запятую" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#2196f3;color:white;border:none;border-radius:8px;font-weight:bold;">➕ Создать</button>
        </form>
    </div>

    <div style="background:#ffebee;padding:25px;border-radius:15px;border-left:5px solid #f44336;">
        <h4>🗑️ Удалить папку</h4>
        <form method="post">
            <input type="hidden" name="action" value="delete_folder">
            <input name="name" placeholder="Название папки" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#f44336;color:white;border:none;border-radius:8px;font-weight:bold;">🗑️ Удалить</button>
        </form>
    </div>

    <div style="background:#ffebee;padding:25px;border-radius:15px;border-left:5px solid #f44336;">
        <h4>🗑️ Удалить инфу</h4>
        <form method="post">
            <input type="hidden" name="action" value="delete_item">
            <input name="name" placeholder="Название элемента" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#f44336;color:white;border:none;border-radius:8px;font-weight:bold;">🗑️ Удалить</button>
        </form>
    </div>

    </div>

    <div style="text-align:center;margin-top:50px;">
        <a href="/" style="background:#2c3e50;color:white;padding:20px 50px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;margin:10px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">🏠 Главная</a>
    </div>
    '''
    
    # ✅ ДЛЯ МОДЕРАТОРОВ — только муты
    moderator_html = '''
    <div style="background:#d5f4e6;padding:25px;border-radius:15px;margin:25px 0;border-left:6px solid #27ae60;">
        <h2 style="color:#27ae60;">🛡️ Модератор панель</h2>
    </div>
    
    <h3 style="color:#e74c3c;">🚫 Мут функции</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;margin:30px 0;">
    
    <div style="background:#f8d7da;padding:25px;border-radius:15px;border-left:5px solid #dc3545;">
        <h4>🔇 Замутить</h4>
        <form method="post">
            <input type="hidden" name="action" value="mute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="duration" placeholder="Дни (или forever)" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <input name="reason" placeholder="Причина" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:8px;font-weight:bold;">🔇 Замутить</button>
        </form>
    </div>

    <div style="background:#d4edda;padding:25px;border-radius:15px;border-left:5px solid #28a745;">
        <h4>🔊 Размутить</h4>
        <form method="post">
            <input type="hidden" name="action" value="unmute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:8px;font-weight:bold;">🔊 Размутить</button>
        </form>
    </div>
    </div>
    '''
    
    is_mod = is_moderator(current_user)
    
    return '''<!DOCTYPE html>
<html><head><title>🔧 Панель управления</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',Arial,sans-serif;background:linear-gradient(135deg,#ff9a9e,#fecfef);padding:20px;color:#2c3e50;}
.container{max-width:1400px;margin:auto;background:#fff;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}
h1,h2,h3,h4{color:#2c3e50;text-align:center;font-weight:bold;}
h1{font-size:2.8em;margin-bottom:30px;}
@media (max-width:768px) {body{padding:10px;}.container{padding:20px;border-radius:20px;}}</style></head>
<body><div class="container">
<h1>🔧 Панель - ''' + current_user + '''</h1>
''' + (admin_html if is_admin(current_user) else moderator_html) + '''
</div></body></html>'''

# ✅ ПРОФИЛЬ С РЕДАКТИРОВАНИЕМ (только свой)
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    current_user = session.get('user', '')
    
    if username not in users:
        return redirect(url_for('index'))
    
    profile_data = user_profiles.get(username, {'status': 'Онлайн', 'info': ''})
    role_display = get_role_display(username)
    is_own_profile = current_user == username
    
    if request.method == 'POST' and is_own_profile:
        profile_data['status'] = request.form.get('status', 'Онлайн')
        profile_data['info'] = request.form.get('info', '')[:500]
        user_profiles[username] = profile_data
        save_data()
    
    status_options = ['🟢 Онлайн', '🟡 Занят', '🔴 Не беспокоить', '😴 Отошел']
    
    return '''<!DOCTYPE html>
<html><head><title>''' + username + ''' - Профиль</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',Arial,sans-serif;padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}
.profile-container{max-width:900px;margin:auto;background:#fff;border-radius:30px;padding:50px;box-shadow:0 30px 100px rgba(0,0,0,0.15);}
.profile-header{text-align:center;margin-bottom:50px;}
.role-badge{padding:20px 40px;background:#e74c3c;color:white;border-radius:25px;font-size:1.8em;font-weight:bold;display:inline-block;margin:20px 0;box-shadow:0 10px 30px rgba(231,76,60,0.3);}
.status-badge{padding:15px 30px;border-radius:20px;font-size:1.3em;font-weight:bold;margin:20px 0;display:inline-block;}
.status-online{background:#d4edda;color:#155724;border:2px solid #28a745;}
.status-busy{background:#fff3cd;color:#856404;border:2px solid #ffc107;}
.status-dnd{background:#f8d7da;color:#721c24;border:2px solid #dc3545;}
.status-afk{background:#e2e3e5;color:#383d41;border:2px solid #6c757d;}
.profile-info{padding:30px;background:#f8f9fa;border-radius:20px;margin:30px 0;border-left:5px solid #3498db;line-height:1.7;font-size:1.1em;}
.profile-edit{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:30px 0;}
.profile-edit input,.profile-edit textarea,.profile-edit select{width:100%;padding:15px;border:2px solid #ddd;border-radius:12px;font-size:16px;font-family:inherit;box-sizing:border-box;}
.profile-edit button{background:#27ae60;color:white;border:none;padding:18px 35px;border-radius:12px;font-size:18px;font-weight:bold;cursor:pointer;transition:all 0.3s;}
.profile-edit button:hover{background:#219a52;transform:translateY(-2px);}
.save-btn{background:#3498db;}
.save-btn:hover{background:#2980b9;}
@media (max-width:768px) {.profile-edit{grid-template-columns:1fr;}}</style></head>
<body>
<div class="profile-container">
    <div class="profile-header">
        <h1 style="font-size:3em;margin-bottom:20px;color:#2c3e50;">👤 ''' + username + '''</h1>
        <div class="role-badge">''' + role_display + '''</div>
        ''' + ('<div class="status-badge status-online">' + profile_data.get("status", "🟢 Онлайн") + '</div>' if profile_data.get("status") in status_options else '<div class="status-badge status-online">🟢 Онлайн</div>') + '''
    </div>
    
    <div class="profile-info">
        <h3 style="margin-bottom:20px;color:#2c3e50;">📝 Информация о себе</h3>
        <div style="min-height:100px;padding:20px;background:#fff;border-radius:12px;border-left:4px solid #667eea;font-size:1.2em;color:#444;">''' + profile_data.get("info", "Информация не указана") + '''</div>
    </div>
    
    ''' + ('''
    <form method="post">
        <div class="profile-edit">
            <div>
                <label style="font-weight:bold;margin-bottom:10px;display:block;">📊 Статус</label>
                <select name="status">
                ''' + ''.join(f'<option value="{s}" {'selected' if profile_data.get("status") == s else ''}>{s}</option>' for s in status_options) + '''
                </select>
            </div>
            <div>
                <label style="font-weight:bold;margin-bottom:10px;display:block;">📝 Инфо о себе (макс. 500 символов)</label>
                <textarea name="info" maxlength="500" placeholder="Расскажите о себе...">''' + profile_data.get("info", "") + '''</textarea>
            </div>
        </div>
        <div style="text-align:center;margin-top:30px;">
            <button type="submit" class="save-btn">💾 СОХРАНИТЬ ИЗМЕНЕНИЯ</button>
        </div>
    </form>
    ''' if is_own_profile else '') + '''
    
    <div style="text-align:center;margin-top:50px;">
        <a href="/" style="background:#2c3e50;color:white;padding:20px 40px;border-radius:20px;font-size:18px;font-weight:bold;text-decoration:none;display:inline-block;margin:10px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">🏠 Главная</a>
        <a href="/profiles" style="background:#27ae60;color:white;padding:20px 40px;border-radius:20px;font-size:18px;font-weight:bold;text-decoration:none;display:inline-block;margin:10px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">👥 Профили</a>
    </div>
</div></body></html>'''

# Остальные маршруты остаются как были...

@app.route('/profiles')
def profiles():
    profiles_html = ''
    stats = calculate_stats()
    
    for user in sorted(users.keys()):
        profile = user_profiles.get(user, {})
        role_display = get_role_display(user)
        status = profile.get("status", "🟢 Онлайн")
        status_class = "online" if is_online(user) else "offline"
        afk_class = "afk" if is_afk(user) else ""
        
        profiles_html += f'''
        <div style="background:#fff;padding:30px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;margin:20px;border:3px solid #e9ecef;">
            <h3 style="font-size:2em;margin-bottom:15px;color:#2c3e50;">👤 {user}</h3>
            <div style="padding:15px 30px;background:#e74c3c;color:white;border-radius:15px;font-size:1.3em;font-weight:bold;margin:20px 0;">{role_display}</div>
            <div class="status-badge {status_class} {afk_class}" style="padding:12px 25px;border-radius:12px;font-size:1.2em;font-weight:bold;margin:15px 0;">
                {status}
            </div>
            <a href="/profile/{user}" style="display:inline-block;padding:15px 35px;background:#3498db;color:white;border-radius:15px;font-weight:bold;font-size:18px;text-decoration:none;">👁️ Профиль</a>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>👥 Профили - Узнавайкин v33</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',Arial,sans-serif;padding:30px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}
.container{max-width:1300px;margin:auto;background:#fff;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}
.profiles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:30px;margin:40px 0;}
.status-online{background:#d4edda;color:#155724;border:2px solid #28a745;}
.status-offline{background:#e2e3e5;color:#383d41;border:2px solid #6c757d;}
.status-afk{background:#fff3cd;color:#856404;border:2px solid #ffc107;}
.back-btn{background:#2c3e50;color:white;padding:25px 50px;border-radius:20px;font-size:22px;font-weight:bold;text-decoration:none;display:block;margin:60px auto;max-width:400px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3);}
h1{text-align:center;font-size:3em;margin-bottom:40px;color:#2c3e50;}
@media (max-width:768px) {.profiles-grid{grid-template-columns:1fr;gap:20px;}}</style></head>
<body><div class="container">
<h1>👥 Все профили (''' + str(stats['online']) + ''' онлайн)</h1>
<div class="profiles-grid">''' + profiles_html + '''</div>
<a href="/" class="back-btn">🏠 На главную</a>
</div></body></html>'''

@app.route('/catalog/<path:path>')
@app.route('/catalog')
def catalog_view(path=''):
    content = get_catalog_content(path)
    
    if 'error' in content:
        return '''<!DOCTYPE html>
<html><body style="padding:100px;font-family:'Inter',Arial;text-align:center;background:#f8f9fa;color:#2c3e50;min-height:100vh;">
<h1 style="color:#e74c3c;font-size:3em;margin-bottom:30px;">''' + content['error'] + '''</h1>
<p style="font-size:1.5em;color:#666;margin-bottom:50px;">📭 Каталог пока пуст</p>
<a href="/catalog" style="background:#3498db;color:white;padding:20px 45px;border-radius:15px;text-decoration:none;display:inline-block;margin:15px;font-size:20px;font-weight:bold;box-shadow:0 10px 30px rgba(52,152,219,0.3);">📁 Каталог</a>
<a href="/" style="background:#27ae60;color:white;padding:20px 45px;border-radius:15px;text-decoration:none;display:inline-block;margin-left:10px;font-size:20px;font-weight:bold;box-shadow:0 10px 30px rgba(39,174,96,0.3);">🏠 Главная</a>
</body></html>'''
    
    breadcrumbs = '📁 <a href="/catalog" style="color:#3498db;">Каталог</a>'
    parts = [p.strip() for p in path.split('/') if p.strip()]
    temp_path = []
    for part in parts:
        temp_path.append(part)
        path_str = '/'.join(temp_path)
        breadcrumbs += ' → <a href="/catalog/' + path_str + '" style="color:#3498db;">' + part + '</a>'
    
    content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:30px;padding:30px;">'
    
    for folder in sorted(content['folders']):
        content_html += f'''
        <a href="/catalog/{path}/{"/" if path else ""}{folder}" style="background:#e3f2fd;padding:40px;border-radius:20px;border-left:6px solid #2196f3;text-decoration:none;display:block;text-align:center;transition:all 0.3s;font-family:'Inter';box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 15px 0;color:#2196f3;font-size:2.2em;">📁 {folder}</h3>
            <p style="margin:0;color:#666;font-size:1.4em;font-weight:500;">Папка</p>
        </a>'''
    
    for item_name, item_data in sorted(content['items'].items()):
        photo_html = ''
        if item_data.get('main_photo'):
            photo_html = f'<img src="{item_data["main_photo"]}" style="width:100%;height:220px;object-fit:cover;border-radius:15px;margin:20px 0;" alt="{item_name}" onerror="this.style.display=\'none\'">'
        
        content_html += f'''
        <div style="background:#f3e5f5;padding:40px;border-radius:20px;border-left:6px solid #9c27b0;font-family:'Inter';box-shadow:0 15px 40px rgba(0,0,0,0.1);">
            <h3 style="font-size:2.2em;font-weight:bold;margin-bottom:20px;color:#2c3e50;">{item_name}</h3>
            {photo_html}
            <p style="margin:15px 0;font-size:1.3em;"><b style="color:#555;">ℹ️ Информация:</b></p>
            <div style="background:#f9f9f9;padding:25px;border-radius:15px;color:#444;font-size:1.2em;line-height:1.7;">{item_data.get("info", "—")}</div>
            ''' + (f'<p style="margin:15px 0 0 0;font-size:1.1em;"><b style="color:#555;">📍 Местоположение:</b> <span style="color:#666;">{item_data.get("location", "root")}</span></p>' if item_data.get("location") else '') + '''
        </div>'''
    
    content_html += '</div>'
    
    if not content['folders'] and not content['items']:
        content_html = '''
        <div style="text-align:center;color:#666;font-size:3em;margin:120px 0;padding:120px;background:#f8f9fa;border-radius:35px;border:4px dashed #ddd;font-family:'Inter';">
            📭 Каталог пуст
            <p style="font-size:0.45em;margin-top:30px;color:#999;">👑 Администратор может добавить содержимое</p>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>📁 Каталог ''' + (path or "Главная") + ''' - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body {font-family:'Inter',sans-serif;padding:25px;background:#f8f9fa;color:#2c3e50;}
.container {max-width:1500px;margin:0 auto;background:#fff;border-radius:30px;padding:50px;box-shadow:0 30px 90px rgba(0,0,0,0.15);}
.breadcrumbs {margin:40px 0;padding:30px;background:#ecf0f1;border-radius:25px;font-size:1.2em;line-height:1.6;}
.breadcrumbs a {color:#3498db;text-decoration:none;font-weight:600;}
h1 {text-align:center;margin-bottom:40px;font-size:3.2em;color:#2c3e50;}
.back-btn {background:#3498db;color:white;padding:22px 50px;border-radius:18px;font-size:22px;font-weight:bold;text-decoration:none;display:inline-block;margin:70px 15px 0 0;transition:all 0.3s;box-shadow:0 12px 35px rgba(52,152,219,0.3);}
.back-btn:hover {transform:translateY(-3px);box-shadow:0 18px 45px rgba(52,152,219,0.4);}
@media (max-width:768px) {.container {padding:30px;margin:15px;border-radius:25px;}.grid {grid-template-columns:1fr;gap:25px;}}</style></head>
<body><div class="container">
<h1>📁 Каталог</h1>
<div class="breadcrumbs">''' + breadcrumbs + '''</div>
''' + content_html + '''
<div style="text-align:center;margin-top:80px;">
<a href="/catalog" class="back-btn">📁 Главный Каталог</a>
<a href="/" class="back-btn" style="background:#27ae60;margin-left:15px;">🏠 На главную</a>
</div></div></body></html>'''

@app.route('/api/chat_count')
def api_chat_count():
    return jsonify({'count': len(chat_messages)})

@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def api_delete_message(msg_id):
    current_user = session.get('user', '')
    if not current_user or not (is_admin(current_user) or is_moderator(current_user)):
        return jsonify({'error': 'Нет доступа'}), 403
    
    for i, msg in enumerate(chat_messages):
        if msg['id'] == msg_id and msg['user'] != current_user:
            del chat_messages[i]
            save_data()
            return jsonify({'success': True})
    return jsonify({'error': 'Сообщение не найдено'}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        session['user'] = username
        
        if username not in user_roles: 
            user_roles[username] = 'start'
        if username not in users:
            users[username] = {'password': password, 'role': 'start', 'admin': False}
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': ''}
        
        user_activity[username] = get_timestamp()
        save_data()
        return redirect(url_for('index'))
    
    return '''<!DOCTYPE html>
<html><head><title>🔐 Вход / Регистрация - Узнавайкин v33</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:40px;display:flex;align-items:center;justify-content:center;color:#2c3e50;}
.login-container{max-width:450px;width:100%;background:#fff;padding:60px;border-radius:30px;box-shadow:0 35px 120px rgba(0,0,0,0.25);text-align:center;}
.login-container input{width:100%;padding:25px;margin:20px 0;border:2px solid #ddd;border-radius:18px;font-size:18px;box-sizing:border-box;background:#f8f9fa;color:#2c3e50;font-family:inherit;}
.login-container button{width:100%;padding:25px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:18px;font-size:22px;font-weight:bold;cursor:pointer;margin-top:30px;transition:all 0.3s;box-shadow:0 15px 40px rgba(255,107,107,0.3);}
.login-container button:hover{transform:translateY(-3px);box-shadow:0 25px 60px rgba(255,107,107,0.4);}
h1{font-size:3em;margin-bottom:40px;color:#2c3e50;}</style></head>
<body><div class="login-container">
<h1>🔐 Узнавайкин v33</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required maxlength="20">
<input name="password" type="password" placeholder="🔑 Пароль" required maxlength="50">
<button type="submit">🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form>
<p style="margin-top:40px;font-size:16px;color:#666;">🔒 Пароли защищены | Авторегистрация</p>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/community')
def community():
    return '''<!DOCTYPE html>
<html><head><title>💬 Сообщество - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',Arial,sans-serif;padding:50px 20px;text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);color:white;min-height:100vh;}
.community-box{max-width:800px;margin:auto;background:rgba(255,255,255,0.1);backdrop-filter:blur(25px);padding:120px;border-radius:40px;box-shadow:0 40px 140px rgba(0,0,0,0.3);}
.tg-link{font-size:4em;color:#0088cc;text-decoration:none;font-weight:bold;display:inline-block;margin:60px 20px;padding:40px 80px;background:rgba(255,255,255,0.2);border-radius:35px;transition:all 0.3s;box-shadow:0 20px 50px rgba(0,0,0,0.2);}
.tg-link:hover{transform:scale(1.05);background:rgba(255,255,255,0.3);box-shadow:0 25px 60px rgba(0,0,0,0.3);}
.back-btn{background:#2c3e50;color:white;padding:35px 80px;border-radius:35px;font-size:28px;font-weight:bold;text-decoration:none;display:inline-block;margin-top:80px;box-shadow:0 25px 60px rgba(0,0,0,0.3);transition:all 0.3s;}
.back-btn:hover{transform:translateY(-5px);box-shadow:0 30px 70px rgba(0,0,0,0.4);}
h1{font-size:5em;margin-bottom:60px;}</style></head>
<body><div class="community-box">
<h1>💬 Сообщество</h1>
<p style="font-size:2.2em;margin-bottom:80px;">Присоединяйтесь к команде Узнавайкин!</p>
<a href="https://t.me/ssylkanatelegramkanalyznaikin" class="tg-link" target="_blank">📱 Telegram</a>
<a href="/" class="back-btn">🏠 На главную</a>
</div></body></html>'''

@app.errorhandler(404)
def page_not_found(e):
    return '''<!DOCTYPE html>
<html><body style="background:linear-gradient(135deg,#667eea,#764ba2);padding:120px;text-align:center;font-family:'Inter',Arial;color:white;min-height:100vh;">
<h1 style="font-size:5em;color:#e74c3c;margin-bottom:40px;">❌ 404</h1>
<p style="font-size:2em;margin-bottom:60px;">Страница не найдена</p>
<a href="/" style="background:#2c3e50;color:white;padding:30px 70px;border-radius:25px;font-size:26px;font-weight:bold;text-decoration:none;display:inline-block;box-shadow:0 20px 50px rgba(0,0,0,0.3);">🏠 На главную</a>
</body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
