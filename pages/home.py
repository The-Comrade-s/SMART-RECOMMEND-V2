import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (get_products, format_price, render_stars,
                           track_activity, toggle_wishlist, is_in_wishlist,
                           get_viewed_product_ids)
from utils.styles import SHARED_CSS


def product_card(p, col_key=""):
    pid = int(p["product_id"]) if hasattr(p, "__getitem__") else int(p.product_id)
    name = p["name"] if hasattr(p, "__getitem__") else p.name
    cat = p["category"] if hasattr(p, "__getitem__") else p.category
    price = p["price"] if hasattr(p, "__getitem__") else p.price
    orig = p.get("original_price", 0) if hasattr(p, "get") else getattr(p, "original_price", 0)
    img = p["image_url"] if hasattr(p, "__getitem__") else p.image_url
    rating = float(p["rating"] if hasattr(p, "__getitem__") else p.rating)
    reviews = p["review_count"] if hasattr(p, "__getitem__") else p.review_count
    is_new = p.get("is_new_arrival", 0) if hasattr(p, "get") else getattr(p, "is_new_arrival", 0)
    is_trend = p.get("is_trending", 0) if hasattr(p, "get") else getattr(p, "is_trending", 0)

    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None
    in_wish = is_in_wishlist(uid, pid) if uid else False
    wish_icon = "❤️" if in_wish else "🤍"

    badge = ""
    if is_new:
        badge = '<span class="badge-new">NEW</span>'
    elif is_trend:
        badge = '<span class="badge-trending">🔥 Trending</span>'

    stars = render_stars(rating)
    discount = ""
    if orig and orig > price:
        pct = int((orig - price) / orig * 100)
        discount = f'<span style="background:#fef2f2;color:#ef4444;font-size:0.7rem;font-weight:700;padding:0.1rem 0.4rem;border-radius:4px;margin-left:0.3rem;">-{pct}%</span>'

    st.markdown(f"""
    <div class="product-card">
        <div class="product-img-wrap">
            <img src="{img}" onerror="this.src='https://via.placeholder.com/400x300?text=Product'" />
        </div>
        <div class="product-info">
            <div style="margin-bottom:0.3rem;">{badge}</div>
            <p class="product-name" title="{name}">{name}</p>
            <p class="product-cat">{cat}</p>
            <div class="product-stars">{stars} <span style="color:#888;font-size:0.75rem;">({reviews})</span></div>
            <div style="display:flex;align-items:center;flex-wrap:wrap;">
                <span class="product-price">{format_price(price)}</span>
                {f'<span class="product-orig-price">{format_price(orig)}</span>' if orig and orig > price else ''}
                {discount}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button("View Product", key=f"view_{pid}_{col_key}", use_container_width=True, type="primary"):
            if uid:
                track_activity(uid, pid, "view")
            st.session_state.selected_product = pid
            st.session_state.page = "product"
            st.rerun()
    with c2:
        if st.button(wish_icon, key=f"wish_{pid}_{col_key}", use_container_width=True):
            if uid:
                toggle_wishlist(uid, pid)
                st.rerun()
            else:
                st.warning("Login to save wishlist")


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    first_name = user.get("name", "").split()[0] if user else "Guest"
    uid = user.get("user_id") if user else None

    # Top nav
    st.markdown(f"""
    <div class="top-nav">
        <div class="brand-logo">Smart<span>Recommend</span>
            <span style="font-size:0.7rem;font-weight:400;color:#888;margin-left:0.5rem;">AI Product Recommender</span>
        </div>
        <div style="display:flex;align-items:center;gap:1rem;">
            <span style="font-size:1.3rem;cursor:pointer;">🔔</span>
            <span style="font-size:0.88rem;color:#555;font-weight:500;">Good Evening, <b>{first_name}</b> ▾</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Layout: main + right panel
    main_col, right_col = st.columns([3, 1])

    with main_col:
        # Search bar
        search_q = st.text_input("", placeholder="🔍  Search for products, brands and more...",
                                  label_visibility="collapsed", key="home_search")
        if search_q:
            st.session_state.search_query = search_q
            st.session_state.page = "search"
            st.rerun()

        # Hero Banner
        st.markdown("""
        <div class="hero-banner">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                <div>
                    <h1>Discover Products<br>You'll <span>Love</span></h1>
                    <p>Our AI engine analyzes your preferences and behavior<br>to recommend the best products just for you.</p>
                    <button class="hero-btn">Explore Recommendations ›</button>
                </div>
                <div style="font-size:5rem;opacity:0.3;">🎧📱💻</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Featured Categories
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">Featured Categories</h3>
            <a class="view-all" href="#">View All</a>
        </div>
        """, unsafe_allow_html=True)

        cats = [
            ("📱", "Smartphones"), ("💻", "Laptops"), ("🎧", "Electronics"),
            ("👗", "Fashion"), ("🏠", "Home & Kitchen"), ("📚", "Books"),
            ("🎮", "Gaming"), ("⋯", "More")
        ]
        cat_cols = st.columns(len(cats))
        for i, (icon, label) in enumerate(cats):
            with cat_cols[i]:
                if st.button(f"{icon}\n{label}", key=f"cat_{i}", use_container_width=True):
                    st.session_state.search_category = label if label != "More" else None
                    st.session_state.page = "search"
                    st.rerun()

        # Recommended For You
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">Recommended for You</h3>
            <a class="view-all" href="#">View All</a>
        </div>
        """, unsafe_allow_html=True)

        viewed_ids = get_viewed_product_ids(uid) if uid else []

        try:
            from models.recommendation_engine import RecommendationEngine
            if "rec_engine" not in st.session_state:
                st.session_state.rec_engine = RecommendationEngine()
            engine = st.session_state.rec_engine
            if uid and viewed_ids:
                recs = engine.get_hybrid_recommendations(uid, viewed_ids, n=5)
            else:
                recs = engine._get_popular(5)
        except Exception:
            recs = []

        if recs:
            rec_cols = st.columns(min(5, len(recs)))
            for i, rec in enumerate(recs[:5]):
                with rec_cols[i]:
                    pid = rec["product_id"]
                    img = rec.get("image_url", "")
                    in_wish = is_in_wishlist(uid, pid) if uid else False
                    wish_icon = "❤️" if in_wish else "🤍"
                    stars = render_stars(float(rec.get("rating", 4.5)))
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="product-img-wrap">
                            <img src="{img}" onerror="this.src='https://via.placeholder.com/300'" />
                        </div>
                        <div class="product-info">
                            <p class="product-name" title="{rec['name']}">{rec['name']}</p>
                            <p class="product-cat">{rec.get('category','')}</p>
                            <div class="product-stars">{stars}</div>
                            <p class="product-price">{format_price(rec['price'])}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        if st.button("View Product", key=f"rec_view_{pid}_{i}", use_container_width=True, type="primary"):
                            if uid: track_activity(uid, pid, "view")
                            st.session_state.selected_product = pid
                            st.session_state.page = "product"
                            st.rerun()
                    with c2:
                        if st.button(wish_icon, key=f"rec_wish_{pid}_{i}", use_container_width=True):
                            if uid: toggle_wishlist(uid, pid); st.rerun()
        else:
            featured = get_products(limit=5)
            cols = st.columns(min(5, len(featured)))
            for i, (_, row) in enumerate(featured.iterrows()):
                with cols[i]:
                    product_card(row, f"feat_{i}")

        # Trending Now
        st.markdown("""
        <div class="section-header" style="margin-top:2rem;">
            <h3 class="section-title">Trending Now</h3>
            <a class="view-all" href="#">View All</a>
        </div>
        """, unsafe_allow_html=True)

        trending = get_products(sort_by="popular", limit=5)
        trend_cols = st.columns(5)
        for i, (_, row) in enumerate(trending.iterrows()):
            with trend_cols[i]:
                st.markdown(f'<div class="trending-num">{i+1}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="product-card" style="cursor:pointer;">
                    <div class="product-img-wrap" style="height:130px;">
                        <img src="{row['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name" style="font-size:0.8rem;">{row['name']}</p>
                        <p class="product-price" style="font-size:0.9rem;">{format_price(row['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"trend_{i}_{row['product_id']}", use_container_width=True):
                    if uid: track_activity(uid, int(row["product_id"]), "view")
                    st.session_state.selected_product = int(row["product_id"])
                    st.session_state.page = "product"
                    st.rerun()

        # Footer info strip
        st.markdown("""
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:2rem;padding:1.5rem;
             background:white;border-radius:16px;border:1px solid #eef0f7;">
            <div style="flex:1;display:flex;align-items:center;gap:0.75rem;min-width:180px;">
                <span style="font-size:1.8rem;">🚚</span>
                <div>
                    <div style="font-weight:700;font-size:0.88rem;color:#1a1d2e;">Fast & Secure Delivery</div>
                    <div style="font-size:0.78rem;color:#888;">Get your products delivered fast and securely</div>
                </div>
            </div>
            <div style="flex:1;display:flex;align-items:center;gap:0.75rem;min-width:180px;">
                <span style="font-size:1.8rem;">💬</span>
                <div>
                    <div style="font-weight:700;font-size:0.88rem;color:#1a1d2e;">24/7 Customer Support</div>
                    <div style="font-size:0.78rem;color:#888;">We're here to help you anytime you need us</div>
                </div>
            </div>
            <div style="flex:1;display:flex;align-items:center;gap:0.75rem;min-width:180px;">
                <span style="font-size:1.8rem;">⚙️</span>
                <div>
                    <div style="font-weight:700;font-size:0.88rem;color:#1a1d2e;">100% Satisfaction</div>
                    <div style="font-size:0.78rem;color:#888;">We guarantee the best shopping experience</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right panel
    with right_col:
        # Why This Recommendation
        st.markdown("""
        <div class="why-rec-panel">
            <h4>Why This Recommendation?</h4>
            <p style="font-size:0.8rem;color:#666;margin:0 0 1rem 0;">
                We recommended these products based on:
            </p>
            <div class="why-item"><span class="why-icon">👁️</span> Products you viewed</div>
            <div class="why-item"><span class="why-icon">❤️</span> Items in your wishlist</div>
            <div class="why-item"><span class="why-icon">👥</span> Users with similar interests</div>
            <div class="why-item"><span class="why-icon">📂</span> Your preferred categories</div>
            <br>
            <a style="color:#6c5ce7;font-size:0.83rem;font-weight:600;cursor:pointer;">Learn More →</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Your Activity
        from utils.helpers import get_user_stats
        stats = get_user_stats(uid) if uid else {"viewed": 0, "wishlist": 0, "ratings": 0, "orders": 0}

        st.markdown(f"""
        <div class="why-rec-panel">
            <h4>Your Activity</h4>
            <div style="display:flex;flex-direction:column;gap:0.6rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.82rem;color:#555;">👁️ Products Viewed</span>
                    <span style="font-weight:800;color:#1a1d2e;">{stats['viewed']}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.82rem;color:#555;">⭐ Products Rated</span>
                    <span style="font-weight:800;color:#1a1d2e;">{stats['ratings']}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.82rem;color:#555;">❤️ Wishlist Items</span>
                    <span style="font-weight:800;color:#1a1d2e;">{stats['wishlist']}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.82rem;color:#555;">🛒 Purchases</span>
                    <span style="font-weight:800;color:#1a1d2e;">{stats['orders']}</span>
                </div>
            </div>
            <br>
            <a style="color:#6c5ce7;font-size:0.83rem;font-weight:600;cursor:pointer;">View Full Activity →</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Recommendation Accuracy
        try:
            if "rec_engine" in st.session_state and uid:
                accuracy = st.session_state.rec_engine.get_recommendation_accuracy(uid)
            else:
                accuracy = 78
        except Exception:
            accuracy = 78

        st.markdown(f"""
        <div class="why-rec-panel">
            <h4>Recommendation Accuracy</h4>
            <div style="text-align:center;padding:1rem 0;">
                <div style="font-size:2.5rem;font-weight:800;color:#1a1d2e;">{accuracy}%</div>
                <div style="margin:0.75rem auto;width:80px;height:80px;position:relative;">
                    <svg viewBox="0 0 80 80" style="transform:rotate(-90deg);">
                        <circle cx="40" cy="40" r="32" fill="none" stroke="#eef0f7" stroke-width="8"/>
                        <circle cx="40" cy="40" r="32" fill="none" stroke="#10b981" stroke-width="8"
                            stroke-dasharray="{int(accuracy * 2.01)} 201"
                            stroke-linecap="round"/>
                    </svg>
                </div>
                <p style="font-size:0.8rem;color:#555;margin:0;">
                    {'Great! Our recommendations are working well for you.' if accuracy >= 80 else 'Keep exploring to improve recommendations.'}
                </p>
            </div>
            <a style="color:#6c5ce7;font-size:0.83rem;font-weight:600;cursor:pointer;">See Analytics →</a>
        </div>
        """, unsafe_allow_html=True)
