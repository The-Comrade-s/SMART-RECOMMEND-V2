"""SmartRecommend - Wishlist Page (Light Theme)"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text, log_activity

def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    c1,c2 = st.columns([4,1])
    with c1: st.markdown("""<div style="font-size:1.3rem;font-weight:800;color:#1e1b4b;">Wishlist 💝</div>""", unsafe_allow_html=True)
    with c2: st.button("Edit", key="edit_wl")

    ids = st.session_state.get("wishlist",[])
    if not ids and not products_df.empty:
        ids = products_df.head(4)["product_id"].tolist()
        st.session_state.wishlist = ids

    if not ids or products_df.empty:
        st.markdown("""<div style="text-align:center;padding:3rem;color:#9ca3af;">
          <div style="font-size:3rem;margin-bottom:1rem;">💝</div>
          <div style="font-weight:700;color:#1e1b4b;font-size:1.1rem;">Your wishlist is empty</div>
          <div style="font-size:0.82rem;margin-top:0.3rem;">Start adding products you love!</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Browse Products"): st.session_state.current_page = "Search"; st.rerun()
        return

    wish_prods = products_df[products_df["product_id"].isin(ids)]
    total = wish_prods["price"].sum()
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
         background:#f5f3ff;border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem;
         border:1.5px solid #ddd6fe;">
      <div style="font-size:0.82rem;color:#6b7280;">{len(wish_prods)} items · Total value:</div>
      <div style="font-weight:800;color:#7c3aed;font-size:1.1rem;">{format_naira(total)}</div>
    </div>
    """, unsafe_allow_html=True)

    for _,p in wish_prods.iterrows():
        icon = CATEGORY_ICONS.get(p.get("category",""),"🛍️")
        ci,cd,ca = st.columns([1,4,2])
        with ci:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border-radius:12px;
                 height:72px;width:72px;display:flex;align-items:center;justify-content:center;
                 font-size:2rem;border:1.5px solid #ddd6fe;">{icon}</div>
            """, unsafe_allow_html=True)
        with cd:
            st.markdown(f"""
            <div>
              <div style="font-weight:600;color:#1e1b4b;font-size:0.9rem;">{p.get('name','')}</div>
              <div style="font-size:0.73rem;color:#9ca3af;margin:2px 0;">{p.get('category','')} · ⭐ {p.get('rating',4.0):.1f}</div>
              <div style="font-weight:700;color:#7c3aed;font-size:0.95rem;">{format_naira(p.get('price',0))}</div>
            </div>
            """, unsafe_allow_html=True)
        with ca:
            a1,a2 = st.columns(2)
            with a1:
                if st.button("🛒 Buy", key=f"wb_{p['product_id']}", use_container_width=True):
                    log_activity(st.session_state.user_id, p["product_id"], "purchase"); st.toast("Added to cart! 🛒")
            with a2:
                if st.button("🗑️", key=f"wd_{p['product_id']}", use_container_width=True):
                    st.session_state.wishlist.remove(p["product_id"]); st.rerun()
        st.markdown("""<div class="sr-divider" style="margin:0.5rem 0;"></div>""", unsafe_allow_html=True)
