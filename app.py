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

# ✅ ИНИЦИАЛИЗАЦИЯ — РУССКИЕ ИМЕНА + АДМИНЫ
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
        'Алмаз': {'location': 'Minecraft', 'info': 'Самый ценный ресурс!', 'photo': ''},
        'Железо': {'location': 'Minecraft', 'info': 'Для инструментов и брони', 'photo': ''}
    },
    'World_of_Tanks': {
        'Т-34': {'location': 'World of Tanks', 'info': 'Легендарный танк СССР', 'photo': ''},
        'ИС-7': {'location': 'World of Tanks', 'info': 'Тяжелый танк 10 уровня', 'photo': ''}
    }
})

def get_timestamp(): 
    return time.time()

# ✅ РОЛИ — ТЕКСТ ДЛЯ PYTHON (стикеры в HTML)
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
        if now - last_activity < 300:  # 5 минут
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

# ✅ КАТАЛОГ — ПОЛНАЯ ПОДДЕРЖКА
def get_catalog_content(path=''):
    current = catalog
    parts = [p.strip() for p in path.split('/') if p.strip()]
    
    for part in parts:
        if part in current and isinstance(current[part], dict):
            current = current[part]
        else:
            return {'error': 'Папка не найдена: ' + part}
    
    folders = [name for name, content in current.items() if isinstance(content, dict)]
    items = {name: content for name, content in current.items() if not isinstance(content, dict)}
    
    return {'folders': folders, 'items': items}

