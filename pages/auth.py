"""
SmartRecommend - Auth Page (Light Theme)
"""
import streamlit as st
import sqlite3, hashlib, os, re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "database.db")

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_auth_table():
    try:
        conn = get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS auth_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, city TEXT, age INTEGER,
            preferred_categories TEXT, date_joined TEXT)""")
        conn.commit(); conn.close()
    except: pass

def register_user(full_name, email, password, city, age):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO auth_users (full_name,email,password_hash,city,age,date_joined,preferred_categories) VALUES (?,?,?,?,?,?,?)",
            (full_name, email, hash_password(password), city, age, datetime.now().isoformat(), "[]"))
        conn.commit(); conn.close()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Email already registered. Please login."
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    try:
        conn = get_conn()
        cur = conn.execute("SELECT * FROM auth_users WHERE email=? AND password_hash=?",
                           (email, hash_password(password)))
        user = cur.fetchone(); conn.close()
        if user:
            cols = ["user_id","full_name","email","password_hash","city","age","preferred_categories","date_joined"]
            return True, dict(zip(cols, user))
        return False, None
    except: return False, None

def valid_email(e): return re.match(r"[^@]+@[^@]+\.[^@]+", e)

def render():
    init_auth_table()

    st.markdown("""
    <style>
    .stApp { background: #f5f3ff !important; }
    .auth-center {
        max-width: 460px;
        margin: 1.5rem auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem;">
      <div style="font-size:3rem;">🛍️</div>
      <div style="font-size:1.8rem;font-weight:800;color:#1e1b4b;letter-spacing:-0.02em;">
        Smart<span style="color:#7c3aed;">Recommend</span>
      </div>
      <div style="font-size:0.72rem;color:#9ca3af;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;">
        AI Product Recommender
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐  Login", "✨  Create Account"])

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    with tab_login:
        st.markdown("""
        <div style="margin:1rem 0 1.5rem;">
          <div style="font-weight:700;font-size:1.2rem;color:#1e1b4b;">Welcome back 👋</div>
          <div style="font-size:0.82rem;color:#6b7280;margin-top:2px;">
            Login to get your personalized recommendations
          </div>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email Address", placeholder="yourname@email.com", key="l_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="l_pass")
        st.checkbox("Remember me", key="remember")

        if st.button("Login", use_container_width=True, key="login_btn"):
            if not email or not password:
                st.error("Please fill in all fields.")
            elif not valid_email(email):
                st.error("Enter a valid email address.")
            else:
                ok, user = login_user(email, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = user["user_id"]
                    st.session_state.user_name  = user["full_name"]
                    st.session_state.user_email = user["email"]
                    st.session_state.user_city  = user.get("city","Lagos")
                    st.session_state.current_page = "Home"
                    st.success(f"Welcome back, {user['full_name'].split()[0]}! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.markdown("""<div style="text-align:center;color:#9ca3af;font-size:0.78rem;margin:0.8rem 0;">— or —</div>""", unsafe_allow_html=True)

        if st.button("👤  Continue as Guest", use_container_width=True, key="guest_btn"):
            st.session_state.logged_in    = True
            st.session_state.user_id      = 1
            st.session_state.user_name    = "Guest User"
            st.session_state.user_email   = "guest@smartrecommend.com"
            st.session_state.user_city    = "Lagos"
            st.session_state.current_page = "Home"
            st.rerun()

    # ── SIGNUP ────────────────────────────────────────────────────────────────
    with tab_signup:
        st.markdown("""
        <div style="margin:1rem 0 1.5rem;">
          <div style="font-weight:700;font-size:1.2rem;color:#1e1b4b;">Create your account ✨</div>
          <div style="font-size:0.82rem;color:#6b7280;margin-top:2px;">
            Join thousands of Nigerians getting smart recommendations
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: fn = st.text_input("First Name", placeholder="e.g. Emeka", key="s_fn")
        with c2: ln = st.text_input("Last Name",  placeholder="e.g. Okafor", key="s_ln")

        s_email = st.text_input("Email Address", placeholder="yourname@gmail.com", key="s_email")

        c3, c4 = st.columns(2)
        with c3: s_pass = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="s_pass")
        with c4: s_conf = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="s_conf")

        c5, c6 = st.columns(2)
        with c5:
            s_city = st.selectbox("City", ["Lagos","Abuja","Port Harcourt","Ibadan",
                                            "Kano","Enugu","Benin City","Warri"], key="s_city")
        with c6:
            s_age = st.number_input("Age", min_value=16, max_value=80, value=25, key="s_age")

        s_cats = st.multiselect("Preferred Categories (optional)",
            ["Smartphones","Laptops","Electronics","Fashion","Home & Kitchen","Books","Gaming"], key="s_cats")

        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="s_agree")

        if s_pass:
            length = len(s_pass)
            if length < 6:
                st.markdown('<div style="color:#ef4444;font-size:0.75rem;">⚠️ Too short (min 6 characters)</div>', unsafe_allow_html=True)
            elif length < 10:
                st.markdown('<div style="color:#f59e0b;font-size:0.75rem;">🔒 Strength: Medium</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#10b981;font-size:0.75rem;">✅ Strength: Strong</div>', unsafe_allow_html=True)

        if st.button("Create Account", use_container_width=True, key="signup_btn"):
            errors = []
            if not fn or not ln:       errors.append("Enter your full name.")
            if not valid_email(s_email): errors.append("Enter a valid email.")
            if len(s_pass) < 6:        errors.append("Password must be at least 6 characters.")
            if s_pass != s_conf:        errors.append("Passwords do not match.")
            if not agree:               errors.append("Please agree to the Terms of Service.")

            if errors:
                for e in errors: st.error(e)
            else:
                ok, msg = register_user(f"{fn} {ln}", s_email, s_pass, s_city, s_age)
                if ok:
                    _, user = login_user(s_email, s_pass)
                    if user:
                        st.session_state.logged_in    = True
                        st.session_state.user_id      = user["user_id"]
                        st.session_state.user_name    = f"{fn} {ln}"
                        st.session_state.user_email   = s_email
                        st.session_state.user_city    = s_city
                        st.session_state.preferred_categories = s_cats
                        st.session_state.current_page = "Home"
                        st.success(f"Welcome to SmartRecommend, {fn}! 🎉")
                        st.balloons()
                        st.rerun()
                else:
                    st.error(msg)

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;font-size:0.72rem;color:#9ca3af;">
      🔒 Your data is secure · SmartRecommend © 2025 · Made in Nigeria 🇳🇬
    </div>
    """, unsafe_allow_html=True)
