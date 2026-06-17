import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (get_product_by_id, format_price, render_stars,
                           track_activity, toggle_wishlist, is_in_wishlist)
from utils.styles import SHARED_CSS
from database.db_setup import get_connection


def submit_rating(uid, pid, rating, review):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT rating_id FROM ratings WHERE user_id=? AND product_id=?", (uid, pid))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE ratings SET rating=?, review_text=? WHERE user_id=? AND product_id=?",
                  (rating, review, uid, pid))
    else:
        c.execute("INSERT INTO ratings (user_id, product_id, rating, review_text) VALUES (?,?,?,?)",
                  (uid, pid, rating, review))
    conn.commit()
    conn.close()


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None

    pid = st.session_state.get("selected_product")
    if not pid:
        st.warning("No product selected.")
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    product = get_product_by_id(pid)
    if not product:
        st.error("Product not found.")
        return

    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.page = "search"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.4])

    with left:
        st.markdown(f"""
        <div style="background:white;border-radius:20px;padding:1.5rem;
             border:1px solid #eef0f7;text-align:center;">
            <img src="{product['image_url']}"
                 onerror="this.src='https://via.placeholder.com/400x350?text={product['name'].replace(' ','+')}'"
                 style="width:100%;max-height:320px;object-fit:contain;border-radius:12px;" />
            <div style="display:flex;justify-content:center;gap:0.5rem;margin-top:1rem;">
                <span style="width:8px;height:8px;background:#6c5ce7;border-radius:50%;display:inline-block;"></span>
                <span style="width:8px;height:8px;background:#eef0f7;border-radius:50%;display:inline-block;"></span>
                <span style="width:8px;height:8px;background:#eef0f7;border-radius:50%;display:inline-block;"></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        in_wish = is_in_wishlist(uid, pid) if uid else False
        stars_html = render_stars(float(product["rating"]))
        discount_html = ""
        if product.get("original_price") and product["original_price"] > product["price"]:
            pct = int((product["original_price"] - product["price"]) / product["original_price"] * 100)
            discount_html = f'<span style="background:#fef2f2;color:#ef4444;font-size:0.8rem;font-weight:700;padding:0.2rem 0.6rem;border-radius:6px;margin-left:0.5rem;">-{pct}% OFF</span>'

        features = [f.strip() for f in product.get("description", "").split(",") if f.strip()]

        st.markdown(f"""
        <div style="padding:0.5rem 0;">
            <p style="color:#888;font-size:0.85rem;margin:0 0 0.5rem 0;">{product['category']} › {product.get('subcategory','')}</p>
            <h2 style="font-size:1.6rem;font-weight:800;color:#1a1d2e;margin:0 0 0.5rem 0;">{product['name']}</h2>
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="color:#f59e0b;font-size:1rem;">{stars_html}</span>
                <a style="color:#6c5ce7;font-size:0.83rem;font-weight:600;">
                    {product['rating']} ({product['review_count']} Reviews)
                </a>
            </div>
            <div style="display:flex;align-items:baseline;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem;">
                <span style="font-size:2rem;font-weight:900;color:#6c5ce7;">{format_price(product['price'])}</span>
                {f'<span style="font-size:1rem;color:#aaa;text-decoration:line-through;">{format_price(product["original_price"])}</span>' if product.get("original_price") and product["original_price"] > product["price"] else ''}
                {discount_html}
            </div>
            <span style="background:#ecfdf5;color:#10b981;font-size:0.82rem;font-weight:700;
                  padding:0.3rem 0.8rem;border-radius:50px;">
                {'✓ In Stock' if product.get('in_stock',1) else '✗ Out of Stock'}
            </span>
        </div>
        """, unsafe_allow_html=True)

        if features:
            feats_html = "".join([f'<li style="font-size:0.85rem;color:#444;padding:0.2rem 0;">✓ {f}</li>' for f in features[:5]])
            st.markdown(f"""
            <div style="background:#f8f9ff;border-radius:12px;padding:1rem;margin:1rem 0;">
                <p style="font-weight:700;color:#1a1d2e;margin:0 0 0.5rem 0;font-size:0.9rem;">Key Features</p>
                <ul style="margin:0;padding-left:0;list-style:none;">{feats_html}</ul>
            </div>
            """, unsafe_allow_html=True)

        # Why recommend
        st.markdown("""
        <div style="background:#fff8f0;border:1px solid #fed7aa;border-radius:12px;padding:1rem;margin-bottom:1rem;">
            <p style="font-weight:700;color:#92400e;margin:0 0 0.4rem 0;font-size:0.88rem;">Why we recommend this?</p>
            <p style="font-size:0.82rem;color:#78350f;margin:0 0 0.6rem 0;">
                Based on your interest in similar products and users with similar preferences.
            </p>
            <span style="background:#ede9fe;color:#6c5ce7;font-size:0.72rem;font-weight:700;
                  padding:0.2rem 0.6rem;border-radius:50px;margin-right:0.3rem;">You viewed this category</span>
            <span style="background:#fef3c7;color:#92400e;font-size:0.72rem;font-weight:700;
                  padding:0.2rem 0.6rem;border-radius:50px;margin-right:0.3rem;">Top rated by users like you</span>
            <span style="background:#ecfdf5;color:#065f46;font-size:0.72rem;font-weight:700;
                  padding:0.2rem 0.6rem;border-radius:50px;">High popularity</span>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        b1, b2, b3 = st.columns([2, 1, 1])
        with b1:
            if st.button("🛒  Add to Wishlist", use_container_width=True, type="primary"):
                if uid:
                    added = toggle_wishlist(uid, pid)
                    track_activity(uid, pid, "wishlist")
                    st.success("Added to wishlist! ❤️" if added else "Removed from wishlist")
                    st.rerun()
                else:
                    st.warning("Please login first")
        with b2:
            wish_label = "❤️ Saved" if in_wish else "🤍 Save"
            if st.button(wish_label, use_container_width=True):
                if uid:
                    toggle_wishlist(uid, pid)
                    st.rerun()
        with b3:
            if st.button("👍 Like", use_container_width=True):
                if uid:
                    track_activity(uid, pid, "like")
                    st.success("Liked!")

    # Rate this product
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;">
        <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">⭐ Rate This Product</h4>
    </div>
    """, unsafe_allow_html=True)

    with st.form("rate_form"):
        user_rating = st.slider("Your Rating", 1.0, 5.0, 4.0, 0.5)
        review_text = st.text_area("Write a Review (optional)", placeholder="Share your experience...")
        if st.form_submit_button("Submit Rating", type="primary"):
            if uid:
                submit_rating(uid, pid, user_rating, review_text)
                track_activity(uid, pid, "like")
                st.success("Rating submitted! Thank you 🙏")
            else:
                st.warning("Please login to rate")

    # Similar products
    st.markdown("""
    <div class="section-header" style="margin-top:2rem;">
        <h3 class="section-title">Similar Products</h3>
    </div>
    """, unsafe_allow_html=True)

    try:
        if "rec_engine" not in st.session_state:
            from models.recommendation_engine import RecommendationEngine
            st.session_state.rec_engine = RecommendationEngine()
        similar = st.session_state.rec_engine.get_content_recommendations(pid, n=4)
    except Exception:
        similar = []

    if similar:
        sim_cols = st.columns(4)
        for i, rec in enumerate(similar[:4]):
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
                        <p class="product-price" style="font-size:0.95rem;">{format_price(rec['price'])}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"sim_{rec['product_id']}_{i}", use_container_width=True):
                    if uid: track_activity(uid, rec["product_id"], "view")
                    st.session_state.selected_product = rec["product_id"]
                    st.rerun()
