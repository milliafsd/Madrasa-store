import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import base64
import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import plotly.graph_objects as go

# ========== صفحہ کنفیگریشن ==========
st.set_page_config(
    page_title="جامعہ ملیہ اسلامیہ - اسٹور مینجمنٹ",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== وائٹ تھیم ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');
* {
    font-family: 'Noto Nastaliq Urdu', serif;
}
.stApp {
    background: #ffffff;
}
.main-header {
    color: #1a3c5e;
    text-align: center;
    padding: 20px;
    border-bottom: 2px solid #1a3c5e;
}
.sidebar .sidebar-content {
    background: #f5f7fa;
}
.card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-title {
    color: #1a3c5e;
    font-size: 18px;
    font-weight: 700;
}
.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #1a3c5e;
}
.badge-low { background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 20px; }
.badge-ok { background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; }
.badge-issued { background: #fef9c3; color: #854d0e; padding: 4px 12px; border-radius: 20px; }
.badge-returned { background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; }
.room-card {
    background: #f8fafc;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 20px;
    transition: 0.2s;
    cursor: pointer;
}
.room-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.room-icon { font-size: 36px; }
.room-name { color: #1a3c5e; font-size: 16px; font-weight: 600; }
.room-count { color: #4b5563; font-size: 12px; }
.btn-gold {
    background: #1a3c5e;
    color: #ffffff;
    font-weight: 700;
    border: none;
    padding: 8px 20px;
    border-radius: 8px;
    cursor: pointer;
}
.btn-gold:hover { background: #2a5a7a; box-shadow: 0 4px 12px rgba(26,60,94,0.3); }
.ai-panel {
    background: #f8fafc;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 24px;
}
.ai-response {
    background: #ffffff;
    border-radius: 10px;
    padding: 16px;
    min-height: 80px;
    white-space: pre-wrap;
    color: #1a3c5e;
    border: 1px solid #e5e7eb;
}
.print-receipt {
    background: #ffffff;
    padding: 30px;
    border: 1px dashed #1a3c5e;
    border-radius: 10px;
    max-width: 800px;
    margin: 0 auto;
    direction: rtl;
    font-family: 'Noto Nastaliq Urdu', serif;
}
.print-receipt .header {
    text-align: center;
    border-bottom: 2px solid #1a3c5e;
    padding-bottom: 15px;
    margin-bottom: 20px;
}
.print-receipt .header h1 {
    color: #1a3c5e;
    font-size: 24px;
    margin: 0;
}
.print-receipt .header h3 {
    color: #4b5563;
    font-size: 18px;
    margin: 5px 0;
}
.print-receipt .header p {
    color: #6b7280;
    font-size: 14px;
}
.print-receipt table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}
.print-receipt table th {
    background: #1a3c5e;
    color: #ffffff;
    padding: 10px;
    text-align: center;
}
.print-receipt table td {
    padding: 8px 10px;
    border-bottom: 1px solid #e5e7eb;
    text-align: center;
}
.print-receipt .total {
    font-size: 18px;
    font-weight: 700;
    color: #1a3c5e;
    margin: 15px 0;
}
.print-receipt .signature {
    margin-top: 30px;
    border-top: 1px dashed #1a3c5e;
    padding-top: 20px;
    display: flex;
    justify-content: space-between;
}
.print-receipt .signature div {
    width: 200px;
}
.print-receipt .signature .line {
    border-bottom: 1px solid #1a3c5e;
    height: 30px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# ========== ڈیٹا لوڈ / سیو ==========
DATA_FILE = 'store_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        data = {
            "users": [
                {"id": 1, "username": "admin", "password": "admin123", "role": "admin", "name": "ایڈمن صاحب"},
                {"id": 2, "username": "user1", "password": "user123", "role": "user", "name": "محمد احمد"},
                {"id": 3, "username": "user2", "password": "user456", "role": "user", "name": "عبداللہ خان"},
            ],
            "categories": ["کتب و کاپیاں", "صفائی کا سامان", "بجلی کا سامان", "فرنیچر", "کھانے پینے کی اشیاء", "کمپیوٹر و ٹیکنالوجی", "دیگر"],
            "rooms": [
                {"id": 1, "name": "دفتر مہتمم", "color": "#1a3c5e", "icon": "🏛️"},
                {"id": 2, "name": "لائبریری", "color": "#1a3c5e", "icon": "📚"},
                {"id": 3, "name": "کمپیوٹر لیب", "color": "#1a3c5e", "icon": "💻"},
                {"id": 4, "name": "باورچی خانہ", "color": "#1a3c5e", "icon": "🍽️"},
                {"id": 5, "name": "مرکزی اسٹور", "color": "#1a3c5e", "icon": "🏪"},
            ],
            "items": [
                {"id": 1, "name": "A4 پیپر ریم", "roomId": 5, "category": "کتب و کاپیاں", "quantity": 50, "unit": "ریم", "minQty": 10},
                {"id": 2, "name": "بال پوائنٹ قلم", "roomId": 5, "category": "کتب و کاپیاں", "quantity": 200, "unit": "عدد", "minQty": 30},
                {"id": 3, "name": "جھاڑو", "roomId": 5, "category": "صفائی کا سامان", "quantity": 8, "unit": "عدد", "minQty": 2},
                {"id": 4, "name": "صابن", "roomId": 5, "category": "صفائی کا سامان", "quantity": 24, "unit": "عدد", "minQty": 5},
                {"id": 5, "name": "LED بلب", "roomId": 5, "category": "بجلی کا سامان", "quantity": 20, "unit": "عدد", "minQty": 5},
                {"id": 6, "name": "پرنٹر", "roomId": 3, "category": "کمپیوٹر و ٹیکنالوجی", "quantity": 2, "unit": "عدد", "minQty": 1},
                {"id": 7, "name": "کرسی", "roomId": 1, "category": "فرنیچر", "quantity": 6, "unit": "عدد", "minQty": 2},
                {"id": 8, "name": "چائے پتی", "roomId": 4, "category": "کھانے پینے کی اشیاء", "quantity": 3, "unit": "کلو", "minQty": 1},
            ],
            "transactions": [
                {"id": 1, "itemId": 1, "itemName": "A4 پیپر ریم", "userId": 2, "userName": "محمد احمد", "type": "issue", "qty": 5,
                 "date": "2025-06-10", "returnDate": None, "expectedReturn": "2025-06-20", "note": "امتحانی پرچے", "status": "issued"},
                {"id": 2, "itemId": 3, "itemName": "جھاڑو", "userId": 3, "userName": "عبداللہ خان", "type": "issue", "qty": 2,
                 "date": "2025-06-08", "returnDate": "2025-06-12", "expectedReturn": "2025-06-15", "note": "صفائی کے لیے", "status": "returned"},
            ]
        }
        save_data(data)
        return data

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

def generate_barcode(item_id, item_name):
    try:
        code = barcode.get_barcode_class('code128')
        barcode_obj = code(str(item_id), writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer, {'write_text': False, 'font_size': 12})
        buffer.seek(0)
        img = Image.open(buffer)
        return img
    except:
        return None

# ========== سیشن اسٹیٹ ==========
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'selected_room_3d' not in st.session_state:
    st.session_state.selected_room_3d = None

data = st.session_state.data

# ========== رسید پرنٹ / HTML ==========
def generate_receipt_html(title="رسید", items=None, total_qty=None):
    if items is None:
        items = data['items']
    total = sum(i['quantity'] for i in items)
    html = f"""
    <div class="print-receipt" id="receipt">
        <div class="header">
            <h1>🕌 جامعہ ملیہ اسلامیہ فیصل آباد</h1>
            <h3>📦 اسٹور مینجمنٹ سسٹم</h3>
            <p>تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p style="font-size:12px; color:#6b7280;">یہ رسید کمپیوٹر سے تیار کی گئی ہے</p>
        </div>
        <h4 style="text-align:center; color:#1a3c5e;">{title}</h4>
        <table>
            <thead>
                <tr>
                    <th>سامان</th>
                    <th>کیٹیگری</th>
                    <th>مقدار</th>
                    <th>یونٹ</th>
                    <th>کم از کم</th>
                </tr>
            </thead>
            <tbody>
    """
    for item in items:
        html += f"""
        <tr>
            <td>{item['name']}</td>
            <td>{item['category']}</td>
            <td>{item['quantity']}</td>
            <td>{item['unit']}</td>
            <td>{item['minQty']}</td>
        </tr>
        """
    html += f"""
            </tbody>
        </table>
        <div class="total">
            کل مقدار: {total} {'' if total_qty else 'یونٹس'}
        </div>
        <div class="signature">
            <div>
                <span>جاری کنندہ کا دستخط</span>
                <div class="line"></div>
            </div>
            <div>
                <span>وصول کنندہ کا دستخط</span>
                <div class="line"></div>
            </div>
            <div>
                <span>تاریخ</span>
                <div class="line"></div>
            </div>
        </div>
        <p style="text-align:center; font-size:11px; color:#6b7280; margin-top:30px;">
            یہ رسید کمپیوٹرائزڈ نظام سے تیار کی گئی ہے۔ اس کی تصدیق متعلقہ افسر سے کروائیں۔
        </p>
    </div>
    """
    return html

def render_print_receipt_button(items=None, title="رسید"):
    html_content = generate_receipt_html(title, items)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="receipt_{datetime.now().strftime("%Y%m%d_%H%M")}.html" class="btn-gold" style="text-decoration:none;padding:8px 16px;border-radius:6px;margin:5px;display:inline-block;">📄 رسید ڈاؤن لوڈ کریں</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.markdown("""
    <button onclick="window.print()" class="btn-gold" style="padding:8px 16px;border-radius:6px;border:none;margin:5px;cursor:pointer;">
        🖨️ پرنٹ کریں
    </button>
    """, unsafe_allow_html=True)

def render_print_button():
    st.markdown("""
    <button onclick="window.print()" class="btn-gold" style="padding:8px 16px;border-radius:6px;border:none;margin:5px;cursor:pointer;">
        🖨️ پرنٹ کریں
    </button>
    """, unsafe_allow_html=True)

def render_html_download_button(content, filename="page.html", label="📄 HTML ڈاؤن لوڈ کریں"):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="btn-gold" style="text-decoration:none;padding:8px 16px;border-radius:6px;margin:5px;display:inline-block;">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

# ========== سائیڈ بار ==========
def render_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='color:#1a3c5e;text-align:center;'>🕌 جامعہ</h1>", unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            st.markdown(f"""
            <div style='background:#e5edf5;border-radius:10px;padding:12px;margin-bottom:20px;'>
                <strong style='color:#1a3c5e;'>{user['name']}</strong>
                <span style='background:#1a3c5e;color:#ffffff;padding:2px 10px;border-radius:20px;font-size:12px;'>
                    {'ایڈمن' if user['role']=='admin' else 'صارف'}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            pages = ["📊 ڈیش بورڈ", "🏠 کمرے", "📦 سامان", "➡️ جاری کریں", "↩️ واپسی"]
            if user['role'] == 'admin':
                pages.append("🤖 AI تجزیہ")
                pages.append("💾 بیک اپ")
                pages.append("🏷️ بارکوڈ")
                pages.append("🗺️ نقشہ جات")
                pages.append("🌐 3D ویو")
            
            selected = st.radio("", pages, index=0)
            page_map = {
                "📊 ڈیش بورڈ": "dashboard",
                "🏠 کمرے": "rooms",
                "📦 سامان": "items",
                "➡️ جاری کریں": "issue",
                "↩️ واپسی": "returns",
                "🤖 AI تجزیہ": "ai",
                "💾 بیک اپ": "backup",
                "🏷️ بارکوڈ": "barcode",
                "🗺️ نقشہ جات": "maps",
                "🌐 3D ویو": "three_d"
            }
            st.session_state.page = page_map.get(selected, "dashboard")
            
            if st.button("🚪 لاگ آؤٹ", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            st.markdown("### 🔐 لاگ ان")
            username = st.text_input("صارف نام", placeholder="username")
            password = st.text_input("پاسورڈ", type="password", placeholder="password")
            if st.button("داخل ہوں", use_container_width=True):
                found = next((u for u in data['users'] if u['username'] == username and u['password'] == password), None)
                if found:
                    st.session_state.user = found
                    st.rerun()
                else:
                    st.error("غلط صارف نام یا پاسورڈ")
            st.caption("Admin: admin/admin123 | User: user1/user123")

# ========== ڈیش بورڈ ==========
def render_dashboard():
    items = data['items']
    rooms = data['rooms']
    transactions = data['transactions']
    low_stock = [i for i in items if i['quantity'] <= i['minQty']]
    issued = [t for t in transactions if t['status'] == 'issued']
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(items, "📊 ڈیش بورڈ - مکمل انوینٹری")
    with col_actions[2]:
        render_print_button()
    
    st.markdown("<h2 style='color:#1a3c5e;'>📊 ڈیش بورڈ</h2>", unsafe_allow_html=True)
    st.caption(f"تاریخ: {datetime.now().strftime('%Y-%m-%d')}")
    
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} اشیاء** کا ذخیرہ کم ہے — فوری توجہ درکار ہے")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='card' style='text-align:center;'><div>📦</div><div class='stat-value'>{len(items)}</div><div>کل اقسام</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='card' style='text-align:center;'><div>🏠</div><div class='stat-value'>{len(rooms)}</div><div>کمرے</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='card' style='text-align:center;'><div>➡️</div><div class='stat-value'>{len(issued)}</div><div>جاری شدہ</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='card' style='text-align:center;'><div>⚠️</div><div class='stat-value'>{len(low_stock)}</div><div>کم ذخیرہ</div></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("<div class='card'><div class='card-title'>🔄 حالیہ لین دین</div>", unsafe_allow_html=True)
            if transactions:
                df = pd.DataFrame(transactions[-5:][::-1])
                df = df[['itemName', 'userName', 'status']]
                df.columns = ['سامان', 'صارف', 'حالت']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("کوئی لین دین نہیں")
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("<div class='card'><div class='card-title'>🗂️ کیٹیگری کا خلاصہ</div>", unsafe_allow_html=True)
            cat_counts = {}
            for i in items:
                cat_counts[i['category']] = cat_counts.get(i['category'], 0) + 1
            for cat, cnt in cat_counts.items():
                pct = (cnt / len(items)) * 100
                st.markdown(f"<div>{cat} <span style='float:left;'>{cnt}</span></div>", unsafe_allow_html=True)
                st.progress(pct / 100)
            st.markdown("</div>", unsafe_allow_html=True)
    
    if low_stock:
        st.markdown("<div class='card'><div class='card-title'>🚨 کم ذخیرہ</div>", unsafe_allow_html=True)
        low_df = pd.DataFrame(low_stock)
        low_df['کمرہ'] = low_df['roomId'].apply(lambda x: get_room_name(x, rooms))
        low_df = low_df[['name', 'کمرہ', 'quantity', 'minQty']]
        low_df.columns = ['سامان', 'کمرہ', 'موجودہ', 'کم از کم']
        st.dataframe(low_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ========== کمرے ==========
def render_rooms():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ صفحہ دیکھنے کی اجازت ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>🏠 کمرے اور مقامات</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "🏠 کمرے - مکمل فہرست")
    with col_actions[2]:
        render_print_button()
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("+ نیا کمرہ"):
            st.session_state.show_add_room = True
    
    if st.session_state.get('show_add_room', False):
        with st.expander("نیا کمرہ شامل کریں", expanded=True):
            name = st.text_input("کمرے کا نام")
            icon = st.selectbox("آئیکن", ["🏛️", "📚", "💻", "🍽️", "🏪", "🏫", "🕌", "🛠️", "🏋️", "🎯"])
            color = st.color_picker("رنگ", "#1a3c5e")
            if st.button("شامل کریں"):
                if name:
                    new_room = {"id": get_next_id(data['rooms']), "name": name, "icon": icon, "color": color}
                    data['rooms'].append(new_room)
                    save_data(data)
                    st.session_state.show_add_room = False
                    st.rerun()
                else:
                    st.warning("براہ کرم نام درج کریں")
    
    cols = st.columns(3)
    for idx, room in enumerate(data['rooms']):
        with cols[idx % 3]:
            room_items = [i for i in data['items'] if i['roomId'] == room['id']]
            st.markdown(f"""
            <div class='room-card'>
                <div class='room-icon'>{room['icon']}</div>
                <div class='room-name'>{room['name']}</div>
                <div class='room-count'>{len(room_items)} اشیاء</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ حذف کریں", key=f"del_room_{room['id']}"):
                data['rooms'] = [r for r in data['rooms'] if r['id'] != room['id']]
                data['items'] = [i for i in data['items'] if i['roomId'] != room['id']]
                save_data(data)
                st.rerun()

# ========== سامان ==========
def render_items():
    st.markdown("<h2 style='color:#1a3c5e;'>📦 سامان کا انتظام</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "📦 سامان کی مکمل فہرست")
    with col_actions[2]:
        render_print_button()
    
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("🔍 تلاش کریں...", key="item_search")
    with col2:
        filter_cat = st.selectbox("کیٹیگری", ["سب"] + data['categories'], key="item_cat")
    with col3:
        filter_room = st.selectbox("کمرہ", ["سب"] + [r['name'] for r in data['rooms']], key="item_room")
    
    if st.session_state.user['role'] == 'admin':
        if st.button("+ نیا سامان"):
            st.session_state.show_add_item = True
    
    if st.session_state.get('show_add_item', False):
        with st.expander("نیا سامان شامل کریں", expanded=True):
            with st.form("add_item_form"):
                name = st.text_input("سامان کا نام")
                room = st.selectbox("کمرہ", [r['name'] for r in data['rooms']])
                category = st.selectbox("کیٹیگری", data['categories'])
                qty = st.number_input("مقدار", min_value=1, step=1)
                unit = st.text_input("یونٹ", "عدد")
                min_qty = st.number_input("کم از کم مقدار", min_value=1, step=1, value=1)
                submitted = st.form_submit_button("شامل کریں")
                if submitted and name:
                    room_id = next((r['id'] for r in data['rooms'] if r['name'] == room), None)
                    new_item = {
                        "id": get_next_id(data['items']),
                        "name": name,
                        "roomId": room_id,
                        "category": category,
                        "quantity": qty,
                        "unit": unit,
                        "minQty": min_qty
                    }
                    data['items'].append(new_item)
                    save_data(data)
                    st.session_state.show_add_item = False
                    st.rerun()
    
    filtered = data['items']
    if search:
        filtered = [i for i in filtered if search in i['name']]
    if filter_cat != "سب":
        filtered = [i for i in filtered if i['category'] == filter_cat]
    if filter_room != "سب":
        room_id = next((r['id'] for r in data['rooms'] if r['name'] == filter_room), None)
        if room_id:
            filtered = [i for i in filtered if i['roomId'] == room_id]
    
    if filtered:
        df = pd.DataFrame(filtered)
        df['کمرہ'] = df['roomId'].apply(lambda x: get_room_name(x, data['rooms']))
        df['حالت'] = df.apply(lambda x: "کم ذخیرہ" if x['quantity'] <= x['minQty'] else "دستیاب", axis=1)
        df = df[['name', 'کمرہ', 'category', 'quantity', 'unit', 'minQty', 'حالت']]
        df.columns = ['سامان', 'کمرہ', 'کیٹیگری', 'مقدار', 'یونٹ', 'کم از کم', 'حالت']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("کوئی سامان نہیں ملا")

# ========== جاری کریں ==========
def render_issue():
    st.markdown("<h2 style='color:#1a3c5e;'>➡️ سامان جاری کریں</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "➡️ جاری کردہ سامان کی فہرست")
    with col_actions[2]:
        render_print_button()
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("<div class='card'><div class='card-title'>📋 اندراج فارم</div>", unsafe_allow_html=True)
            with st.form("issue_form"):
                available_items = [i for i in data['items'] if i['quantity'] > 0]
                if not available_items:
                    st.warning("کوئی سامان دستیاب نہیں")
                else:
                    item_names = [f"{i['name']} (دستیاب: {i['quantity']} {i['unit']})" for i in available_items]
                    selected = st.selectbox("سامان", item_names)
                    qty = st.number_input("مقدار", min_value=1, step=1)
                    user_name = st.text_input("لینے والے کا نام", value=st.session_state.user['name'] if st.session_state.user['role'] == 'user' else "")
                    expected_return = st.date_input("واپسی کی تاریخ", value=None)
                    note = st.text_area("نوٹ / مقصد")
                    submitted = st.form_submit_button("✅ سامان جاری کریں")
                    if submitted:
                        item_idx = item_names.index(selected)
                        item = available_items[item_idx]
                        if qty > item['quantity']:
                            st.error("مقدار دستیاب نہیں")
                        else:
                            new_tx = {
                                "id": get_next_id(data['transactions']),
                                "itemId": item['id'],
                                "itemName": item['name'],
                                "userId": st.session_state.user['id'],
                                "userName": user_name,
                                "type": "issue",
                                "qty": qty,
                                "date": datetime.now().strftime('%Y-%m-%d'),
                                "returnDate": None,
                                "expectedReturn": expected_return.strftime('%Y-%m-%d') if expected_return else None,
                                "note": note,
                                "status": "issued"
                            }
                            data['transactions'].append(new_tx)
                            for i in data['items']:
                                if i['id'] == item['id']:
                                    i['quantity'] -= qty
                                    break
                            save_data(data)
                            st.success("سامان کامیابی سے جاری کر دیا گیا")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("<div class='card'><div class='card-title'>📊 جاری سامان کی فہرست</div>", unsafe_allow_html=True)
            issued = [t for t in data['transactions'] if t['status'] == 'issued']
            if issued:
                df = pd.DataFrame(issued)
                df = df[['itemName', 'userName', 'qty', 'expectedReturn']]
                df.columns = ['سامان', 'کس کو', 'مقدار', 'واپسی']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("کوئی سامان جاری نہیں")
            st.markdown("</div>", unsafe_allow_html=True)

# ========== واپسی ==========
def render_returns():
    st.markdown("<h2 style='color:#1a3c5e;'>↩️ واپسی کا نظم</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "↩️ واپسی کی تاریخ")
    with col_actions[2]:
        render_print_button()
    
    issued = [t for t in data['transactions'] if t['status'] == 'issued']
    
    if issued:
        st.subheader("⏳ واپسی باقی سامان")
        for tx in issued:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 1])
            with col1:
                st.write(tx['itemName'])
            with col2:
                st.write(tx['userName'])
            with col3:
                st.write(tx['qty'])
            with col4:
                st.write(tx['expectedReturn'] or "—")
            with col5:
                if st.button(f"↩️ واپس", key=f"return_{tx['id']}"):
                    for t in data['transactions']:
                        if t['id'] == tx['id']:
                            t['status'] = 'returned'
                            t['returnDate'] = datetime.now().strftime('%Y-%m-%d')
                            break
                    for item in data['items']:
                        if item['id'] == tx['itemId']:
                            item['quantity'] += tx['qty']
                            break
                    save_data(data)
                    st.rerun()
            st.divider()
    else:
        st.success("تمام سامان واپس ہو چکا ✅")
    
    st.subheader("📜 مکمل تاریخ")
    all_tx = sorted(data['transactions'], key=lambda x: x['id'], reverse=True)
    if all_tx:
        df = pd.DataFrame(all_tx)
        df = df[['itemName', 'userName', 'qty', 'date', 'returnDate', 'status']]
        df.columns = ['سامان', 'نام', 'مقدار', 'اجراء', 'واپسی', 'حالت']
        st.dataframe(df, use_container_width=True, hide_index=True)

# ========== AI ==========
def render_ai():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ فیچر دستیاب ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>🤖 AI تجزیہ</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "🤖 AI تجزیہ رپورٹ")
    with col_actions[2]:
        render_print_button()
    
    st.markdown("""
    <div class='ai-panel'>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;'>
            <div style='font-size:36px;'>🤖</div>
            <div><h5 style='color:#1a3c5e;'>AI مشیر — جامعہ اسٹور</h5><small style='color:#4b5563;'>مقامی تجزیہ (Claude API اختیاری)</small></div>
        </div>
    """, unsafe_allow_html=True)
    
    query = st.text_input("کوئی بھی سوال پوچھیں...", placeholder="مثلاً: کم ذخیرہ اشیاء کی فہرست دیں")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("کم ذخیرہ"):
            query = "کم ذخیرہ اشیاء کی فہرست دیں"
    with col2:
        if st.button("مکمل جائزہ"):
            query = "اسٹور کا مکمل جائزہ دیں"
    with col3:
        if st.button("زیادہ استعمال"):
            query = "سب سے زیادہ استعمال ہونے والی اشیاء کون سی ہیں؟"
    
    if query:
        with st.spinner("AI جواب تیار کر رہا ہے..."):
            if "کم ذخیرہ" in query:
                low = [i for i in data['items'] if i['quantity'] <= i['minQty']]
                if low:
                    response = "کم ذخیرہ اشیاء:\n" + "\n".join([f"- {i['name']}: {i['quantity']} (کم از کم {i['minQty']})" for i in low])
                else:
                    response = "تمام اشیاء کا ذخیرہ کافی ہے۔"
            elif "جائزہ" in query:
                total = sum(i['quantity'] for i in data['items'])
                issued = len([t for t in data['transactions'] if t['status'] == 'issued'])
                response = f"اسٹور کا جائزہ:\nکل اقسام: {len(data['items'])}\nکل مقدار: {total}\nجاری اشیاء: {issued}\nکمرے: {len(data['rooms'])}"
            elif "استعمال" in query:
                item_counts = {}
                for t in data['transactions']:
                    if t['status'] == 'issued':
                        item_counts[t['itemName']] = item_counts.get(t['itemName'], 0) + t['qty']
                if item_counts:
                    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    response = "سب سے زیادہ استعمال ہونے والی اشیاء:\n" + "\n".join([f"- {name}: {count} بار" for name, count in sorted_items])
                else:
                    response = "ابھی تک کوئی سامان جاری نہیں ہوا۔"
            else:
                response = "براہ کرم مخصوص سوال پوچھیں، مثلاً 'کم ذخیرہ' یا 'جائزہ'۔"
            
            st.markdown(f"<div class='ai-response'>{response}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== بیک اپ ==========
def render_backup():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ فیچر دستیاب ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>💾 بیک اپ ڈیٹا</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📥 ڈیٹا ڈاؤن لوڈ کریں")
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 ڈیٹا JSON میں ڈاؤن لوڈ کریں",
            data=json_str,
            file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 📤 ڈیٹا اپ لوڈ کریں (ریسٹور)")
        uploaded_file = st.file_uploader("JSON فائل منتخب کریں", type="json")
        if uploaded_file is not None:
            try:
                new_data = json.load(uploaded_file)
                if all(k in new_data for k in ['users', 'rooms', 'items', 'transactions']):
                    if st.button("✅ ڈیٹا ریسٹور کریں"):
                        data.clear()
                        data.update(new_data)
                        save_data(data)
                        st.session_state.data = data
                        st.success("ڈیٹا کامیابی سے ریسٹور ہو گیا!")
                        st.rerun()
                else:
                    st.error("غلط JSON فارمیٹ - براہ کرم درست بیک اپ فائل اپ لوڈ کریں")
            except:
                st.error("فائل پڑھنے میں خرابی - براہ کرم درست JSON فائل اپ لوڈ کریں")

# ========== بارکوڈ ==========
def render_barcode():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ فیچر دستیاب ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>🏷️ بارکوڈ جنریٹر</h2>", unsafe_allow_html=True)
    
    st.markdown("ہر آئٹم کے لیے بارکوڈ بنائیں اور ڈاؤن لوڈ کریں۔")
    
    items = data['items']
    item_names = [f"{i['name']} (ID: {i['id']})" for i in items]
    selected = st.selectbox("آئٹم منتخب کریں", item_names)
    
    if selected:
        idx = item_names.index(selected)
        item = items[idx]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**آئٹم:** {item['name']}")
            st.write(f"**ID:** {item['id']}")
            st.write(f"**کیٹیگری:** {item['category']}")
            st.write(f"**مقدار:** {item['quantity']} {item['unit']}")
            
            # Print receipt for this item
            if st.button("🖨️ اس آئٹم کی رسید پرنٹ کریں"):
                single_item = [item]
                html = generate_receipt_html(f"آئٹم: {item['name']}", single_item)
                st.components.v1.html(html, height=500, scrolling=True)
                render_print_receipt_button(single_item, f"بارکوڈ - {item['name']}")
        
        with col2:
            img = generate_barcode(item['id'], item['name'])
            if img:
                # Scale up for better quality
                img = img.resize((400, 120), Image.LANCZOS)
                st.image(img, caption=f"بارکوڈ - {item['name']}", use_container_width=True)
                
                # Download button for barcode
                buf = io.BytesIO()
                img.save(buf, format='PNG', dpi=(300, 300))
                b64 = base64.b64encode(buf.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="barcode_{item["id"]}.png" class="btn-gold" style="text-decoration:none;padding:8px 16px;border-radius:6px;margin:5px;display:inline-block;">⬇️ بارکوڈ ڈاؤن لوڈ کریں (HD)</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Print button for barcode
                st.markdown("""
                <button onclick="window.print()" class="btn-gold" style="padding:8px 16px;border-radius:6px;border:none;margin:5px;cursor:pointer;">
                    🖨️ بارکوڈ پرنٹ کریں
                </button>
                """, unsafe_allow_html=True)
            else:
                st.warning("بارکوڈ بناتے وقت خرابی - براہ کرم `python-barcode` انسٹال کریں")

# ========== نقشہ جات ==========
def render_maps():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ فیچر دستیاب ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>🗺️ کمرے کا مکمل نقشہ</h2>", unsafe_allow_html=True)
    
    col_actions = st.columns([4,1,1])
    with col_actions[1]:
        render_print_receipt_button(data['items'], "🗺️ نقشہ جات کی رپورٹ")
    with col_actions[2]:
        render_print_button()
    
    st.markdown("### کمرہ منتخب کریں")
    room_names = [r['name'] for r in data['rooms']]
    selected_room = st.selectbox("کمرہ", room_names)
    
    if selected_room:
        room_id = next((r['id'] for r in data['rooms'] if r['name'] == selected_room), None)
        if room_id:
            room_items = [i for i in data['items'] if i['roomId'] == room_id]
            
            st.markdown("### 📐 کمرے کا 2D منصوبہ")
            
            svg_width = 800
            svg_height = 600
            svg_content = f"""
            <svg width="{svg_width}" height="{svg_height}" style="background:#f8fafc;border:1px solid #d0d7de;border-radius:10px;">
                <rect x="50" y="50" width="700" height="500" fill="none" stroke="#1a3c5e" stroke-width="3" rx="5"/>
                <text x="400" y="40" text-anchor="middle" fill="#1a3c5e" font-size="20" font-family="Noto Nastaliq Urdu">{selected_room}</text>
                <rect x="350" y="545" width="100" height="10" fill="#2d6a4f"/>
                <text x="400" y="570" text-anchor="middle" fill="#4b5563" font-size="12">دروازہ</text>
            """
            
            furniture_map = {
                "کرسی": {"icon": "🪑", "x": 150, "y": 150, "w": 60, "h": 60},
                "میز": {"icon": "🪑", "x": 300, "y": 200, "w": 80, "h": 40},
                "الماری": {"icon": "🗄️", "x": 100, "y": 300, "w": 70, "h": 100},
                "قالین": {"icon": "🧶", "x": 400, "y": 350, "w": 150, "h": 100},
                "کتاب": {"icon": "📚", "x": 600, "y": 150, "w": 60, "h": 80},
                "کمپیوٹر": {"icon": "💻", "x": 500, "y": 250, "w": 80, "h": 50},
                "پرنٹر": {"icon": "🖨️", "x": 650, "y": 400, "w": 70, "h": 40},
                "صابن": {"icon": "🧼", "x": 700, "y": 100, "w": 40, "h": 40},
                "چائے": {"icon": "☕", "x": 200, "y": 450, "w": 50, "h": 50},
            }
            
            placed = 0
            for item in room_items:
                for f_name, f_data in furniture_map.items():
                    if f_name in item['name']:
                        x = f_data['x'] + (placed * 10) % 100
                        y = f_data['y'] + (placed * 5) % 50
                        svg_content += f"""
                        <rect x="{x}" y="{y}" width="{f_data['w']}" height="{f_data['h']}" fill="rgba(26,60,94,0.1)" stroke="#1a3c5e" stroke-width="1" rx="4"/>
                        <text x="{x + f_data['w']//2}" y="{y + f_data['h']//2 + 5}" text-anchor="middle" font-size="24" fill="#1a3c5e">{f_data['icon']}</text>
                        <text x="{x + f_data['w']//2}" y="{y + f_data['h'] + 15}" text-anchor="middle" fill="#4b5563" font-size="10" font-family="Noto Nastaliq Urdu">{item['name']}</text>
                        """
                        placed += 1
                        break
            
            if placed == 0:
                svg_content += f"""
                <text x="400" y="300" text-anchor="middle" fill="#4b5563" font-size="16">اس کمرے میں کوئی فرنیچر نہیں ہے</text>
                """
            
            svg_content += """
            </svg>
            """
            
            st.components.v1.html(svg_content, height=650, width=850)
            
            st.markdown("### 🪑 اس کمرے میں موجود اشیاء")
            if room_items:
                df = pd.DataFrame(room_items)
                df['کمرہ'] = selected_room
                df = df[['name', 'category', 'quantity', 'unit']]
                df.columns = ['سامان', 'کیٹیگری', 'مقدار', 'یونٹ']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("اس کمرے میں کوئی سامان نہیں ہے")

# ========== 3D ویو (ہر کمرے کے لیے الگ) ==========
def render_three_d():
    if st.session_state.user['role'] != 'admin':
        st.error("صرف ایڈمن کو یہ فیچر دستیاب ہے")
        return
    st.markdown("<h2 style='color:#1a3c5e;'>🌐 کمرے کا 3D ویو</h2>", unsafe_allow_html=True)
    
    # Select room
    room_names = [r['name'] for r in data['rooms']]
    selected_room_name = st.selectbox("کمرہ منتخب کریں", room_names, index=0)
    room = next((r for r in data['rooms'] if r['name'] == selected_room_name), data['rooms'][0])
    room_items = [i for i in data['items'] if i['roomId'] == room['id']]
    
    # Generate furniture list for Three.js
    furniture_js = ""
    # Map item names to Three.js objects
    furniture_map = {
        "کرسی": {"color": "0xc9a84c", "w": 0.6, "h": 0.6, "d": 0.6, "type": "box"},
        "میز": {"color": "0x4a148c", "w": 1.0, "h": 0.1, "d": 0.6, "type": "box"},
        "الماری": {"color": "0x1b5e20", "w": 0.8, "h": 1.2, "d": 0.4, "type": "box"},
        "قالین": {"color": "0x8b5a2b", "w": 1.5, "h": 0.02, "d": 1.0, "type": "plane"},
        "کتاب": {"color": "0xef4444", "w": 0.15, "h": 0.4, "d": 0.5, "type": "box"},
        "کمپیوٹر": {"color": "0x3b82f6", "w": 0.6, "h": 0.4, "d": 0.3, "type": "box"},
        "پرنٹر": {"color": "0x6b7280", "w": 0.5, "h": 0.3, "d": 0.4, "type": "box"},
    }
    
    positions = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 0), (-3, 0), (3, 0), (0, -3), (0, 3)]
    pos_idx = 0
    for item in room_items:
        for f_name, f_data in furniture_map.items():
            if f_name in item['name']:
                x, z = positions[pos_idx % len(positions)]
                pos_idx += 1
                color = f_data["color"]
                w, h, d = f_data["w"], f_data["h"], f_data["d"]
                if f_data["type"] == "plane":
                    furniture_js += f"""
                    const carpetMat = new THREE.MeshStandardMaterial({{ color: {color}, transparent: true, opacity: 0.6, side: THREE.DoubleSide }});
                    const carpet = new THREE.Mesh(new THREE.PlaneGeometry({w}, {d}), carpetMat);
                    carpet.rotation.x = -Math.PI / 2;
                    carpet.position.set({x}, -0.48, {z});
                    scene.add(carpet);
                    """
                else:
                    furniture_js += f"""
                    const geo = new THREE.BoxGeometry({w}, {h}, {d});
                    const mat = new THREE.MeshStandardMaterial({{ color: {color} }});
                    const mesh = new THREE.Mesh(geo, mat);
                    mesh.position.set({x}, {h/2}, {z});
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;
                    scene.add(mesh);
                    """
                break
    
    # Three.js code
    three_js_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: #ffffff; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xffffff);
            
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 10);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.autoRotate = true;
            controls.autoRotateSpeed = 2.0;
            
            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(5, 10, 7);
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            const pointLight = new THREE.PointLight(0x1a3c5e, 0.3, 20);
            pointLight.position.set(-3, 5, 3);
            scene.add(pointLight);
            
            const floorGeometry = new THREE.PlaneGeometry(8, 8);
            const floorMaterial = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, side: THREE.DoubleSide }});
            const floor = new THREE.Mesh(floorGeometry, floorMaterial);
            floor.rotation.x = -Math.PI / 2;
            floor.position.y = -0.5;
            floor.receiveShadow = true;
            scene.add(floor);
            
            const gridHelper = new THREE.GridHelper(8, 8, 0x1a3c5e, 0xd0d7de);
            gridHelper.position.y = -0.49;
            scene.add(gridHelper);
            
            function createWall(x, y, z, w, h, d, color) {{
                const geometry = new THREE.BoxGeometry(w, h, d);
                const material = new THREE.MeshStandardMaterial({{ color: color, transparent: true, opacity: 0.15 }});
                const wall = new THREE.Mesh(geometry, material);
                wall.position.set(x, y, z);
                wall.castShadow = true;
                wall.receiveShadow = true;
                scene.add(wall);
            }}
            
            // Room walls with room color
            const roomColor = 0x1a3c5e; // from room color
            createWall(0, 2, -4, 8, 4, 0.2, roomColor);
            createWall(-4, 2, 0, 0.2, 4, 8, roomColor);
            createWall(4, 2, 0, 0.2, 4, 8, roomColor);
            
            // Room label (using a sprite or just a simple text in CSS would be complex, we skip)
            
            // Furniture
            {furniture_js}
            
            // Floor label (using a simple plane with text, but we skip for simplicity)
            
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(three_js_code, height=600, width=800)
    st.caption(f"💡 کمرہ: {selected_room_name} | ماؤس سے گھمائیں، زوم کریں۔ خودکار گھومنے کے لیے کلک کریں۔")
    
    # Print and download
    col1, col2 = st.columns(2)
    with col1:
        render_print_button()
    with col2:
        render_html_download_button(three_js_code, f"3d_{selected_room_name}.html", "🌐 3D ویو ڈاؤن لوڈ کریں")

# ========== مین ==========
def main():
    render_sidebar()
    
    if not st.session_state.user:
        st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;height:70vh;'>
            <div style='text-align:center;'>
                <div style='font-size:72px;'>🕌</div>
                <h1 style='color:#1a3c5e;'>جامعہ ملیہ اسلامیہ فیصل آباد</h1>
                <p style='color:#4b5563;'>براہ کرم سائیڈ بار میں لاگ ان کریں</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "rooms":
        render_rooms()
    elif page == "items":
        render_items()
    elif page == "issue":
        render_issue()
    elif page == "returns":
        render_returns()
    elif page == "ai":
        render_ai()
    elif page == "backup":
        render_backup()
    elif page == "barcode":
        render_barcode()
    elif page == "maps":
        render_maps()
    elif page == "three_d":
        render_three_d()

if __name__ == "__main__":
    main()
