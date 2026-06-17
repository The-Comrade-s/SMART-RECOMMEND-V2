import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))

from database.db_setup import init_db, seed_products, seed_interactions
from utils.helpers import login_user, register_user
from utils.styles import SHARED_CSS

st.set_page_config(
    page_title="SmartRecommend",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource(show_spinner="Setting up SmartRecommend...")
def setup_database():
    """Run once per server lifecycle — survives reruns & page switches."""
    init_db()
    seed_products()
    seed_interactions()
    return True


# Init DB — cached so it only runs once even across multiple users
setup_database()

st.markdown(SHARED_CSS, unsafe_allow_html=True)


def auth_page():
    st.markdown("""
    <div style="min-height:100vh; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
         display:flex; align-items:center; justify-content:center; padding:2rem;">
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="background:white;border-radius:24px;padding:2.5rem;
             box-shadow:0 20px 60px rgba(0,0,0,0.15);">
            <div style="text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🛍️</div>
                <h2 style="font-size:1.9rem;font-weight:800;color:#1a1d2e;margin:0;">
                    Smart<span style="color:#6c5ce7;">Recommend</span>
                </h2>
                <p style="color:#888;font-size:0.88rem;margin:0.3rem 0 0 0;">
                    AI-Powered Product Recommender
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab = st.radio("", ["Login", "Register"], horizontal=True,
                       label_visibility="collapsed")

        if tab == "Login":
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("📧 Email Address", placeholder="you@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login →", use_container_width=True, type="primary")
                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        user = login_user(email.strip(), password)
                        if user:
                            st.session_state.user = user
                            st.session_state.page = "home"
                            st.success(f"Welcome back, {user['name'].split()[0]}! 👋")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

            st.markdown("""
            <div style="text-align:center;margin-top:1rem;color:#888;font-size:0.82rem;">
                Demo: <b>oluwavictor@gmail.com</b> / <b>demo123</b>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("reg_form"):
                name = st.text_input("👤 Full Name", placeholder="John Doe")
                email = st.text_input("📧 Email Address", placeholder="you@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Min. 6 characters")
                confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password")
                submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")
                if submitted:
                    if not all([name, email, password, confirm]):
                        st.error("Please fill in all fields.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        user, err = register_user(name.strip(), email.strip(), password)
                        if user:
                            st.session_state.user = user
                            st.session_state.page = "home"
                            st.success(f"Welcome to SmartRecommend, {name.split()[0]}! 🎉")
                            st.rerun()
                        else:
                            st.error(err)


def render_sidebar():
    user = st.session_state.get("user", {})
    current = st.session_state.get("page", "home")

    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <h2>Smart<span>Recommend</span></h2>
            <p>AI Product Recommender</p>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("home", "🏠", "Home"),
            ("search", "🔍", "Search Products"),
            ("categories", "📂", "Categories"),
            ("recommendations", "✨", "Recommendations"),
            ("wishlist", "❤️", "Wishlist"),
            ("profile", "👤", "Profile"),
            ("analytics", "📊", "Analytics Dashboard"),
        ]

        for page_key, icon, label in nav_items:
            is_active = current == page_key
            style = "background:#6c5ce7;color:white;" if is_active else "color:#8890b5;"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Top categories mini chart
        st.markdown("""
        <div style="padding:0 0.5rem;">
            <p style="font-size:0.8rem;font-weight:700;color:#8890b5;text-transform:uppercase;
               letter-spacing:0.05em;margin-bottom:0.75rem;">Top Categories</p>
        </div>
        """, unsafe_allow_html=True)

        cats = [("Electronics", 40, "#6c5ce7"), ("Fashion", 20, "#a78bfa"),
                ("Home & Kitchen", 15, "#10b981"), ("Books", 10, "#f59e0b"), ("Others", 15, "#64748b")]
        for cat, pct, color in cats:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:0.25rem 0.5rem;font-size:0.78rem;">
                <span style="color:#c8ccdf;">● {cat}</span>
                <span style="color:#8890b5;">{pct}%</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Upgrade card
        st.markdown("""
        <div class="upgrade-card">
            <div style="font-size:1.5rem;">👑</div>
            <h4>Upgrade Your Experience</h4>
            <p>Get personalized recommendations and exclusive offers</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪  Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def main():
    if "user" not in st.session_state:
        auth_page()
        return

    if "page" not in st.session_state:
        st.session_state.page = "home"

    render_sidebar()

    page = st.session_state.get("page", "home")

    if page == "home":
        from pages.home import render
        render()
    elif page == "search":
        from pages.search import render
        render()
    elif page == "categories":
        from pages.search import render
        render()
    elif page == "recommendations":
        from pages.recommendations import render
        render()
    elif page == "wishlist":
        from pages.wishlist import render
        render()
    elif page == "profile":
        from pages.profile import render
        render()
    elif page == "analytics":
        from pages.analytics import render
        render()
    elif page == "product":
        from pages.product_detail import render
        render()


if __name__ == "__main__":
    main()
