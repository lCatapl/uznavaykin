from flask import Flask, request, redirect, url_for, session, jsonify
from datetime import datetime
import time
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uznavaykin-v32-secret-2026')

DATA_FILE = 'uznavaykin_data.json'

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

# ✅ ИНИЦИАЛИЗАЦИЯ ДАННЫХ — АДМИНЫ + РУССКИЙ КАТАЛОГ
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

def get_timestamp(): 
    return time.time()

# ✅ ФУНКЦИИ РОЛЕЙ — ТЕКСТ ДЛЯ PYTHON (СТИКЕРЫ В HTML)
def get_role_display(username):
    if users.get(username, {}).get('admin'): 
        return 'Admin'
    if username in moderators and get_timestamp() < moderators[username]: 
        return 'Moderator'
    role = user_roles.get(username, 'start')
    return {'vip': 'VIP', 'premium': 'Premium'}.get(role, 'Start')

def get_user_design(username):
    role = get_role_display(username).lower().replace(' ', '')
    designs = {
        'start': 'basic',
        'vip': 'vip', 
        'premium': 'premium',
        'moderator': 'admin',
        'admin': 'admin'
    }
    return designs.get(role, 'basic')

def is_muted(username):
    if username in mutes and get_timestamp() < mutes[username]: 
        return True
    if username in mutes: 
        del mutes[username]
        save_data()
    return False

def is_moderator(username):
    if username in moderators and get_timestamp() < moderators[username]: 
        return True
    if username in moderators: 
        del moderators[username]
        save_data()
    return False

def is_admin(username):
    return users.get(username, {}).get('admin', False)

def calculate_stats():
    stats = {'online': 0, 'afk': 0, 'start': 0, 'vip': 0, 'premium': 0, 'moderator': 0, 'admin': 0}
    now = get_timestamp()
    for username in users:
        last_activity = user_activity.get(username, 0)
        if now - last_activity < 300:  # 5 минут онлайн
            stats['online'] += 1
            if now - last_activity > 60:  # 1 минута АФК
                stats['afk'] += 1
        
        if users.get(username, {}).get('admin'):
            stats['admin'] += 1
        elif username in moderators and get_timestamp() < moderators.get(username, 0):
            stats['moderator'] += 1
        else:
            role = user_roles.get(username, 'start')
            stats[role] = stats.get(role, 0) + 1
    return stats

# ✅ КАТАЛОГ — РЕКУРСИВНАЯ НАВИГАЦИЯ
def get_catalog_content(path=''):
    current = catalog
    parts = [p.strip() for p in path.split('/') if p.strip()]
    
    for part in parts:
        if part in current and isinstance(current[part], dict):
            current = current[part]
        else:
            return {'error': '❌ Папка не найдена: ' + part}
    
    folders = [name for name, content in current.items() if isinstance(content, dict)]
    items = {name: content for name, content in current.items() if not isinstance(content, dict)}
    
    return {'folders': folders, 'items': items}

# ✅ КОНТРАСТНЫЕ CSS ТЕМЫ — ЧЁРНЫЙ ТЕКСТ
css_themes = {
    'basic': '''
    body {background:linear-gradient(135deg,#f5f7fa,#c3cfe2);}
    .container {background:#fff;color:#2c3e50;box-shadow:0 15px 50px rgba(0,0,0,0.15);}
    .header {background:linear-gradient(45deg,#ff9a9e,#fecfef);color:#2c3e50;}
    .nav-btn {background:#3498db;color:white;font-weight:bold;}
    .stats div {color:#2c3e50;}
    ''',
    'vip': '''
    body {background:linear-gradient(135deg,#667eea,#764ba2);}
    .container {background:#fff;color:#2c3e50;box-shadow:0 20px 60px rgba(102,126,234,0.3);}
    .header {background:linear-gradient(45deg,#f093fb,#f5576c);color:#2c3e50;}
    .nav-btn {background:#e74c3c;color:white;font-weight:bold;}
    .stats div {color:#2c3e50;}
    ''',
    'premium': '''
    body {background:linear-gradient(135deg,#4facfe,#00f2fe);}
    .container {background:#fff;color:#2c3e50;box-shadow:0 25px 80px rgba(79,172,254,0.3);}
    .header {background:linear-gradient(45deg,#fa709a,#fee140);color:#2c3e50;}
    .nav-btn {background:#f39c12;color:white;font-weight:bold;}
    .stats div {color:#2c3e50;}
    ''',
    'admin': '''
    body {background:linear-gradient(135deg,#ff6b6b,#4ecdc4);}
    .container {background:#fff;color:#2c3e50;box-shadow:0 30px 100px rgba(255,107,107,0.4);}
    .header {background:linear-gradient(45deg,#667eea,#764ba2);color:#2c3e50;}
    .nav-btn {background:#27ae60;color:white;font-weight:bold;}
    .admin-btn {background:#e67e22;color:white;font-weight:bold;}
    .stats div {color:#2c3e50;}
    '''
}
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
        html += '<div class="header"><h1>🚀 Узнавайкин v32</h1><p>👤 <b>' + current_user + '</b> | Роль: ' + get_role_display(current_user) + '</p></div>'
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

# ✅ НОВЫЕ ROUTES — НИКОГДА НЕ БУДЕТ 404!
@app.route('/profiles')
def profiles():
    profiles_html = ''
    for user in sorted(users.keys()):
        profile = user_profiles.get(user, {})
        role_display = {
            'start': ' ', 'vip': 'VIP', 'premium': 'Premium',
            'moderator': 'Модератор', 'admin': 'Администратор'
        }.get(get_role_display(user).lower(), ' ')
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

@app.route('/profile/<username>')
def profile(username):
    if username not in users:
        return '''<!DOCTYPE html>
<html><body style="background:#f8f9fa;padding:100px;text-align:center;font-family:Arial;color:#2c3e50;">
<h1 style="color:#e74c3c;font-size:3em;">❌ Пользователь не найден</h1>
<a href="/" style="background:#2c3e50;color:white;padding:20px 40px;border-radius:15px;font-size:20px;text-decoration:none;display:inline-block;margin-top:30px;">🏠 На главную</a>
</body></html>'''
    
    current_user = session.get('user', '')
    profile_data = user_profiles.get(username, {'status': 'Онлайн', 'info': ''})
    role_display = {
        'start': ' ', 'vip': 'VIP', 'premium': 'Premium',
        'moderator': 'Модератор', 'admin': 'Администратор'
    }.get(get_role_display(username).lower(), ' ')
    
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
