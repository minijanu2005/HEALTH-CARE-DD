"""Production-style healthcare admin theme (Streamlit)."""

HEALTHCARE_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 0.8rem; max-width: 1480px; }

    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e8edf3;
    }
    [data-testid="stSidebar"] * { color: #1e293b !important; }
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 12px !important;
        justify-content: flex-start !important;
        font-weight: 600 !important;
        border: 1px solid #e2e8f0 !important;
        background: #f8fafc !important;
        color: #334155 !important;
        margin-bottom: 0.35rem !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #2563eb, #0284c7) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.25) !important;
    }
    .sidebar-user { margin: 0.5rem 0 1rem; }
    .sidebar-user-name { font-weight: 700; color: #0f172a !important; font-size: 0.95rem; }
    .sidebar-user-role { color: #64748b !important; font-size: 0.8rem; }
    .nav-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8 !important;
        margin: 0.5rem 0 0.35rem;
    }
    .brand-box {
        background: linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 100%);
        color: #fff !important;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .brand-box * { color: #fff !important; }
    .brand-title { font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em; }
    .brand-sub { font-size: 0.78rem; opacity: 0.9; }

    .app-topbar {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }
    .app-topbar h1 { font-size: 1.5rem; margin: 0; color: #0f172a; font-weight: 800; }
    .app-topbar .crumb { color: #64748b; font-size: 0.82rem; margin-bottom: 0.15rem; }

    .hero-banner {
        background: linear-gradient(120deg, #eff6ff 0%, #f0fdfa 100%);
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .hero-banner h2 { margin: 0; color: #0f172a; font-weight: 800; font-size: 1.45rem; }
    .hero-banner p { margin: 0.35rem 0 0; color: #475569; }
    .hero-banner.compact { padding: 1rem 1.2rem; margin-bottom: 0.85rem; }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        min-height: 108px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
    }
    .kpi-label { color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-value { color: #0f172a; font-size: 1.85rem; font-weight: 800; line-height: 1.1; margin-top: 0.35rem; }
    .kpi-sub { color: #94a3b8; font-size: 0.78rem; margin-top: 0.25rem; }

    .panel-head h3 { margin: 0; color: #0f172a; font-size: 1.05rem; font-weight: 700; }
    .panel-head p { margin: 0.15rem 0 0.75rem; color: #64748b; font-size: 0.85rem; }

    .content-panel {
        background: #fff;
        border: 1px solid #e8edf3;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
    }

    .login-card {
        background: #fff;
        border: 1px solid #e8edf3;
        border-radius: 20px;
        padding: 1.75rem 1.5rem 1.25rem;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        text-align: center;
        margin-bottom: 1rem;
    }
    .login-logo { font-size: 2rem; margin-bottom: 0.35rem; }
    .login-title { font-size: 1.65rem; font-weight: 800; color: #1d4ed8; margin-bottom: 0.15rem; }
    .login-subtitle { color: #64748b; font-size: 0.92rem; margin-bottom: 0.35rem; }
    .login-tag { color: #94a3b8; font-size: 0.78rem; }
    .login-hint {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        color: #475569;
        font-size: 0.85rem;
    }
    .login-page-bg .block-container { background: transparent; }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .badge-scheduled { background:#dbeafe; color:#1d4ed8; }
    .badge-completed { background:#dcfce7; color:#15803d; }
    .badge-cancelled { background:#fee2e2; color:#b91c1c; }
    .badge-no-show { background:#fef3c7; color:#b45309; }

    div[data-testid="stFormSubmitButton"] > button,
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #1d4ed8, #0284c7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        background: #f1f5f9;
        font-weight: 600;
    }
    div[data-testid="stMain"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 220px);
    }
</style>
"""


def status_badge_html(status: str) -> str:
    css = {
        "Scheduled": "badge-scheduled",
        "Completed": "badge-completed",
        "Cancelled": "badge-cancelled",
        "No-show": "badge-no-show",
    }.get(status, "badge-scheduled")
    return f'<span class="badge {css}">{status}</span>'