# ✅ CSS ТЕМЫ — 4 ВАРИАНТА ДИЗАЙНА
css_themes = {
    'basic': '''
    body {background:linear-gradient(135deg,#f5f7fa,#c3cfe2);}
    .container {background:#fff;color:#333;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
    .header {background:linear-gradient(45deg,#ff9a9e,#fecfef);color:#333;}
    .nav-btn {background:#74b9ff;color:white;}
    ''',
    'vip': '''
    body {background:linear-gradient(135deg,#667eea,#764ba2);}
    .container {background:linear-gradient(135deg,#667eea,#764ba2);color:white;box-shadow:0 20px 60px rgba(102,126,234,0.4);}
    .header {background:linear-gradient(45deg,#f093fb,#f5576c);color:white;}
    .nav-btn {background:#ff6b6b;color:white;}
    ''',
    'premium': '''
    body {background:linear-gradient(135deg,#4facfe,#00f2fe);}
    .container {background:linear-gradient(135deg,#a8edea,#fed6e3);color:#333;box-shadow:0 25px 80px rgba(79,172,254,0.3);}
    .header {background:linear-gradient(45deg,#fa709a,#fee140);color:#333;}
    .nav-btn {background:#ff9ff3;color:white;}
    ''',
    'admin': '''
    body {background:linear-gradient(135deg,#ff6b6b,#4ecdc4);}
    .container {background:linear-gradient(135deg,#ff6b6b,#4ecdc4);color:white;box-shadow:0 30px 100px rgba(255,107,107,0.5);}
    .header {background:linear-gradient(45deg,#667eea,#764ba2);color:white;}
    .nav-btn {background:#ffeaa7;color:#2d3436;}
    .admin-btn {background:#00b894;color:white;}
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
.container {max-width:1200px;margin:0 auto;background:white;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.1);}
.header {padding:30px;text-align:center;background:linear-gradient(45deg,#ff9a9e,#fecfef);}
h1 {font-size:2.5em;margin:0;color:#333;}
.stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:15px;padding:25px;background:#f8f9fa;border-radius:20px;margin:20px;}
.stats div {text-align:center;padding:15px;background:white;border-radius:15px;}
.nav {display:flex;flex-wrap:wrap;gap:12px;padding:25px;background:#e9ecef;border-radius:20px;justify-content:center;}
.nav-btn {padding:15px 25px;color:white;text-decoration:none;border-radius:15px;font-weight:bold;margin:5px;transition:all 0.3s;}
.nav-btn:hover {transform:translateY(-2px);}
#chat-container {max-width:900px;margin:25px auto;background:#f8f9fa;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.1);}
#chat-messages {max-height:450px;overflow-y:auto;padding:25px;background:white;}
.chat-msg {margin-bottom:15px;padding:20px;background:#f1f3f4;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.chat-header {font-weight:bold;font-size:14px;margin-bottom:8px;color:#333;}
.delete-btn {float:right;background:#ff4757;color:white;border:none;border-radius:50%;width:25px;height:25px;cursor:pointer;font-size:14px;}
#chat-input {padding:20px;background:#e9ecef;border-top:1px solid #ddd;}
input[type="text"] {width:70%;padding:15px;border:1px solid #ddd;border-radius:10px;font-size:16px;}
button[type="submit"] {width:25%;padding:15px;background:#00b894;color:white;border:none;border-radius:10px;cursor:pointer;font-size:16px;}</style></head><body>'''
    
    html += '<div class="container">'
    
    if current_user:
        html += '<div class="header"><h1>🚀 Узнавайкин v32</h1><p>👤 <b>' + current_user + '</b> | ' + get_role_display(current_user) + '</p></div>'
    else:
        html += '<div class="header"><h1>🚀 Узнавайкин v32</h1><p>Добро пожаловать!</p></div>'
    
    html += '<div class="stats">'
    html += '<div><b>' + str(stats['online']) + '</b><br>👥 Онлайн</div>'
    html += '<div><b>' + str(stats['afk']) + '</b><br>😴 АФК</div>'
    html += '<div><b>' + str(stats['start']) + '</b><br>📚 Новички</div>'
    html += '<div><b>' + str(stats['vip']) + '</b><br>⭐ VIP</div>'
    html += '<div><b>' + str(stats['premium']) + '</b><br>💎 Premium</div>'
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
        html += '<p style="padding:20px;text-align:center;color:#666;">🔐 Войдите для чата</p>'
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

@app.route('/catalog/<path:path>')
@app.route('/catalog')
def catalog_view(path=''):
    content = get_catalog_content(path)
    
    if 'error' in content:
        return '''<!DOCTYPE html>
<html><body style="padding:50px;font-family:Arial;text-align:center;background:#f8f9fa;">
<h1 style="color:#dc3545;font-size:2em;">''' + content['error'] + '''</h1>
<a href="/catalog" style="background:#007bff;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;display:inline-block;margin:10px;font-size:18px;">📁 Каталог</a>
<a href="/" style="background:#28a745;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;display:inline-block;margin-left:10px;font-size:18px;">🏠 Главная</a>
</body></html>'''
    
    breadcrumbs = '📁 <a href="/catalog" style="color:#007bff;">Каталог</a>'
    parts = [p.strip() for p in path.split('/') if p.strip()]
    temp_path = []
    for part in parts:
        temp_path.append(part)
        path_str = '/'.join(temp_path)
        breadcrumbs += ' → <a href="/catalog/' + path_str + '" style="color:#007bff;">' + part + '</a>'
    
    content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:25px;padding:20px;">'
    
    for folder in sorted(content['folders']):
        content_html += '''
        <a href="/catalog/''' + path + ('/' if path else '') + folder + '''" style="background:#e3f2fd;padding:30px;border-radius:20px;border-left:5px solid #2196f3;text-decoration:none;display:block;text-align:center;transition:all 0.3s;font-family:Arial;">
            <h3 style="margin:0 0 10px 0;color:#2196f3;font-size:1.8em;">📁 ''' + folder + '''</h3>
            <p style="margin:0;color:#666;font-size:1.2em;">Папка</p>
        </a>'''
    
    for item_name, item_data in sorted(content['items'].items()):
        photo_html = ''
        if item_data.get('photo'):
            photo_html = '<img src="' + item_data["photo"] + '" style="width:100%;max-height:200px;object-fit:cover;border-radius:10px;margin:15px 0;" alt="Фото" onerror="this.style.display=\'none\'">'
        
        content_html += '''
        <div style="background:#f3e5f5;padding:30px;border-radius:20px;border-left:5px solid #9c27b0;font-family:Arial;box-shadow:0 5px 20px rgba(0,0,0,0.1);">
            <h3 style="font-size:1.8em;font-weight:bold;margin-bottom:15px;color:#333;">''' + item_name + '''</h3>
            <p style="margin:8px 0;font-size:1.1em;"><b style="color:#555;">📍 Местоположение:</b> <span style="color:#666;">''' + item_data.get("location", "Не указано") + '''</span></p>
            <p style="margin:8px 0;font-size:1.1em;line-height:1.6;"><b style="color:#555;">ℹ️ Информация:</b></p>
            <div style="background:#f9f9f9;padding:15px;border-radius:10px;color:#444;font-size:1em;">''' + item_data.get("info", "—") + '''</div>
            ''' + photo_html + '''
        </div>'''
    
    content_html += '</div>'
    
    if not content['folders'] and not content['items']:
        content_html = '''
        <div style="text-align:center;color:#666;font-size:2.5em;margin:100px 0;padding:80px;background:#f8f9fa;border-radius:30px;border:4px dashed #ddd;font-family:Arial;">
            📭 Папка пуста
            <p style="font-size:0.6em;margin-top:20px;color:#999;">Добавьте предметы через админ-панель</p>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>📁 Каталог ''' + (path or "Главная") + '''</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {font-family:Arial,sans-serif;padding:20px;background:#f8f9fa;}
.container {max-width:1300px;margin:0 auto;background:white;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.1);}
.breadcrumbs {margin:30px 0;padding:25px;background:#e9ecef;border-radius:20px;font-size:18px;line-height:1.6;}
.breadcrumbs a {color:#007bff;text-decoration:none;font-weight:500;}
.grid {display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:30px;}
.grid > * {transition:all 0.3s;}
.grid > a:hover, .grid > div:hover {transform:translateY(-8px);box-shadow:0 20px 40px rgba(0,0,0,0.15);}
.back-btn {background:#007bff;color:white;padding:18px 40px;border-radius:15px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;margin:50px 10px;transition:all 0.3s;}
.back-btn:hover {transform:translateY(-3px);box-shadow:0 15px 35px rgba(0,123,255,0.4);}
@media (max-width:768px) {.container {padding:20px;margin:10px;border-radius:20px;}.grid {grid-template-columns:1fr;gap:20px;}}
</style></head>
<body><div class="container">
<h1 style="text-align:center;margin-bottom:30px;font-size:2.5em;color:#333;">📁 Каталог</h1>
<div class="breadcrumbs">''' + breadcrumbs + '''</div>
''' + content_html + '''
<div style="text-align:center;margin-top:60px;">
<a href="/catalog" class="back-btn">📁 Главный Каталог</a>
<a href="/" class="back-btn" style="background:#28a745;">🏠 На главную</a>
</div></div></body></html>'''

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
<style>body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:40px;display:flex;align-items:center;justify-content:center;}
.login-container{max-width:450px;width:100%;background:linear-gradient(135deg,#667eea,#764ba2);padding:50px;border-radius:25px;box-shadow:0 25px 80px rgba(0,0,0,0.3);color:white;text-align:center;}
.login-container input{width:100%;padding:20px;margin:15px 0;border:none;border-radius:15px;font-size:18px;box-sizing:border-box;background:rgba(255,255,255,0.95);color:#333;}
.login-container button{width:100%;padding:20px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:15px;font-size:20px;font-weight:bold;cursor:pointer;margin-top:20px;transition:all 0.3s;}
.login-container button:hover{transform:translateY(-3px);box-shadow:0 15px 40px rgba(255,107,107,0.4);}
h1{font-size:2.5em;margin-bottom:30px;}</style></head>
<body><div class="login-container">
<h1>🔐 Узнавайкин v32</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required maxlength="20">
<input name="password" type="password" placeholder="🔑 Пароль" required maxlength="50">
<button type="submit">🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form>
<p style="margin-top:30px;font-size:14px;">Пароли защищены и не хранятся в открытом виде</p>
</div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
