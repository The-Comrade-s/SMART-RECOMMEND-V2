import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (get_products, format_price, render_stars,
                           track_activity, toggle_wishlist, is_in_wishlist, get_categories)
from utils.styles import SHARED_CSS


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None

    st.markdown("""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
        <h2 style="font-size:1.5rem;font-weight:800;color:#1a1d2e;margin:0;">🔍 Search Products</h2>
    </div>
    """, unsafe_allow_html=True)

    # Search bar
    col_s, col_f = st.columns([5, 1])
    with col_s:
        search_q = st.text_input("", placeholder="🔍  Search for products...",
                                  label_visibility="collapsed",
                                  value=st.session_state.get("search_query", ""),
                                  key="search_input")
    with col_f:
        st.button("⚙️ Filters", use_container_width=True)

    # Category pills
    categories = get_categories()
    selected_cat = st.session_state.get("search_category", "All")

    st.markdown("<p style='font-weight:700;color:#1a1d2e;margin:1.2rem 0 0.5rem 0;'>Categories</p>",
                unsafe_allow_html=True)

    cat_icons = {"All": "⊞", "Smartphones": "📱", "Laptops": "💻",
                 "Electronics": "🎧", "Fashion": "👗", "Home & Kitchen": "🏠",
                 "Books": "📚", "Gaming": "🎮"}

    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            icon = cat_icons.get(cat, "📦")
            is_active = selected_cat == cat
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{icon}\n{cat}", key=f"scat_{cat}", use_container_width=True, type=btn_style):
                st.session_state.search_category = cat
                selected_cat = cat
                st.rerun()

    # Filters
    st.markdown("<p style='font-weight:700;color:#1a1d2e;margin:1.2rem 0 0.5rem 0;'>Filters</p>",
                unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        price_range = st.slider("Price Range (₦)", 0, 2000000, (0, 2000000),
                                step=10000, format="₦%d")
    with f2:
        min_rating = st.select_slider("Min Rating", options=[0, 2.0, 3.0, 4.0, 4.5],
                                       value=0, format_func=lambda x: f"⭐ {x}+" if x else "Any")
    with f3:
        sort_by = st.selectbox("Sort By", ["Most Popular", "Highest Rated", "Price: Low to High",
                                            "Price: High to Low", "Newest First"],
                               label_visibility="visible")

    sort_map = {
        "Most Popular": "popular", "Highest Rated": "rating",
        "Price: Low to High": "price_low", "Price: High to Low": "price_high",
        "Newest First": "newest"
    }

    # Fetch products
    cat_filter = selected_cat if selected_cat != "All" else None
    products_df = get_products(
        category=cat_filter,
        search=search_q if search_q else None,
        min_price=price_range[0],
        max_price=price_range[1],
        min_rating=min_rating if min_rating else None,
        sort_by=sort_map.get(sort_by, "popular"),
        limit=60
    )

    # Results header
    st.markdown(f"""
    <div class="section-header" style="margin-top:1rem;">
        <h3 class="section-title">Products ({len(products_df)})</h3>
    </div>
    """, unsafe_allow_html=True)

    if products_df.empty:
        st.markdown("""
        <div style="text-align:center;padding:4rem;color:#888;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
            <h3>No products found</h3>
            <p>Try adjusting your search or filters</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Product list — 2 cols on mobile friendly, 3 on desktop
    for row_start in range(0, min(len(products_df), 60), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx >= len(products_df):
                break
            row = products_df.iloc[idx]
            pid = int(row["product_id"])
            in_wish = is_in_wishlist(uid, pid) if uid else False
            wish_icon = "❤️" if in_wish else "🤍"
            stars = render_stars(float(row["rating"]))
            disc = ""
            if row["original_price"] and row["original_price"] > row["price"]:
                pct = int((row["original_price"] - row["price"]) / row["original_price"] * 100)
                disc = f'<span style="background:#fef2f2;color:#ef4444;font-size:0.7rem;font-weight:700;padding:0.1rem 0.4rem;border-radius:4px;margin-left:0.4rem;">-{pct}%</span>'

            with col:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap" style="height:160px;">
                        <img src="{row['image_url']}"
                             onerror="this.src='https://via.placeholder.com/300x200?text={row['name'].replace(' ','+')}'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name" title="{row['name']}">{row['name']}</p>
                        <p class="product-cat">{row['category']}</p>
                        <div class="product-stars">{stars}
                            <span style="color:#888;font-size:0.72rem;">({row['review_count']})</span>
                        </div>
                        <div style="display:flex;align-items:center;flex-wrap:wrap;">
                            <span class="product-price">{format_price(row['price'])}</span>
                            {f'<span class="product-orig-price">{format_price(row["original_price"])}</span>' if row['original_price'] and row['original_price'] > row['price'] else ''}
                            {disc}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn1, btn2 = st.columns([3, 1])
                with btn1:
                    if st.button("View Product", key=f"sv_{pid}_{idx}", use_container_width=True, type="primary"):
                        if uid: track_activity(uid, pid, "view")
                        st.session_state.selected_product = pid
                        st.session_state.page = "product"
                        st.rerun()
                with btn2:
                    if st.button(wish_icon, key=f"sw_{pid}_{idx}", use_container_width=True):
                        if uid:
                            toggle_wishlist(uid, pid)
                            st.rerun()
                        else:
                            st.warning("Login to save")
