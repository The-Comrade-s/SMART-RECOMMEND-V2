import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (format_price, render_stars, track_activity,
                           toggle_wishlist, is_in_wishlist, get_viewed_product_ids,
                           get_products)
from utils.styles import SHARED_CSS


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#1a1d2e;margin-bottom:1.5rem;">
        ✨ Recommendations
    </h2>
    """, unsafe_allow_html=True)

    # Tabs
    tab_sel = st.radio("", ["For You", "Similar Items", "Trending"],
                        horizontal=True, label_visibility="collapsed")

    # Load engine
    try:
        if "rec_engine" not in st.session_state:
            from models.recommendation_engine import RecommendationEngine
            with st.spinner("Loading recommendation engine..."):
                st.session_state.rec_engine = RecommendationEngine()
        engine = st.session_state.rec_engine
    except Exception as e:
        st.error(f"Engine error: {e}")
        return

    viewed_ids = get_viewed_product_ids(uid) if uid else []

    if tab_sel == "For You":
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">Recommended for You</h3>
        </div>
        """, unsafe_allow_html=True)

        if uid and viewed_ids:
            recs = engine.get_hybrid_recommendations(uid, viewed_ids, n=8)
        else:
            recs = engine._get_popular(8)

        if not recs:
            st.info("Browse some products first to get personalized recommendations!")
            return

        cols = st.columns(4)
        for i, rec in enumerate(recs[:8]):
            with cols[i % 4]:
                pid = rec["product_id"]
                in_wish = is_in_wishlist(uid, pid) if uid else False
                wish_icon = "❤️" if in_wish else "🤍"
                stars = render_stars(float(rec.get("rating", 4.0)))
                confidence = rec.get("confidence", 80)

                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap">
                        <img src="{rec['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name">{rec['name']}</p>
                        <p class="product-cat">{rec.get('category','')}</p>
                        <div class="product-stars">{stars}
                            <span style="color:#888;font-size:0.72rem;">({rec.get('review_count',0)})</span>
                        </div>
                        <p class="product-price">{format_price(rec['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Explainable reasons
                reasons = rec.get("reasons", [])
                if reasons:
                    tags_html = "".join([f'<span class="rec-reason-tag">{r}</span>' for r in reasons[:2]])
                    st.markdown(f'<div style="margin:0.3rem 0;">{tags_html}</div>', unsafe_allow_html=True)

                # Confidence bar
                st.markdown(f"""
                <div style="margin:0.3rem 0 0.5rem 0;">
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#888;margin-bottom:2px;">
                        <span>Match score</span><span style="color:#10b981;font-weight:700;">{confidence}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width:{confidence}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns([3, 1])
                with c1:
                    if st.button("View", key=f"ry_{pid}_{i}", use_container_width=True, type="primary"):
                        if uid: track_activity(uid, pid, "view")
                        st.session_state.selected_product = pid
                        st.session_state.page = "product"
                        st.rerun()
                with c2:
                    if st.button(wish_icon, key=f"rw_{pid}_{i}", use_container_width=True):
                        if uid: toggle_wishlist(uid, pid); st.rerun()

        # Because you viewed
        if viewed_ids:
            st.markdown("""
            <div class="section-header" style="margin-top:2rem;">
                <h3 class="section-title">Because You Viewed These</h3>
            </div>
            """, unsafe_allow_html=True)

            from utils.helpers import get_product_by_id
            last_viewed = get_product_by_id(viewed_ids[0]) if viewed_ids else None
            if last_viewed:
                st.markdown(f"""
                <p style="color:#888;font-size:0.85rem;margin-bottom:1rem;">
                    Based on <b style="color:#6c5ce7;">{last_viewed['name']}</b>
                </p>
                """, unsafe_allow_html=True)

            similar = engine.get_content_recommendations(viewed_ids[0], n=3) if viewed_ids else []
            if similar:
                sim_cols = st.columns(3)
                for i, rec in enumerate(similar):
                    with sim_cols[i]:
                        stars = render_stars(float(rec.get("rating", 4.0)))
                        st.markdown(f"""
                        <div class="product-card">
                            <div class="product-img-wrap" style="height:140px;">
                                <img src="{rec['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                            </div>
                            <div class="product-info">
                                <p class="product-name">{rec['name']}</p>
                                <div class="product-stars" style="font-size:0.75rem;">{stars}</div>
                                <p class="product-price">{format_price(rec['price'])}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("View", key=f"bv_{rec['product_id']}_{i}", use_container_width=True):
                            if uid: track_activity(uid, rec["product_id"], "view")
                            st.session_state.selected_product = rec["product_id"]
                            st.session_state.page = "product"
                            st.rerun()

        # Customers also bought
        st.markdown("""
        <div class="section-header" style="margin-top:2rem;">
            <h3 class="section-title">Customers Also Bought</h3>
        </div>
        """, unsafe_allow_html=True)
        also = engine._get_popular(4, exclude=viewed_ids)
        also_cols = st.columns(4)
        for i, rec in enumerate(also[:4]):
            with also_cols[i]:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap" style="height:140px;">
                        <img src="{rec['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name">{rec['name']}</p>
                        <p class="product-price">{format_price(rec['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"ab_{rec['product_id']}_{i}", use_container_width=True):
                    if uid: track_activity(uid, rec["product_id"], "view")
                    st.session_state.selected_product = rec["product_id"]
                    st.session_state.page = "product"
                    st.rerun()

    elif tab_sel == "Similar Items":
        st.markdown("""
        <p style="color:#888;font-size:0.88rem;">Products similar to what you've viewed</p>
        """, unsafe_allow_html=True)

        if not viewed_ids:
            st.info("Browse some products to see similar items here!")
            return

        recs = engine.get_content_recommendations(viewed_ids[0], n=8)
        cols = st.columns(4)
        for i, rec in enumerate(recs[:8]):
            with cols[i % 4]:
                stars = render_stars(float(rec.get("rating", 4.0)))
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap">
                        <img src="{rec['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name">{rec['name']}</p>
                        <p class="product-cat">{rec['category']}</p>
                        <div class="product-stars">{stars}</div>
                        <p class="product-price">{format_price(rec['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"si_{rec['product_id']}_{i}", use_container_width=True, type="primary"):
                    if uid: track_activity(uid, rec["product_id"], "view")
                    st.session_state.selected_product = rec["product_id"]
                    st.session_state.page = "product"
                    st.rerun()

    else:  # Trending
        st.markdown("""
        <p style="color:#888;font-size:0.88rem;">Trending products right now</p>
        """, unsafe_allow_html=True)

        trending = get_products(sort_by="popular", limit=8)
        cols = st.columns(4)
        for i, (_, row) in enumerate(trending.iterrows()):
            with cols[i % 4]:
                pid = int(row["product_id"])
                stars = render_stars(float(row["rating"]))
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap">
                        <div class="trending-num">{i+1}</div>
                        <img src="{row['image_url']}" onerror="this.src='https://via.placeholder.com/300'" />
                    </div>
                    <div class="product-info">
                        <p class="product-name">{row['name']}</p>
                        <div class="product-stars">{stars}</div>
                        <p class="product-price">{format_price(row['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"tr_{pid}_{i}", use_container_width=True, type="primary"):
                    if uid: track_activity(uid, pid, "view")
                    st.session_state.selected_product = pid
                    st.session_state.page = "product"
                    st.rerun()
