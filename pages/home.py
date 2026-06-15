"""
SmartRecommend - Home Page (Light Theme)
"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text, log_activity


def product_card(p, key_prefix="", rank=None):
    icon = CATEGORY_ICONS.get(p.get("category", ""), "🛍️")
    in_wish = p["product_id"] in st.session_state.get("wishlist", [])
    rank_html = f'<div class="rank-badge" style="position:absolute;top:8px;left:8px;">{rank}</div>' if rank else ""
    heart = "💜" if in_wish else "🤍"

    st.markdown(f"""
    <div class="product-card">
      <div style="height:150px;background:linear-gradient(135deg,#f5f3ff,#ede9fe);
           display:flex;align-items:center;justify-content:center;
           font-size:3.2rem;position:relative;">
        {icon}{rank_html}
      </div>
      <div class="product-body">
        <div class="product-category">{p.get('category','')}</div>
        <div class="product-name">{truncate_text(str(p.get('name','')), 42)}</div>
        <div class="product-rating">⭐ {p.get('rating',4.0):.1f}
          <span style="color:#9ca3af;font-size:0.72rem;">({int(p.get('num_reviews',0))})</span>
        </div>
        <div class="product-price">{format_naira(p.get('price',0))}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("View", key=f"{key_prefix}_v_{p['product_id']}", use_container_width=True):
            st.session_state.current_product = p.to_dict()
            log_activity(st.session_state.user_id, p["product_id"], "view")
            if p["product_id"] not in st.session_state.viewed_products:
                st.session_state.viewed_products.append(p["product_id"])
            st.session_state.current_page = "Search"
            st.rerun()
    with c2:
        if st.button(heart, key=f"{key_prefix}_w_{p['product_id']}", use_container_width=True):
            if not in_wish:
                st.session_state.wishlist.append(p["product_id"])
                log_activity(st.session_state.user_id, p["product_id"], "wishlist")
                st.toast("Added to wishlist! 💜")
            else:
                st.session_state.wishlist.remove(p["product_id"])
                st.toast("Removed from wishlist")
            st.rerun()


