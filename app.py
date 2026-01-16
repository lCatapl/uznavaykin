from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
from datetime import datetime
import os
import json
import time

app = Flask(__name__)
app.secret_key = 'uznaykin_v35_secret_2026_abc123_xyz789'  # ✅ ФИКС GUNICORN

# Глобальные данные
users = {}
user_roles = {}
user_profiles = {}
user_activity = {}
chat_messages = []
mutes = {'by': {}, 'reason': {}, 'muted_by': {}}
catalog = {}
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
                mutes = data.get('mutes', {'by': {}, 'reason': {}})
                catalog = data.get('catalog', {})
    except:
        pass
    
    auto_admins = ['CatNap', 'Назар']
    for username in auto_admins:
        if username not in users:
            users[username] = {'password': '120187', 'role': 'admin'}
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': '👑 Авто-администратор'}
        user_roles[username] = 'admin'
        user_activity[username] = time.time()
    
    save_data()

def save_data():
    data = {
        'users': users, 'user_roles': user_roles, 'user_profiles': user_profiles,
        'user_activity': user_activity, 'chat_messages': chat_messages,
        'mutes': mutes, 'catalog': catalog
    }
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_timestamp():
    return time.time()

def parse_duration(days, unit):
    multipliers = {'секунд': 1, 'минут': 60, 'часов': 3600, 'дней': 86400, 'лет': 31536000}
    if unit == 'навсегда':
        return 0
    try:
        return float(days) * multipliers.get(unit, 1)
    except:
        return 3600

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
    now = get_timestamp()
    
    for user in users:
        if is_online(user):
            stats['online'] += 1
            if is_afk(user):
                stats['afk'] += 1
            role = user_roles.get(user, 'start')
            stats[role] += 1
    return stats

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
    return f'<span style="color:{role_data["color"]};">{role_data["icon"]} {role_data["label"]}</span>'

def is_admin(username): 
    return user_roles.get(username) == 'admin'

def is_moderator(username): 
    return user_roles.get(username) == 'moderator'

def is_muted(username):
    if username not in mutes['by']:
        return False
    end_time = mutes['by'][username]
    if end_time == 0:
        return True
    return get_timestamp() < end_time

def get_catalog_content(path=''):
    parts = [p.strip() for p in path.split('/') if p.strip()]
    current = catalog
    
    if not parts:
        folders = [k for k,v in catalog.items() if isinstance(v, dict) and v.get('type') == 'folder']
        items = {k:v for k,v in catalog.items() if isinstance(v, dict) and v.get('type') == 'item'}
        return {'folders': sorted(folders), 'items': items}
    
    for part in parts:
        if part in current and isinstance(current[part], dict):
            current = current[part]
        else:
            return {'error': 'Папка не найдена'}
    
    folders = [k for k,v in current.items() if isinstance(v, dict) and v.get('type') == 'folder']
    items = {k:v for k,v in current.items() if isinstance(v, dict) and v.get('type') == 'item'}
    return {'folders': sorted(folders), 'items': items}

load_data()

css = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:'Inter',sans-serif;background:#f8f9fa;color:#2c3e50;}
.container {max-width:1200px;margin:0 auto;background:#fff;border-radius:25px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.15);}'''

@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = session.get('user', '')
    stats = calculate_stats()
    
    if request.method == 'POST' and current_user and not is_muted(current_user):
        message = request.form['message'].strip()
        if message and len(message) <= 300:
            if message.startswith('/profile '):
                target = message[9:].strip().lstrip('@')
                chat_messages.append({
                    'id': len(chat_messages), 'user': current_user, 'text': f'👤 /profile/{target}',
                    'time': get_timestamp(), 'role': get_role_display(current_user)
                })
            else:
                chat_messages.append({
                    'id': len(chat_messages), 'user': current_user, 'text': message,
                    'time': get_timestamp(), 'role': get_role_display(current_user)
                })
            user_activity[current_user] = get_timestamp()
            save_data()
    
    if current_user:
        user_activity[current_user] = get_timestamp()
    
    full_css = css + '''
    .header {padding:30px;text-align:center;background:linear-gradient(45deg,#ff9a9e,#fecfef);}
    h1 {font-size:2.5em;color:#2c3e50;}
    .stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:15px;padding:25px;background:#f8f9fa;border-radius:20px;margin:20px 0;}
    .stats div {text-align:center;padding:15px;background:#fff;border-radius:15px;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
    .nav {display:flex;flex-wrap:wrap;gap:12px;padding:25px;background:#ecf0f1;border-radius:20px;justify-content:center;}
    .nav-btn {padding:15px 25px;color:white;text-decoration:none;border-radius:15px;font-weight:bold;transition:all 0.3s;}
    .nav-btn:hover {transform:translateY(-2px);box-shadow:0 10px 25px rgba(0,0,0,0.2);}
    #chat-container {max-width:900px;margin:25px auto;background:#f8f9fa;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.15);}
    #chat-messages {max-height:450px;overflow-y:auto;padding:25px;background:#fff;}
    .chat-msg {margin-bottom:15px;padding:20px;background:#f1f3f4;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
    .chat-header {font-weight:bold;font-size:14px;margin-bottom:8px;color:#2c3e50;}
    .delete-btn {float:right;background:#e74c3c;color:white;border:none;border-radius:50%;width:25px;height:25px;cursor:pointer;font-size:14px;}
    #chat-input {padding:20px;background:#ecf0f1;border-top:1px solid #ddd;}
    input[type="text"] {width:70%;padding:15px;border:1px solid #ddd;border-radius:10px;font-size:16px;}
    button[type="submit"] {width:25%;padding:15px;background:#27ae60;color:white;border:none;border-radius:10px;cursor:pointer;font-size:16px;font-weight:bold;}
    #mutelist-container {background:#ffebee;padding:15px;border-radius:10px;margin:20px 25px;display:none;}
    .rules-box {background:#ffeaa7;padding:20px;border-radius:15px;margin:0 25px 20px 25px;max-height:200px;overflow-y:auto;border-left:5px solid #fdcb6e;}
    .mute-timer {background:#ff6b6b;color:white;padding:20px;border-radius:15px;margin:20px;text-align:center;}
    #rules-content {font-size:0.9em;line-height:1.5;color:#2d3436;}
    '''
    
    html = '''<!DOCTYPE html>
<html><head><title>🚀 Узнавайкин v35</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>''' + full_css + '''</style></head><body>'''
    
    html += '<div class="container">'
    if current_user:
        html += f'<div class="header"><h1>🚀 Узнавайкин v35</h1><p>👤 <b>{current_user}</b> | {get_role_display(current_user)}</p></div>'
    else:
        html += '<div class="header"><h1>🚀 Узнавайкин v35</h1><p>👋 Добро пожаловать, Гость!</p></div>'
    
    html += f'<div class="stats">'
    html += f'<div><b>{stats["online"]}</b><br>👥 Онлайн</div>'
    html += f'<div><b>{stats["afk"]}</b><br>😴 АФК</div>'
    html += f'<div><b>{stats["start"]}</b><br>📚 Обычные</div>'
    html += f'<div><b>{stats["vip"]}</b><br>⭐ VIP</div>'
    html += f'<div><b>{stats["premium"]}</b><br>💎 Premium</div>'
    html += f'<div><b>{stats["moderator"]}</b><br>🛡️ Модератор</div>'
    html += f'<div><b>{stats["admin"]}</b><br>👑 Администратор</div>'
    html += '</div>'
    
    html += '''
    <div id="chat-container">
        <div class="rules-box">
            <h3 style="color:#2d3436;margin-bottom:10px;">📜 Правила чата</h3>
            <div id="rules-content">
                <b>1. Правила для всех</b><br>
                1.1 Запрещён спам <span style="color:#e74c3c;">(мут от 10 до 60 минут)</span><br>
                1.2 Запрещён флуд <span style="color:#e74c3c;">(мут от 1 до 5 часов)</span><br>
                1.3 Запрещён мат <span style="color:#e74c3c;">(1 мат = 10 минут)</span><br>
                1.4 Запрещено упоминать родственников в плохом значении <span style="color:#e74c3c;">(мут от 1 до 10 часов)</span><br>
                1.5 Запрещена реклама других сайтов <span style="color:#e74c3c;">(мут от 30 до 60 минут)</span><br>
                1.6 Запрещено выдавать себя за Администратора <span style="color:#e74c3c;">(мут от 2 до 24 часов)</span><br><br>
                
                <b>2. Правила для Модераторов</b><br>
                2.1 Мутить без причины или причины, которой нет в списке <span style="color:#e74c3c;">(снятие с должности при повторном действии)</span><br>
                2.2 Мутить на срок больше или меньше предела <span style="color:#e74c3c;">(мут от 10 до 30 минут и при повторном действии снятие с должности на 10 дней)</span><br>
                2.3 Удаление чужих сообщений без причины <span style="color:#e74c3c;">(снятие с должности при повторном действии) (для доказательства нужно обратиться в "Жалобы")</span><br><br>
                
                <b>P. S.</b><br>
                1. Администратор может в любой момент менять правила<br>
                2. Если вас замутили, то лучше больше так не делайте, так как за повторные действие время мута увеличивается (до предела)
            </div>
        </div>
        <div id="chat-messages">'''
    
    for msg in reversed(chat_messages[-50:]):
        delete_btn = ''
        if current_user and (is_admin(current_user) or is_moderator(current_user)):
            delete_btn = f'<button class="delete-btn" onclick="deleteMessage({msg["id"]})">×</button>'
        html += f'''
        <div class="chat-msg">
            {delete_btn}
            <div class="chat-header">{msg["user"]} <span style="color:#666;">{msg["role"]} {datetime.fromtimestamp(msg["time"]).strftime("%H:%M")}</span></div>
            <div>{msg["text"]}</div>
        </div>'''
    
    html += '</div><div id="chat-input">'
    if current_user and not is_muted(current_user):
        html += '<form method="post" id="chatForm"><input type="text" name="message" id="messageInput" placeholder="/profile @ник или сообщение... (макс. 300 символов)" maxlength="300"><button type="submit">📤 Отправить</button></form>'
    else:
        html += '<p style="padding:20px;text-align:center;color:#666;font-size:18px;">🔐 Войдите для чата</p>'
    html += '</div></div>'
    
    html += '''
    <div id="mutelist-container">
        <h4 style="color:#c53030;">🔇 МутЛист</h4>
        <div id="mutelist">Загрузка...</div>
    </div>'''
    
    if current_user and is_muted(current_user):
        end_time = mutes['by'].get(current_user, 0)
        reason = mutes['reason'].get(current_user, 'Причина не указана')
        html += f'''
        <div class="mute-timer">
            <h3>🔇 Вы замучены!</h3>
            <div id="mute-timer" data-end="{end_time}">Загрузка...</div>
            <p>{reason}</p>
        </div>'''
    
    html += '<div class="nav">'
    html += '<a href="/catalog" class="nav-btn" style="background:#667eea;">📁 Каталог</a>'
    html += '<a href="/profiles" class="nav-btn" style="background:#764ba2;">👥 Профили</a>'
    html += '<a href="/community" class="nav-btn" style="background:#27ae60;">💬 Сообщество</a>'
    if current_user:
        html += f'<a href="/profile/{current_user}" class="nav-btn" style="background:#f39c12;">👤 Профиль</a>'
        if is_admin(current_user):
            html += '<a href="/admin" class="nav-btn" style="background:#e74c3c;">🔧 Админ</a>'
        html += '<a href="/logout" class="nav-btn" style="background:#95a5a6;">🚪 Выход</a>'
    else:
        html += '<a href="/login" class="nav-btn" style="background:#f39c12;">🔐 Войти</a>'
    html += '</div></div>'
    
    html += f'''
    <script>
    let lastMsgCount = {len(chat_messages)};
    let chatLoaded = false;
    const messagesDiv = document.getElementById('chat-messages');
    
    function updateChat() {{
        fetch('/api/chat').then(r=>r.json()).then(data => {{
            if(data.messages.length > lastMsgCount) {{
                lastMsgCount = data.messages.length;
                messagesDiv.innerHTML = data.html;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }}
        }});
    }}
    setInterval(updateChat, 3000);
    
    setInterval(() => {{
        fetch('/api/mutelist').then(r=>r.json()).then(data => {{
            const container = document.getElementById('mutelist-container');
            if(data.length > 0) {{
                container.style.display = 'block';
                let list = '';
                data.forEach(m => {{
                    list += `<div style="padding:8px 0;border-bottom:1px solid #fdd;">🔇 ${{m.user}} (${{m.by}}) до ${{m.ends}}</div>`;
                }});
                document.getElementById('mutelist').innerHTML = list;
            }} else {{
                container.style.display = 'none';
            }}
        }});
    }}, 5000);
    
    const muteTimer = document.getElementById('mute-timer');
    if(muteTimer) {{
        let endTime = parseFloat(muteTimer.dataset.end) * 1000;
        setInterval(() => {{
            let diff = endTime - Date.now();
            if(diff > 0) {{
                let s = Math.floor(diff/1000);
                let m = Math.floor(s/60);
                let h = Math.floor(m/60);
                muteTimer.textContent = `${{h}}ч ${{m%60}}м ${{s%60}}с`;
            }} else {{
                muteTimer.textContent = 'Мут снят!';
                setTimeout(() => location.reload(), 2000);
            }}
        }}, 1000);
    }}
    
    setInterval(() => fetch('/api/ping', {{method: 'POST'}}), 30000);
    
    function deleteMessage(msgId) {{
        if(confirm('Удалить сообщение?')) {{
            fetch(`/api/delete_message/${{msgId}}`, {{method: 'DELETE'}})
            .then(r=>r.json()).then(data => {{
                if(data.success) location.reload();
            }});
        }}
    }}
    </script></body></html>'''
    return html

@app.route('/api/chat')
def api_chat():
    html = ''
    current_user = session.get('user', '')
    for msg in reversed(chat_messages[-50:]):
        delete_btn = ''
        if current_user and (is_admin(current_user) or is_moderator(current_user)):
            delete_btn = f'<button class="delete-btn" onclick="deleteMessage({msg["id"]})">×</button>'
        html += f'''
        <div class="chat-msg">
            {delete_btn}
            <div class="chat-header">{msg["user"]} <span style="color:#666;">{msg["role"]} {datetime.fromtimestamp(msg["time"]).strftime("%H:%M")}</span></div>
            <div>{msg["text"]}</div>
        </div>'''
    return jsonify({'messages': chat_messages[-50:], 'html': html})

@app.route('/api/mutelist')
def mutelist():
    now = get_timestamp()
    mutelist = []
    for user, end_time in mutes['by'].items():
        if end_time > now or end_time == 0:
            ends = 'навсегда' if end_time == 0 else datetime.fromtimestamp(end_time).strftime('%H:%M')
            mutelist.append({
                'user': user, 
                'by': mutes['muted_by'].get(user, 'Админ'), 
                'ends': ends, 
                'reason': mutes['reason'].get(user, '')
            })
    return jsonify(mutelist)

@app.route('/api/ping', methods=['POST'])
def ping():
    current_user = session.get('user', '')
    if current_user:
        user_activity[current_user] = get_timestamp()
        save_data()
    return jsonify({'ok': True})

@app.route('/api/delete_message/<int:msg_id>', methods=['DELETE'])
def api_delete_message(msg_id):
    current_user = session.get('user', '')
    if not current_user or not (is_admin(current_user) or is_moderator(current_user)):
        return jsonify({'error': 'Нет доступа'}), 403
    
    for i, msg in enumerate(chat_messages):
        if msg['id'] == msg_id:
            del chat_messages[i]
            save_data()
            return jsonify({'success': True})
    return jsonify({'error': 'Сообщение не найдено'}), 404

@app.route('/catalog/<path:path>')
@app.route('/catalog')
def catalog_view(path=''):
    content = get_catalog_content(path)
    
    if 'error' in content or not content['folders'] and not content['items']:
        return '''<!DOCTYPE html>
<html><head><title>📁 Каталог - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter',sans-serif;padding:50px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;text-align:center;}
.container{max-width:800px;margin:auto;background:#fff;border-radius:30px;padding:80px;box-shadow:0 40px 120px rgba(0,0,0,0.2);}
.empty-icon{font-size:8em;color:#bdc3c7;margin:40px 0;}
.btn-back{background:#2c3e50;color:white;padding:25px 60px;border-radius:25px;font-size:24px;font-weight:bold;text-decoration:none;display:inline-block;box-shadow:0 20px 50px rgba(0,0,0,0.3);transition:all 0.3s;}
.btn-back:hover{transform:translateY(-5px);box-shadow:0 25px 60px rgba(0,0,0,0.4);}</style></head>
<body><div class="container">
<div class="empty-icon">📭</div>
<h1 style="font-size:4em;color:#2c3e50;margin-bottom:30px;">Каталог пуст</h1>
<p style="font-size:1.8em;color:#666;margin-bottom:60px;">👑 Администратор может добавить содержимое</p>
<a href="/" class="btn-back">🏠 На главную</a>
</div></body></html>'''
    
    breadcrumbs = '<a href="/catalog" style="color:#3498db;">📁 Каталог</a>'
    parts = [p.strip() for p in path.split('/') if p.strip()]
    temp_path = []
    for part in parts:
        temp_path.append(part)
        path_str = '/'.join(temp_path)
        breadcrumbs += f' → <a href="/catalog/{path_str}" style="color:#3498db;">{part}</a>'
    
    content_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:30px;padding:40px;">'
    
    for folder in sorted(content['folders']):
        content_html += f'''
        <a href="/catalog/{path}{"/" if path else ""}{folder}" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:40px;border-radius:25px;border-left:8px solid #2196f3;text-align:center;transition:all 0.3s;box-shadow:0 15px 40px rgba(33,150,243,0.2);">
                <div style="font-size:4em;margin-bottom:20px;">📁</div>
                <h3 style="font-size:2.2em;color:#2196f3;margin:0 0 15px 0;font-weight:bold;">{folder}</h3>
                <p style="font-size:1.4em;color:#666;font-weight:500;margin:0;">Папка</p>
            </div>
        </a>'''
    
    for item_name, item_data in sorted(content['items'].items()):
        photo_html = ''
        if item_data.get('main_photo'):
            photo_html = f'<img src="{item_data["main_photo"]}" style="width:100%;height:250px;object-fit:cover;border-radius:20px;margin-bottom:25px;box-shadow:0 10px 30px rgba(0,0,0,0.2);" alt="{item_name}" onerror="this.style.display=\'none\'">'
        
        content_html += f'''
        <div style="background:linear-gradient(135deg,#f3e5f5,#e1bee7);padding:40px;border-radius:25px;border-left:8px solid #9c27b0;box-shadow:0 15px 40px rgba(156,39,176,0.2);">
            {photo_html}
            <h3 style="font-size:2.4em;font-weight:bold;color:#2c3e50;margin-bottom:20px;">{item_name}</h3>
            <div style="background:#f9f9f9;padding:25px;border-radius:20px;font-size:1.2em;color:#444;line-height:1.7;">{item_data.get("info", "—")}</div>
        </div>'''
    
    content_html += '</div>'
    
    return f'''<!DOCTYPE html>
<html><head><title>📁 Каталог {path or "Главная"} - Узнавайкин</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter',sans-serif;padding:30px;background:#f8f9fa;color:#2c3e50;}}
.container{{max-width:1600px;margin:auto;background:#fff;border-radius:35px;padding:60px;box-shadow:0 40px 120px rgba(0,0,0,0.15);}}
.breadcrumbs{{padding:30px;background:#ecf0f1;border-radius:25px;margin-bottom:40px;font-size:1.3em;line-height:1.6;}}
.breadcrumbs a{{color:#3498db;text-decoration:none;font-weight:600;}}
h1{{text-align:center;font-size:3.5em;color:#2c3e50;margin-bottom:50px;}}
.btn{{background:#3498db;color:white;padding:25px 60px;border-radius:25px;font-size:24px;font-weight:bold;text-decoration:none;display:inline-block;margin:20px 10px;transition:all 0.3s;box-shadow:0 15px 40px rgba(52,152,219,0.3);}}
.btn:hover{{transform:translateY(-5px);box-shadow:0 25px 60px rgba(52,152,219,0.4);}}
@media (max-width:768px) {{.container{{padding:30px;margin:15px;border-radius:25px;}}}} </style></head>
<body><div class="container">
<h1>📁 Каталог</h1>
<div class="breadcrumbs">{breadcrumbs}</div>
{content_html}
<div style="text-align:center;margin-top:80px;">
<a href="/catalog" class="btn">📁 Главный Каталог</a>
<a href="/" class="btn" style="background:#27ae60;">🏠 На главную</a>
</div></div></body></html>'''

@app.route('/profiles')
def profiles():
    stats = calculate_stats()
    profiles_html = ''
    for user in sorted(users.keys()):
        role_html = get_role_display(user)
        status = '🟢 Онлайн' if is_online(user) else '⚫ Оффлайн'
        status_class = 'online' if is_online(user) else 'offline'
        profiles_html += f'''
        <div style="background:#fff;padding:30px;border-radius:20px;box-shadow:0 15px 40px rgba(0,0,0,0.1);text-align:center;margin:20px;">
            <h3 style="font-size:2em;color:#2c3e50;">👤 {user}</h3>
            <div style="padding:15px 30px;color:white;border-radius:15px;font-size:1.3em;font-weight:bold;margin:20px 0;">{role_html}</div>
            <div class="status-badge {status_class}" style="padding:12px 25px;border-radius:12px;font-size:1.2em;font-weight:bold;">{status}</div>
            <a href="/profile/{user}" style="display:inline-block;padding:15px 35px;background:#3498db;color:white;border-radius:15px;font-weight:bold;font-size:18px;text-decoration:none;">👁️ Профиль</a>
        </div>'''
    
    return f'''<!DOCTYPE html>
<html><head><title>👥 Профили</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:30px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}}
.container{{max-width:1300px;margin:auto;background:#fff;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}}
.status-online{{background:#d4edda;color:#155724;border:2px solid #28a745;}} .status-offline{{background:#e2e3e5;color:#383d41;border:2px solid #6c757d;}}
.profiles-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:30px;margin:40px 0;}}</style></head>
<body><div class="container">
<h1 style="text-align:center;font-size:3em;margin-bottom:40px;">👥 Профили ({stats["online"]} онлайн)</h1>
<div class="profiles-grid">{profiles_html}</div>
<a href="/" style="background:#2c3e50;color:white;padding:25px 50px;border-radius:20px;font-size:22px;font-weight:bold;text-decoration:none;display:block;margin:60px auto;">🏠 Главная</a>
</div></body></html>'''

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    current_user = session.get('user', '')
    if username not in users:
        return redirect(url_for('index'))
    
    profile_data = user_profiles.get(username, {'status': '🟢 Онлайн', 'info': ''})
    is_own = current_user == username
    
    if request.method == 'POST' and is_own:
        profile_data['status'] = request.form.get('status', '🟢 Онлайн')
        profile_data['info'] = request.form['info'][:500]
        user_profiles[username] = profile_data
        save_data()
    
    edit_form = ''
    if is_own:
        edit_form = f'''
        <form method="post">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:30px 0;">
            <select name="status" style="padding:20px;border:2px solid #ddd;border-radius:15px;font-size:18px;">
                <option>{"selected" if profile_data.get("status") == "🟢 Онлайн" else ""}>🟢 Онлайн</option>
                <option>{"selected" if profile_data.get("status") == "🟡 Занят" else ""}>🟡 Занят</option>
                <option>{"selected" if profile_data.get("status") == "🔴 Не беспокоить" else ""}>🔴 Не беспокоить</option>
                <option>{"selected" if profile_data.get("status") == "😴 Отошел" else ""}>😴 Отошел</option>
            </select>
            <textarea name="info" maxlength="500" style="padding:20px;border:2px solid #ddd;border-radius:15px;font-size:16px;height:120px;">{profile_data.get("info", "")}</textarea>
        </div>
        <button type="submit" style="background:#27ae60;color:white;padding:18px 35px;border:none;border-radius:12px;font-size:18px;font-weight:bold;">💾 Сохранить</button>
        </form>'''
    
    return f'''<!DOCTYPE html>
<html><head><title>{username}</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;}}
.profile-container{{max-width:900px;margin:auto;background:#fff;border-radius:30px;padding:50px;box-shadow:0 30px 100px rgba(0,0,0,0.15);}}</style></head>
<body><div class="profile-container">
<h1 style="font-size:3em;text-align:center;color:#2c3e50;margin-bottom:30px;">👤 {username}</h1>
<div style="padding:20px 40px;color:white;border-radius:25px;font-size:1.8em;font-weight:bold;display:inline-block;margin:20px 0;">{get_role_display(username)}</div>
<div style="padding:30px;background:#f8f9fa;border-radius:20px;margin:30px 0;font-size:1.2em;">{profile_data.get("info", "Информация не указана")}</div>
{edit_form}
<a href="/" style="background:#2c3e50;color:white;padding:20px 40px;border-radius:20px;font-size:18px;font-weight:bold;text-decoration:none;display:inline-block;margin:20px;">🏠 Главная</a>
</div></body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        session['user'] = username
        
        if username not in user_roles:
            user_roles[username] = 'start'
        if username not in users:
            users[username] = {'password': password, 'role': 'start'}
            user_profiles[username] = {'status': '🟢 Онлайн', 'info': ''}
            user_activity[username] = get_timestamp()
        save_data()
        return redirect(url_for('index'))
    
    return '''<!DOCTYPE html>
<html><head><title>🔐 Вход</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:'Inter';background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px;}
.login-box{background:#fff;padding:60px;border-radius:30px;box-shadow:0 35px 120px rgba(0,0,0,0.25);width:100%;max-width:450px;}
input{width:100%;padding:25px;margin:15px 0;border:2px solid #ddd;border-radius:15px;font-size:18px;box-sizing:border-box;}
button{width:100%;padding:25px;background:linear-gradient(45deg,#ff6b6b,#4ecdc4);color:white;border:none;border-radius:15px;font-size:20px;font-weight:bold;cursor:pointer;}</style></head>
<body><div class="login-box">
<h1 style="text-align:center;font-size:2.8em;color:#2c3e50;margin-bottom:30px;">🔐 Узнавайкин v35</h1>
<form method="post">
<input name="username" placeholder="👤 Логин" required maxlength="20">
<input name="password" type="password" placeholder="🔑 Пароль" required>
<button>🚀 ВОЙТИ / РЕГИСТРАЦИЯ</button>
</form></div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/community')
def community():
    return '''<!DOCTYPE html>
<html><head><title>💬 Сообщество</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:100px;background:linear-gradient(135deg,#667eea,#764ba2);color:#2c3e50;text-align:center;}}
.container{{max-width:800px;margin:auto;background:#fff;border-radius:30px;padding:80px;box-shadow:0 40px 120px rgba(0,0,0,0.2);}}</style></head>
<body><div class="container">
<h1 style="font-size:4em;color:#2c3e50;margin-bottom:40px;">💬 Сообщество</h1>
<p style="font-size:2em;margin:60px 0;"><a href="https://t.me/ssylkanatelegramkanalyznaikin" target="_blank" style="color:#27ae60;font-size:1.4em;font-weight:bold;">Telegram Канал</a></p>
<a href="/" style="background:#2c3e50;color:white;padding:25px 60px;border-radius:25px;font-size:24px;font-weight:bold;text-decoration:none;display:inline-block;">🏠 На главную</a>
</div></body></html>'''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    current_user = session.get('user', '')
    if not is_admin(current_user):
        return redirect(url_for('index'))
    
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        current_time = get_timestamp()
        
        if action == 'mute':
            target = request.form['target'].strip()
            days = request.form['days']
            unit = request.form['unit']
            reason = request.form['reason'].strip()[:100]
            
            duration = parse_duration(days, unit)
            end_time = 0 if duration == 0 else current_time + duration
            
            if target in users and target != current_user:
                mutes['by'][target] = end_time
                mutes['reason'][target] = reason
                mutes['muted_by'][target] = current_user
                chat_messages.append({
                    'id': len(chat_messages), 'user': 'СИСТЕМА', 
                    'text': f'🔇 {target} замучен {current_user} на {days} {unit} | {reason}',
                    'time': current_time, 'role': 'Модерация'
                })
                message = f'✅ {target} замучен на {days} {unit}!'
        
        elif action == 'unmute':
            target = request.form['target'].strip()
            if target in mutes['by']:
                del mutes['by'][target]
                del mutes['reason'][target]
                del mutes['muted_by'][target]
                message = f'✅ {target} размучен!'
        
        elif action == 'make_moderator':
            target = request.form['target'].strip()
            if target in users and target != current_user:
                user_roles[target] = 'moderator'
                message = f'✅ {target} теперь модератор!'
        
        elif action == 'remove_moderator':
            target = request.form['target'].strip()
            if target in users and user_roles.get(target) == 'moderator':
                user_roles[target] = 'start'
                message = f'✅ У {target} снята модерация!'
        
        save_data()
    
    stats = calculate_stats()
    
    admin_html = f'''
    <div style="background:#d5f4e6;padding:25px;border-radius:15px;margin:25px 0;border-left:6px solid #27ae60;">
        <h2>📊 {stats['online']} онлайн, {stats['afk']} АФК</h2>
    </div>'''
    
    if message:
        admin_html += f'<div style="background:#d4edda;color:#155724;padding:20px;border-radius:15px;margin:25px 0;">{message}</div>'
    
    admin_html += '''
    <h3 style="color:#e74c3c;">👑 Админ функции</h3>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;">
    
    <div style="background:#f8d7da;padding:25px;border-radius:15px;border-left:5px solid #dc3545;">
        <h4>🔇 Замутить</h4>
        <form method="post">
            <input type="hidden" name="action" value="mute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
            <div style="display:grid;grid-template-columns:2fr 1fr;gap:10px;">
                <input name="days" placeholder="Число" type="number" min="1" required style="padding:12px;border:1px solid #ddd;border-radius:8px;">
                <select name="unit" required style="padding:12px;border:1px solid #ddd;border-radius:8px;">
                    <option value="секунд">секунд</option><option value="минут">минут</option>
                    <option value="часов">часов</option><option value="дней">дней</option>
                    <option value="лет">лет</option><option value="навсегда">навсегда</option>
                </select>
            </div>
            <input name="reason" placeholder="Причина" style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:8px;font-weight:bold;">🔇 Замутить</button>
        </form>
    </div>

    <div style="background:#d4edda;padding:25px;border-radius:15px;border-left:5px solid #28a745;">
        <h4>🔊 Размутить</h4>
        <form method="post">
            <input type="hidden" name="action" value="unmute">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:8px;font-weight:bold;">🔊 Размутить</button>
        </form>
    </div>

    <div style="background:#fff3cd;padding:25px;border-radius:15px;border-left:5px solid #ffc107;">
        <h4>🛡️ Назначить модератора</h4>
        <form method="post">
            <input type="hidden" name="action" value="make_moderator">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#ffc107;color:#000;border:none;border-radius:8px;font-weight:bold;">Назначить</button>
        </form>
    </div>

    <div style="background:#fff3cd;padding:25px;border-radius:15px;border-left:5px solid #ffc107;">
        <h4>❌ Снять модератора</h4>
        <form method="post">
            <input type="hidden" name="action" value="remove_moderator">
            <input name="target" placeholder="👤 Ник" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
            <button type="submit" style="width:100%;padding:12px;background:#ffc107;color:#000;border:none;border-radius:8px;font-weight:bold;">Снять</button>
        </form>
    </div>
    </div>'''
    
    return f'''<!DOCTYPE html>
<html><head><title>🔧 Админ-панель</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#ff9a9e,#fecfef);padding:20px;color:#2c3e50;}}
.container{{max-width:1400px;margin:auto;background:#fff;border-radius:30px;padding:40px;box-shadow:0 30px 100px rgba(0,0,0,0.2);}}</style></head>
<body><div class="container">
<h1 style="text-align:center;font-size:2.8em;margin-bottom:30px;">🔧 Админ-панель - {current_user}</h1>
{admin_html}
<a href="/" style="background:#2c3e50;color:white;padding:20px 50px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:block;margin:50px auto;text-align:center;">🏠 Главная</a>
</div></body></html>'''

@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html><head><title>404</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{{font-family:'Inter';padding:100px;background:linear-gradient(135deg,#667eea,#764ba2);color:#e74c3c;text-align:center;}}</style></head>
<body><h1 style="font-size:8em;margin-bottom:30px;">404</h1><p style="font-size:2em;">Страница не найдена</p><a href="/" style="background:#2c3e50;color:white;padding:20px 50px;border-radius:20px;font-size:20px;font-weight:bold;text-decoration:none;display:inline-block;">🏠 На главную</a></body></html>''', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

