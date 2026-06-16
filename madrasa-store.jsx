import { useState, useEffect, useRef } from "react";

// ═══════════════════════════════════════════════
// MOCK DATA & CONSTANTS
// ═══════════════════════════════════════════════
const USERS = [
  { id: 1, username: "admin", password: "admin123", role: "admin", name: "ایڈمن صاحب" },
  { id: 2, username: "user1", password: "user123", role: "user", name: "محمد احمد" },
  { id: 3, username: "user2", password: "user456", role: "user", name: "عبداللہ خان" },
];

const CATEGORIES = ["کتب و کاپیاں", "صفائی کا سامان", "بجلی کا سامان", "فرنیچر", "کھانے پینے کی اشیاء", "کمپیوٹر و ٹیکنالوجی", "دیگر"];

const INIT_ROOMS = [
  { id: 1, name: "دفتر مہتمم", color: "#1a472a", icon: "🏛️" },
  { id: 2, name: "لائبریری", color: "#0d47a1", icon: "📚" },
  { id: 3, name: "کمپیوٹر لیب", color: "#4a148c", icon: "💻" },
  { id: 4, name: "باورچی خانہ", color: "#bf360c", icon: "🍽️" },
  { id: 5, name: "مرکزی اسٹور", color: "#37474f", icon: "🏪" },
];

const INIT_ITEMS = [
  { id: 1, name: "A4 پیپر ریم", roomId: 5, category: "کتب و کاپیاں", quantity: 50, unit: "ریم", minQty: 10 },
  { id: 2, name: "بال پوائنٹ قلم", roomId: 5, category: "کتب و کاپیاں", quantity: 200, unit: "عدد", minQty: 30 },
  { id: 3, name: "جھاڑو", roomId: 5, category: "صفائی کا سامان", quantity: 8, unit: "عدد", minQty: 2 },
  { id: 4, name: "صابن", roomId: 5, category: "صفائی کا سامان", quantity: 24, unit: "عدد", minQty: 5 },
  { id: 5, name: "LED بلب", roomId: 5, category: "بجلی کا سامان", quantity: 20, unit: "عدد", minQty: 5 },
  { id: 6, name: "پرنٹر", roomId: 3, category: "کمپیوٹر و ٹیکنالوجی", quantity: 2, unit: "عدد", minQty: 1 },
  { id: 7, name: "کرسی", roomId: 1, category: "فرنیچر", quantity: 6, unit: "عدد", minQty: 2 },
  { id: 8, name: "چائے پتی", roomId: 4, category: "کھانے پینے کی اشیاء", quantity: 3, unit: "کلو", minQty: 1 },
];

const INIT_TRANSACTIONS = [
  { id: 1, itemId: 1, itemName: "A4 پیپر ریم", userId: 2, userName: "محمد احمد", type: "issue", qty: 5, date: "2025-06-10", returnDate: null, expectedReturn: "2025-06-20", note: "امتحانی پرچے", status: "issued" },
  { id: 2, itemId: 3, itemName: "جھاڑو", userId: 3, userName: "عبداللہ خان", type: "issue", qty: 2, date: "2025-06-08", returnDate: "2025-06-12", expectedReturn: "2025-06-15", note: "صفائی کے لیے", status: "returned" },
];

