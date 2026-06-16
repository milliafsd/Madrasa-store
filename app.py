import json
import os
from datetime import datetime, date
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # پروڈکشن میں تبدیل کریں
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ========== ڈیٹا فائل ==========
DATA_FILE = 'store_data.json'

# ========== ڈیفالٹ ڈیٹا ==========
DEFAULT_USERS = [
    {"id": 1, "username": "admin", "password": "admin123", "role": "admin", "name": "ایڈمن صاحب"},
    {"id": 2, "username": "user1", "password": "user123", "role": "user", "name": "محمد احمد"},
    {"id": 3, "username": "user2", "password": "user456", "role": "user", "name": "عبداللہ خان"},
]

DEFAULT_CATEGORIES = ["کتب و کاپیاں", "صفائی کا سامان", "بجلی کا سامان", "فرنیچر", "کھانے پینے کی اشیاء", "کمپیوٹر و ٹیکنالوجی", "دیگر"]

DEFAULT_ROOMS = [
    {"id": 1, "name": "دفتر مہتمم", "color": "#1a472a", "icon": "🏛️"},
    {"id": 2, "name": "لائبریری", "color": "#0d47a1", "icon": "📚"},
    {"id": 3, "name": "کمپیوٹر لیب", "color": "#4a148c", "icon": "💻"},
    {"id": 4, "name": "باورچی خانہ", "color": "#bf360c", "icon": "🍽️"},
    {"id": 5, "name": "مرکزی اسٹور", "color": "#37474f", "icon": "🏪"},
]

DEFAULT_ITEMS = [
    {"id": 1, "name": "A4 پیپر ریم", "roomId": 5, "category": "کتب و کاپیاں", "quantity": 50, "unit": "ریم", "minQty": 10},
    {"id": 2, "name": "بال پوائنٹ قلم", "roomId": 5, "category": "کتب و کاپیاں", "quantity": 200, "unit": "عدد", "minQty": 30},
    {"id": 3, "name": "جھاڑو", "roomId": 5, "category": "صفائی کا سامان", "quantity": 8, "unit": "عدد", "minQty": 2},
    {"id": 4, "name": "صابن", "roomId": 5, "category": "صفائی کا سامان", "quantity": 24, "unit": "عدد", "minQty": 5},
    {"id": 5, "name": "LED بلب", "roomId": 5, "category": "بجلی کا سامان", "quantity": 20, "unit": "عدد", "minQty": 5},
    {"id": 6, "name": "پرنٹر", "roomId": 3, "category": "کمپیوٹر و ٹیکنالوجی", "quantity": 2, "unit": "عدد", "minQty": 1},
    {"id": 7, "name": "کرسی", "roomId": 1, "category": "فرنیچر", "quantity": 6, "unit": "عدد", "minQty": 2},
    {"id": 8, "name": "چائے پتی", "roomId": 4, "category": "کھانے پینے کی اشیاء", "quantity": 3, "unit": "کلو", "minQty": 1},
]

DEFAULT_TRANSACTIONS = [
    {"id": 1, "itemId": 1, "itemName": "A4 پیپر ریم", "userId": 2, "userName": "محمد احمد", "type": "issue", "qty": 5,
     "date": "2025-06-10", "returnDate": None, "expectedReturn": "2025-06-20", "note": "امتحانی پرچے", "status": "issued"},
    {"id": 2, "itemId": 3, "itemName": "جھاڑو", "userId": 3, "userName": "عبداللہ خان", "type": "issue", "qty": 2,
     "date": "2025-06-08", "returnDate": "2025-06-12", "expectedReturn": "2025-06-15", "note": "صفائی کے لیے", "status": "returned"},
]

# ========== ڈیٹا لوڈ / سیو ==========
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "users": DEFAULT_USERS,
            "categories": DEFAULT_CATEGORIES,
            "rooms": DEFAULT_ROOMS,
            "items": DEFAULT_ITEMS,
            "transactions": DEFAULT_TRANSACTIONS
        }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== ہیلپر فنکشنز ==========
def get_next_id(collection):
    return max([item['id'] for item in collection] + [0]) + 1

def get_room_name(room_id, rooms):
    for r in rooms:
        if r['id'] == room_id:
            return r['name']
    return "نامعلوم"

