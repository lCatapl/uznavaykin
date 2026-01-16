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

# ✅ ИНИЦИАЛИЗАЦИЯ ДАННЫХ — БЕЗ ЭМОДЗИ В КЛЮЧАХ
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
        'Almaz': {'location': 'Minecraft', 'info': 'Самый ценный ресурс!', 'photo': ''},
        'Zhelezo': {'location': 'Minecraft', 'info': 'Для инструментов', 'photo': ''}
    },
    'World_of_Tanks': {
        'T_34': {'location': 'World of Tanks', 'info': 'Легендарный танк СССР', 'photo': ''},
        'IS_7': {'location': 'World of Tanks', 'info': 'Тяжелый танк 10 уровня', 'photo': ''}
    }
})

def get_timestamp(): 
    return time.time()

# ✅ БЕЗ ЭМОДЗИ — Python 3.13 совместимость
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
        
        role = user_roles.get(username, 'start')
        if users.get(username, {}).get('admin'):
            stats['admin'] += 1
        elif username in moderators:
            stats['moderator'] += 1
        else:
            stats[role] = stats.get(role, 0) + 1
    return stats

# ✅ КАТАЛОГ ФУНКЦИИ — РАБОТАЮТ
def get_catalog_content(path=''):
    current = catalog
    parts = [p.strip() for p in path.split('/') if p.strip()]
    
    for part in parts:
        if part in current and isinstance(current[part], dict):
            current = current[part]
        else:
            return {'error': 'Folder not found: ' + part}
    
    folders = [name for name, content in current.items() if isinstance(content, dict)]
    items = {name: content for name, content in current.items() if not isinstance(content, dict)}
    
    return {'folders': folders, 'items': items}

