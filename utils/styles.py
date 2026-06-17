SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Global ── */
.stApp { background: #f8f9ff; }
[data-testid="stSidebar"] {
    background: #1a1d2e !important;
    border-right: 1px solid #2d3154;
}
[data-testid="stSidebar"] * { color: #c8ccdf !important; }
[data-testid="stSidebar"] .sidebar-logo { color: white !important; }

/* Hide default streamlit header */
#MainMenu, footer { visibility: hidden; }

/* ── Top navbar ── */
.top-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 1.5rem; background: white;
    border-bottom: 1px solid #eef0f7;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
.brand-logo { font-size: 1.4rem; font-weight: 800; color: #1a1d2e; }
.brand-logo span { color: #6c5ce7; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px; padding: 2.5rem;
    color: white; position: relative; overflow: hidden;
    margin-bottom: 2rem;
}
.hero-banner h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.hero-banner h1 span { color: #ffd700; }
.hero-banner p { font-size: 0.95rem; opacity: 0.9; max-width: 400px; }
.hero-btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: white; color: #6c5ce7; font-weight: 700;
    padding: 0.7rem 1.5rem; border-radius: 50px;
    text-decoration: none; margin-top: 1rem;
    transition: transform 0.2s; cursor: pointer;
    border: none; font-size: 0.9rem;
}
.hero-btn:hover { transform: translateY(-2px); }

/* ── Section header ── */
.section-header {
    display: flex; justify-content: space-between; align-items: center;
    margin: 1.5rem 0 1rem 0;
}
.section-title { font-size: 1.25rem; font-weight: 700; color: #1a1d2e; margin: 0; }
.view-all { color: #6c5ce7; font-size: 0.85rem; font-weight: 600; cursor: pointer; text-decoration: none; }

/* ── Category chips ── */
.cat-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.cat-chip {
    display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
    padding: 0.75rem 1rem; background: white; border-radius: 12px;
    border: 1.5px solid #eef0f7; cursor: pointer;
    transition: all 0.2s; min-width: 70px; text-align: center;
    font-size: 0.75rem; color: #555; font-weight: 500;
}
.cat-chip:hover { border-color: #6c5ce7; color: #6c5ce7; box-shadow: 0 2px 8px rgba(108,92,231,0.15); }
.cat-chip.active { background: #6c5ce7; border-color: #6c5ce7; color: white; }
.cat-icon { font-size: 1.5rem; }

/* ── Product card ── */
.product-card {
    background: white; border-radius: 16px; overflow: hidden;
    border: 1px solid #eef0f7; transition: all 0.25s;
    height: 100%; position: relative;
}
.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(108,92,231,0.15);
    border-color: #6c5ce7;
}
.product-img-wrap {
    width: 100%; height: 180px; overflow: hidden;
    background: #f8f9ff; display: flex; align-items: center; justify-content: center;
}
.product-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.product-info { padding: 1rem; }
.product-name { font-weight: 700; font-size: 0.9rem; color: #1a1d2e; margin: 0 0 0.2rem 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-cat { font-size: 0.75rem; color: #888; margin: 0 0 0.4rem 0; }
.product-stars { color: #f59e0b; font-size: 0.8rem; }
.product-price { font-size: 1.05rem; font-weight: 800; color: #6c5ce7; margin: 0.4rem 0 0 0; }
.product-orig-price { font-size: 0.78rem; color: #aaa; text-decoration: line-through; margin-left: 0.4rem; }
.badge-new { background: #10b981; color: white; font-size: 0.65rem; font-weight: 700;
    padding: 0.15rem 0.5rem; border-radius: 50px; }
.badge-trending { background: #f59e0b; color: white; font-size: 0.65rem; font-weight: 700;
    padding: 0.15rem 0.5rem; border-radius: 50px; }
.card-actions { display: flex; gap: 0.5rem; padding: 0 1rem 1rem 1rem; }
.btn-view {
    flex: 1; background: #6c5ce7; color: white; border: none;
    padding: 0.5rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600;
    cursor: pointer; transition: all 0.2s;
}
.btn-view:hover { background: #5849d4; }
.btn-wish {
    background: #f8f9ff; border: 1.5px solid #eef0f7; color: #888;
    width: 36px; border-radius: 8px; cursor: pointer; font-size: 1rem;
    transition: all 0.2s;
}
.btn-wish.active { color: #ef4444; border-color: #fecdd3; background: #fff5f5; }
.btn-wish:hover { color: #ef4444; }

/* ── Recommendation card ── */
.rec-card {
    background: white; border-radius: 16px; padding: 1rem;
    border: 1px solid #eef0f7; display: flex; gap: 1rem;
    align-items: flex-start; transition: all 0.2s; margin-bottom: 0.75rem;
}
.rec-card:hover { border-color: #6c5ce7; box-shadow: 0 4px 16px rgba(108,92,231,0.1); }
.rec-card-img { width: 72px; height: 72px; border-radius: 10px; object-fit: cover; flex-shrink: 0; }
.rec-reason-tag {
    display: inline-block; background: #eef0ff; color: #6c5ce7;
    font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.6rem;
    border-radius: 50px; margin: 0.15rem 0.15rem 0 0;
}
.confidence-bar { height: 4px; background: #eef0f7; border-radius: 2px; margin-top: 0.4rem; }
.confidence-fill { height: 4px; background: #10b981; border-radius: 2px; }

/* ── Stats widget ── */
.stat-box {
    background: white; border-radius: 12px; padding: 1rem 1.25rem;
    border: 1px solid #eef0f7; text-align: center;
}
.stat-num { font-size: 1.6rem; font-weight: 800; color: #6c5ce7; }
.stat-label { font-size: 0.75rem; color: #888; margin-top: 0.1rem; }

/* ── Why rec panel ── */
.why-rec-panel {
    background: white; border-radius: 16px; padding: 1.25rem;
    border: 1px solid #eef0f7;
}
.why-rec-panel h4 { font-size: 0.95rem; font-weight: 700; color: #1a1d2e; margin: 0 0 1rem 0; }
.why-item { display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.83rem; color: #444; padding: 0.4rem 0; }
.why-icon { font-size: 1rem; }

/* ── Auth page ── */
.auth-container {
    max-width: 420px; margin: 3rem auto;
    background: white; border-radius: 24px; padding: 2.5rem;
    box-shadow: 0 8px 40px rgba(108,92,231,0.12);
}
.auth-logo { text-align: center; margin-bottom: 1.5rem; }
.auth-logo h2 { font-size: 1.8rem; font-weight: 800; color: #1a1d2e; }
.auth-logo h2 span { color: #6c5ce7; }
.auth-tab {
    display: flex; background: #f8f9ff; border-radius: 12px;
    padding: 0.25rem; margin-bottom: 1.5rem;
}
.auth-tab-btn {
    flex: 1; padding: 0.6rem; border: none; border-radius: 10px;
    font-weight: 600; font-size: 0.9rem; cursor: pointer;
    background: transparent; color: #888; transition: all 0.2s;
}
.auth-tab-btn.active { background: white; color: #6c5ce7; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

/* ── Sidebar nav ── */
.sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid #2d3154; margin-bottom: 0.5rem; }
.sidebar-brand h2 { font-size: 1.3rem; font-weight: 800; color: white !important; margin: 0; }
.sidebar-brand h2 span { color: #a78bfa !important; }
.sidebar-brand p { font-size: 0.75rem; color: #8890b5 !important; margin: 0.2rem 0 0 0; }
.nav-item {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.75rem 1rem; border-radius: 10px; margin: 0.15rem 0.5rem;
    color: #8890b5; font-size: 0.88rem; font-weight: 500; cursor: pointer;
    transition: all 0.2s;
}
.nav-item:hover { background: #2d3154; color: white; }
.nav-item.active { background: #6c5ce7; color: white; }
.nav-icon { font-size: 1.05rem; }

/* ── Trending rank ── */
.trending-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 6px; font-size: 0.75rem;
    font-weight: 800; background: #6c5ce7; color: white; margin-bottom: 0.5rem;
}

/* ── Wishlist item ── */
.wish-item {
    background: white; border-radius: 14px; padding: 1rem;
    border: 1px solid #eef0f7; display: flex; gap: 1rem;
    align-items: center; margin-bottom: 0.75rem;
}
.wish-img { width: 64px; height: 64px; object-fit: cover; border-radius: 10px; }
.wish-remove { color: #ef4444; cursor: pointer; font-size: 1.2rem; }

/* ── Profile ── */
.profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px; padding: 2rem; color: white; text-align: center;
}
.profile-avatar {
    width: 80px; height: 80px; border-radius: 50%;
    border: 3px solid white; margin: 0 auto 1rem auto; object-fit: cover;
}
.profile-name { font-size: 1.4rem; font-weight: 800; margin: 0; }
.profile-email { font-size: 0.85rem; opacity: 0.85; margin: 0.2rem 0 0 0; }
.pref-bar-wrap { margin: 0.4rem 0; }
.pref-label { display: flex; justify-content: space-between; font-size: 0.8rem; color: #555; margin-bottom: 0.2rem; }
.pref-bar { height: 6px; background: #eef0f7; border-radius: 3px; }
.pref-fill { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #6c5ce7, #a78bfa); }

/* ── Upgrade banner ── */
.upgrade-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 14px; padding: 1.25rem; color: white; text-align: center;
    margin: 1rem 0.5rem;
}
.upgrade-card h4 { font-size: 0.95rem; font-weight: 700; margin: 0.5rem 0 0.3rem 0; }
.upgrade-card p { font-size: 0.78rem; opacity: 0.88; margin: 0 0 0.8rem 0; }
.upgrade-btn {
    background: white; color: #6c5ce7; font-weight: 700;
    padding: 0.5rem 1.2rem; border-radius: 50px; font-size: 0.82rem;
    border: none; cursor: pointer;
}

/* ── Input styling ── */
.stTextInput input, .stSelectbox select {
    border-radius: 12px !important; border: 1.5px solid #eef0f7 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus { border-color: #6c5ce7 !important; box-shadow: 0 0 0 3px rgba(108,92,231,0.1) !important; }
.stButton > button {
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important; transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6c5ce7, #a78bfa) !important;
    border: none !important; color: white !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(108,92,231,0.35) !important;
}

/* ── Filter pill buttons ── */
.filter-pill {
    display: inline-flex; align-items: center;
    background: #f8f9ff; border: 1.5px solid #eef0f7;
    color: #555; font-size: 0.8rem; font-weight: 500;
    padding: 0.4rem 0.9rem; border-radius: 50px; cursor: pointer;
    margin: 0.2rem; transition: all 0.2s;
}
.filter-pill:hover, .filter-pill.active {
    background: #6c5ce7; border-color: #6c5ce7; color: white;
}

/* ── Dashboard chart area ── */
.dashboard-card {
    background: white; border-radius: 16px; padding: 1.25rem;
    border: 1px solid #eef0f7; margin-bottom: 1rem;
}
.dashboard-card h4 { font-size: 0.95rem; font-weight: 700; color: #1a1d2e; margin: 0 0 1rem 0; }

/* ── Toast notification ── */
.toast {
    position: fixed; bottom: 2rem; right: 2rem;
    background: #1a1d2e; color: white; padding: 0.75rem 1.25rem;
    border-radius: 12px; font-size: 0.85rem; font-weight: 500;
    z-index: 9999; animation: fadeIn 0.3s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-banner h1 { font-size: 1.5rem; }
    .product-img-wrap { height: 140px; }
}
</style>
"""
