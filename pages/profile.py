"""SmartRecommend - Profile Page (Light Theme)"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text

def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    initials = "".join(w[0].upper() for w in st.session_state.user_name.split()[:2])

    st.markdown(f"""
    <div style="background:linear-gradient(120deg,#4c1d95,#7c3aed,#8b5cf6);border-radius:20px;
         padding:2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;">
      <div style="display:flex;align-items:center;gap:1.2rem;position:relative;z-index:1;">
        <div style="width:68px;height:68px;border-radius:50%;background:rgba(255,255,255,0.2);
             border:3px solid rgba(255,255,255,0.4);display:flex;align-items:center;
             justify-content:center;font-size:1.5rem;font-weight:800;color:white;">{initials}</div>
        <div>
          <div style="font-weight:800;color:white;font-size:1.3rem;">{st.session_state.user_name}</div>
          <div style="font-size:0.8rem;color:rgba(255,255,255,0.75);">{st.session_state.user_email}</div>
        </div>
        <div style="margin-left:auto;display:flex;gap:2rem;">
          {''.join(f'<div style="text-align:center;"><div style="font-weight:800;color:white;font-size:1.2rem;">{v}</div><div style="font-size:0.7rem;color:rgba(255,255,255,0.65);">{l}</div></div>'
          for v,l in [(st.session_state.orders_count,"Orders"),(len(st.session_state.wishlist)+st.session_state.wishlist_count,"Wishlist"),(st.session_state.products_viewed,"Viewed"),(st.session_state.ratings_given,"Ratings")])}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    cl, cr = st.columns([1,2])
    with cl:
        st.markdown("""<div class="sr-card">""", unsafe_allow_html=True)
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">Account</div>""", unsafe_allow_html=True)
        for icon,label in [("👤","Personal Information"),("💳","Payment Methods"),("📍","Address Book"),("📦","Order History")]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:0.65rem 0;border-bottom:1px solid #f3f4f6;cursor:pointer;">
              <div style="display:flex;align-items:center;gap:8px;font-size:0.83rem;color:#374151;">
                <span>{icon}</span><span>{label}</span>
              </div>
              <span style="color:#9ca3af;">›</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin:1rem 0 0.6rem;">Preferences</div>""", unsafe_allow_html=True)
        for icon,label in [("🏷️","Category Interests"),("🔔","Notification Settings"),("🔒","Privacy & Security")]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:0.65rem 0;border-bottom:1px solid #f3f4f6;cursor:pointer;">
              <div style="display:flex;align-items:center;gap:8px;font-size:0.83rem;color:#374151;">
                <span>{icon}</span><span>{label}</span>
              </div>
              <span style="color:#9ca3af;">›</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="prof_logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

    with cr:
        st.markdown("""<div class="sr-card" style="margin-bottom:1rem;">
          <div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">🧠 User Preference Intelligence</div>
          <div style="font-size:0.78rem;color:#6b7280;margin-bottom:0.8rem;">Built from your browsing, ratings and purchase history</div>
        """, unsafe_allow_html=True)
        for cat,pct,color in [("Technology",70,"#7c3aed"),("Gaming",20,"#ef4444"),("Books",10,"#f59e0b"),("Fashion",5,"#f43f5e")]:
            st.markdown(f"""
            <div style="margin:6px 0;">
              <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#374151;margin-bottom:3px;">
                <span>{cat}</span><span style="color:{color};font-weight:600;">{pct}%</span>
              </div>
              <div style="height:6px;background:#f3f4f6;border-radius:3px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:3px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin:0.8rem 0 0.6rem;">Recently Viewed</div>""", unsafe_allow_html=True)
        viewed_ids = st.session_state.get("viewed_products",[])
        show_prods = products_df[products_df["product_id"].isin(viewed_ids[:4])] if viewed_ids else products_df.head(4)
        if not show_prods.empty:
            vc = st.columns(4)
            for i,(_,p) in enumerate(show_prods.iterrows()):
                with vc[i]:
                    icon = CATEGORY_ICONS.get(p.get("category",""),"🛍️")
                    st.markdown(f"""
                    <div style="background:#f9fafb;border:1.5px solid #e5e7eb;border-radius:12px;
                         padding:0.7rem;text-align:center;">
                      <div style="font-size:1.6rem;">{icon}</div>
                      <div style="font-size:0.68rem;color:#374151;font-weight:500;margin-top:3px;">{truncate_text(str(p.get('name','')),18)}</div>
                      <div style="font-size:0.72rem;color:#7c3aed;font-weight:600;">{format_naira(p.get('price',0))}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">✏️ Edit Profile</div>""", unsafe_allow_html=True)
        new_name = st.text_input("Full Name", value=st.session_state.user_name, key="p_name")
        new_city = st.selectbox("City", ["Lagos","Abuja","Port Harcourt","Ibadan","Kano","Enugu"], key="p_city")
        new_cats = st.multiselect("Preferred Categories", list(CATEGORY_ICONS.keys())[:-1],
                                   default=st.session_state.preferred_categories, key="p_cats")
        if st.button("💾 Save Changes", use_container_width=True, key="save_prof"):
            st.session_state.user_name = new_name
            st.session_state.user_city = new_city
            st.session_state.preferred_categories = new_cats
            st.success("✅ Profile updated!"); st.rerun()