# ========== بیس ٹیمپلیٹ (HTML) ==========
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جامعہ ملیہ اسلامیہ - اسٹور مینجمنٹ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Nastaliq Urdu', serif; background: #0a0e1a; color: #e8eaf0; }
        .sidebar { background: linear-gradient(180deg, #0d1f14 0%, #0a0e1a 100%); min-height: 100vh; padding: 20px; border-left: 1px solid rgba(201,168,76,0.2); }
        .sidebar .brand { font-size: 24px; color: #c9a84c; text-align: center; margin-bottom: 30px; }
        .sidebar .nav-link { color: #9ca3af; border-radius: 10px; padding: 10px 15px; margin-bottom: 4px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { background: rgba(201,168,76,0.12); color: #c9a84c; }
        .main-content { padding: 20px; background: #111827; }
        .card { background: #1a2234; border: 1px solid rgba(201,168,76,0.2); border-radius: 14px; }
        .card-header { background: rgba(201,168,76,0.04); border-bottom: 1px solid rgba(201,168,76,0.2); color: #c9a84c; }
        .btn-gold { background: linear-gradient(135deg, #c9a84c, #a07830); color: #0a0e1a; font-weight: 700; }
        .btn-gold:hover { color: #0a0e1a; box-shadow: 0 4px 12px rgba(201,168,76,0.3); }
        .stat-card { background: #1a2234; border: 1px solid rgba(201,168,76,0.2); border-radius: 14px; padding: 20px; text-align: center; }
        .stat-value { font-size: 28px; font-weight: 700; color: #c9a84c; }
        .badge-low { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
        .badge-ok { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
        .badge-issued { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
        .badge-returned { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
        .table { color: #e8eaf0; }
        .table th { border-bottom: 1px solid rgba(201,168,76,0.2); color: #c9a84c; }
        .table td { border-bottom: 1px solid rgba(255,255,255,0.04); }
        .alert-bar { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); border-radius: 10px; padding: 12px 16px; color: #fca5a5; }
        .login-card { background: rgba(17,24,39,0.9); border: 1px solid rgba(201,168,76,0.2); border-radius: 20px; padding: 40px; backdrop-filter: blur(20px); }
        .login-card h1 { color: #c9a84c; }
        .form-control { background: #1a2234; border: 1px solid rgba(201,168,76,0.2); color: #e8eaf0; }
        .form-control:focus { border-color: #c9a84c; box-shadow: 0 0 0 3px rgba(201,168,76,0.1); }
        .form-label { color: #9ca3af; }
        .room-card { border-radius: 14px; padding: 20px; cursor: pointer; transition: 0.2s; border: 1px solid rgba(255,255,255,0.08); }
        .room-card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
        .room-icon { font-size: 36px; }
        .room-name { font-size: 16px; font-weight: 600; color: #fff; }
        .room-count { font-size: 12px; color: rgba(255,255,255,0.6); }
        .ai-panel { background: linear-gradient(135deg, #0d1f14, #0a0e1a); border: 1px solid rgba(201,168,76,0.3); border-radius: 14px; padding: 24px; }
        .ai-response { background: #1a2234; border-radius: 10px; padding: 16px; min-height: 80px; white-space: pre-wrap; }
        .ai-prompt-btn { background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.2); color: #c9a84c; border-radius: 20px; padding: 6px 14px; font-size: 12px; cursor: pointer; }
        .ai-prompt-btn:hover { background: rgba(201,168,76,0.15); }
        .progress { height: 6px; background: #1a2234; }
        .progress-bar-gold { background: linear-gradient(90deg, #c9a84c, #a07830); }
        @media (max-width: 768px) {
            .sidebar { min-height: auto; }
        }
        /* RTL fixes */
        .nav-link { text-align: right; }
        .dropdown-menu { text-align: right; }
    </style>
</head>
<body>
    {% if not session.user %}
        <!-- لاگ ان صفحہ -->
        <div class="container d-flex align-items-center justify-content-center min-vh-100">
            <div class="login-card w-100" style="max-width: 420px;">
                <div class="text-center mb-4">
                    <div style="font-size: 52px;">🕌</div>
                    <h1>جامعہ ملیہ اسلامیہ فیصل آباد</h1>
                    <p class="text-secondary">اسٹور مینجمنٹ سسٹم</p>
                </div>
                {% with messages = get_flashed_messages() %}
                    {% if messages %}
                        <div class="alert alert-danger">{{ messages[0] }}</div>
                    {% endif %}
                {% endwith %}
                <form method="POST" action="{{ url_for('login') }}">
                    <div class="mb-3">
                        <label class="form-label">صارف نام</label>
                        <input type="text" name="username" class="form-control" placeholder="username" dir="ltr">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">پاسورڈ</label>
                        <input type="password" name="password" class="form-control" placeholder="password" dir="ltr">
                    </div>
                    <button type="submit" class="btn btn-gold w-100">🔐 داخل ہوں</button>
                </form>
                <p class="text-center text-secondary mt-3" style="font-size:12px;">Admin: admin/admin123 | User: user1/user123</p>
            </div>
        </div>
    {% else %}
        <!-- مکمل ایپ -->
        <div class="container-fluid">
            <div class="row">
                <!-- سائیڈ بار -->
                <nav class="col-md-3 col-lg-2 d-md-block sidebar p-0">
                    <div class="brand p-3">🕌 جامعہ</div>
                    <div class="user-info p-3 border-bottom border-secondary">
                        <strong>{{ session.user.name }}</strong> 
                        <span class="badge bg-warning text-dark">{{ 'ایڈمن' if session.user.role == 'admin' else 'صارف' }}</span>
                    </div>
                    <ul class="nav flex-column mt-3">
                        <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'dashboard' }}" href="{{ url_for('dashboard') }}">📊 ڈیش بورڈ</a></li>
                        {% if session.user.role == 'admin' %}
                            <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'rooms' }}" href="{{ url_for('rooms') }}">🏠 کمرے</a></li>
                        {% endif %}
                        <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'items' }}" href="{{ url_for('items') }}">📦 سامان</a></li>
                        <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'issue' }}" href="{{ url_for('issue') }}">➡️ جاری کریں</a></li>
                        <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'returns' }}" href="{{ url_for('returns') }}">↩️ واپسی</a></li>
                        {% if session.user.role == 'admin' %}
                            <li class="nav-item"><a class="nav-link {{ 'active' if request.endpoint == 'ai' }}" href="{{ url_for('ai') }}">🤖 AI تجزیہ</a></li>
                        {% endif %}
                        <li class="nav-item"><a class="nav-link text-danger" href="{{ url_for('logout') }}">🚪 لاگ آؤٹ</a></li>
                    </ul>
                </nav>

                <!-- مین کونٹینٹ -->
                <main class="col-md-9 col-lg-10 main-content">
                    {% block content %}{% endblock %}
                </main>
            </div>
        </div>
    {% endif %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# ========== راؤٹس ==========
@app.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(BASE_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    data = load_data()
    user = next((u for u in data['users'] if u['username'] == username and u['password'] == password), None)
    if user:
        session['user'] = user
        return redirect(url_for('dashboard'))
    else:
        flash('غلط صارف نام یا پاسورڈ')
        return render_template_string(BASE_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# ----- ڈیش بورڈ -----
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    data = load_data()
    items = data['items']
    rooms = data['rooms']
    transactions = data['transactions']
    total_items = sum(i['quantity'] for i in items)
    low_stock = [i for i in items if i['quantity'] <= i['minQty']]
    issued = [t for t in transactions if t['status'] == 'issued']
    returned = [t for t in transactions if t['status'] == 'returned']
    # کیٹیگری کا خلاصہ
    cat_counts = {}
    for i in items:
        cat_counts[i['category']] = cat_counts.get(i['category'], 0) + 1
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-gold">📊 ڈیش بورڈ</h2>
            <span class="text-secondary">{{ now.strftime('%Y-%m-%d') }}</span>
        </div>
        {% if low_stock|length > 0 %}
            <div class="alert-bar mb-3">⚠️ <strong>{{ low_stock|length }} اشیاء</strong> کا ذخیرہ کم ہے — فوری توجہ درکار ہے</div>
        {% endif %}
        <div class="row g-3 mb-4">
            <div class="col-md-3"><div class="stat-card"><div>📦</div><div class="stat-value">{{ items|length }}</div><div>کل اقسام</div></div></div>
            <div class="col-md-3"><div class="stat-card"><div>🏠</div><div class="stat-value">{{ rooms|length }}</div><div>کمرے</div></div></div>
            <div class="col-md-3"><div class="stat-card"><div>➡️</div><div class="stat-value">{{ issued|length }}</div><div>جاری شدہ</div></div></div>
            <div class="col-md-3"><div class="stat-card"><div>⚠️</div><div class="stat-value">{{ low_stock|length }}</div><div>کم ذخیرہ</div></div></div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <div class="card"><div class="card-header">🔄 حالیہ لین دین</div>
                <div class="card-body p-0">
                    <table class="table table-striped table-hover mb-0">
                        <thead><tr><th>سامان</th><th>صارف</th><th>حالت</th></tr></thead>
                        <tbody>
                            {% for t in transactions[-5:]|reverse %}
                            <tr><td>{{ t.itemName }}</td><td>{{ t.userName }}</td>
                                <td><span class="badge {{ 'badge-issued' if t.status=='issued' else 'badge-returned' }}">{{ 'جاری' if t.status=='issued' else 'واپس' }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div></div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="card"><div class="card-header">🗂️ کیٹیگری کا خلاصہ</div>
                <div class="card-body">
                    {% for cat, cnt in cat_counts.items() %}
                        <div class="mb-2"><span>{{ cat }}</span> <span class="float-end">{{ cnt }}</span>
                        <div class="progress"><div class="progress-bar progress-bar-gold" style="width: {{ (cnt/items|length*100)|round(1) }}%;"></div></div></div>
                    {% endfor %}
                </div></div>
            </div>
        </div>
        {% if low_stock %}
        <div class="card"><div class="card-header">🚨 کم ذخیرہ</div>
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead><tr><th>سامان</th><th>کمرہ</th><th>موجودہ</th><th>کم از کم</th></tr></thead>
                <tbody>
                {% for i in low_stock %}
                    <tr><td>{{ i.name }}</td><td>{{ get_room_name(i.roomId, rooms) }}</td><td class="text-danger">{{ i.quantity }}</td><td>{{ i.minQty }}</td></tr>
                {% endfor %}
                </tbody>
            </table>
        </div></div>
        {% endif %}
        {% endblock %}
    ''', items=items, rooms=rooms, transactions=transactions, low_stock=low_stock, 
       issued=issued, cat_counts=cat_counts, now=datetime.now(), get_room_name=get_room_name)

# ----- کمرے (صرف ایڈمن) -----
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            new_room = {
                'id': get_next_id(data['rooms']),
                'name': request.form.get('name'),
                'icon': request.form.get('icon', '🏠'),
                'color': request.form.get('color', '#1a472a')
            }
            data['rooms'].append(new_room)
            save_data(data)
            flash('کمرہ شامل کر دیا گیا')
        elif action == 'delete':
            room_id = int(request.form.get('room_id'))
            data['rooms'] = [r for r in data['rooms'] if r['id'] != room_id]
            # اس کمرے سے منسلک اشیاء کو بھی حذف کریں (یا unlink)
            data['items'] = [i for i in data['items'] if i['roomId'] != room_id]
            save_data(data)
            flash('کمرہ حذف کر دیا گیا')
        return redirect(url_for('rooms'))
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-gold">🏠 کمرے اور مقامات</h2>
            <button class="btn btn-gold" data-bs-toggle="modal" data-bs-target="#addRoomModal">+ نیا کمرہ</button>
        </div>
        <div class="row g-3">
            {% for room in rooms %}
            <div class="col-md-4">
                <div class="room-card" style="background: linear-gradient(135deg, {{ room.color }}dd, {{ room.color }}88);">
                    <div class="room-icon">{{ room.icon }}</div>
                    <div class="room-name">{{ room.name }}</div>
                    <div class="room-count">{{ items|selectattr('roomId', 'equalto', room.id)|list|length }} اشیاء</div>
                    <form method="POST" onsubmit="return confirm('واقعی حذف کریں؟')" class="mt-2">
                        <input type="hidden" name="action" value="delete">
                        <input type="hidden" name="room_id" value="{{ room.id }}">
                        <button type="submit" class="btn btn-sm btn-danger">🗑️ حذف کریں</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        <!-- Add Modal -->
        <div class="modal fade" id="addRoomModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="background:#1a2234; color:#e8eaf0;">
                    <div class="modal-header border-secondary"><h5 class="modal-title text-gold">نیا کمرہ</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
                    <form method="POST">
                        <div class="modal-body">
                            <input type="hidden" name="action" value="add">
                            <div class="mb-3"><label class="form-label">نام</label><input type="text" name="name" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">آئیکن</label>
                                <div class="d-flex flex-wrap gap-2">
                                    {% for ic in ['🏛️','📚','💻','🍽️','🏪','🏫','🕌','🛠️','🏋️','🎯'] %}
                                    <button type="button" class="btn btn-outline-secondary" onclick="document.getElementById('iconInput').value='{{ ic }}'; this.classList.add('active');">{{ ic }}</button>
                                    {% endfor %}
                                    <input type="hidden" id="iconInput" name="icon" value="🏠">
                                </div>
                            </div>
                            <div class="mb-3"><label class="form-label">رنگ</label>
                                <div class="d-flex flex-wrap gap-2">
                                    {% for c in ['#1a472a','#0d47a1','#4a148c','#bf360c','#37474f','#1b5e20','#880e4f','#004d40'] %}
                                    <div style="width:30px;height:30px;border-radius:8px;background:{{ c }};cursor:pointer;" onclick="document.getElementById('colorInput').value='{{ c }}'; this.style.border='2px solid gold';"></div>
                                    {% endfor %}
                                    <input type="hidden" id="colorInput" name="color" value="#1a472a">
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer border-secondary"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">منسوخ</button><button type="submit" class="btn btn-gold">شامل کریں</button></div>
                    </form>
                </div>
            </div>
        </div>
        {% endblock %}
    ''', rooms=data['rooms'], items=data['items'])

# ----- سامان کا انتظام -----
@app.route('/items', methods=['GET', 'POST'])
def items():
    if 'user' not in session:
        return redirect(url_for('index'))
    data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            new_item = {
                'id': get_next_id(data['items']),
                'name': request.form.get('name'),
                'roomId': int(request.form.get('roomId')),
                'category': request.form.get('category'),
                'quantity': int(request.form.get('quantity')),
                'unit': request.form.get('unit'),
                'minQty': int(request.form.get('minQty', 1))
            }
            data['items'].append(new_item)
            save_data(data)
            flash('سامان شامل کر دیا گیا')
        elif action == 'edit':
            item_id = int(request.form.get('item_id'))
            for i in data['items']:
                if i['id'] == item_id:
                    i.update({
                        'name': request.form.get('name'),
                        'roomId': int(request.form.get('roomId')),
                        'category': request.form.get('category'),
                        'quantity': int(request.form.get('quantity')),
                        'unit': request.form.get('unit'),
                        'minQty': int(request.form.get('minQty', 1))
                    })
                    break
            save_data(data)
            flash('سامان میں ترمیم کر دی گئی')
        elif action == 'delete':
            item_id = int(request.form.get('item_id'))
            data['items'] = [i for i in data['items'] if i['id'] != item_id]
            save_data(data)
            flash('سامان حذف کر دیا گیا')
        return redirect(url_for('items'))
    # فلٹرز
    search = request.args.get('search', '')
    filter_cat = request.args.get('category', 'سب')
    filter_room = request.args.get('room', 'سب')
    filtered = data['items']
    if search:
        filtered = [i for i in filtered if search in i['name']]
    if filter_cat != 'سب':
        filtered = [i for i in filtered if i['category'] == filter_cat]
    if filter_room != 'سب':
        filtered = [i for i in filtered if i['roomId'] == int(filter_room)]
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-gold">📦 سامان کا انتظام</h2>
            <button class="btn btn-gold" data-bs-toggle="modal" data-bs-target="#itemModal" onclick="clearForm()">+ نیا سامان</button>
        </div>
        <form method="GET" class="row g-2 mb-3">
            <div class="col-md-4"><input type="text" name="search" class="form-control" placeholder="🔍 تلاش کریں..." value="{{ search }}"></div>
            <div class="col-md-3"><select name="category" class="form-select"><option value="سب">تمام کیٹیگریز</option>{% for c in categories %}<option value="{{ c }}" {% if filter_cat==c %}selected{% endif %}>{{ c }}</option>{% endfor %}</select></div>
            <div class="col-md-3"><select name="room" class="form-select"><option value="سب">تمام کمرے</option>{% for r in rooms %}<option value="{{ r.id }}" {% if filter_room==r.id|string %}selected{% endif %}>{{ r.name }}</option>{% endfor %}</select></div>
            <div class="col-md-2"><button type="submit" class="btn btn-gold w-100">فلٹر</button></div>
        </form>
        <div class="card"><div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead><tr><th>سامان</th><th>کمرہ</th><th>کیٹیگری</th><th>مقدار</th><th>کم از کم</th><th>حالت</th>{% if session.user.role=='admin' %}<th>عمل</th>{% endif %}</tr></thead>
                <tbody>
                {% for item in filtered %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td>{{ get_room_name(item.roomId, rooms) }}</td>
                        <td><span class="badge bg-info text-dark">{{ item.category }}</span></td>
                        <td class="{{ 'text-danger' if item.quantity <= item.minQty else 'text-success' }}">{{ item.quantity }} {{ item.unit }}</td>
                        <td>{{ item.minQty }}</td>
                        <td><span class="badge {{ 'badge-low' if item.quantity <= item.minQty else 'badge-ok' }}">{{ 'کم ذخیرہ' if item.quantity <= item.minQty else 'دستیاب' }}</span></td>
                        {% if session.user.role=='admin' %}
                        <td>
                            <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#itemModal" 
                                onclick="editItem({{ item.id }}, '{{ item.name }}', {{ item.roomId }}, '{{ item.category }}', {{ item.quantity }}, '{{ item.unit }}', {{ item.minQty }})">✏️</button>
                            <form method="POST" style="display:inline;" onsubmit="return confirm('واقعی حذف کریں؟')">
                                <input type="hidden" name="action" value="delete"><input type="hidden" name="item_id" value="{{ item.id }}">
                                <button type="submit" class="btn btn-sm btn-danger">🗑️</button>
                            </form>
                        </td>
                        {% endif %}
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div></div>
        <!-- Add/Edit Modal -->
        <div class="modal fade" id="itemModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="background:#1a2234; color:#e8eaf0;">
                    <div class="modal-header border-secondary"><h5 class="modal-title text-gold" id="itemModalLabel">نیا سامان</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
                    <form method="POST">
                        <div class="modal-body">
                            <input type="hidden" name="action" id="formAction" value="add">
                            <input type="hidden" name="item_id" id="editItemId" value="">
                            <div class="mb-3"><label class="form-label">سامان کا نام</label><input type="text" name="name" id="itemName" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">کمرہ</label><select name="roomId" id="itemRoom" class="form-select">{% for r in rooms %}<option value="{{ r.id }}">{{ r.name }}</option>{% endfor %}</select></div>
                            <div class="mb-3"><label class="form-label">کیٹیگری</label><select name="category" id="itemCategory" class="form-select">{% for c in categories %}<option value="{{ c }}">{{ c }}</option>{% endfor %}</select></div>
                            <div class="row g-2"><div class="col-6"><label class="form-label">مقدار</label><input type="number" name="quantity" id="itemQty" class="form-control" required></div>
                            <div class="col-6"><label class="form-label">یونٹ</label><input type="text" name="unit" id="itemUnit" class="form-control" placeholder="عدد، کلو وغیرہ"></div></div>
                            <div class="mb-3"><label class="form-label">کم از کم مقدار (الرٹ)</label><input type="number" name="minQty" id="itemMinQty" class="form-control" value="1"></div>
                        </div>
                        <div class="modal-footer border-secondary"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">منسوخ</button><button type="submit" class="btn btn-gold" id="submitBtn">شامل کریں</button></div>
                    </form>
                </div>
            </div>
        </div>
        <script>
            function clearForm() {
                document.getElementById('formAction').value = 'add';
                document.getElementById('itemModalLabel').innerText = 'نیا سامان';
                document.getElementById('submitBtn').innerText = 'شامل کریں';
                document.getElementById('itemName').value = '';
                document.getElementById('itemQty').value = '';
                document.getElementById('itemUnit').value = '';
                document.getElementById('itemMinQty').value = '1';
                document.getElementById('editItemId').value = '';
            }
            function editItem(id, name, roomId, category, qty, unit, minQty) {
                document.getElementById('formAction').value = 'edit';
                document.getElementById('itemModalLabel').innerText = 'سامان میں ترمیم';
                document.getElementById('submitBtn').innerText = 'محفوظ کریں';
                document.getElementById('itemName').value = name;
                document.getElementById('itemRoom').value = roomId;
                document.getElementById('itemCategory').value = category;
                document.getElementById('itemQty').value = qty;
                document.getElementById('itemUnit').value = unit;
                document.getElementById('itemMinQty').value = minQty;
                document.getElementById('editItemId').value = id;
            }
        </script>
        {% endblock %}
    ''', items=data['items'], rooms=data['rooms'], categories=data['categories'], 
       search=search, filter_cat=filter_cat, filter_room=filter_room, filtered=filtered, 
       get_room_name=get_room_name)

# ----- سامان جاری کریں -----
@app.route('/issue', methods=['GET', 'POST'])
def issue():
    if 'user' not in session:
        return redirect(url_for('index'))
    data = load_data()
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        qty = int(request.form.get('qty'))
        user_name = request.form.get('user_name')
        expected_return = request.form.get('expected_return')
        note = request.form.get('note', '')
        # چیک کریں کہ آئٹم موجود ہے اور مقدار کافی ہے
        item = next((i for i in data['items'] if i['id'] == item_id), None)
        if item and item['quantity'] >= qty:
            # ٹرانزیکشن بنائیں
            new_tx = {
                'id': get_next_id(data['transactions']),
                'itemId': item_id,
                'itemName': item['name'],
                'userId': session['user']['id'],
                'userName': user_name,
                'type': 'issue',
                'qty': qty,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'returnDate': None,
                'expectedReturn': expected_return,
                'note': note,
                'status': 'issued'
            }
            data['transactions'].append(new_tx)
            # مقدار کم کریں
            item['quantity'] -= qty
            save_data(data)
            flash('سامان کامیابی سے جاری کر دیا گیا')
        else:
            flash('ناکافی مقدار یا آئٹم موجود نہیں')
        return redirect(url_for('issue'))
    issued = [t for t in data['transactions'] if t['status'] == 'issued']
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <h2 class="text-gold mb-4">➡️ سامان جاری کریں</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}<div class="alert alert-success">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <div class="row">
            <div class="col-md-6 mb-3">
                <div class="card"><div class="card-header">📋 اندراج فارم</div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3"><label class="form-label">سامان</label>
                            <select name="item_id" class="form-select" required>
                                <option value="">منتخب کریں</option>
                                {% for i in items if i.quantity > 0 %}
                                <option value="{{ i.id }}">{{ i.name }} (دستیاب: {{ i.quantity }} {{ i.unit }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="row g-2"><div class="col-6"><label class="form-label">مقدار</label><input type="number" name="qty" class="form-control" min="1" required></div>
                        <div class="col-6"><label class="form-label">واپسی کی تاریخ</label><input type="date" name="expected_return" class="form-control"></div></div>
                        <div class="mb-3"><label class="form-label">لینے والے کا نام</label><input type="text" name="user_name" class="form-control" value="{{ session.user.name if session.user.role=='user' else '' }}" {% if session.user.role=='user' %}readonly{% endif %} required></div>
                        <div class="mb-3"><label class="form-label">نوٹ / مقصد</label><textarea name="note" class="form-control" rows="2"></textarea></div>
                        <button type="submit" class="btn btn-gold w-100">✅ سامان جاری کریں</button>
                    </form>
                </div></div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="card"><div class="card-header">📊 جاری سامان کی فہرست</div>
                <div class="card-body p-0">
                    <table class="table table-hover mb-0">
                        <thead><tr><th>سامان</th><th>کس کو</th><th>مقدار</th><th>واپسی</th></tr></thead>
                        <tbody>
                        {% for t in issued %}
                            <tr><td>{{ t.itemName }}</td><td>{{ t.userName }}</td><td>{{ t.qty }}</td>
                                <td class="{% if t.expectedReturn and t.expectedReturn < now.strftime('%Y-%m-%d') %}text-danger{% endif %}">{{ t.expectedReturn or '—' }}</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div></div>
            </div>
        </div>
        {% endblock %}
    ''', items=data['items'], issued=issued, now=datetime.now())

# ----- واپسی -----
@app.route('/returns', methods=['GET', 'POST'])
def returns():
    if 'user' not in session:
        return redirect(url_for('index'))
    data = load_data()
    if request.method == 'POST':
        tx_id = int(request.form.get('tx_id'))
        for tx in data['transactions']:
            if tx['id'] == tx_id and tx['status'] == 'issued':
                tx['status'] = 'returned'
                tx['returnDate'] = datetime.now().strftime('%Y-%m-%d')
                # مقدار واپس شامل کریں
                for item in data['items']:
                    if item['id'] == tx['itemId']:
                        item['quantity'] += tx['qty']
                        break
                break
        save_data(data)
        flash('سامان واپس کر دیا گیا')
        return redirect(url_for('returns'))
    issued = [t for t in data['transactions'] if t['status'] == 'issued']
    all_tx = sorted(data['transactions'], key=lambda x: x['id'], reverse=True)
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <h2 class="text-gold mb-4">↩️ واپسی کا نظم</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}<div class="alert alert-success">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <div class="card mb-3"><div class="card-header">⏳ واپسی باقی سامان <span class="badge badge-issued">{{ issued|length }}</span></div>
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead><tr><th>سامان</th><th>لینے والا</th><th>مقدار</th><th>تاریخ اجراء</th><th>واپسی تاریخ</th><th>نوٹ</th><th>عمل</th></tr></thead>
                <tbody>
                {% for t in issued %}
                    <tr><td>{{ t.itemName }}</td><td>{{ t.userName }}</td><td>{{ t.qty }}</td>
                        <td>{{ t.date }}</td>
                        <td class="{% if t.expectedReturn and t.expectedReturn < now.strftime('%Y-%m-%d') %}text-danger{% endif %}">{{ t.expectedReturn or '—' }}</td>
                        <td>{{ t.note or '—' }}</td>
                        <td>
                            {% if session.user.role=='admin' or session.user.id==t.userId %}
                            <form method="POST" onsubmit="return confirm('واپس کر رہے ہیں؟')">
                                <input type="hidden" name="tx_id" value="{{ t.id }}">
                                <button type="submit" class="btn btn-sm btn-success">↩️ واپس</button>
                            </form>
                            {% endif %}
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div></div>
        <div class="card"><div class="card-header">📜 مکمل تاریخ</div>
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead><tr><th>سامان</th><th>نام</th><th>مقدار</th><th>اجراء</th><th>واپسی</th><th>حالت</th></tr></thead>
                <tbody>
                {% for t in all_tx %}
                    <tr><td>{{ t.itemName }}</td><td>{{ t.userName }}</td><td>{{ t.qty }}</td>
                        <td>{{ t.date }}</td><td>{{ t.returnDate or '—' }}</td>
                        <td><span class="badge {{ 'badge-issued' if t.status=='issued' else 'badge-returned' }}">{{ 'جاری' if t.status=='issued' else 'واپس' }}</span></td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div></div>
        {% endblock %}
    ''', issued=issued, all_tx=all_tx, now=datetime.now())

# ----- AI تجزیہ (صرف ایڈمن) -----
@app.route('/ai', methods=['GET', 'POST'])
def ai():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    data = load_data()
    response = None
    if request.method == 'POST':
        query = request.form.get('query')
        # یہاں آپ Claude API استعمال کر سکتے ہیں، لیکن مثال کے لیے مقامی جواب
        # اگر API کلید موجود ہو تو استعمال کریں، ورنہ سادہ جواب
        # (مثال کے لیے ہم صرف ایک سادہ رسپانس دیں گے)
        if 'کم ذخیرہ' in query:
            low = [i for i in data['items'] if i['quantity'] <= i['minQty']]
            if low:
                response = "کم ذخیرہ اشیاء:\n" + "\n".join([f"- {i['name']}: {i['quantity']} (کم از کم {i['minQty']})" for i in low])
            else:
                response = "تمام اشیاء کا ذخیرہ کافی ہے۔"
        elif 'جائزہ' in query:
            total = sum(i['quantity'] for i in data['items'])
            issued = len([t for t in data['transactions'] if t['status'] == 'issued'])
            response = f"اسٹور کا جائزہ:\nکل اقسام: {len(data['items'])}\nکل مقدار: {total}\nجاری اشیاء: {issued}\nکمرے: {len(data['rooms'])}"
        else:
            response = "براہ کرم مخصوص سوال پوچھیں، مثلاً 'کم ذخیرہ' یا 'جائزہ'۔"
    return render_template_string(BASE_TEMPLATE + '''
        {% block content %}
        <h2 class="text-gold mb-4">🤖 AI تجزیہ</h2>
        <div class="ai-panel">
            <div class="d-flex align-items-center mb-3">
                <div style="font-size:36px;">🤖</div>
                <div class="ms-2"><h5>AI مشیر — جامعہ اسٹور</h5><small class="text-secondary">مقامی تجزیہ (Claude API اختیاری)</small></div>
            </div>
            <form method="POST" class="mb-3">
                <div class="input-group">
                    <input type="text" name="query" class="form-control" placeholder="کوئی بھی سوال پوچھیں..." required>
                    <button type="submit" class="btn btn-gold">پوچھیں</button>
                </div>
            </form>
            <div class="ai-response">
                {% if response %}
                    {{ response }}
                {% else %}
                    اوپر دیے گئے سوالات میں سے کوئی منتخب کریں یا اپنا سوال لکھیں...
                {% endif %}
            </div>
            <div class="mt-3">
                <button class="ai-prompt-btn" onclick="document.querySelector('input[name=query]').value='کم ذخیرہ اشیاء کی فہرست دیں'; this.form.submit();">کم ذخیرہ</button>
                <button class="ai-prompt-btn" onclick="document.querySelector('input[name=query]').value='اسٹور کا مکمل جائزہ دیں'; this.form.submit();">مکمل جائزہ</button>
                <button class="ai-prompt-btn" onclick="document.querySelector('input[name=query]').value='سب سے زیادہ استعمال ہونے والی اشیاء کون سی ہیں؟'; this.form.submit();">زیادہ استعمال</button>
            </div>
        </div>
        {% endblock %}
    ''', response=response)

# ========== مین ==========
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
