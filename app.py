"""
SmartRecommend - AI Product Recommendation Engine
"""
import streamlit as st
import pandas as pd
import os
import sys
import warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from utils.helpers import init_session

st.set_page_config(
    page_title="SmartRecommend",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary: #7c3aed;
  --primary-light: #ede9fe;
  --primary-mid: #8b5cf6;
  --accent: #f59e0b;
  --success: #10b981;
  --danger: #ef4444;
  --bg: #f8f7ff;
  --bg-white: #ffffff;
  --sidebar-bg: #1e1b4b;
  --sidebar-active: #4c1d95;
  --text-dark: #1e1b4b;
  --text-mid: #4b5563;
  --text-light: #9ca3af;
  --border: #e5e7eb;
  --shadow: 0 2px 12px rgba(124,58,237,0.08);
  --shadow-md: 0 4px 20px rgba(124,58,237,0.12);
}

/* ── Reset & base ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
}
.stApp {
  background: var(--bg) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: none !important;
  width: 240px !important;
}
section[data-testid="stSidebar"] > div {
  background: var(--sidebar-bg) !important;
  padding: 0 !important;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--primary) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 0.5rem 1.2rem !important;
  transition: all 0.2s !important;
  box-shadow: 0 2px 8px rgba(124,58,237,0.25) !important;
}
.stButton > button:hover {
  background: #6d28d9 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(124,58,237,0.35) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
  background: var(--bg-white) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-dark) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.88rem !important;
  padding: 0.6rem 1rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
}
.stSelectbox > div > div {
  background: var(--bg-white) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-dark) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-white) !important;
  border-radius: 12px !important;
  border: 1.5px solid var(--border) !important;
  padding: 4px !important;
  gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  color: var(--text-mid) !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
  background: var(--primary) !important;
  color: white !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
  background: var(--bg-white) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.2rem !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="metric-container"] label {
  color: var(--text-light) !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
  color: var(--text-dark) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 1.8rem !important;
  font-weight: 700 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--bg-white) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-dark) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 4px; }

/* ══════════════════════════════════════
   REUSABLE COMPONENTS
══════════════════════════════════════ */

/* Card */
.sr-card {
  background: var(--bg-white);
  border: 1.5px solid var(--border);
  border-radius: 18px;
  padding: 1.4rem;
  box-shadow: var(--shadow);
  transition: all 0.22s ease;
}
.sr-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: #c4b5fd;
}

/* Product card */
.product-card {
  background: var(--bg-white);
  border: 1.5px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.22s ease;
  height: 100%;
  box-shadow: var(--shadow);
}
.product-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
  border-color: #c4b5fd;
}
.product-body { padding: 0.9rem; }
.product-name {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-dark);
  margin-bottom: 2px;
  line-height: 1.35;
}
.product-category {
  font-size: 0.7rem;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 5px;
}
.product-price {
  font-weight: 700;
  font-size: 1rem;
  color: var(--primary);
  margin-top: 4px;
}
.product-rating { font-size: 0.78rem; color: var(--accent); }

/* Hero banner */
.hero-banner {
  background: linear-gradient(120deg, #f5f3ff 0%, #ede9fe 60%, #faf5ff 100%);
  border: 1.5px solid #ddd6fe;
  border-radius: 20px;
  padding: 2.2rem 2.5rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

/* Section heading */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 1.5rem 0 1rem;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-dark);
}
.view-all-link {
  font-size: 0.8rem;
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
}

/* Badge */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin: 2px;
}
.badge-primary { background: var(--primary-light); color: var(--primary); }
.badge-success { background: #d1fae5; color: #065f46; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-danger  { background: #fee2e2; color: #991b1b; }

/* Sidebar brand */
.brand-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 1.4rem 1.2rem 1.2rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.brand-name {
  font-family: 'Inter', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: white;
  letter-spacing: -0.02em;
}
.brand-name span { color: #a78bfa; }
.brand-tag {
  font-size: 0.62rem;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Sidebar nav item */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  color: rgba(255,255,255,0.65);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  margin: 1px 8px;
}
.nav-item:hover { background: rgba(255,255,255,0.07); color: white; }
.nav-item.active {
  background: var(--primary);
  color: white;
  font-weight: 600;
}

/* User card in sidebar */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 1rem 1.2rem;
  border-top: 1px solid rgba(255,255,255,0.08);
  margin-top: auto;
}

/* Category pill */
.cat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: var(--bg-white);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 0.8rem 0.5rem;
  cursor: pointer;
  transition: all 0.18s;
  text-align: center;
}
.cat-pill:hover, .cat-pill.active {
  background: var(--primary-light);
  border-color: #a78bfa;
}
.cat-icon { font-size: 1.5rem; }
.cat-label { font-size: 0.68rem; color: var(--text-mid); font-weight: 500; }