# CSS ТЕМЫ — БЕЗ ЭМОДЗИ
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
<html><head><title>Uznavaikin v32</title>
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
        html += '<div class="header"><h1>Uznavaikin v32</h1><p>User: <b>' + current_user + '</b> | ' + get_role_display(current_user) + '</p></div>'
    else:
        html += '<div class="header"><h1>Uznavaikin v32</h1><p>Welcome!</p></div>'
    
    html += '<div class="stats">'
    html += '<div><b>' + str(stats['online']) + '</b><br>Online</div>'
    html += '<div><b>' + str(stats['afk']) + '</b><br>AFK</div>'
    html += '<div><b>' + str(stats['start']) + '</b><br>Start</div>'
    html += '<div><b>' + str(stats['vip']) + '</b><br>VIP</div>'
    html += '<div><b>' + str(stats['premium']) + '</b><br>Premium</div>'
    html += '</div>'
    
    html += '<div id="chat-container"><div id="chat-messages">'
    
    for msg in reversed(chat_messages[-50:]):
        delete_btn = ''
        if current_user and (is_admin(current_user) or is_moderator(current_user)) and msg['user'] != current_user:
            delete_btn = '<button class="delete-btn" onclick="deleteMessage(' + str(msg['id']) + ')">x</button>'
        
        html += '<div class="chat-msg">'
        html += delete_btn
        html += '<div class="chat-header">' + msg["user"] + ' <span style="color:#666;">' + msg["role"] + ' ' + datetime.fromtimestamp(msg["time"]).strftime("%H:%M") + '</span></div>'
        html += '<div>' + msg["text"] + '</div>'
        html += '</div>'

    html += '</div><div id="chat-input">'
    if current_user and not is_muted(current_user):
        html += '<form method="post" id="chatForm"><input type="text" name="message" id="messageInput" placeholder="Message... (max 300 chars)" maxlength="300"><button type="submit">Send</button></form>'
    else:
        html += '<p>Login to chat</p>'
    html += '</div></div>'
    
    html += '<div class="nav">'
    html += '<a href="/catalog" class="nav-btn">Catalog</a>'
    html += '<a href="/profiles" class="nav-btn">Profiles</a>'
    html += '<a href="/community" class="nav-btn">Community</a>'
    if current_user:
        html += '<a href="/profile/' + current_user + '" class="nav-btn">My Profile</a>'
        if is_admin(current_user):
            html += '<a href="/admin" class="nav-btn">Admin</a>'
        html += '<a href="/logout" class="nav-btn">Logout</a>'
    else:
        html += '<a href="/login" class="nav-btn">Login</a>'
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
    if(confirm('Delete message?')) {
        fetch(`/api/delete_message/${msgId}`, {method: 'DELETE'})
        .then(r => r.json())
        .then(data => {
            if(data.success) location.reload();
        }).catch(() => alert('Error'));
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
        return jsonify({'error': 'No access'}), 403
    
    for i, msg in enumerate(chat_messages):
        if msg['id'] == msg_id and msg['user'] != current_user:
            del chat_messages[i]
            save_data()
            return jsonify({'success': True})
    return jsonify({'error': 'Message not found'}), 404

@app.route('/catalog/<path:path>')
@app.route('/catalog')
def catalog_view(path=''):
    content = get_catalog_content(path)
    
    if 'error' in content:
        return '''<!DOCTYPE html>
<html><body style="padding:50px;font-family:Arial;text-align:center;background:#f8f9fa;">
<h1 style="color:#dc3545;font-size:2em;">''' + content['error'] + '''</h1>
<a href="/catalog" style="background:#007bff;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;display:inline-block;margin:10px;font-size:18px;">Catalog</a>
<a href="/" style="background:#28a745;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;display:inline-block;margin-left:10px;font-size:18px;">Home</a>
</body></html>'''
    
    breadcrumbs = 'Catalog <a href="/catalog" style="color:#007bff;">Home</a>'
    parts = [p.strip() for p in path.split('/') if p.strip()]
    temp_path = []
    for part in parts:
        temp_path.append(part)
        path_str = '/'.join(temp_path)
        breadcrumbs += ' -> <a href="/catalog/' + path_str + '" style="color:#007bff;">' + part + '</a>'
    
    content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:25px;padding:20px;">'
    
    for folder in sorted(content['folders']):
        content_html += '''
        <a href="/catalog/''' + path + ('/' if path else '') + folder + '''" style="background:#e3f2fd;padding:30px;border-radius:20px;border-left:5px solid #2196f3;text-decoration:none;display:block;text-align:center;transition:all 0.3s;font-family:Arial;">
            <h3 style="margin:0 0 10px 0;color:#2196f3;font-size:1.8em;">[FOLDER] ''' + folder + '''</h3>
            <p style="margin:0;color:#666;font-size:1.2em;">Folder</p>
        </a>'''
    
    for item_name, item_data in sorted(content['items'].items()):
        photo_html = ''
        if item_data.get('photo'):
            photo_html = '<img src="' + item_data["photo"] + '" style="width:100%;max-height:200px;object-fit:cover;border-radius:10px;margin:15px 0;" alt="Photo" onerror="this.style.display=\'none\'">'
        
        content_html += '''
        <div style="background:#f3e5f5;padding:30px;border-radius:20px;border-left:5px solid #9c27b0;font-family:Arial;box-shadow:0 5px 20px rgba(0,0,0,0.1);">
            <h3 style="font-size:1.8em;font-weight:bold;margin-bottom:15px;color:#333;">''' + item_name + '''</h3>
            <p style="margin:8px 0;font-size:1.1em;"><b style="color:#555;">Location:</b> <span style="color:#666;">''' + item_data.get("location", "Not specified") + '''</span></p>
            <p style="margin:8px 0;font-size:1.1em;line-height:1.6;"><b style="color:#555;">Info:</b></p>
            <div style="background:#f9f9f9;padding:15px;border-radius:10px;color:#444;font-size:1em;">''' + item_data.get("info", "—") + '''</div>
            ''' + photo_html + '''
        </div>'''
    
    content_html += '</div>'
    
    if not content['folders'] and not content['items']:
        content_html = '''
        <div style="text-align:center;color:#666;font-size:2.5em;margin:100px 0;padding:80px;background:#f8f9fa;border-radius:30px;border:4px dashed #ddd;font-family:Arial;">
            Empty folder
            <p style="font-size:0.6em;margin-top:20px;color:#999;">Add items via admin panel</p>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>Catalog ''' + (path or "Main") + '''</title>
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
<h1 style="text-align:center;margin-bottom:30px;font-size:2.5em;color:#333;">Catalog</h1>
<div class="breadcrumbs">''' + breadcrumbs + '''</div>
''' + content_html + '''
<div style="text-align:center;margin-top:60px;">
<a href="/catalog" class="back-btn">Main Catalog</a>
<a href="/" class="back-btn" style="background:#28a745;">Home</a>
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
            user_profiles[username] = {'bio': '', 'status': 'Online', 'info': ''}
        
        user_activity[username] = get_timestamp()
        save_data()
        return redirect(url_for('index'))
    
    return '''<!DOCTYPE html>
<html><head><title>Login - Uznavaikin</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:40px;display:flex;align-items:center;justify-content:center;}
.login-container{max-width:450px;width:100%;background:linear-gradient(135deg,#667eea,#764ba2);padding:50px;border-radius:25px;box-shadow:0 25px 80px rgba(0,0,0,0.3);color:white;text-align:center;}
.login-container input{width:100%;padding:20px;margin:15px 0;border:none;border-radius:15px;font-size:18px;box-sizing:border-box;background:rgba(255,255,255,0.95);color:#333;}
.login-container button{width:100%;padding:20px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:15px;font-size:20px;font-weight:bold;cursor:pointer;margin-top:20px;transition:all 0.3s;}
.login-container button:hover{transform:translateY(-3px);box-shadow:0 15px 40px rgba(255,107,107,0.4);}
h1{font-size:2.5em;margin-bottom:30px;}</style></head>
<body><div class="login-container">
<h1>Uznavaikin v32</h1>
<form method="post">
<input name="username" placeholder="Username" required maxlength="20">
<input name="password" type="password" placeholder="Password" required maxlength="50">
<button type="submit">LOGIN / REGISTER</button>
</form>
<p style="margin-top:30px;font-size:14px;">Passwords are protected</p>
</div></body></html>'''

@app.route('/profiles')
def profiles():
    profiles_html = ''
    for user in sorted(users.keys()):
        profile = user_profiles.get(user, {})
        role_display = get_role_display(user)
        profiles_html += '''
        <div style="background:white;padding:30px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;margin:20px;">
            <h3 style="font-size:2em;margin-bottom:15px;color:#333;">''' + user + '''</h3>
            <div style="padding:15px 25px;background:#e8f5e8;border-radius:15px;font-size:1.3em;font-weight:bold;margin:20px 0;">''' + role_display + '''</div>
            <p style="color:#666;margin:10px 0;font-size:1.1em;">''' + profile.get("status", "Online") + '''</p>
            <a href="/profile/''' + user + '''" style="display:inline-block;padding:15px 35px;background:#007bff;color:white;border-radius:15px;font-weight:bold;font-size:18px;text-decoration:none;">View Profile</a>
        </div>'''
    
    return '''<!DOCTYPE html>
<html><head><title>Profiles</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial,sans-serif;padding:30px;background:#f0f2f5;}
.container{max-width:1200px;margin:auto;}
.profiles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:30px;margin:40px 0;}
.back-btn{background:#007bff;color:white;padding:25px 50px;border-radius:20px;font-size:22px;font-weight:bold;text-decoration:none;display:block;margin:60px auto;max-width:400px;text-align:center;}
@media (max-width:768px) {.profiles-grid{grid-template-columns:1fr;gap:20px;}}</style></head>
<body><div class="container">
<h1 style="text-align:center;margin-bottom:50px;font-size:3em;color:#333;">All Profiles</h1>
<div class="profiles-grid">''' + profiles_html + '''</div>
<a href="/" class="back-btn">Home</a>
</div></body></html>'''

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    if username not in users:
        return '''<!DOCTYPE html>
<html><body style="background:#f0f2f5;padding:100px;text-align:center;font-family:Arial;">
<h1 style="color:#dc3545;font-size:3em;">User not found</h1>
<a href="/" style="background:#007bff;color:white;padding:20px 40px;border-radius:15px;font-size:20px;text-decoration:none;display:inline-block;margin-top:30px;">Home</a>
</body></html>'''
    
    current_user = session.get('user', '')
    profile_data = user_profiles.get(username, {'status': 'Online', 'info': ''})
    is_owner = current_user == username
    role_display = get_role_display(username)
    
    if request.method == 'POST' and is_owner:
        profile_data['status'] = request.form.get('status', 'Online')[:50]
        profile_data['info'] = request.form.get('info', '')[:500]
        user_profiles[username] = profile_data
        save_data()
    
    if is_owner:
        status_html = '''
        <form method="post" style="margin-top:20px;">
            <input name="status" value="''' + profile_data.get("status", "Online") + '''" placeholder="Status (50 chars max)" maxlength="50" style="width:100%;padding:18px;border:2px solid #ddd;border-radius:15px;font-size:18px;box-sizing:border-box;">
            <button type="submit" style="width:100%;padding:18px;background:#28a745;color:white;border:none;border-radius:15px;font-size:18px;margin-top:15px;cursor:pointer;font-weight:bold;">Save Status</button>
        </form>'''
    else:
        status_html = '<div style="font-size:1.4em;color:#27ae60;padding:25px;background:#e8f5e8;border-radius:20px;margin:20px 0;">' + profile_data.get("status", "Online") + '</div>'
    
    if is_owner:
        info_html = '''
        <form method="post" style="margin-top:20px;">
            <textarea name="info" placeholder="About yourself... (500 chars max)" rows="6" maxlength="500" style="width:100%;padding:20px;border:2px solid #ddd;border-radius:15px;font-size:16px;font-family:Arial;box-sizing:border-box;">''' + profile_data.get("info", "") + '''</textarea>
            <button type="submit" style="width:100%;padding:20px;background:#3498db;color:white;border:none;border-radius:15px;font-size:18px;margin-top:20px;cursor:pointer;font-weight:bold;">Save Info</button>
        </form>'''
    else:
        info_html = '<div style="padding:30px;background:#f8f9fa;border-radius:20px;line-height:1.8;font-size:1.2em;border-left:6px solid #3498db;margin:30px 0;">' + profile_data.get("info", "No info") + '</div>'
    
    return '''<!DOCTYPE html>
<html><head><title>''' + username + ''' - Profile</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial,sans-serif;padding:40px;background:#f0f2f5;}
.profile-card{background:white;max-width:900px;margin:auto;padding:60px;border-radius:30px;box-shadow:0 30px 100px rgba(0,0,0,0.15);text-align:center;}
.role-badge{padding:25px 50px;background:#e74c3c;color:white;border-radius:35px;font-size:2em;font-weight:bold;display:inline-block;margin:40px 0;box-shadow:0 15px 40px rgba(0,0,0,0.2);}
.back-btn{background:#007bff;color:white;padding:22px 55px;border-radius:25px;font-size:22px;font-weight:bold;display:inline-block;margin-top:50px;text-decoration:none;box-shadow:0 10px 30px rgba(0,0,0,0.2);}
.back-btn:hover{transform:translateY(-3px);box-shadow:0 15px 40px rgba(0,0,0,0.3);}
@media (max-width:768px) {.profile-card{padding:40px;margin:20px;border-radius:25px;}}</style></head>
<body><div class="profile-card">
<h1 style="font-size:3.5em;margin-bottom:30px;color:#2c3e50;">''' + username + '''</h1>
<div class="role-badge">''' + role_display + '''</div>
''' + status_html + '''
<div style="margin:50px 0;padding:40px;background:#ecf0f1;border-radius:25px;">
<h2 style="color:#2c3e50;margin-bottom:30px;font-size:2em;">About:</h2>
''' + info_html + '''
</div>
<a href="/" class="back-btn">Home</a>
<a href="/profiles" class="back-btn" style="background:#28a745;margin-left:20px;">Profiles</a>
</div></body></html>'''

@app.route('/community')
def community():
    return '''<!DOCTYPE html>
<html><head><title>Community</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;padding:100px 20px;text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);color:white;min-height:100vh;}
.community-box{max-width:700px;margin:auto;background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:100px;border-radius:35px;box-shadow:0 35px 120px rgba(0,0,0,0.3);}
.tg-link{font-size:3.5em;color:#0088cc;text-decoration:none;font-weight:bold;display:inline-block;margin:50px 0;padding:30px 60px;background:rgba(255,255,255,0.2);border-radius:30px;transition:all 0.3s;box-shadow:0 15px 40px rgba(0,0,0,0.2);}
.tg-link:hover{transform:scale(1.05);background:rgba(255,255,255,0.3);box-shadow:0 20px 50px rgba(0,0,0,0.3);}
.back-btn{background:#007bff;color:white;padding:30px 70px;border-radius:30px;font-size:26px;font-weight:bold;text-decoration:none;display:inline-block;margin-top:70px;box-shadow:0 20px 50px rgba(0,0,0,0.3);transition:all 0.3s;}
.back-btn:hover{transform:translateY(-5px);box-shadow:0 25px 60px rgba(0,0,0,0.4);}</style></head>
<body><div class="community-box">
<h1 style="font-size:4.5em;margin-bottom:50px;">Uznavaikin Community</h1>
<p style="font-size:1.8em;margin-bottom:60px;">Join our team!</p>
<a href="https://t.me/ssylkanatelegramkanalyznaikin" class="tg-link" target="_blank">Telegram</a>
<a href="/" class="back-btn">Home</a>
</div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

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
                    'user': 'SYSTEM',
                    'text': target + ' muted by ' + current_user + ' until ' + datetime.fromtimestamp(get_timestamp() + duration).strftime("%H:%M") + ' | Reason: ' + reason,
                    'time': get_timestamp(),
                    'role': 'Moderation'
                })
                message = target + ' muted for ' + str(duration/60) + ' minutes!'
        save_data()
    
    stats = calculate_stats()
    admin_html = '''
    <div style="background:#e8f5e8;padding:20px;border-radius:15px;margin:20px 0;">
        <h2 style="color:#27ae60;">Statistics</h2>
        <p>Total users: ''' + str(len(users)) + '''</p>
        <p>Chat messages: ''' + str(len(chat_messages)) + '''</p>
        <p>Catalog sections: ''' + str(len(catalog)) + '''</p>
    </div>''' + (message and '<div style="background:#d4edda;color:#155724;padding:15px;border-radius:10px;margin:20px 0;border:1px solid #c3e6cb;"><b>' + message + '</b></div>' or '') + '''
    <h3 style="color:#dc3545;">Mute User</h3>
    <form method="post">
        <input type="hidden" name="action" value="mute">
        <input name="target" placeholder="Username" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
        <input type="number" name="duration" value="5" min="1" max="1440" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;"> minutes
        <input name="reason" placeholder="Reason" maxlength="100" style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
        <button type="submit" style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:8px;cursor:pointer;">MUTE</button>
    </form>'''
    
    return '''<!DOCTYPE html>
<html><head><title>Admin Panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#ff9a9e,#fecfef);padding:30px;color:#333;}
.container{max-width:1400px;margin:auto;background:white;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}
h1{text-align:center;color:#2d3436;font-size:3em;margin-bottom:30px;}
h2,h3{color:#2d3436;margin-top:30px;}
form{margin:20px 0;}
input{font-family:inherit;}
.back-btn{background:#6c757d;color:white;padding:20px 40px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;margin:40px 20px;box-shadow:0 10px 30px rgba(0,0,0,0.2);transition:all 0.3s;}
.back-btn:hover{transform:translateY(-3px);box-shadow:0 15px 40px rgba(0,0,0,0.3);}
@media (max-width:768px) {body{padding:10px;}.container{padding:20px;border-radius:20px;}}</style></head>
<body><div class="container">
<h1>Admin Panel - ''' + current_user + '''</h1>
''' + admin_html + '''
<div style="text-align:center;">
<a href="/" class="back-btn">Home</a>
</div></div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

