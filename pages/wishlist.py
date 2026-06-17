import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (get_wishlist, format_price, render_stars,
                           toggle_wishlist, track_activity)
from utils.styles import SHARED_CSS


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None

    col_title, col_edit = st.columns([4, 1])
    with col_title:
        st.markdown("""
        <h2 style="font-size:1.5rem;font-weight:800;color:#1a1d2e;margin-bottom:1.5rem;">❤️ Wishlist</h2>
        """, unsafe_allow_html=True)
    with col_edit:
        st.markdown("<br>", unsafe_allow_html=True)
        edit_mode = st.button("✏️ Edit", use_container_width=True)

    if not uid:
        st.info("Please login to view your wishlist.")
        return

    wishlist_df = get_wishlist(uid)

    if wishlist_df.empty:
        st.markdown("""
        <div style="text-align:center;padding:4rem;color:#888;">
            <div style="font-size:4rem;margin-bottom:1rem;">🤍</div>
            <h3 style="color:#1a1d2e;">Your wishlist is empty</h3>
            <p>Save products you love to your wishlist</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Products", type="primary"):
            st.session_state.page = "search"
            st.rerun()
        return

    st.markdown(f"""
    <p style="color:#888;font-size:0.85rem;margin-bottom:1.5rem;">
        {len(wishlist_df)} item{'s' if len(wishlist_df) != 1 else ''} saved
    </p>
    """, unsafe_allow_html=True)

    # Main + sidebar layout
    main_col, side_col = st.columns([2, 1])

    with main_col:
        for _, row in wishlist_df.iterrows():
            pid = int(row["product_id"])
            stars = render_stars(float(row["rating"]))

            discount_html = ""
            if row.get("original_price") and row["original_price"] > row["price"]:
                pct = int((row["original_price"] - row["price"]) / row["original_price"] * 100)
                discount_html = f'<span style="background:#fef2f2;color:#ef4444;font-size:0.72rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:4px;margin-left:0.4rem;">-{pct}%</span>'

            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:1rem;border:1px solid #eef0f7;
                 display:flex;gap:1rem;align-items:flex-start;margin-bottom:0.75rem;">
                <img src="{row['image_url']}"
                     onerror="this.src='https://via.placeholder.com/80x80'"
                     style="width:80px;height:80px;object-fit:cover;border-radius:12px;flex-shrink:0;" />
                <div style="flex:1;">
                    <p style="font-weight:700;font-size:0.95rem;color:#1a1d2e;margin:0 0 0.2rem 0;">{row['name']}</p>
                    <p style="font-size:0.78rem;color:#888;margin:0 0 0.3rem 0;">{row['category']}</p>
                    <div style="color:#f59e0b;font-size:0.82rem;">{stars}
                        <span style="color:#888;font-size:0.72rem;">({row['review_count']})</span>
                    </div>
                    <div style="display:flex;align-items:center;flex-wrap:wrap;margin-top:0.3rem;">
                        <span style="font-size:1.1rem;font-weight:800;color:#6c5ce7;">{format_price(row['price'])}</span>
                        {f'<span style="font-size:0.82rem;color:#aaa;text-decoration:line-through;margin-left:0.4rem;">{format_price(row["original_price"])}</span>' if row.get("original_price") and row["original_price"] > row["price"] else ''}
                        {discount_html}
                    </div>
                    <span style="background:#ecfdf5;color:#10b981;font-size:0.72rem;font-weight:700;
                          padding:0.15rem 0.5rem;border-radius:50px;margin-top:0.3rem;display:inline-block;">
                        {'✓ In Stock' if row.get('in_stock',1) else '✗ Out of Stock'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn1, btn2, btn3 = st.columns([2, 1, 1])
            with btn1:
                if st.button("View Product", key=f"wv_{pid}", use_container_width=True, type="primary"):
                    track_activity(uid, pid, "view")
                    st.session_state.selected_product = pid
                    st.session_state.page = "product"
                    st.rerun()
            with btn2:
                if st.button("🛒 Buy Now", key=f"wb_{pid}", use_container_width=True):
                    track_activity(uid, pid, "purchase")
                    st.success("Order placed! 🎉")
            with btn3:
                if st.button("🗑️ Remove", key=f"wr_{pid}", use_container_width=True):
                    toggle_wishlist(uid, pid)
                    st.rerun()

    with side_col:
        # Order summary
        total = wishlist_df["price"].sum()
        savings = 0
        for _, row in wishlist_df.iterrows():
            if row.get("original_price") and row["original_price"] > row["price"]:
                savings += row["original_price"] - row["price"]

        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;position:sticky;top:80px;">
            <h4 style="font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">Order Summary</h4>
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #f1f5f9;">
                <span style="color:#555;font-size:0.88rem;">Subtotal ({len(wishlist_df)} items)</span>
                <span style="font-weight:600;font-size:0.88rem;">{format_price(total)}</span>
            </div>
            {'<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #f1f5f9;"><span style="color:#10b981;font-size:0.88rem;">You Save</span><span style="font-weight:600;color:#10b981;font-size:0.88rem;">-' + format_price(savings) + '</span></div>' if savings > 0 else ''}
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #f1f5f9;">
                <span style="color:#555;font-size:0.88rem;">Delivery</span>
                <span style="font-weight:600;color:#10b981;font-size:0.88rem;">Free</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:0.75rem 0;margin-top:0.25rem;">
                <span style="font-weight:700;color:#1a1d2e;">Total</span>
                <span style="font-weight:800;color:#6c5ce7;font-size:1.1rem;">{format_price(total)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🛒 Checkout All Items", use_container_width=True, type="primary"):
            for _, row in wishlist_df.iterrows():
                track_activity(uid, int(row["product_id"]), "purchase")
            st.success(f"Order of {len(wishlist_df)} items placed! 🎉")
