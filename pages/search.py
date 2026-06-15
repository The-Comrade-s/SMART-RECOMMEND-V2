"""
SmartRecommend - Search & Product Detail (Light Theme)
"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text, log_activity

def render_detail(p, engine, products_df):
    if st.button("← Back to Search", key="back_btn"):
        st.session_state.current_product = None
        st.rerun()

    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    icon = CATEGORY_ICONS.get(p.get("category",""), "🛍️")
    col_img, col_info = st.columns([1, 2])

    with col_img:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border-radius:18px;
             height:280px;display:flex;align-items:center;justify-content:center;
             font-size:6rem;border:1.5px solid #ddd6fe;position:relative;">
          {icon}
          <div style="position:absolute;top:10px;right:10px;font-size:0.72rem;
               background:{'#d1fae5' if p.get('in_stock',True) else '#fee2e2'};
               color:{'#065f46' if p.get('in_stock',True) else '#991b1b'};
               border-radius:6px;padding:2px 8px;font-weight:600;">
            {'● In Stock' if p.get('in_stock',True) else '● Out of Stock'}
          </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🛒 Add to Cart", key="d_cart", use_container_width=True):
                log_activity(st.session_state.user_id, p["product_id"], "purchase")
                st.toast("Added to cart! 🛒")
        with b2:
            in_w = p["product_id"] in st.session_state.wishlist
            if st.button("💜 Saved" if in_w else "🤍 Wishlist", key="d_wish", use_container_width=True):
                if not in_w:
                    st.session_state.wishlist.append(p["product_id"])
                    log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                    st.toast("Added to wishlist! 💜")
                else:
                    st.session_state.wishlist.remove(p["product_id"])
                st.rerun()

        st.markdown("**Rate this product:**")
        rating_val = st.slider("", 1.0, 5.0, 4.0, 0.5, key="u_rating", label_visibility="collapsed")
        if st.button("⭐ Submit Rating", key="sub_rating", use_container_width=True):
            st.session_state.rated_products[p["product_id"]] = rating_val
            st.toast(f"Rating submitted: {rating_val}⭐")

    with col_info:
        st.markdown(f"""
        <div style="font-size:0.75rem;color:#9ca3af;margin-bottom:0.6rem;">
          Home › {p.get('category','')} › {truncate_text(str(p.get('name','')),30)}
        </div>
        <span class="badge badge-primary">{p.get('category','')}</span>
        <h2 style="font-weight:800;color:#1e1b4b;margin:0.6rem 0 0.3rem;line-height:1.2;font-size:1.5rem;">
          {p.get('name','')}
        </h2>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;">
          <span style="color:#f59e0b;">{'⭐'*int(p.get('rating',4))}</span>
          <span style="font-weight:700;color:#f59e0b;">{p.get('rating',4.0):.1f}</span>
          <span style="color:#9ca3af;font-size:0.8rem;">({int(p.get('num_reviews',0))} Reviews)</span>
        </div>
        <div style="font-size:2rem;font-weight:800;color:#7c3aed;margin-bottom:0.8rem;">
          {format_naira(p.get('price',0))}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#f9fafb;border-radius:12px;padding:1rem;margin:0.6rem 0;">
          <div style="font-size:0.72rem;color:#9ca3af;text-transform:uppercase;
               letter-spacing:0.07em;margin-bottom:0.4rem;font-weight:600;">Key Features</div>
          {"".join(f'<div style="font-size:0.82rem;color:#374151;margin-bottom:4px;">✓ {f.strip()}</div>' for f in str(p.get('description','')).split(',')[:4])}
        </div>
        """, unsafe_allow_html=True)

        if engine:
            try:
                exp = engine.explain_recommendation(p["product_id"],
                    user_id=st.session_state.user_id,
                    viewed_products=st.session_state.viewed_products,
                    liked_categories=st.session_state.preferred_categories)
                reasons = exp.get("reasons",[])
                tags    = exp.get("tags",[])
                conf    = exp.get("confidence",80)
                if reasons:
                    chips = " ".join(f'<span class="badge badge-primary">{t}</span>' for t in tags[:3])
                    st.markdown(f"""
                    <div style="background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:12px;padding:1rem;margin-top:0.8rem;">
                      <div style="font-size:0.82rem;font-weight:700;color:#065f46;margin-bottom:0.4rem;">
                        🤖 Why we recommend this?
                      </div>
                      <div style="font-size:0.78rem;color:#6b7280;margin-bottom:0.5rem;">
                        Based on your interest in similar products and users with similar preferences.
                      </div>
                      <div>{chips}</div>
                      <div style="font-size:0.75rem;color:#6b7280;margin-top:0.5rem;">
                        Confidence Score: <strong style="color:#10b981;">{conf}%</strong>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            except: pass

    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="section-title" style="margin-bottom:1rem;">You May Also Like</div>""", unsafe_allow_html=True)

    try:
        similar = engine.recommend_similar(p["product_id"], n=4) if engine else products_df.head(4)
    except:
        similar = products_df.head(4)

    sim_cols = st.columns(4)
    for i, (_, sp) in enumerate(similar.head(4).iterrows()):
        with sim_cols[i]:
            icon2 = CATEGORY_ICONS.get(sp.get("category",""), "🛍️")
            st.markdown(f"""
            <div class="product-card">
              <div style="height:110px;background:linear-gradient(135deg,#f5f3ff,#ede9fe);
                   display:flex;align-items:center;justify-content:center;font-size:2.5rem;">
                {icon2}
              </div>
              <div class="product-body">
                <div class="product-name">{truncate_text(str(sp.get('name','')),38)}</div>
                <div class="product-rating">⭐ {sp.get('rating',4.0):.1f}</div>
                <div class="product-price">{format_naira(sp.get('price',0))}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View", key=f"sim_{sp['product_id']}_{i}", use_container_width=True):
                st.session_state.current_product = sp.to_dict()
                log_activity(st.session_state.user_id, sp["product_id"], "view")
                st.rerun()


