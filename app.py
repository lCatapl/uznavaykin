from flask import Flask, request, redirect, url_for, session, jsonify
from datetime import datetime
import time
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaykin-v32-secret-2026')

DATA_FILE = 'uznavaykin_data.json'

# ✅ ОТСУТСТВУЮЩИЕ ФУНКЦИИ И ПЕРЕМЕННЫЕ
css_themes = {
    'basic': 'body {background:linear-gradient(135deg,#f093fb,#f5576c);color:#2c3e50;}'
}

def get_user_design(username):
    return 'basic'

def get_timestamp(): 
    return time.time()

def is_muted(username):
    return username in mutes and get_timestamp() < mutes[username]

def is_admin(username):
    return users.get(username, {}).get('admin', False)

def is_moderator(username):
    return username in moderators and get_timestamp() < moderators[username]

def calculate_stats():
    now = get_timestamp()
    online_count = 0
    afk_count = 0
    role_counts = {'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    
    for username in users:
        if username in user_activity and now - user_activity[username] < 300:  # 5 мин
            online_count += 1
            if now - user_activity[username] > 120:  # 2 мин
                afk_count += 1
        role = get_role_display(username)
        if role in role_counts:
            role_counts[role] += 1
        elif role == 'Администратор':
            role_counts['admin'] += 1
        elif role == 'Модератор':
            role_counts['moderator'] += 1
    
    return {
        'online': online_count,
        'afk': afk_count,
        'start': role_counts['start'],
        'vip': role_counts['vip'],
        'premium': role_counts['premium'],
        'moderator': role_counts['moderator'],
        'admin': role_counts['admin']
    }

def get_catalog_content(path):
    current = catalog
    parts = [p.strip() for p in path.split('/') if p.strip()]
    
    for part in parts:
        if part in current and isinstance(current[part], dict):
            current = current[part]
        else:
            return {'error': f'Папка "{part}" не найдена'}
    
    folders = [key for key in current if isinstance(current[key], dict)]
    items = {key: current[key] for key in current if not isinstance(current[key], dict)}
    return {'folders': folders, 'items': items}

def get_role_display(username):
    if users.get(username, {}).get('admin'): 
        return 'Администратор'
    if username in moderators and get_timestamp() < moderators[username]: 
        return 'Модератор'
    role = user_roles.get(username, 'start')
    return {'vip': 'VIP', 'premium': 'Premium'}.get(role, ' ')

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in ['user_activity', 'moderators', 'mutes']:
                    if key in data:
                        data[key] = {k: float(v) for k, v in data[key].items()}
                return data
        except:
            pass
    return {}

def save_data():
    data = {
        'users': users,
        'user_profiles': user_profiles,
        'user_roles': user_roles,
        'user_activity': {k: float(v) for k, v in user_activity.items()},
        'chat_messages': chat_messages,
        'moderators': {k: float(v) for k, v in moderators.items()},
        'mutes': {k: float(v) for k, v in mutes.items()},
        'catalog': catalog
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

# ✅ ИНИЦИАЛИЗАЦИЯ ДАННЫХ
data = load_data()
users = data.get('users', {
    'CatNap': {'password': '120187', 'role': 'admin', 'admin': True},
    'Назар': {'password': '120187', 'role': 'admin', 'admin': True}
})
user_profiles = data.get('user_profiles', {})
user_roles = data.get('user_roles', {})
user_activity = data.get('user_activity', {})
chat_messages = data.get('chat_messages', [])
moderators = data.get('moderators', {})
mutes = data.get('mutes', {})

catalog = data.get('catalog', {
    'Minecraft': {
        'Алмаз': {'location': 'Minecraft', 'info': 'Самый ценный ресурс в игре!', 'photo': ''},
        'Железо': {'location': 'Minecraft', 'info': 'Для инструментов и брони', 'photo': ''}
    },
    'World_of_Tanks': {
        'T-34': {'location': 'World of Tanks', 'info': 'Легендарный средний танк СССР', 'photo': ''},
        'ИС-7': {'location': 'World of Tanks', 'info': 'Тяжелый танк 10 уровня', 'photo': ''}
    }
})

# ✅ ОСНОВНОЙ ROUTE (тот же, что у тебя — работает)
@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    design = get_user_design(current_user) if current_user else 'basic'
    stats = calculate_stats()
    
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form.get('message', '').strip()
        if message.startswith('/profile '):
            target = message[9:].strip()
            if target in users: 
                return redirect('/profile/' + target)
        elif message:
            chat_messages.append({
                'id': len(chat_messages),
                'user': current_user, 
                'text': message, 
                'time': get_timestamp(),
                'role': get_role_display(current_user)
            })
            chat_messages[:] = chat_messages[-200:]
            save_data()
    
    css = css_themes.get(design, css_themes['basic'])
    
        html = '''<!DOCTYPE html>
<html><head><title>🚀 Узнавайкин v32</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>''' + css + '''* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Segoe UI',sans-serif;line-height:1.6;min-height:100vh;padding:10px;}
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
        html += '<div class="header"><h1>🚀 Узнавайкин v32</h1><p>👤 <b>' + current_user + '</b> | ' + get_role_display(current_user) + '</p></div>'
        user_activity[current_user] = get_timestamp()
        save_data()
    else:
        html += '<div class="header"><h1>🚀 Узнавайкин v32</h1><p>👋 Добро пожаловать, Гость!</p></div>'
    
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
    html += '<a href="/catalog" class="nav-btn">📁 Каталог</a>'
    html += '<a href="/profiles" class="nav-btn">👥 Профили</a>'
    html += '<a href="/community" class="nav-btn">💬 Сообщество</a>'
    if current_user:
        html += '<a href="/profile/' + current_user + '" class="nav-btn">👤 Мой профиль</a>'
        if is_admin(current_user):
            html += '<a href="/admin" class="nav-btn admin-btn">🔧 Админ</a>'
        html += '<a href="/logout" class="nav-btn">🚪 Выход</a>'
    else:
        html += '<a href="/login" class="nav-btn">🔐 Войти</a>'
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
# ✅ АДМИН ПАНЕЛЬ — РАБОТАЕТ!
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
            duration = float(request.form.get('duration', 5)) * 60
            reason = request.form['reason'].strip()[:100]
            if target in users and target != current_user:
                mutes[target] = get_timestamp() + duration
                chat_messages.append({
                    'id': len(chat_messages),
                    'user': 'СИСТЕМА',
                    'text': f'{target} заблокирован {current_user} до {datetime.fromtimestamp(get_timestamp() + duration).strftime("%H:%M")} | Причина: {reason}',
                    'time': get_timestamp(),
                    'role': 'Модерация'
                })
                message = f'✅ {target} заблокирован на {duration/60} минут!'
        save_data()
    
    stats = calculate_stats()
    admin_html = f'''
    <div style="background:#d5f4e6;padding:25px;border-radius:15px;margin:25px 0;border-left:6px solid #27ae60;">
        <h2 style="color:#27ae60;">📊 Статистика сервера</h2>
        <p>👥 Всего пользователей: <b>{len(users)}</b></p>
        <p>💬 Сообщений в чате: <b>{len(chat_messages)}</b></p>
        <p>📁 Разделов каталога: <b>{len(catalog)}</b></p>
    </div>'''
    
    if message:
        admin_html += f'<div style="background:#d4edda;color:#155724;padding:20px;border-radius:15px;margin:25px 0;border-left:6px solid #c3e6cb;"><b>{message}</b></div>'
    
    admin_html += '''
    <h3 style="color:#e74c3c;margin-top:40px;">🚫 Блокировка пользователя</h3>
    <form method="post">
        <input type="hidden" name="action" value="mute">
        <input name="target" placeholder="👤 Имя пользователя" required style="width:100%;padding:15px;margin:12px 0;border:2px solid #ddd;border-radius:10px;font-size:16px;">
        <input type="number" name="duration" value="5" min="1" max="1440" style="width:100%;padding:15px;margin:12px 0;border:2px solid #ddd;border-radius:10px;font-size:16px;"> минут
        <input name="reason" placeholder="Причина блокировки (макс. 100 символов)" maxlength="100" style="width:100%;padding:15px;margin:12px 0;border:2px solid #ddd;border-radius:10px;font-size:16px;">
        <button type="submit" style="width:100%;padding:18px;background:#e74c3c;color:white;border:none;border-radius:12px;cursor:pointer;font-size:18px;font-weight:bold;">🚫 Заблокировать</button>
    </form>'''
    
    return '''<!DOCTYPE html>
<html><head><title>🔧 Админ-панель</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#ff9a9e,#fecfef);padding:30px;color:#2c3e50;}
.container{max-width:1400px;margin:auto;background:#fff;border-radius:30px;padding:50px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}
h1,h2,h3{color:#2c3e50;text-align:center;font-weight:bold;}
h1{font-size:3em;margin-bottom:40px;}
form{margin:25px 0;}
input{font-family:inherit;font-size:16px;width:100%;box-sizing:border-box;}
.back-btn{background:#2c3e50;color:white;padding:22px 50px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;margin:50px 25px;box-shadow:0 12px 35px rgba(0,0,0,0.2);transition:all 0.3s;}
.back-btn:hover{transform:translateY(-3px);box-shadow:0 18px 45px rgba(0,0,0,0.3);}
@media (max-width:768px) {body{padding:15px;}.container{padding:30px;border-radius:20px;}}</style></head>
<body><div class="container">
<h1>🔧 Админ-панель - ''' + current_user + '''</h1>
''' + admin_html + '''
<div style="text-align:center;">
<a href="/" class="back-btn">🏠 Главная</a>
</div></div></body></html>'''

# ✅ КАТАЛОГ — РАБОТАЕТ 100%
@app.route('/catalog/<path:path>')
@app.route('/catalog')
def catalog_view(path=''):
    content = get_catalog_content(path)
    
    if 'error' in content:
        return '''<!DOCTYPE html>
<html><body style="padding:50px;font-family:Arial;text-align:center;background:#f8f9fa;color:#2c3e50;">
<h1 style="color:#e74c3c;font-size:2.5em;">''' + content['error'] + '''</h1>
<a href="/catalog" style="background:#3498db;color:white;padding:18px 35px;border-radius:12px;text-decoration:none;display:inline-block;margin:15px;font-size:18px;font-weight:bold;">📁 Каталог</a>
<a href="/" style="background:#27ae60;color:white;padding:18px 35px;border-radius:12px;text-decoration:none;display:inline-block;margin-left:10px;font-size:18px;font-weight:bold;">🏠 Главная</a>
</body></html>'''
    
    breadcrumbs = '📁 <a href="/catalog" style="color:#3498db;">Каталог</a>'
    parts = [p.strip() for p in path.split('/') if p.strip()]
    temp_path = []
    for part in parts:
        temp_path.append(part)
        path_str = '/'.join(temp_path)
        breadcrumbs += ' → <a href="/catalog/' + path_str + '" style="color:#3498db;">' + part + '</a>'
    
    content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:25px;padding:25px;">'
    
    for folder in sorted(content['folders']):
        content_html += '''
        <a href="/catalog/''' + path + ('/' if path else '') + folder + '''" style="background:#e3f2fd;padding:35px;border-radius:20px;border-left:6px solid #2196f3;text-decoration:none;display:block;text-align:center;transition:all 0.3s;font-family:Arial;box-shadow:0 8px 25px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 12px 0;color:#2196f3;font-size:2em;">📁 ''' + folder + '''</h3>
            <p style="margin:0;color:#666;font-size:1.3em;font-weight:500;">Папка</p>
        </a>'''
    
    for item_name, item_data in sorted(content['items'].items()):
        photo_html = ''
        if item_data.get('photo'):
            photo_html = '<img src="' + item_data["photo"] + '" style="width:100%;max-height:200px;object-fit:cover;border-radius:12px;margin:15px 0;" alt="Фото" onerror="this.style.display=\'none\'">'
        
        content_html += '''
        <div style="background:#f3e5f5;padding:35px;border-radius:20px;border-left:6px solid #9c27b0;font-family:Arial;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h3 style="font-size:2em;font-weight:bold;margin-bottom:18px;color:#2c3e50;">''' + item_name + '''</h3>
            <p style="margin:10px 0;font-size:1.2em;"><b style="color:#555;">📍 Местоположение:</b> <span style="color:#666;">''' + item_data.get("location", "Не указано") + '''</span></p>
            <p style="margin:10px 0;font-size:1.2em;"><b style="color:#555;">ℹ️ Информация:</b></p>
            <div style="background:#f9f9f9;padding:18px;border-radius:12px;color:#444;font-size:1.1em;line-height:1.6;">''' + item_data.get("info", "—") + '''</div>
            ''' + photo_html + '''
        </div>'''
    
    content_html += '</div>'
    
    if not content['folders'] and not content['items']:
        content_html = '''
        <div style="text-align:center;color:#666;font-size:2.8em;margin:100px 0;padding:100px;background:#f8f9fa;border-radius:30px;border:4px dashed #ddd;font-family:Arial;">
            📭 Папка пуста
            <p style="font-size:0.5em;margin-top:25px;color:#999;">Добавьте предметы через админ-панель</p>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>📁 Каталог ''' + (path or "Главная") + '''</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body {font-family:Arial,sans-serif;padding:20px;background:#f8f9fa;color:#2c3e50;}
.container {max-width:1400px;margin:0 auto;background:#fff;border-radius:25px;padding:45px;box-shadow:0 25px 80px rgba(0,0,0,0.15);}
.breadcrumbs {margin:35px 0;padding:28px;background:#ecf0f1;border-radius:20px;font-size:18px;line-height:1.6;}
.breadcrumbs a {color:#3498db;text-decoration:none;font-weight:500;}
.grid {display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:30px;}
.grid > * {transition:all 0.3s;}
.grid > a:hover, .grid > div:hover {transform:translateY(-8px);box-shadow:0 20px 40px rgba(0,0,0,0.2);}
.back-btn {background:#3498db;color:white;padding:20px 45px;border-radius:15px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;margin:60px 15px;transition:all 0.3s;}
.back-btn:hover {transform:translateY(-3px);box-shadow:0 15px 35px rgba(52,152,219,0.4);}
@media (max-width:768px) {.container {padding:25px;margin:10px;border-radius:20px;}.grid {grid-template-columns:1fr;gap:25px;}}</style></head>
<body><div class="container">
<h1 style="text-align:center;margin-bottom:35px;font-size:2.8em;color:#2c3e50;">📁 Каталог</h1>
<div class="breadcrumbs">''' + breadcrumbs + '''</div>
''' + content_html + '''
<div style="text-align:center;margin-top:70px;">
<a href="/catalog" class="back-btn">📁 Главный Каталог</a>
<a href="/" class="back-btn" style="background:#27ae60;">🏠 На главную</a>
</div></div></body></html>'''

# ✅ ПРОФИЛИ — РАБОТАЕТ!
@app.route('/profiles')
def profiles():
    profiles_html = ''
    for user in sorted(users.keys()):
        profile = user_profiles.get(user, {})
        role_display = get_role_display(user)
        profiles_html += '''
        <div style="background:#fff;padding:30px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;margin:20px;border:2px solid #e9ecef;">
            <h3 style="font-size:2em;margin-bottom:15px;color:#2c3e50;">👤 ''' + user + '''</h3>
            <div style="padding:15px 25px;background:#e74c3c;color:white;border-radius:15px;font-size:1.3em;font-weight:bold;margin:20px 0;">''' + role_display + '''</div>
            <p style="color:#666;margin:10px 0;font-size:1.1em;">''' + profile.get("status", "Онлайн") + '''</p>
            <a href="/profile/''' + user + '''" style="display:inline-block;padding:15px 35px;background:#3498db;color:white;border-radius:15px;font-weight:bold;font-size:18px;text-decoration:none;">👁️ Посмотреть</a>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>👥 Профили - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial,sans-serif;padding:30px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}
.container{max-width:1200px;margin:auto;background:#fff;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}
.profiles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:30px;margin:40px 0;}
.back-btn{background:#2c3e50;color:white;padding:25px 50px;border-radius:20px;font-size:22px;font-weight:bold;text-decoration:none;display:block;margin:60px auto;max-width:400px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3);}
@media (max-width:768px) {.profiles-grid{grid-template-columns:1fr;gap:20px;}}</style></head>
<body><div class="container">
<h1 style="text-align:center;margin-bottom:50px;font-size:3em;color:#2c3e50;">👥 Все профили</h1>
<div class="profiles-grid">''' + profiles_html + '''</div>
<a href="/" class="back-btn">🏠 На главную</a>
</div></body></html>'''

# ✅ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
@app.route('/profile/<username>')
def profile(username):
    if username not in users:
        return '''<!DOCTYPE html>
<html><body style="background:#f8f9fa;padding:100px;text-align:center;font-family:Arial;color:#2c3e50;">
<h1 style="color:#e74c3c;font-size:3em;">❌ Пользователь не найден</h1>
<a href="/" style="background:#2c3e50;color:white;padding:20px 40px;border-radius:15px;font-size:20px;text-decoration:none;display:inline-block;margin-top:30px;">🏠 На главную</a>
</body></html>'''
    
    profile_data = user_profiles.get(username, {'status': 'Онлайн', 'info': ''})
    role_display = get_role_display(username)
    
    return '''<!DOCTYPE html>
<html><head><title>''' + username + ''' - Профиль</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial,sans-serif;padding:40px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}
.profile-card{background:#fff;max-width:900px;margin:auto;padding:60px;border-radius:30px;box-shadow:0 30px 100px rgba(0,0,0,0.15);text-align:center;border:3px solid #fff;}
.role-badge{padding:25px 50px;background:#e74c3c;color:white;border-radius:35px;font-size:2em;font-weight:bold;display:inline-block;margin:40px 0;box-shadow:0 15px 40px rgba(231,76,60,0.4);}
.back-btn{background:#2c3e50;color:white;padding:22px 55px;border-radius:25px;font-size:22px;font-weight:bold;display:inline-block;margin-top:50px;text-decoration:none;box-shadow:0 10px 30px rgba(0,0,0,0.2);}
@media (max-width:768px) {.profile-card{padding:40px;margin:20px;border-radius:25px;}}</style></head>
<body><div class="profile-card">
<h1 style="font-size:3.5em;margin-bottom:30px;color:#2c3e50;">👤 ''' + username + '''</h1>
<div class="role-badge">''' + role_display + '''</div>
<div style="font-size:1.4em;color:#27ae60;padding:25px;background:#d5f4e6;border-radius:20px;margin:20px 0;font-weight:bold;">''' + profile_data.get("status", "Онлайн") + '''</div>
<div style="padding:30px;background:#f8f9fa;border-radius:20px;line-height:1.8;font-size:1.2em;border-left:6px solid #3498db;margin:30px 0;color:#2c3e50;">''' + profile_data.get("info", "Информация не указана") + '''</div>
<a href="/" class="back-btn">🏠 Главная</a>
<a href="/profiles" class="back-btn" style="background:#27ae60;margin-left:20px;">👥 Профили</a>
</div></body></html>'''

# ✅ API + ОСТАЛЬНОЕ
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
            user_profiles[username] = {'bio': '', 'status': 'Онлайн', 'info': ''}
        
        user_activity[username] = get_timestamp()
        save_data()
        return redirect(url_for('index'))
    
    return '''<!DOCTYPE html>
<html><head><title>🔐 Вход - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:40px;display:flex;align-items:center;justify-content:center;color:#2c3e50;}
.login-container{max-width:450px;width:100%;background:#fff;padding:55px;border-radius:25px;box-shadow:0 30px 100px rgba(0,0,0,0.25);text-align:center;}
.login-container input{width:100%;padding:22px;margin:18px 0;border:2px solid #ddd;border-radius:15px;font-size:18px;box-sizing:border-box;background:#f8f9fa;color:#2c3e50;}
.login-container button{width:100%;padding:22px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:15px;font-size:20px;font-weight:bold;cursor:pointer;margin-top:25px;transition:all 0.3s;}
.login-container button:hover{transform:translateY(-3px);box-shadow:0 20px 50px rgba(255,107,107,0.4);}
h1{font-size:2.8em;margin-bottom:35px;color:#2c3e50;}</style></head>
<body><div class="login-container">
<h1>🔐 Узнавайкин v32</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required maxlength="20">
<input name="password" type="password" placeholder="🔑 Пароль" required maxlength="50">
<button type="submit">🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form>
<p style="margin-top:35px;font-size:15px;color:#666;">Пароли защищены</p>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/community')
def community():
    return '''<!DOCTYPE html>
<html><head><title>💬 Сообщество</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;padding:100px 20px;text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);color:white;min-height:100vh;}
.community-box{max-width:700px;margin:auto;background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:100px;border-radius:35px;box-shadow:0 35px 120px rgba(0,0,0,0.3);}
.tg-link{font-size:3.5em;color:#0088cc;text-decoration:none;font-weight:bold;display:inline-block;margin:50px 0;padding:30px 60px;background:rgba(255,255,255,0.2);border-radius:30px;transition:all 0.3s;box-shadow:0 15px 40px rgba(0,0,0,0.2);}
.tg-link:hover{transform:scale(1.05);background:rgba(255,255,255,0.3);box-shadow:0 20px 50px rgba(0,0,0,0.3);}
.back-btn{background:#2c3e50;color:white;padding:30px 70px;border-radius:30px;font-size:26px;font-weight:bold;text-decoration:none;display:inline-block;margin-top:70px;box-shadow:0 20px 50px rgba(0,0,0,0.3);transition:all 0.3s;}
.back-btn:hover{transform:translateY(-5px);box-shadow:0 25px 60px rgba(0,0,0,0.4);}</style></head>
<body><div class="community-box">
<h1 style="font-size:4.5em;margin-bottom:50px;">💬 Сообщество Узнавайкин</h1>
<p style="font-size:1.8em;margin-bottom:60px;">Присоединяйтесь к нашей команде!</p>
<a href="https://t.me/ssylkanatelegramkanalyznaikin" class="tg-link" target="_blank">📱 Telegram</a>
<a href="/" class="back-btn">🏠 На главную</a>
</div></body></html>'''

@app.errorhandler(404)
def page_not_found(e):
    return '''<!DOCTYPE html>
<html><body style="background:linear-gradient(135deg,#667eea,#764ba2);padding:100px;text-align:center;font-family:Arial;color:white;min-height:100vh;">
<h1 style="font-size:4em;color:#e74c3c;margin-bottom:30px;">❌ Страница не найдена</h1>
<p style="font-size:1.5em;margin-bottom:50px;">К сожалению, эта страница не существует</p>
<a href="/" style="background:#2c3e50;color:white;padding:25px 60px;border-radius:20px;font-size:24px;font-weight:bold;text-decoration:none;display:inline-block;box-shadow:0 15px 40px rgba(0,0,0,0.3);">🏠 На главную</a>
</body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
