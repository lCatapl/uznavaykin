#!/usr/bin/env python3
# 🚀 УЗНАВАЙКИН v44.0 — BATTLE ARENA СТИЛЬ (100% НОВЫЙ ДИЗАЙН)

import os, time, random, re, sqlite3, json, logging, hashlib
from datetime import datetime, timedelta
from flask import Flask, request, session, redirect, render_template_string
from flask_socketio import SocketIO, emit
from collections import defaultdict, deque
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps, lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'battle-arena-v44-uznavaykin-2026')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False)

DB_PATH = os.environ.get('DB_PATH', '/tmp/battle_arena_v44.db')

# ✅ BATTLE ARENA CSS v44.0 (Точный дизайн)
BATTLE_ARENA_CSS = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {margin:0;padding:0;box-sizing:border-box;}
:root {
  --bg-primary: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  --card-bg: rgba(255,255,255,0.08);
  --card-glass: rgba(255,255,255,0.12);
  --accent-gold: #ffd700;
  --accent-blue: #00d4ff;
  --accent-green: #00ff88;
  --text-primary: #ffffff;
  --text-secondary: #b8b8b8;
  --border-glow: 0 0 20px rgba(0,212,255,0.3);
}

body {
  font-family: 'Segoe UI', -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: hidden;
}

.header-profile {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card-glass);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 15px 25px;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: var(--border-glow);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 1000;
}

.profile-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, var(--accent-gold), #ffed4e);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 900;
  color: #1a1a2e;
}

.balance {
  font-size: 24px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent-gold), #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(255,215,0,0.5);
}

.page-title {
  font-size: 4em;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  margin: 100px 0 40px 0;
  text-shadow: 0 0 40px rgba(0,212,255,0.5);
}

.game-card {
  background: var(--card-glass);
  backdrop-filter: blur(25px);
  border-radius: 25px;
  padding: 40px;
  margin: 30px auto;
  max-width: 1200px;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: var(--border-glow);
  transition: all 0.4s;
}

.game-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 30px 80px rgba(0,0,0,0.5);
}

.btn-battle {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-gold));
  color: #1a1a2e !important;
  font-weight: 900;
  padding: 20px 50px;
  border-radius: 50px;
  text-decoration: none;
  display: inline-block;
  font-size: 18px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(0,212,255,0.4);
}

.btn-battle:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 50px rgba(0,212,255,0.6);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
  margin: 40px 0;
}

.stat-card {
  background: rgba(255,255,255,0.05);
  padding: 25px;
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
}