def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    engine      = st.session_state.get("engine")
    if products_df.empty:
        st.error("Data not loaded."); return

    if st.session_state.get("current_product"):
        render_detail(st.session_state.current_product, engine, products_df)
        return

    st.markdown("""<div style="font-size:1.3rem;font-weight:800;color:#1e1b4b;margin-bottom:1rem;">Search Products</div>""", unsafe_allow_html=True)

    s_col, sort_col = st.columns([3,1])
    with s_col:
        query = st.text_input("", placeholder="🔍  Search products...",
                               value=st.session_state.get("search_query",""),
                               key="s_input", label_visibility="collapsed")
    with sort_col:
        sort_opt = st.selectbox("", ["Most Popular","Highest Rated","Price ↑","Price ↓"],
                                 key="sort_s", label_visibility="collapsed")

    # Category pills
    st.markdown("<div style='margin:0.8rem 0 0.4rem;font-size:0.72rem;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;'>Categories</div>", unsafe_allow_html=True)
    all_cats = ["All"] + list(CATEGORY_ICONS.keys())[:-1]
    selected_cat = st.session_state.get("selected_category","All")
    cat_cols = st.columns(len(all_cats))
    for i, cat in enumerate(all_cats):
        with cat_cols[i]:
            icon = CATEGORY_ICONS.get(cat,"🛍️")
            active = selected_cat == cat
            bg = "#ede9fe" if active else "#ffffff"
            border = "#a78bfa" if active else "#e5e7eb"
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {border};border-radius:10px;
                 padding:0.5rem 0.2rem;text-align:center;">
              <div style="font-size:1.2rem;">{icon}</div>
              <div style="font-size:0.62rem;color:#4b5563;font-weight:500;">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(cat, key=f"sc_{cat}", use_container_width=True, label_visibility="collapsed"):
                st.session_state.selected_category = cat
                st.session_state.search_page = 0
                st.rerun()

    # Filters + Results
    f_col, r_col = st.columns([1, 3])
    with f_col:
        st.markdown("""<div class="sr-card"><div style="font-weight:700;color:#1e1b4b;margin-bottom:1rem;">🎛️ Filters</div></div>""", unsafe_allow_html=True)
        max_p = int(products_df["price"].max()) if not products_df.empty else 3000000
        price_range = st.slider("Price (₦)", 0, max_p, (0, max_p//2), key="p_filter", label_visibility="visible")
        min_r = st.select_slider("Min Rating", [1.0,2.0,3.0,4.0,4.5], value=1.0, key="r_filter",
                                  format_func=lambda x: f"{'⭐'*int(x)} & above")
        if st.button("Reset Filters", use_container_width=True, key="reset_f"):
            st.session_state.selected_category = "All"
            st.session_state.search_query = ""
            st.rerun()

    with r_col:
        filtered = products_df.copy()
        if selected_cat != "All":
            filtered = filtered[filtered["category"] == selected_cat]
        if query:
            mask = (filtered["name"].str.contains(query,case=False,na=False) |
                    filtered["description"].str.contains(query,case=False,na=False) |
                    filtered["category"].str.contains(query,case=False,na=False))
            filtered = filtered[mask]
        filtered = filtered[(filtered["price"]>=price_range[0]) &
                             (filtered["price"]<=price_range[1]) &
                             (filtered["rating"]>=min_r)]
        if sort_opt == "Most Popular":    filtered = filtered.sort_values("purchases", ascending=False)
        elif sort_opt == "Highest Rated": filtered = filtered.sort_values("rating", ascending=False)
        elif sort_opt == "Price ↑":       filtered = filtered.sort_values("price", ascending=True)
        elif sort_opt == "Price ↓":       filtered = filtered.sort_values("price", ascending=False)

        st.markdown(f"""<div style="font-weight:600;color:#6b7280;font-size:0.82rem;margin-bottom:0.8rem;">Products ({len(filtered):,})</div>""", unsafe_allow_html=True)

        PAGE = 12
        if "search_page" not in st.session_state: st.session_state.search_page = 0
        page_prods = filtered.iloc[st.session_state.search_page*PAGE:(st.session_state.search_page+1)*PAGE]

        g_cols = st.columns(3)
        for i, (_, p) in enumerate(page_prods.iterrows()):
            with g_cols[i%3]:
                icon = CATEGORY_ICONS.get(p.get("category",""),"🛍️")
                in_w = p["product_id"] in st.session_state.wishlist
                st.markdown(f"""
                <div class="product-card">
                  <div style="height:130px;background:linear-gradient(135deg,#f5f3ff,#ede9fe);
                       display:flex;align-items:center;justify-content:center;font-size:3rem;">
                    {icon}
                  </div>
                  <div class="product-body">
                    <div class="product-category">{p.get('category','')}</div>
                    <div class="product-name">{truncate_text(str(p.get('name','')),40)}</div>
                    <div class="product-rating">⭐ {p.get('rating',4.0):.1f} <span style="color:#9ca3af;font-size:0.7rem;">({int(p.get('num_reviews',0))})</span></div>
                    <div class="product-price">{format_naira(p.get('price',0))}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("View", key=f"sv_{p['product_id']}_{i}", use_container_width=True):
                        st.session_state.current_product = p.to_dict()
                        log_activity(st.session_state.user_id, p["product_id"], "view")
                        if p["product_id"] not in st.session_state.viewed_products:
                            st.session_state.viewed_products.append(p["product_id"])
                        st.rerun()
                with b2:
                    if st.button("💜" if in_w else "🤍", key=f"sw_{p['product_id']}_{i}", use_container_width=True):
                        if not in_w:
                            st.session_state.wishlist.append(p["product_id"])
                            log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                            st.toast("Added to wishlist! 💜")
                        else:
                            st.session_state.wishlist.remove(p["product_id"])
                        st.rerun()

        total_pages = max(1, (len(filtered)-1)//PAGE+1)
        if total_pages > 1:
            pc = st.columns(5)
            with pc[1]:
                if st.button("◀ Prev", use_container_width=True, disabled=st.session_state.search_page==0):
                    st.session_state.search_page -= 1; st.rerun()
            with pc[2]:
                st.markdown(f"<div style='text-align:center;color:#6b7280;padding:0.5rem 0;font-size:0.8rem;'>Page {st.session_state.search_page+1}/{total_pages}</div>", unsafe_allow_html=True)
            with pc[3]:
                if st.button("Next ▶", use_container_width=True, disabled=st.session_state.search_page>=total_pages-1):
                    st.session_state.search_page += 1; st.rerun()