/* Divider */
.sr-divider {
  height: 1px;
  background: var(--border);
  margin: 1rem 0;
}

/* Confidence bar */
.conf-bar { height: 7px; border-radius: 4px; background: #f3f4f6; margin: 5px 0; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--primary), var(--primary-mid)); }

/* Pref bar */
.pref-bar-wrap { margin: 5px 0; }
.pref-label { display: flex; justify-content: space-between; font-size: 0.75rem; color: rgba(255,255,255,0.55); margin-bottom: 3px; }
.pref-bar { height: 5px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
.pref-fill { height: 100%; border-radius: 3px; }

/* Rank badge */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px; height: 26px;
  border-radius: 7px;
  background: var(--primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
}

/* In/out stock */
.in-stock  { color: var(--success); font-size: 0.73rem; font-weight: 600; }
.out-stock { color: var(--danger);  font-size: 0.73rem; font-weight: 600; }

/* Gauge */
.gauge-value {
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--primary);
}

/* Reason chip */
.reason-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--primary-light);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.73rem;
  color: var(--primary);
  font-weight: 500;
  margin: 2px;
}

/* Top search bar area */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-white);
  border-bottom: 1.5px solid var(--border);
  padding: 0.75rem 1.5rem;
  margin-bottom: 1.2rem;
  border-radius: 0 0 16px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* User avatar */
.avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-mid));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .hero-banner { padding: 1.3rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Session init ──────────────────────────────────────────────────────────────
init_session()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    import pages.auth as auth_page
    auth_page.render()
    st.stop()

# ── Data setup ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def setup_and_load():
    data_dir   = os.path.join(ROOT, "data")
    db_dir     = os.path.join(ROOT, "database")
    model_path = os.path.join(ROOT, "models", "recommendation_model.pkl")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(db_dir,   exist_ok=True)
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)

    products_csv   = os.path.join(data_dir, "products.csv")
    ratings_csv    = os.path.join(data_dir, "ratings.csv")
    users_csv      = os.path.join(data_dir, "users.csv")
    activities_csv = os.path.join(data_dir, "activities.csv")
    db_path        = os.path.join(db_dir, "database.db")

    if not os.path.exists(ratings_csv) or not os.path.exists(products_csv):
        from utils.data_generator import generate_all_data
        generate_all_data(data_dir, db_path)

    if not os.path.exists(model_path):
        from utils.recommendation_engine import build_and_save_model
        build_and_save_model(products_csv, ratings_csv, model_path)

    from utils.recommendation_engine import HybridRecommender
    engine        = HybridRecommender.load(model_path)
    products_df   = pd.read_csv(products_csv)
    users_df      = pd.read_csv(users_csv)
    activities_df = pd.read_csv(activities_csv)
    return engine, products_df, users_df, activities_df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    initials = "".join(w[0].upper() for w in st.session_state.user_name.split()[:2])
    st.markdown(f"""
    <div class="brand-wrap">
      <div style="font-size:1.6rem;">🛍️</div>
      <div>
        <div class="brand-name">Smart<span>Recommend</span></div>
        <div class="brand-tag">AI Product Recommender</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Nav
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    nav_items = [
        ("🏠", "Home"),
        ("🔍", "Search Products"),
        ("⭐", "Recommendations"),
        ("💝", "Wishlist"),
        ("👤", "Profile"),
        ("📊", "Analytics Dashboard"),
        ("⚙️", "Admin Panel"),
    ]

    page_map = {
        "Home": "Home",
        "Search Products": "Search",
        "Recommendations": "Recommendations",
        "Wishlist": "Wishlist",
        "Profile": "Profile",
        "Analytics Dashboard": "Analytics",
        "Admin Panel": "Admin",
    }

    for icon, label in nav_items:
        page_key = page_map[label]
        is_active = st.session_state.current_page == page_key
        bg = "background:rgba(124,58,237,0.85);color:white;" if is_active else "color:rgba(255,255,255,0.65);"
        st.markdown(f"""
        <div class="nav-item {'active' if is_active else ''}" style="{bg}">
          <span style="font-size:1rem;">{icon}</span>
          <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_key}", use_container_width=True,
                     label_visibility="collapsed"):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="padding:0 8px;">
    <div style="font-size:0.68rem;color:rgba(255,255,255,0.35);text-transform:uppercase;
         letter-spacing:0.08em;margin-bottom:0.6rem;padding-left:4px;">Top Categories</div>
    """, unsafe_allow_html=True)

    for cat, pct, color in [("Electronics",40,"#8b5cf6"),("Fashion",20,"#f43f5e"),
                              ("Home & Kitchen",15,"#10b981"),("Books",10,"#f59e0b"),
                              ("Others",15,"#0ea5e9")]:
        st.markdown(f"""
        <div class="pref-bar-wrap">
          <div class="pref-label"><span>{cat}</span><span style="color:{color};font-weight:600;">{pct}%</span></div>
          <div class="pref-bar"><div class="pref-fill" style="width:{pct}%;background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Upgrade card
    st.markdown("""
    <div style="margin:0 8px;background:linear-gradient(135deg,#4c1d95,#7c3aed);
         border-radius:14px;padding:1rem;text-align:center;">
      <div style="font-size:1.1rem;margin-bottom:0.3rem;">👑</div>
      <div style="font-weight:700;color:white;font-size:0.82rem;margin-bottom:0.2rem;">Upgrade Your Experience</div>
      <div style="font-size:0.7rem;color:rgba(255,255,255,0.65);margin-bottom:0.7rem;">
        Get personalized recommendations and exclusive offers
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Upgrade Now", key="upgrade_btn", use_container_width=True):
        st.toast("Coming soon! 🚀")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # User + Logout at bottom
    st.markdown(f"""
    <div style="border-top:1px solid rgba(255,255,255,0.08);padding:0.8rem 1.2rem;
         display:flex;align-items:center;gap:10px;">
      <div class="avatar">{initials}</div>
      <div style="flex:1;min-width:0;">
        <div style="font-weight:600;color:white;font-size:0.82rem;
             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          {st.session_state.user_name}
        </div>
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.45);">
          {st.session_state.user_city}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ── Top bar (search + user greeting) ─────────────────────────────────────────