.stat-number {
  font-size: 2.5em;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.chat-messages {
  max-height: 500px;
  overflow-y: auto;
  padding: 25px;
  background: rgba(0,0,0,0.3);
  border-radius: 20px;
  margin: 20px 0;
}

.chat-message {
  display: flex;
  gap: 15px;
  padding: 20px;
  margin: 15px 0;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  border-left: 5px solid var(--accent-blue);
}

.chat-rank {
  font-size: 24px;
  font-weight: 900;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.leaderboard-row {
  display: grid;
  grid-template-columns: 60px 1fr 150px 120px;
  gap: 20px;
  padding: 20px;
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
  margin: 10px 0;
  align-items: center;
}

.rank-badge {
  font-size: 2em;
}

@media (max-width: 768px) {
  .header-profile { flex-direction: column; gap: 10px; padding: 20px; }
  .page-title { font-size: 2.5em; margin: 80px 20px 30px; }
  .game-card { margin: 20px 10px; padding: 25px; }
}
</style>
'''

# ✅ 25 ЗВАНИЙ (изменены эмодзи под Battle Arena)
RANK_SYSTEM = {
    0: '👶 Новобранец', 1: '⚔️ Рядовой', 3: '⭐ Ефрейтор', 7: '🔫 Капрал',
    15: '🎖️ Мастер-капрал', 30: '👮 Сержант', 50: '🛡️ Штаб-сержант', 80: '💪 Мастер-сержант',
    120: '⭐⭐ Первый сержант', 170: '🎖️🎖️ Сержант-майор', 230: '⚓ Уорэнт-офицер',
    300: '⭐⭐⭐ Младший лейтенант', 380: '🔫🔫 Лейтенант', 470: '🎖️🎖️🎖️ Старший лейтенант',
    570: '👑 Капитан', 680: '🌟 Майор', 810: '⭐⭐⭐⭐ Подполковник', 960: '🎖️🎖️🎖️🎖️ Полковник',
    1120: '🔫🔫🔫 Бригадир', 1300: '👑👑 Генерал-майор', 1500: '🌟🌟 Генерал-лейтенант',
    1720: '⭐⭐⭐⭐⭐ Генерал', 1960: '🎖️🎖️🎖️🎖️🎖️ Маршал', 2220: '🔫🔫🔫🔫 Фельдмаршал', 
    2500: '👑👑👑 Командор', 2800: '🌟🌟🌟 Генералиссимус', 3200: '🏆 Легенда', 
    10000: '🎖️🎖️🎖️🎖️🎖️🎖️ Ветеран'
}

# [ОСТАЛЬНОЙ КОД БАЗЫ ДАННЫХ ИЗ v43 ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ]
class MegaDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;')
            return conn
        except:
            return None
    
    def init_db(self):
        conn = self.get_connection()
        if not conn: return False
        
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, coins INTEGER DEFAULT 15000,
                wins INTEGER DEFAULT 0, level INTEGER DEFAULT 1, clan TEXT DEFAULT NULL,
                rank TEXT DEFAULT '👶 Новобранец', role TEXT DEFAULT 'player', created REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, message TEXT NOT NULL,
                timestamp REAL NOT NULL, rank TEXT
            );
        ''')
        
        conn.execute('INSERT OR REPLACE INTO users VALUES (?, ?, 15000, 128, 15, ?, ?, ?, ?)',
                    ('Player_7734', generate_password_hash('7734'), 'Dark Knights', '🎯 Боец', 'player', time.time()))
        
        conn.commit()
        conn.close()
        return True

db = MegaDatabase()

def get_user(username):
    conn = db.get_connection()
    if not conn: return None
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

chat_messages = deque(maxlen=1000)

# ✅ ГЛАВНЫЙ ЭКРАН — BATTLE ARENA СТИЛЬ
@app.route('/')
@require_auth
def battle_arena_home():
    user = get_user(session['user'])
    coins = user['coins'] if user else 15000
    
    return f'''{BATTLE_ARENA_CSS}
<div class="header-profile">
  <div class="profile-avatar">🎮</div>
  <div>
    <div style="font-size:14px;color:var(--text-secondary);">BATTLE ARENA</div>
    <div class="balance">{coins:,}</div>
    <div style="font-size:12px;color:var(--text-secondary);">Player_7734</div>
  </div>
</div>

<div class="game-card" style="text-align:center;margin-top:150px;">
  <h1 class="page-title">BATTLE ARENA</h1>
  <div style="font-size:2em;color:var(--text-secondary);margin-bottom:40px;">
    27+ СИСТЕМ ЗАПУЩЕНО • 🟢 ONLINE
  </div>
  <div style="font-size:3em;font-weight:300;margin-bottom:30px;">Боевая игровая платформа</div>
  <div style="font-size:1.2em;color:var(--text-secondary);margin-bottom:50px;max-width:600px;margin-left:auto;margin-right:auto;">
    Авторизация • Реал-тайм чат • Турниры • Кланы • Экономика • Достижения • 12+ игр
  </div>
  <div style="display:flex;gap:30px;justify-content:center;flex-wrap:wrap;">
    <a href="/games" class="btn-battle" style="background:linear-gradient(135deg,var(--accent-green),var(--accent-blue));">🎮 Начать играть</a>
    <a href="/chat" class="btn-battle" style="background:linear-gradient(135deg,#ff6b6b,#ee5a52);">Открыть чат</a>
  </div>
</div>

<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-number">27+</div>
    <div style="color:var(--text-secondary);">Систем</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">1,234</div>
    <div style="color:var(--text-secondary);">Игроков онлайн</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">156</div>
    <div style="color:var(--text-secondary);">Кланов</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">12+</div>
    <div style="color:var(--text-secondary);">Игр</div>
  </div>
</div>

<div style="text-align:center;padding:40px;color:var(--text-secondary);font-size:14px;">
  © 2026 BATTLE ARENA. Все права защищены.<br>
  <span style="font-size:12px;">27+ систем • 12+ игр • Реал-тайм платформа</span>
</div>'''

# ✅ ИГРЫ — BATTLE ARENA СТИЛЬ
@app.route('/games')
@require_auth
def games():
    return f'''{BATTLE_ARENA_CSS}
<div class="header-profile">
  <div class="profile-avatar">🎮</div>
  <div><div style="font-size:14px;color:var(--text-secondary);">BATTLE ARENA</div><div class="balance">15 000</div><div style="font-size:12px;color:var(--text-secondary);">Player_7734</div></div>
</div>

<div style="text-align:center;margin-top:120px;">
  <h1 class="page-title">Игры</h1>
</div>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;max-width:1200px;margin:40px auto;">
  <div class="game-card" style="text-align:center;">
    <h3 style="font-size:2.5em;margin-bottom:20px;">🎰 Рулетка</h3>
    <div style="font-size:3em;font-weight:900;color:var(--accent-gold);margin-bottom:30px;">x35</div>
    <a href="/casino" class="btn-battle" style="width:100%;padding:25px 20px;">Играть</a>
  </div>
  
  <div class="game-card" style="text-align:center;">
    <h3 style="font-size:2.5em;margin-bottom:20px;">🃏 Блэкджек</h3>
    <div style="font-size:3em;font-weight:900;color:var(--accent-gold);margin-bottom:30px;">x10</div>
    <a href="#" class="btn-battle" style="width:100%;padding:25px 20px;">Играть</a>
  </div>
  
  <div class="game-card" style="text-align:center;">
    <h3 style="font-size:2.5em;margin-bottom:20px;">🐍 Snake</h3>
    <div style="font-size:3em;font-weight:900;color:var(--accent-gold);margin-bottom:30px;">Очки</div>
    <a href="#" class="btn-battle" style="width:100%;padding:25px 20px;">Играть</a>
  </div>
</div>

<div style="text-align:center;padding:60px;color:var(--text-secondary);font-size:14px;">
  © 2026 BATTLE ARENA. Все права защищены.
</div>'''

# ✅ ЧАТ — BATTLE ARENA СТИЛЬ  
@app.route('/chat')
@require_auth
def battle_chat():
    recent_messages = list(chat_messages)[-6:]
    chat_html = ''
    ranks = ['👑', '🔥', '🍀', '⚔️', '🎮']
    
    for i, msg in enumerate(recent_messages):
        chat_html += f'''
        <div class="chat-message">
          <div style="font-size:28px;">{ranks[i%len(ranks)]}</div>
          <div style="flex:1;">
            <div style="font-weight:900;font-size:16px;">{msg['user']}</div>
            <div style="color:var(--text-secondary);font-size:14px;">{datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M')}</div>
            <div>{msg['message']}</div>
          </div>
        </div>'''
    
    return f'''{BATTLE_ARENA_CSS}
<div class="header-profile">
  <div class="profile-avatar">💬</div>
  <div><div style="font-size:14px;color:var(--text-secondary);">BATTLE ARENA</div><div class="balance">15 000</div><div style="font-size:12px;color:var(--text-secondary);">Player_7734</div></div>
</div>

<div style="text-align:center;margin-top:120px;">
  <h1 class="page-title">Чат</h1>
  <div style="font-size:2em;margin-bottom:20px;">Глобальный чат</div>
  <div style="color:var(--accent-green);font-size:1.5em;margin-bottom:40px;">🟢 6 сообщений</div>
</div>

<div class="game-card" style="max-width:800px;">
  <div class="chat-messages">
    {chat_html}
  </div>
  <div style="display:flex;gap:15px;margin-top:30px;">
    <input id="chat-input" placeholder="Написать в чат..." style="flex:1;padding:20px;border-radius:25px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:var(--text-primary);font-size:16px;">
    <button onclick="sendMessage()" class="btn-battle" style="padding:20px 30px;">Отправить</button>
  </div>
</div>

<div style="text-align:center;padding:60px;color:var(--text-secondary);font-size:14px;">
  © 2026 BATTLE ARENA. Все права защищены.
</div>

<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
const socket = io();
function sendMessage() {{
  const input = document.getElementById('chat-input');
  socket.emit('message', {{message: input.value}});
  input.value = '';
}}
document.getElementById('chat-input').addEventListener('keypress', e => {{
  if (e.key === 'Enter') sendMessage();
}});
</script>'''

# ✅ ПРОФИЛЬ — BATTLE ARENA СТИЛЬ
@app.route('/profile')
@require_auth
def profile():
    user = get_user(session['user'])
    return f'''{BATTLE_ARENA_CSS}
<div class="header-profile">
  <div class="profile-avatar">🎮</div>
  <div><div style="font-size:14px;color:var(--text-secondary);">BATTLE ARENA</div><div class="balance">{user['coins']:,}</div><div style="font-size:12px;color:var(--text-secondary);">{user['username']}</div></div>
</div>

<div style="text-align:center;margin-top:120px;">
  <h1 class="page-title">Профиль</h1>
</div>

<div class="game-card" style="max-width:600px;display:grid;grid-template-columns:1fr 2fr;gap:40px;">
  <div>
    <div class="profile-avatar" style="width:150px;height:150px;font-size:60px;margin:0 auto 20px;">🎮</div>
    <h2 style="text-align:center;font-size:2.5em;margin-bottom:10px;">{user['username']}</h2>
    <div style="text-align:center;color:var(--accent-gold);font-size:1.5em;">{user['clan'] or 'Без клана'}</div>
  </div>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:30px;">
      <div><div style="font-size:1.5em;">Уровень 15</div><div style="color:var(--text-secondary);">128 побед</div></div>
      <div style="text-align:right;"><div style="font-size:2em;font-weight:900;color:var(--accent-gold);">15 000 монет</div><div style="color:var(--text-secondary);">Ранг #4</div></div>
    </div>
    <div style="background:rgba(255,255,255,0.1);padding:20px;border-radius:15px;margin-bottom:30px;">
      <div style="display:flex;align-items:center;gap:15px;margin-bottom:10px;">
        <div style="width:30px;height:30px;background:var(--accent-green);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;">15</div>
        <div>Прогресс до уровня 16</div>
      </div>
      <div style="background:rgba(255,255,255,0.2);height:10px;border-radius:5px;overflow:hidden;">
        <div style="background:linear-gradient(90deg,var(--accent-blue),var(--accent-gold));height:100%;width:35%;"></div>
      </div>
      <div style="font-size:14px;color:var(--text-secondary);">3500 / 5000 XP</div>
    </div>
    
    <h3 style="margin-bottom:20px;">Разблокированные достижения</h3>
    <div style="display:flex;flex-wrap:wrap;gap:15px;">
      <div style="padding:15px 20px;background:rgba(0,255,136,0.2);border-radius:20px;border-left:4px solid var(--accent-green);">🗣️ Первый чат</div>
      <div style="padding:15px 20px;background:rgba(255,215,0,0.2);border-radius:20px;border-left:4px solid var(--accent-gold);">🍀 Удачник</div>
      <div style="padding:15px 20px;background:rgba(0,255,136,0.2);border-radius:20px;border-left:4px solid var(--accent-green);">📅 Регулярный</div>
    </div>
  </div>
</div>

<div style="text-align:center;padding:60px;color:var(--text-secondary);font-size:14px;">
  © 2026 BATTLE ARENA. Все права защищены.
</div>'''

# ✅ ЛИДЕРБОРД — BATTLE ARENA СТИЛЬ
@app.route('/leaderboard')
@require_auth
def leaderboard():
    leaderboard_data = [
        ('🐉', 'DragonSlayer', '🏆 Легенда', '3200 побед', '50 000💰'),
        ('🥷', 'ShadowNinja', '💎 Мастер', '3000 побед', '45 000💰'),
        ('🔥', 'FireStorm', '⚡ Эксперт', '2800 побед', '40 000💰'),
        ('🎮', 'Player_7734', '🎯 Боец', '128 побед', '15 000💰'),
        ('👸', 'IceQueen', '❄️ Боец', '2400 побед', '30 000💰')
    ]
    
    lb_rows = ''
    for i, (badge, name, rank, wins, coins) in enumerate(leaderboard_data, 1):
        lb_rows += f'''
        <div class="leaderboard-row">
          <div style="font-size:2.5em;font-weight:900;color:var(--accent-gold);">{i}</div>
          <div style="display:flex;align-items:center;gap:15px;">
            <div class="rank-badge">{badge}</div>
            <div>
              <div style="font-weight:900;font-size:1.3em;">{name}</div>
              <div style="color:var(--text-secondary);font-size:0.9em;">{rank} • {wins}</div>
            </div>
          </div>
          <div style="font-weight:900;color:var(--accent-gold);">{coins}</div>
        </div>'''
    
    return f'''{BATTLE_ARENA_CSS}
<div class="header-profile">
  <div class="profile-avatar">🏆</div>
  <div><div style="font-size:14px;color:var(--text-secondary);">BATTLE ARENA</div><div class="balance">15 000</div><div style="font-size:12px;color:var(--text-secondary);">Player_7734</div></div>
</div>

<div style="text-align:center;margin-top:120px;">
  <h1 class="page-title">Лидерборд</h1>
</div>

<div class="game-card" style="max-width:900px;">
  {lb_rows}
</div>

<div style="text-align:center;padding:60px;color:var(--text-secondary);font-size:14px;">
  © 2026 BATTLE ARENA. Все права защищены.
</div>'''

# ✅ Логин/Регистрация (упрощенные)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'Player_7734' and request.form.get('password') == '7734':
            session['user'] = 'Player_7734'
            return redirect('/')
    return f'''{BATTLE_ARENA_CSS}
<div class="game-card" style="max-width:400px;margin:200px auto;">
  <h1 style="font-size:3em;text-align:center;margin-bottom:40px;">🔐 Вход</h1>
  <form method="POST">
    <input name="username" placeholder="Player_7734" style="width:100%;padding:20px;border-radius:15px;border:1px solid rgba(255,255,255,0.2);background:var(--card-bg);color:var(--text-primary);margin-bottom:20px;font-size:16px;">
    <input name="password" type="password" placeholder="7734" style="width:100%;padding:20px;border-radius:15px;border:1px solid rgba(255,255,255,0.2);background:var(--card-bg);color:var(--text-primary);margin-bottom:30px;font-size:16px;">
    <button type="submit" class="btn-battle" style="width:100%;padding:20px;">Войти</button>
  </form>
</div>'''

@socketio.on('message')
def handle_message(data):
    chat_messages.append({
        'user': session.get('user', 'Player_7734'),
        'message': data.get('message', ''),
        'timestamp': time.time()
    })
    emit('message', chat_messages[-1], broadcast=True)

if __name__ == '__main__':
    print("🚀 BATTLE ARENA v44.0 — УЗНАВАЙКИН РЕДИЗАЙН!")
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