// ═══════════════════════════════════════════════
// STYLES
// ═══════════════════════════════════════════════
const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Noto Nastaliq Urdu', serif;
    background: #0a0e1a;
    color: #e8eaf0;
    direction: rtl;
    min-height: 100vh;
  }

  :root {
    --gold: #c9a84c;
    --gold-light: #f0c060;
    --green-dark: #0d2818;
    --green-mid: #1a472a;
    --green-light: #2d6a4f;
    --surface: #111827;
    --surface2: #1a2234;
    --surface3: #222d42;
    --border: rgba(201,168,76,0.2);
    --text: #e8eaf0;
    --text2: #9ca3af;
    --red: #ef4444;
    --blue: #3b82f6;
    --emerald: #10b981;
  }

  .app-shell {
    display: flex;
    min-height: 100vh;
    position: relative;
  }

  /* LOGIN */
  .login-bg {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(ellipse at 30% 50%, #0d2818 0%, #0a0e1a 60%),
                radial-gradient(ellipse at 70% 20%, #1a1a2e 0%, transparent 50%);
    position: relative;
    overflow: hidden;
  }
  .login-bg::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(201,168,76,0.03) 40px, rgba(201,168,76,0.03) 41px),
      repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(201,168,76,0.03) 40px, rgba(201,168,76,0.03) 41px);
  }
  .login-orb {
    position: absolute;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    top: -100px; right: -100px;
    animation: pulse 4s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.1); } }

  .login-card {
    background: rgba(17,24,39,0.9);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 48px 40px;
    width: 420px;
    position: relative;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(201,168,76,0.1);
  }
  .login-logo {
    text-align: center;
    margin-bottom: 32px;
  }
  .login-logo .mosque { font-size: 52px; margin-bottom: 8px; }
  .login-logo h1 { font-size: 22px; color: var(--gold); font-weight: 700; line-height: 1.6; }
  .login-logo p { font-size: 13px; color: var(--text2); margin-top: 4px; font-family: 'Inter', sans-serif; }

  .form-group { margin-bottom: 20px; }
  .form-label { display: block; font-size: 14px; color: var(--text2); margin-bottom: 8px; }
  .form-input {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    color: var(--text);
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    direction: ltr;
    text-align: right;
    transition: border-color 0.2s;
  }
  .form-input:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(201,168,76,0.1); }

  .btn-primary {
    width: 100%;
    background: linear-gradient(135deg, var(--gold) 0%, #a07830 100%);
    color: #0a0e1a;
    border: none;
    border-radius: 10px;
    padding: 14px;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    font-family: 'Noto Nastaliq Urdu', serif;
    transition: all 0.2s;
    margin-top: 8px;
  }
  .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 25px rgba(201,168,76,0.3); }

  .login-error {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #fca5a5;
    margin-bottom: 16px;
    text-align: center;
  }

  /* SIDEBAR */
  .sidebar {
    width: 260px;
    min-height: 100vh;
    background: linear-gradient(180deg, #0d1f14 0%, #0a0e1a 100%);
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: fixed;
    right: 0; top: 0; bottom: 0;
    z-index: 100;
    transition: transform 0.3s;
  }
  .sidebar-header {
    padding: 24px 20px 20px;
    border-bottom: 1px solid var(--border);
    text-align: center;
  }
  .sidebar-header .logo-icon { font-size: 36px; }
  .sidebar-header h2 { font-size: 15px; color: var(--gold); margin-top: 6px; line-height: 1.6; }
  .sidebar-header p { font-size: 11px; color: var(--text2); margin-top: 2px; }

  .sidebar-user {
    margin: 16px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .user-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--gold), #a07830);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
  }
  .user-info { flex: 1; }
  .user-name { font-size: 13px; color: var(--text); }
  .user-role {
    font-size: 10px;
    font-family: 'Inter', sans-serif;
    color: var(--gold);
    background: rgba(201,168,76,0.1);
    border-radius: 4px;
    padding: 1px 6px;
    display: inline-block;
    margin-top: 2px;
  }

  .nav-list { flex: 1; padding: 8px 12px; overflow-y: auto; }
  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 14px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
    color: var(--text2);
    transition: all 0.2s;
    margin-bottom: 2px;
  }
  .nav-item:hover { background: var(--surface2); color: var(--text); }
  .nav-item.active { background: rgba(201,168,76,0.12); color: var(--gold); border: 1px solid rgba(201,168,76,0.2); }
  .nav-icon { font-size: 18px; flex-shrink: 0; }

  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid var(--border);
  }
  .btn-logout {
    width: 100%;
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.2);
    color: #fca5a5;
    border-radius: 8px;
    padding: 10px;
    cursor: pointer;
    font-size: 13px;
    font-family: 'Noto Nastaliq Urdu', serif;
    transition: all 0.2s;
  }
  .btn-logout:hover { background: rgba(239,68,68,0.2); }

  /* MAIN */
  .main-content {
    flex: 1;
    margin-right: 260px;
    min-height: 100vh;
    background: var(--surface);
  }
  .page-header {
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    padding: 20px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .page-title { font-size: 20px; color: var(--gold); }
  .page-subtitle { font-size: 12px; color: var(--text2); margin-top: 2px; font-family: 'Inter', sans-serif; }

  .page-body { padding: 24px 28px; }

  /* CARDS */
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
  .stat-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
  }
  .stat-card.gold::before { background: var(--gold); }
  .stat-card.green::before { background: var(--emerald); }
  .stat-card.blue::before { background: var(--blue); }
  .stat-card.red::before { background: var(--red); }
  .stat-icon { font-size: 28px; margin-bottom: 10px; }
  .stat-value { font-size: 28px; font-weight: 700; color: var(--text); font-family: 'Inter', sans-serif; }
  .stat-label { font-size: 13px; color: var(--text2); margin-top: 4px; }

  /* GRID LAYOUT */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

  .card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 20px;
  }
  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(201,168,76,0.04);
  }
  .card-title { font-size: 15px; color: var(--gold); display: flex; align-items: center; gap: 8px; }
  .card-body { padding: 20px; }

  /* ROOM CARDS */
  .room-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .room-card {
    border-radius: 14px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .room-card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
  .room-card .room-icon { font-size: 36px; margin-bottom: 10px; }
  .room-card .room-name { font-size: 16px; font-weight: 600; color: #fff; }
  .room-card .room-count { font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 4px; font-family: 'Inter', sans-serif; }
  .room-badge {
    position: absolute;
    top: 12px; left: 12px;
    background: rgba(0,0,0,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    color: rgba(255,255,255,0.8);
    font-family: 'Inter', sans-serif;
  }

  /* TABLE */
  .data-table { width: 100%; border-collapse: collapse; }
  .data-table th {
    background: var(--surface3);
    padding: 12px 16px;
    text-align: right;
    font-size: 13px;
    color: var(--gold);
    font-weight: 500;
    border-bottom: 1px solid var(--border);
  }
  .data-table td {
    padding: 12px 16px;
    font-size: 13px;
    color: var(--text);
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .data-table tr:hover td { background: var(--surface3); }

  /* BADGES */
  .badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
  }
  .badge-green { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
  .badge-red { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
  .badge-yellow { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
  .badge-blue { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.2); }

  /* BUTTONS */
  .btn {
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-size: 13px;
    font-family: 'Noto Nastaliq Urdu', serif;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn-gold { background: linear-gradient(135deg, var(--gold), #a07830); color: #0a0e1a; font-weight: 600; }
  .btn-gold:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(201,168,76,0.3); }
  .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text2); }
  .btn-outline:hover { border-color: var(--gold); color: var(--gold); }
  .btn-danger { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: #f87171; }
  .btn-danger:hover { background: rgba(239,68,68,0.2); }
  .btn-success { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #34d399; }
  .btn-success:hover { background: rgba(16,185,129,0.2); }
  .btn-sm { padding: 5px 10px; font-size: 12px; }

  /* MODAL */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }
  .modal {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px;
    width: 520px;
    max-width: 95vw;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 25px 60px rgba(0,0,0,0.6);
  }
  .modal-header {
    padding: 20px 24px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .modal-title { font-size: 16px; color: var(--gold); }
  .modal-body { padding: 24px; }
  .modal-footer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; gap: 10px; justify-content: flex-end; }

  .close-btn {
    background: none; border: none; color: var(--text2); cursor: pointer; font-size: 20px; padding: 4px;
    transition: color 0.2s;
  }
  .close-btn:hover { color: var(--text); }

  /* FORM */
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .form-group-inner { margin-bottom: 16px; }
  .inner-label { font-size: 13px; color: var(--text2); margin-bottom: 6px; display: block; }
  .inner-input, .inner-select, .inner-textarea {
    width: 100%;
    background: var(--surface3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    color: var(--text);
    font-size: 13px;
    font-family: 'Noto Nastaliq Urdu', serif;
    transition: border-color 0.2s;
  }
  .inner-input[dir="ltr"], .inner-input.ltr { direction: ltr; text-align: left; font-family: 'Inter', sans-serif; }
  .inner-input:focus, .inner-select:focus, .inner-textarea:focus {
    outline: none; border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(201,168,76,0.1);
  }
  .inner-select option { background: var(--surface3); }
  .inner-textarea { min-height: 80px; resize: vertical; }

  /* AI PANEL */
  .ai-panel {
    background: linear-gradient(135deg, #0d1f14 0%, #0a0e1a 100%);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 14px;
    padding: 24px;
    position: relative;
    overflow: hidden;
  }
  .ai-panel::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    border-radius: 50%;
  }
  .ai-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
  .ai-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--gold), #a07830);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
  }
  .ai-title { font-size: 16px; color: var(--gold); }
  .ai-subtitle { font-size: 12px; color: var(--text2); font-family: 'Inter', sans-serif; }

  .ai-response {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    font-size: 14px;
    line-height: 2;
    color: var(--text);
    min-height: 80px;
    white-space: pre-wrap;
  }
  .ai-response.loading { animation: shimmer 1.5s infinite; }
  @keyframes shimmer {
    0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; }
  }

  .ai-prompts { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .ai-prompt-btn {
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.2);
    color: var(--gold);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    cursor: pointer;
    font-family: 'Noto Nastaliq Urdu', serif;
    transition: all 0.2s;
  }
  .ai-prompt-btn:hover { background: rgba(201,168,76,0.15); }

  /* SEARCH */
  .search-bar {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
  }
  .search-input {
    flex: 1;
    background: none;
    border: none;
    color: var(--text);
    font-size: 14px;
    font-family: 'Noto Nastaliq Urdu', serif;
    outline: none;
  }

  /* LOW STOCK ALERT */
  .alert-bar {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #fca5a5;
  }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.2); border-radius: 3px; }

  /* PROGRESS BAR */
  .progress-bar {
    height: 6px;
    background: var(--surface3);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
  }
  .progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s;
  }

  @media (max-width: 768px) {
    .sidebar { transform: translateX(100%); }
    .main-content { margin-right: 0; }
    .stat-grid { grid-template-columns: 1fr 1fr; }
    .room-grid { grid-template-columns: 1fr 1fr; }
  }
`;

// ═══════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════
export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [rooms, setRooms] = useState(INIT_ROOMS);
  const [items, setItems] = useState(INIT_ITEMS);
  const [transactions, setTransactions] = useState(INIT_TRANSACTIONS);
  const [selectedRoom, setSelectedRoom] = useState(null);

  return (
    <>
      <style>{CSS}</style>
      {!user ? (
        <LoginPage onLogin={setUser} />
      ) : (
        <div className="app-shell">
          <Sidebar user={user} page={page} setPage={setPage} onLogout={() => setUser(null)} />
          <div className="main-content">
            {page === "dashboard" && (
              <Dashboard items={items} transactions={transactions} rooms={rooms} user={user} />
            )}
            {page === "rooms" && (
              <RoomsPage rooms={rooms} setRooms={setRooms} items={items} user={user}
                selectedRoom={selectedRoom} setSelectedRoom={setSelectedRoom} />
            )}
            {page === "items" && (
              <ItemsPage items={items} setItems={setItems} rooms={rooms} user={user} />
            )}
            {page === "issue" && (
              <IssuePage items={items} setItems={setItems} transactions={transactions}
                setTransactions={setTransactions} user={user} users={USERS} />
            )}
            {page === "returns" && (
              <ReturnsPage transactions={transactions} setTransactions={setTransactions}
                items={items} setItems={setItems} user={user} />
            )}
            {page === "ai" && (
              <AIPage items={items} transactions={transactions} rooms={rooms} />
            )}
          </div>
        </div>
      )}
    </>
  );
}

// ═══════════════════════════════════════════════
// LOGIN
// ═══════════════════════════════════════════════
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    const found = USERS.find(u => u.username === username && u.password === password);
    if (found) { onLogin(found); }
    else { setError("غلط صارف نام یا پاسورڈ"); }
  };

  return (
    <div className="login-bg">
      <div className="login-orb" />
      <div className="login-card">
        <div className="login-logo">
          <div className="mosque">🕌</div>
          <h1>جامعہ ملیہ اسلامیہ فیصل آباد</h1>
          <p>اسٹور مینجمنٹ سسٹم</p>
        </div>
        {error && <div className="login-error">{error}</div>}
        <div className="form-group">
          <label className="form-label">صارف نام</label>
          <input className="form-input" type="text" value={username}
            onChange={e => { setUsername(e.target.value); setError(""); }}
            onKeyDown={e => e.key === "Enter" && handleLogin()}
            placeholder="username" style={{ direction: "ltr", textAlign: "left" }} />
        </div>
        <div className="form-group">
          <label className="form-label">پاسورڈ</label>
          <input className="form-input" type="password" value={password}
            onChange={e => { setPassword(e.target.value); setError(""); }}
            onKeyDown={e => e.key === "Enter" && handleLogin()}
            placeholder="password" style={{ direction: "ltr", textAlign: "left" }} />
        </div>
        <button className="btn-primary" onClick={handleLogin}>🔐 داخل ہوں</button>
        <p style={{ textAlign: "center", fontSize: 12, color: "var(--text2)", marginTop: 20, fontFamily: "Inter" }}>
          Admin: admin / admin123 &nbsp;|&nbsp; User: user1 / user123
        </p>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// SIDEBAR
// ═══════════════════════════════════════════════
function Sidebar({ user, page, setPage, onLogout }) {
  const adminNav = [
    { id: "dashboard", label: "ڈیش بورڈ", icon: "📊" },
    { id: "rooms", label: "کمرے / مقامات", icon: "🏠" },
    { id: "items", label: "سامان کا انتظام", icon: "📦" },
    { id: "issue", label: "سامان جاری کریں", icon: "➡️" },
    { id: "returns", label: "واپسی کا نظم", icon: "↩️" },
    { id: "ai", label: "AI تجزیہ", icon: "🤖" },
  ];
  const userNav = [
    { id: "dashboard", label: "ڈیش بورڈ", icon: "📊" },
    { id: "items", label: "سامان دیکھیں", icon: "📦" },
    { id: "issue", label: "سامان طلب کریں", icon: "➡️" },
    { id: "returns", label: "واپسی", icon: "↩️" },
  ];
  const nav = user.role === "admin" ? adminNav : userNav;

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">🕌</div>
        <h2>جامعہ ملیہ اسلامیہ</h2>
        <p style={{ fontSize: 11, color: "var(--text2)", fontFamily: "Inter" }}>Store Management System</p>
      </div>
      <div className="sidebar-user">
        <div className="user-avatar">{user.name[0]}</div>
        <div className="user-info">
          <div className="user-name">{user.name}</div>
          <div className="user-role">{user.role === "admin" ? "ایڈمن" : "صارف"}</div>
        </div>
      </div>
      <div className="nav-list">
        {nav.map(n => (
          <div key={n.id} className={`nav-item ${page === n.id ? "active" : ""}`}
            onClick={() => setPage(n.id)}>
            <span className="nav-icon">{n.icon}</span>
            <span>{n.label}</span>
          </div>
        ))}
      </div>
      <div className="sidebar-footer">
        <button className="btn-logout" onClick={onLogout}>🚪 لاگ آؤٹ</button>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════
function Dashboard({ items, transactions, rooms, user }) {
  const totalItems = items.reduce((s, i) => s + i.quantity, 0);
  const lowStock = items.filter(i => i.quantity <= i.minQty);
  const issued = transactions.filter(t => t.status === "issued");
  const returned = transactions.filter(t => t.status === "returned");

  const catMap = {};
  items.forEach(i => { catMap[i.category] = (catMap[i.category] || 0) + 1; });

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📊 ڈیش بورڈ</div>
          <div className="page-subtitle">مدرسہ اسٹور - مکمل جائزہ</div>
        </div>
        <div style={{ fontSize: 13, color: "var(--text2)", fontFamily: "Inter" }}>
          {new Date().toLocaleDateString("ur-PK")}
        </div>
      </div>
      <div className="page-body">
        {lowStock.length > 0 && (
          <div className="alert-bar">
            ⚠️ <strong>{lowStock.length} اشیاء</strong> کا ذخیرہ کم ہے — فوری توجہ درکار ہے
          </div>
        )}
        <div className="stat-grid">
          <div className="stat-card gold">
            <div className="stat-icon">📦</div>
            <div className="stat-value">{items.length}</div>
            <div className="stat-label">کل اقسام سامان</div>
          </div>
          <div className="stat-card green">
            <div className="stat-icon">🏠</div>
            <div className="stat-value">{rooms.length}</div>
            <div className="stat-label">کمرے / مقامات</div>
          </div>
          <div className="stat-card blue">
            <div className="stat-icon">➡️</div>
            <div className="stat-value">{issued.length}</div>
            <div className="stat-label">جاری شدہ (واپسی باقی)</div>
          </div>
          <div className="stat-card red">
            <div className="stat-icon">⚠️</div>
            <div className="stat-value">{lowStock.length}</div>
            <div className="stat-label">کم ذخیرہ</div>
          </div>
        </div>

        <div className="grid-2">
          {/* Recent Transactions */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">🔄 حالیہ لین دین</span>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>سامان</th>
                    <th>صارف</th>
                    <th>حالت</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.slice(-5).reverse().map(t => (
                    <tr key={t.id}>
                      <td>{t.itemName}</td>
                      <td>{t.userName}</td>
                      <td>
                        <span className={`badge ${t.status === "issued" ? "badge-yellow" : "badge-green"}`}>
                          {t.status === "issued" ? "جاری" : "واپس"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Category breakdown */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">🗂️ کیٹیگری کا خلاصہ</span>
            </div>
            <div className="card-body">
              {Object.entries(catMap).map(([cat, cnt]) => {
                const pct = Math.round((cnt / items.length) * 100);
                return (
                  <div key={cat} style={{ marginBottom: 14 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                      <span>{cat}</span>
                      <span style={{ color: "var(--gold)", fontFamily: "Inter" }}>{cnt} قسم</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill"
                        style={{ width: pct + "%", background: "linear-gradient(90deg, var(--gold), #a07830)" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Low stock items */}
        {lowStock.length > 0 && (
          <div className="card">
            <div className="card-header">
              <span className="card-title">🚨 کم ذخیرہ — فوری توجہ</span>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <table className="data-table">
                <thead><tr><th>سامان</th><th>کمرہ</th><th>موجودہ</th><th>کم از کم</th><th>حالت</th></tr></thead>
                <tbody>
                  {lowStock.map(i => {
                    const room = rooms.find(r => r.id === i.roomId);
                    return (
                      <tr key={i.id}>
                        <td>{i.name}</td>
                        <td>{room?.name}</td>
                        <td style={{ color: "var(--red)", fontFamily: "Inter" }}>{i.quantity}</td>
                        <td style={{ fontFamily: "Inter" }}>{i.minQty}</td>
                        <td><span className="badge badge-red">کم ذخیرہ</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// ROOMS PAGE
// ═══════════════════════════════════════════════
function RoomsPage({ rooms, setRooms, items, user }) {
  const [showAdd, setShowAdd] = useState(false);
  const [viewRoom, setViewRoom] = useState(null);
  const [newRoom, setNewRoom] = useState({ name: "", icon: "🏠", color: "#1a472a" });

  const addRoom = () => {
    if (!newRoom.name) return;
    setRooms([...rooms, { ...newRoom, id: Date.now() }]);
    setNewRoom({ name: "", icon: "🏠", color: "#1a472a" });
    setShowAdd(false);
  };

  const ICONS = ["🏛️", "📚", "💻", "🍽️", "🏪", "🏫", "🕌", "🛠️", "🏋️", "🎯"];
  const COLORS = ["#1a472a", "#0d47a1", "#4a148c", "#bf360c", "#37474f", "#1b5e20", "#880e4f", "#004d40"];

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🏠 کمرے اور مقامات</div>
          <div className="page-subtitle">تمام کمرے اور ان میں موجود سامان</div>
        </div>
        {user.role === "admin" && (
          <button className="btn btn-gold" onClick={() => setShowAdd(true)}>+ نیا کمرہ</button>
        )}
      </div>
      <div className="page-body">
        <div className="room-grid">
          {rooms.map(room => {
            const roomItems = items.filter(i => i.roomId === room.id);
            return (
              <div key={room.id} className="room-card"
                style={{ background: `linear-gradient(135deg, ${room.color}dd, ${room.color}88)` }}
                onClick={() => setViewRoom(room)}>
                <div className="room-badge">{roomItems.length} اشیاء</div>
                <div className="room-icon">{room.icon}</div>
                <div className="room-name">{room.name}</div>
                <div className="room-count">
                  {roomItems.reduce((s, i) => s + i.quantity, 0)} کل مقدار
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Room Detail Modal */}
      {viewRoom && (
        <Modal title={`${viewRoom.icon} ${viewRoom.name}`} onClose={() => setViewRoom(null)}>
          <table className="data-table">
            <thead>
              <tr><th>سامان</th><th>کیٹیگری</th><th>مقدار</th><th>حالت</th></tr>
            </thead>
            <tbody>
              {items.filter(i => i.roomId === viewRoom.id).map(item => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td><span className="badge badge-blue">{item.category}</span></td>
                  <td style={{ fontFamily: "Inter" }}>{item.quantity} {item.unit}</td>
                  <td>
                    <span className={`badge ${item.quantity <= item.minQty ? "badge-red" : "badge-green"}`}>
                      {item.quantity <= item.minQty ? "کم" : "ٹھیک"}
                    </span>
                  </td>
                </tr>
              ))}
              {items.filter(i => i.roomId === viewRoom.id).length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--text2)", padding: 30 }}>
                  کوئی سامان موجود نہیں
                </td></tr>
              )}
            </tbody>
          </table>
        </Modal>
      )}

      {/* Add Room Modal */}
      {showAdd && (
        <Modal title="نیا کمرہ شامل کریں" onClose={() => setShowAdd(false)}>
          <div className="form-group-inner">
            <label className="inner-label">کمرے کا نام</label>
            <input className="inner-input" value={newRoom.name}
              onChange={e => setNewRoom({ ...newRoom, name: e.target.value })} placeholder="مثلاً: دفتر" />
          </div>
          <div className="form-group-inner">
            <label className="inner-label">آئیکن</label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {ICONS.map(ic => (
                <button key={ic} onClick={() => setNewRoom({ ...newRoom, icon: ic })}
                  style={{ fontSize: 24, background: newRoom.icon === ic ? "rgba(201,168,76,0.2)" : "var(--surface3)",
                    border: newRoom.icon === ic ? "1px solid var(--gold)" : "1px solid var(--border)",
                    borderRadius: 8, padding: "6px 10px", cursor: "pointer" }}>
                  {ic}
                </button>
              ))}
            </div>
          </div>
          <div className="form-group-inner">
            <label className="inner-label">رنگ</label>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {COLORS.map(c => (
                <div key={c} onClick={() => setNewRoom({ ...newRoom, color: c })}
                  style={{ width: 32, height: 32, borderRadius: 8, background: c, cursor: "pointer",
                    border: newRoom.color === c ? "2px solid var(--gold)" : "2px solid transparent" }} />
              ))}
            </div>
          </div>
          <div className="modal-footer" style={{ padding: "16px 0 0", border: "none" }}>
            <button className="btn btn-outline" onClick={() => setShowAdd(false)}>منسوخ</button>
            <button className="btn btn-gold" onClick={addRoom}>شامل کریں</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════
// ITEMS PAGE
// ═══════════════════════════════════════════════
function ItemsPage({ items, setItems, rooms, user }) {
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("سب");
  const [filterRoom, setFilterRoom] = useState("سب");
  const [showAdd, setShowAdd] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState({ name: "", roomId: rooms[0]?.id, category: CATEGORIES[0], quantity: "", unit: "عدد", minQty: "" });

  const filtered = items.filter(i => {
    const matchSearch = i.name.includes(search);
    const matchCat = filterCat === "سب" || i.category === filterCat;
    const matchRoom = filterRoom === "سب" || i.roomId === Number(filterRoom);
    return matchSearch && matchCat && matchRoom;
  });

  const saveItem = () => {
    if (!form.name || !form.quantity) return;
    if (editItem) {
      setItems(items.map(i => i.id === editItem.id ? { ...i, ...form, roomId: Number(form.roomId), quantity: Number(form.quantity), minQty: Number(form.minQty) } : i));
    } else {
      setItems([...items, { ...form, id: Date.now(), roomId: Number(form.roomId), quantity: Number(form.quantity), minQty: Number(form.minQty) }]);
    }
    setShowAdd(false); setEditItem(null);
    setForm({ name: "", roomId: rooms[0]?.id, category: CATEGORIES[0], quantity: "", unit: "عدد", minQty: "" });
  };

  const openEdit = (item) => {
    setEditItem(item);
    setForm({ name: item.name, roomId: item.roomId, category: item.category, quantity: item.quantity, unit: item.unit, minQty: item.minQty });
    setShowAdd(true);
  };

  const deleteItem = (id) => {
    if (confirm("واقعی حذف کریں؟")) setItems(items.filter(i => i.id !== id));
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📦 سامان کا انتظام</div>
          <div className="page-subtitle">تمام اشیاء — کمرہ اور کیٹیگری کے مطابق</div>
        </div>
        {user.role === "admin" && (
          <button className="btn btn-gold" onClick={() => { setEditItem(null); setShowAdd(true); }}>+ نیا سامان</button>
        )}
      </div>
      <div className="page-body">
        {/* Filters */}
        <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
          <input className="inner-input" placeholder="🔍 تلاش کریں..." value={search}
            onChange={e => setSearch(e.target.value)} style={{ flex: 1 }} />
          <select className="inner-select" value={filterCat} onChange={e => setFilterCat(e.target.value)} style={{ width: 180 }}>
            <option value="سب">تمام کیٹیگریز</option>
            {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="inner-select" value={filterRoom} onChange={e => setFilterRoom(e.target.value)} style={{ width: 180 }}>
            <option value="سب">تمام کمرے</option>
            {rooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
        </div>

        <div className="card">
          <table className="data-table">
            <thead>
              <tr><th>سامان</th><th>کمرہ</th><th>کیٹیگری</th><th>مقدار</th><th>کم از کم</th><th>حالت</th>
                {user.role === "admin" && <th>عمل</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => {
                const room = rooms.find(r => r.id === item.roomId);
                const low = item.quantity <= item.minQty;
                return (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 500 }}>{item.name}</td>
                    <td>{room?.icon} {room?.name}</td>
                    <td><span className="badge badge-blue">{item.category}</span></td>
                    <td style={{ fontFamily: "Inter", color: low ? "var(--red)" : "var(--emerald)" }}>
                      {item.quantity} {item.unit}
                    </td>
                    <td style={{ fontFamily: "Inter", color: "var(--text2)" }}>{item.minQty}</td>
                    <td><span className={`badge ${low ? "badge-red" : "badge-green"}`}>{low ? "کم ذخیرہ" : "دستیاب"}</span></td>
                    {user.role === "admin" && (
                      <td style={{ display: "flex", gap: 6 }}>
                        <button className="btn btn-outline btn-sm" onClick={() => openEdit(item)}>✏️</button>
                        <button className="btn btn-danger btn-sm" onClick={() => deleteItem(item.id)}>🗑️</button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showAdd && (
        <Modal title={editItem ? "سامان میں ترمیم" : "نیا سامان شامل کریں"} onClose={() => { setShowAdd(false); setEditItem(null); }}>
          <div className="form-row">
            <div className="form-group-inner">
              <label className="inner-label">سامان کا نام</label>
              <input className="inner-input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="form-group-inner">
              <label className="inner-label">یونٹ</label>
              <input className="inner-input" value={form.unit} onChange={e => setForm({ ...form, unit: e.target.value })} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group-inner">
              <label className="inner-label">کمرہ</label>
              <select className="inner-select" value={form.roomId} onChange={e => setForm({ ...form, roomId: e.target.value })}>
                {rooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
              </select>
            </div>
            <div className="form-group-inner">
              <label className="inner-label">کیٹیگری</label>
              <select className="inner-select" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group-inner">
              <label className="inner-label">موجودہ مقدار</label>
              <input className="inner-input ltr" type="number" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} />
            </div>
            <div className="form-group-inner">
              <label className="inner-label">کم از کم مقدار (الرٹ)</label>
              <input className="inner-input ltr" type="number" value={form.minQty} onChange={e => setForm({ ...form, minQty: e.target.value })} />
            </div>
          </div>
          <div className="modal-footer" style={{ padding: "16px 0 0", border: "none" }}>
            <button className="btn btn-outline" onClick={() => { setShowAdd(false); setEditItem(null); }}>منسوخ</button>
            <button className="btn btn-gold" onClick={saveItem}>{editItem ? "محفوظ کریں" : "شامل کریں"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════
// ISSUE PAGE
// ═══════════════════════════════════════════════
function IssuePage({ items, setItems, transactions, setTransactions, user, users }) {
  const [form, setForm] = useState({ itemId: "", qty: 1, userName: user.role === "user" ? user.name : "", expectedReturn: "", note: "" });
  const [success, setSuccess] = useState(false);

  const issueItem = () => {
    const item = items.find(i => i.id === Number(form.itemId));
    if (!item || !form.qty || !form.userName) return;
    if (Number(form.qty) > item.quantity) { alert("مقدار دستیاب نہیں"); return; }

    const tx = {
      id: Date.now(), itemId: item.id, itemName: item.name,
      userId: user.id, userName: form.userName,
      type: "issue", qty: Number(form.qty),
      date: new Date().toISOString().split("T")[0],
      expectedReturn: form.expectedReturn, returnDate: null,
      note: form.note, status: "issued"
    };
    setTransactions([...transactions, tx]);
    setItems(items.map(i => i.id === item.id ? { ...i, quantity: i.quantity - Number(form.qty) } : i));
    setForm({ itemId: "", qty: 1, userName: user.role === "user" ? user.name : "", expectedReturn: "", note: "" });
    setSuccess(true);
    setTimeout(() => setSuccess(false), 3000);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">➡️ سامان جاری کریں</div>
          <div className="page-subtitle">کسی کو سامان دینے کا اندراج</div>
        </div>
      </div>
      <div className="page-body">
        {success && (
          <div style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 10, padding: "14px 20px", marginBottom: 20, color: "#34d399", fontSize: 14 }}>
            ✅ سامان کامیابی سے جاری کر دیا گیا
          </div>
        )}
        <div className="grid-2">
          <div className="card">
            <div className="card-header"><span className="card-title">📋 اندراج فارم</span></div>
            <div className="card-body">
              <div className="form-group-inner">
                <label className="inner-label">سامان</label>
                <select className="inner-select" value={form.itemId} onChange={e => setForm({ ...form, itemId: e.target.value })}>
                  <option value="">سامان منتخب کریں</option>
                  {items.filter(i => i.quantity > 0).map(i => (
                    <option key={i.id} value={i.id}>{i.name} (دستیاب: {i.quantity} {i.unit})</option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <div className="form-group-inner">
                  <label className="inner-label">مقدار</label>
                  <input className="inner-input ltr" type="number" min="1" value={form.qty}
                    onChange={e => setForm({ ...form, qty: e.target.value })} />
                </div>
                <div className="form-group-inner">
                  <label className="inner-label">واپسی کی تاریخ</label>
                  <input className="inner-input ltr" type="date" value={form.expectedReturn}
                    onChange={e => setForm({ ...form, expectedReturn: e.target.value })} />
                </div>
              </div>
              <div className="form-group-inner">
                <label className="inner-label">لینے والے کا نام</label>
                <input className="inner-input" value={form.userName}
                  onChange={e => setForm({ ...form, userName: e.target.value })}
                  readOnly={user.role === "user"} />
              </div>
              <div className="form-group-inner">
                <label className="inner-label">نوٹ / مقصد</label>
                <textarea className="inner-textarea" value={form.note}
                  onChange={e => setForm({ ...form, note: e.target.value })} placeholder="مقصد یا وجہ لکھیں..." />
              </div>
              <button className="btn btn-gold" style={{ width: "100%" }} onClick={issueItem}>✅ سامان جاری کریں</button>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">📊 جاری سامان کی فہرست</span></div>
            <div className="card-body" style={{ padding: 0 }}>
              <table className="data-table">
                <thead><tr><th>سامان</th><th>کس کو</th><th>مقدار</th><th>واپسی</th></tr></thead>
                <tbody>
                  {transactions.filter(t => t.status === "issued").map(t => (
                    <tr key={t.id}>
                      <td>{t.itemName}</td>
                      <td>{t.userName}</td>
                      <td style={{ fontFamily: "Inter" }}>{t.qty}</td>
                      <td style={{ fontSize: 12, fontFamily: "Inter", color: t.expectedReturn && new Date(t.expectedReturn) < new Date() ? "var(--red)" : "var(--text2)" }}>
                        {t.expectedReturn || "—"}
                      </td>
                    </tr>
                  ))}
                  {transactions.filter(t => t.status === "issued").length === 0 && (
                    <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--text2)", padding: 30 }}>کوئی سامان جاری نہیں</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// RETURNS PAGE
// ═══════════════════════════════════════════════
function ReturnsPage({ transactions, setTransactions, items, setItems, user }) {
  const issued = transactions.filter(t => t.status === "issued");

  const returnItem = (tx) => {
    setTransactions(transactions.map(t =>
      t.id === tx.id ? { ...t, status: "returned", returnDate: new Date().toISOString().split("T")[0] } : t
    ));
    setItems(items.map(i => i.id === tx.itemId ? { ...i, quantity: i.quantity + tx.qty } : i));
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">↩️ واپسی کا نظم</div>
          <div className="page-subtitle">جاری کردہ سامان کی واپسی</div>
        </div>
      </div>
      <div className="page-body">
        <div className="card">
          <div className="card-header">
            <span className="card-title">⏳ واپسی باقی سامان</span>
            <span className="badge badge-yellow">{issued.length}</span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead>
                <tr><th>سامان</th><th>لینے والا</th><th>مقدار</th><th>تاریخ اجراء</th><th>واپسی تاریخ</th><th>نوٹ</th><th>عمل</th></tr>
              </thead>
              <tbody>
                {issued.map(t => {
                  const overdue = t.expectedReturn && new Date(t.expectedReturn) < new Date();
                  return (
                    <tr key={t.id}>
                      <td>{t.itemName}</td>
                      <td>{t.userName}</td>
                      <td style={{ fontFamily: "Inter" }}>{t.qty}</td>
                      <td style={{ fontFamily: "Inter", fontSize: 12 }}>{t.date}</td>
                      <td>
                        <span style={{ fontSize: 12, fontFamily: "Inter", color: overdue ? "var(--red)" : "var(--text2)" }}>
                          {t.expectedReturn || "—"} {overdue && "⚠️"}
                        </span>
                      </td>
                      <td style={{ fontSize: 12, color: "var(--text2)" }}>{t.note || "—"}</td>
                      <td>
                        {(user.role === "admin" || t.userId === user.id) && (
                          <button className="btn btn-success btn-sm" onClick={() => returnItem(t)}>↩️ واپس</button>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {issued.length === 0 && (
                  <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--text2)", padding: 30 }}>
                    تمام سامان واپس ہو چکا ✅
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Full History */}
        <div className="card">
          <div className="card-header"><span className="card-title">📜 مکمل تاریخ</span></div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead><tr><th>سامان</th><th>نام</th><th>مقدار</th><th>اجراء</th><th>واپسی</th><th>حالت</th></tr></thead>
              <tbody>
                {[...transactions].reverse().map(t => (
                  <tr key={t.id}>
                    <td>{t.itemName}</td>
                    <td>{t.userName}</td>
                    <td style={{ fontFamily: "Inter" }}>{t.qty}</td>
                    <td style={{ fontFamily: "Inter", fontSize: 12 }}>{t.date}</td>
                    <td style={{ fontFamily: "Inter", fontSize: 12 }}>{t.returnDate || "—"}</td>
                    <td><span className={`badge ${t.status === "issued" ? "badge-yellow" : "badge-green"}`}>
                      {t.status === "issued" ? "جاری" : "واپس"}
                    </span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// AI PAGE
// ═══════════════════════════════════════════════
function AIPage({ items, transactions, rooms }) {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const prompts = [
    "اسٹور کا مکمل جائزہ دیں",
    "کم ذخیرہ اشیاء کی فہرست دیں",
    "سب سے زیادہ استعمال ہونے والی اشیاء کون سی ہیں؟",
    "واپسی میں تاخیر کی رپورٹ دیں",
    "خریداری کی سفارشات دیں",
    "کمرہ وار تجزیہ کریں",
  ];

  const askAI = async (q = query) => {
    if (!q.trim()) return;
    setLoading(true);
    setResponse("");
    try {
      const storeData = {
        rooms: rooms.map(r => ({ name: r.name, itemCount: items.filter(i => i.roomId === r.id).length })),
        items: items.map(i => ({ name: i.name, qty: i.quantity, min: i.minQty, cat: i.category, room: rooms.find(r => r.id === i.roomId)?.name })),
        transactions: transactions.map(t => ({ item: t.itemName, by: t.userName, status: t.status, date: t.date, expectedReturn: t.expectedReturn }))
      };
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-6",
          max_tokens: 1000,
          system: `آپ جامعہ ملیہ اسلامیہ فیصل آباد کے اسٹور مینجمنٹ سسٹم کے AI مشیر ہیں۔ ہمیشہ اردو میں جواب دیں۔ مختصر، واضح اور عملی مشورے دیں۔`,
          messages: [{ role: "user", content: `اسٹور کا ڈیٹا:\n${JSON.stringify(storeData, null, 2)}\n\nسوال: ${q}` }]
        })
      });
      const data = await res.json();
      setResponse(data.content?.[0]?.text || "جواب نہیں ملا");
    } catch (e) {
      setResponse("خطا: AI سے رابطہ نہیں ہو سکا");
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🤖 AI تجزیہ</div>
          <div className="page-subtitle">مصنوعی ذہانت سے اسٹور کا جائزہ</div>
        </div>
      </div>
      <div className="page-body">
        <div className="ai-panel">
          <div className="ai-header">
            <div className="ai-icon">🤖</div>
            <div>
              <div className="ai-title">AI مشیر — جامعہ اسٹور</div>
              <div className="ai-subtitle">Powered by Claude AI</div>
            </div>
          </div>
          <div className="ai-prompts">
            {prompts.map(p => (
              <button key={p} className="ai-prompt-btn" onClick={() => { setQuery(p); askAI(p); }}>{p}</button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
            <input className="inner-input" style={{ flex: 1 }} value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && askAI()}
              placeholder="کوئی بھی سوال پوچھیں..." />
            <button className="btn btn-gold" onClick={() => askAI()} disabled={loading}>
              {loading ? "⏳" : "پوچھیں"}
            </button>
          </div>
          {response && (
            <div className={`ai-response ${loading ? "loading" : ""}`}>
              {loading ? "AI جواب تیار کر رہا ہے..." : response}
            </div>
          )}
          {!response && !loading && (
            <div className="ai-response" style={{ color: "var(--text2)", fontSize: 13 }}>
              اوپر دیے گئے سوالات میں سے کوئی منتخب کریں یا اپنا سوال لکھیں...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// MODAL COMPONENT
// ═══════════════════════════════════════════════
function Modal({ title, children, onClose }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <span className="modal-title">{title}</span>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}