col_search, col_user = st.columns([3, 1])
with col_search:
    query = st.text_input("", placeholder="🔍  Search for products, brands and more...",
                           key="global_search", label_visibility="collapsed")
    if query:
        st.session_state.search_query = query
        st.session_state.current_page = "Search"
        st.rerun()

with col_user:
    first = st.session_state.user_name.split()[0]
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;padding:0.3rem 0;">
      <div style="position:relative;cursor:pointer;">
        <span style="font-size:1.3rem;">🔔</span>
        <span style="position:absolute;top:-4px;right:-4px;background:#ef4444;color:white;
              border-radius:50%;width:16px;height:16px;font-size:0.6rem;font-weight:700;
              display:flex;align-items:center;justify-content:center;">3</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <div class="avatar" style="width:34px;height:34px;font-size:0.8rem;">
          {st.session_state.user_name[0].upper()}
        </div>
        <div>
          <div style="font-size:0.7rem;color:var(--text-light);">Good Evening,</div>
          <div style="font-size:0.85rem;font-weight:700;color:var(--text-dark);">{first} ▾</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
try:
    need_setup = (
        not os.path.exists(os.path.join(ROOT, "data", "ratings.csv")) or
        not os.path.exists(os.path.join(ROOT, "models", "recommendation_model.pkl"))
    )
    if need_setup:
        with st.status("🚀 First-time setup — this takes ~60 seconds and never repeats...",
                       expanded=True) as status:
            st.write("📦 Generating product catalog (1,500+ products)...")
            st.write("👥 Creating user profiles (5,000 users)...")
            st.write("📊 Simulating interactions (50,000 events)...")
            st.write("🤖 Training hybrid recommendation model...")
            engine, products_df, users_df, activities_df = setup_and_load()
            status.update(label="✅ Setup complete!", state="complete")
    else:
        engine, products_df, users_df, activities_df = setup_and_load()
except Exception as e:
    st.error(f"Setup error: {e}")
    st.stop()

st.session_state["engine"]        = engine
st.session_state["products_df"]   = products_df
st.session_state["users_df"]      = users_df
st.session_state["activities_df"] = activities_df

# ── Route ─────────────────────────────────────────────────────────────────────
page = st.session_state.current_page
if   page == "Home":            import pages.home as p;            p.render()
elif page == "Search":          import pages.search as p;          p.render()
elif page == "Recommendations": import pages.recommendations as p; p.render()
elif page == "Wishlist":        import pages.wishlist as p;         p.render()
elif page == "Profile":         import pages.profile as p;         p.render()
elif page == "Analytics":       import pages.analytics as p;       p.render()
elif page == "Admin":           import pages.admin as p;           p.render()