def render():
    engine = st.session_state.get("engine")
    products_df = st.session_state.get("products_df", pd.DataFrame())
    if products_df.empty:
        st.error("Data not loaded. Please refresh.")
        return

    # ── Hero + Why panel ──────────────────────────────────────────────────────
    col_hero, col_why = st.columns([3, 1])

    with col_hero:
        st.markdown("""
        <div class="hero-banner">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="flex:1;">
              <div style="font-size:2rem;font-weight:800;color:#1e1b4b;line-height:1.2;margin-bottom:0.6rem;">
                Discover Products<br>
                <span style="color:#7c3aed;">You'll Love</span>
              </div>
              <div style="font-size:0.85rem;color:#6b7280;max-width:340px;margin-bottom:1.2rem;line-height:1.6;">
                Our AI engine analyzes your preferences and behavior to recommend the best products just for you.
              </div>
            </div>
            <div style="font-size:4.5rem;opacity:0.9;display:flex;gap:0.8rem;flex-wrap:wrap;
                 max-width:180px;justify-content:center;">
              🎧💻📱⌚
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀  Explore Recommendations", key="hero_cta"):
            st.session_state.current_page = "Recommendations"
            st.rerun()

    with col_why:
        st.markdown("""
        <div class="sr-card" style="height:100%;">
          <div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;font-size:0.95rem;">
            Why This Recommendation?
          </div>
          <div style="font-size:0.8rem;color:#6b7280;margin-bottom:0.8rem;">
            We recommended these products based on:
          </div>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;color:#374151;">👁️ Products you viewed</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;color:#374151;">💜 Items in your wishlist</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;color:#374151;">👥 Users with similar interests</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;color:#374151;">📂 Your preferred categories</div>
          </div>
          <div style="margin-top:1rem;">
            <span style="font-size:0.8rem;color:#7c3aed;font-weight:600;cursor:pointer;">Learn More →</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Featured Categories ───────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">Featured Categories</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    categories = ["Smartphones", "Laptops", "Electronics", "Fashion", "Home & Kitchen", "Books", "Gaming"]
    cat_cols = st.columns(len(categories) + 1)

    for i, cat in enumerate(categories):
        with cat_cols[i]:
            icon = CATEGORY_ICONS.get(cat, "🛍️")
            st.markdown(f"""
            <div class="cat-pill">
              <div class="cat-icon">{icon}</div>
              <div class="cat-label">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(cat, key=f"hcat_{cat}", use_container_width=True,
                         label_visibility="collapsed"):
                st.session_state.selected_category = cat
                st.session_state.current_page = "Search"
                st.rerun()

    with cat_cols[-1]:
        st.markdown("""
        <div class="cat-pill">
          <div class="cat-icon">⋯</div>
          <div class="cat-label">More</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Recommended for You ───────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">Recommended for You</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    viewed = st.session_state.get("viewed_products", [])
    try:
        recs = engine.recommend_for_user(st.session_state.user_id, viewed_products=viewed, n=5) if engine else products_df.nlargest(5, "rating")
    except:
        recs = products_df.nlargest(5, "rating")

    rec_cols = st.columns(5)
    for i, (_, p) in enumerate(recs.head(5).iterrows()):
        with rec_cols[i]:
            product_card(p, key_prefix=f"rec{i}")

    # ── Trending Now ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
      <div class="section-title">Trending Now</div>
      <div class="view-all-link">View All →</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        trending = engine.get_trending(n=5) if engine else products_df.nlargest(5, "purchases")
    except:
        trending = products_df.nlargest(5, "purchases")

    tr_cols = st.columns(5)
    for i, (_, p) in enumerate(trending.head(5).iterrows()):
        with tr_cols[i]:
            product_card(p, key_prefix=f"tr{i}", rank=i+1)

    # ── Activity + Accuracy ───────────────────────────────────────────────────
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    col_act, col_acc = st.columns(2)

    with col_act:
        st.markdown("""
        <div class="sr-card">
          <div style="font-weight:700;color:#1e1b4b;margin-bottom:1rem;font-size:0.95rem;">Your Activity</div>
        </div>
        """, unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            st.metric("👁️ Products Viewed", st.session_state.products_viewed)
            st.metric("💜 Wishlist Items", len(st.session_state.wishlist) + st.session_state.wishlist_count)
        with a2:
            st.metric("⭐ Products Rated", st.session_state.ratings_given)
            st.metric("🛒 Purchases", st.session_state.orders_count)
        if st.button("View Full Activity →", key="full_act"):
            st.session_state.current_page = "Profile"
            st.rerun()

    with col_acc:
        st.markdown("""
        <div class="sr-card">
          <div style="font-weight:700;color:#1e1b4b;margin-bottom:0.5rem;font-size:0.95rem;">
            Recommendation Accuracy
          </div>
          <div style="text-align:center;padding:0.5rem 0;">
            <div class="gauge-value">92%</div>
            <div class="conf-bar"><div class="conf-fill" style="width:92%;"></div></div>
            <div style="font-size:0.8rem;color:#6b7280;margin-top:0.5rem;">
              Great! Our recommendations are working well for you.
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:0.8rem;">
            <div style="background:#f5f3ff;border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.68rem;color:#6b7280;">Content-Based</div>
              <div style="font-weight:700;color:#7c3aed;font-size:1rem;">60%</div>
            </div>
            <div style="background:#f0fdf4;border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.68rem;color:#6b7280;">Collaborative</div>
              <div style="font-weight:700;color:#10b981;font-size:1rem;">40%</div>
            </div>
            <div style="background:#fefce8;border-radius:10px;padding:0.6rem;text-align:center;">
              <div style="font-size:0.68rem;color:#6b7280;">Hybrid</div>
              <div style="font-weight:700;color:#f59e0b;font-size:1rem;">✓</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 See Analytics", key="see_analytics"):
            st.session_state.current_page = "Analytics"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    for col, icon, title, desc in [
        (f1, "🚚", "Fast & Secure Delivery", "We get your products delivered fast and securely"),
        (f2, "🎧", "24/7 Customer Support", "We're here to help you anytime you need us"),
        (f3, "✅", "100% Satisfaction", "We guarantee the best shopping experience"),
    ]:
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;background:#f9fafb;border-radius:14px;">
              <div style="font-size:1.5rem;margin-bottom:5px;">{icon}</div>
              <div style="font-weight:600;color:#1e1b4b;font-size:0.82rem;">{title}</div>
              <div style="font-size:0.72rem;color:#6b7280;margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
