import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import get_user_stats, format_price
from utils.styles import SHARED_CSS


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    if not user:
        st.warning("Please login to view your profile.")
        return

    uid = user.get("user_id")
    name = user.get("name", "User")
    email = user.get("email", "")
    stats = get_user_stats(uid)

    # Profile header card
    st.markdown(f"""
    <div class="profile-header">
        <img src="https://ui-avatars.com/api/?name={name.replace(' ','+')}&background=6c5ce7&color=fff&size=120"
             class="profile-avatar" />
        <h2 class="profile-name">{name}</h2>
        <p class="profile-email">{email}</p>
        <div style="display:flex;justify-content:center;gap:2rem;margin-top:1.5rem;flex-wrap:wrap;">
            <div style="text-align:center;">
                <div style="font-size:1.4rem;font-weight:800;">{stats['orders']}</div>
                <div style="font-size:0.78rem;opacity:0.85;">Orders</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.4rem;font-weight:800;">{stats['wishlist']}</div>
                <div style="font-size:0.78rem;opacity:0.85;">Wishlist</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.4rem;font-weight:800;">{stats['viewed']}</div>
                <div style="font-size:0.78rem;opacity:0.85;">Viewed</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.4rem;font-weight:800;">{stats['ratings']}</div>
                <div style="font-size:0.78rem;opacity:0.85;">Ratings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        # Account section
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;margin-bottom:1rem;">
            <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">Account</h4>
        </div>
        """, unsafe_allow_html=True)

        account_items = [
            ("👤", "Personal Information", "Update your name and email"),
            ("💳", "Payment Methods", "Manage your payment options"),
            ("📍", "Address Book", "Manage delivery addresses"),
            ("📦", "Order History", "View your past orders"),
        ]
        for icon, title, subtitle in account_items:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:0.9rem 1.25rem;
                 border:1px solid #eef0f7;margin-bottom:0.5rem;display:flex;
                 align-items:center;justify-content:space-between;cursor:pointer;
                 transition:all 0.2s;" onmouseover="this.style.borderColor='#6c5ce7'"
                 onmouseout="this.style.borderColor='#eef0f7'">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <div>
                        <div style="font-weight:600;font-size:0.88rem;color:#1a1d2e;">{title}</div>
                        <div style="font-size:0.75rem;color:#888;">{subtitle}</div>
                    </div>
                </div>
                <span style="color:#888;">›</span>
            </div>
            """, unsafe_allow_html=True)

        # Preferences section
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;margin-top:1rem;">
            <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">Preferences</h4>
        </div>
        """, unsafe_allow_html=True)

        pref_items = [
            ("🏷️", "Category Interests"),
            ("🔔", "Notification Settings"),
            ("🔒", "Privacy & Security"),
        ]
        for icon, title in pref_items:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:0.9rem 1.25rem;
                 border:1px solid #eef0f7;margin-bottom:0.5rem;display:flex;
                 align-items:center;justify-content:space-between;cursor:pointer;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <span style="font-weight:600;font-size:0.88rem;color:#1a1d2e;">{title}</span>
                </div>
                <span style="color:#888;">›</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    with right_col:
        # User preferences / category breakdown
        try:
            if "rec_engine" not in st.session_state:
                from models.recommendation_engine import RecommendationEngine
                st.session_state.rec_engine = RecommendationEngine()
            prefs = st.session_state.rec_engine.get_user_preferences(uid)
        except Exception:
            prefs = {}

        if not prefs:
            prefs = {"Electronics": 40, "Smartphones": 25, "Laptops": 20, "Fashion": 10, "Books": 5}

        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;margin-bottom:1rem;">
            <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">User Preferences</h4>
        </div>
        """, unsafe_allow_html=True)

        colors = ["#6c5ce7", "#a78bfa", "#10b981", "#f59e0b", "#ef4444", "#64748b"]
        for i, (cat, pct) in enumerate(list(prefs.items())[:6]):
            color = colors[i % len(colors)]
            st.markdown(f"""
            <div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;
                     color:#555;margin-bottom:0.3rem;">
                    <span style="font-weight:500;">{cat}</span>
                    <span style="font-weight:700;color:{color};">{pct}%</span>
                </div>
                <div style="height:8px;background:#f1f5f9;border-radius:4px;">
                    <div style="height:8px;width:{min(pct,100)}%;background:{color};border-radius:4px;
                         transition:width 0.5s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Edit profile form
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;margin-top:1rem;">
            <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">Edit Profile</h4>
        </div>
        """, unsafe_allow_html=True)

        with st.form("edit_profile"):
            new_name = st.text_input("Full Name", value=name)
            new_email = st.text_input("Email", value=email)
            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                from database.db_setup import get_connection
                conn = get_connection()
                c = conn.cursor()
                c.execute("UPDATE users SET name=?, email=? WHERE user_id=?",
                          (new_name, new_email, uid))
                conn.commit()
                conn.close()
                st.session_state.user["name"] = new_name
                st.session_state.user["email"] = new_email
                st.success("Profile updated! ✓")
                st.rerun()
