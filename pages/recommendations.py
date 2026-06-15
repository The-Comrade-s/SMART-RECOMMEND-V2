"""SmartRecommend - Recommendations Page (Light Theme)"""
import streamlit as st
import pandas as pd
from utils.helpers import format_naira, CATEGORY_ICONS, truncate_text, log_activity

def rec_card(p, engine, idx, pfx="r"):
    icon = CATEGORY_ICONS.get(p.get("category",""),"🛍️")
    in_w = p["product_id"] in st.session_state.get("wishlist",[])
    conf = 80
    tags = []
    if engine:
        try:
            exp = engine.explain_recommendation(p["product_id"], user_id=st.session_state.user_id,
                viewed_products=st.session_state.viewed_products, liked_categories=st.session_state.preferred_categories)
            conf = exp.get("confidence",80); tags = exp.get("tags",[])
        except: pass

    st.markdown(f"""
    <div class="product-card">
      <div style="height:140px;background:linear-gradient(135deg,#f5f3ff,#ede9fe);
           display:flex;align-items:center;justify-content:center;font-size:3rem;position:relative;">
        {icon}
        <div style="position:absolute;bottom:7px;right:7px;background:#7c3aed;color:white;
             border-radius:7px;padding:2px 7px;font-size:0.68rem;font-weight:700;">{conf}% match</div>
      </div>
      <div class="product-body">
        <div class="product-category">{p.get('category','')}</div>
        <div class="product-name">{truncate_text(str(p.get('name','')),40)}</div>
        <div class="product-rating">⭐ {p.get('rating',4.0):.1f} <span style="color:#9ca3af;font-size:0.7rem;">({int(p.get('num_reviews',0))})</span></div>
        <div class="product-price">{format_naira(p.get('price',0))}</div>
        {"".join(f'<span class="badge badge-primary" style="font-size:0.62rem;">{t}</span>' for t in tags[:2])}
      </div>
    </div>
    """, unsafe_allow_html=True)
    b1,b2,b3 = st.columns(3)
    with b1:
        if st.button("View", key=f"{pfx}v{p['product_id']}{idx}", use_container_width=True):
            st.session_state.current_product = p.to_dict()
            log_activity(st.session_state.user_id, p["product_id"], "view")
            if p["product_id"] not in st.session_state.viewed_products:
                st.session_state.viewed_products.append(p["product_id"])
            st.session_state.current_page = "Search"; st.rerun()
    with b2:
        if st.button("💜" if in_w else "🤍", key=f"{pfx}w{p['product_id']}{idx}", use_container_width=True):
            if not in_w:
                st.session_state.wishlist.append(p["product_id"])
                log_activity(st.session_state.user_id, p["product_id"], "wishlist"); st.toast("Added! 💜")
            else: st.session_state.wishlist.remove(p["product_id"])
            st.rerun()
    with b3:
        if st.button("🛒", key=f"{pfx}c{p['product_id']}{idx}", use_container_width=True):
            log_activity(st.session_state.user_id, p["product_id"], "purchase"); st.toast("Added to cart!")

def render():
    engine = st.session_state.get("engine")
    products_df = st.session_state.get("products_df", pd.DataFrame())
    if products_df.empty: st.error("Data not loaded."); return

    st.markdown("""
    <div style="font-size:1.3rem;font-weight:800;color:#1e1b4b;margin-bottom:0.2rem;">Recommendations</div>
    <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1rem;">Personalized picks powered by our Hybrid AI Engine</div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ How our recommendation engine works"):
        c1,c2,c3 = st.columns(3)
        for col,icon,title,desc in [
            (c1,"📝","Content-Based (60%)","TF-IDF + Cosine Similarity on product descriptions, categories and tags"),
            (c2,"👥","Collaborative (40%)","User×Product matrix, K-Nearest Neighbors, finds users with similar taste"),
            (c3,"⚡","Hybrid Score","0.6 × Content Score + 0.4 × Collaborative Score = Final Recommendation")]:
            with col:
                st.markdown(f"""
                <div class="sr-card" style="text-align:center;">
                  <div style="font-size:1.5rem;margin-bottom:0.4rem;">{icon}</div>
                  <div style="font-weight:700;color:#1e1b4b;font-size:0.85rem;">{title}</div>
                  <div style="font-size:0.75rem;color:#6b7280;margin-top:0.3rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["🎯 For You","🔗 Similar Items","🔥 Trending","🆕 New Arrivals"])

    with tab1:
        viewed = st.session_state.get("viewed_products",[])
        try: recs = engine.recommend_for_user(st.session_state.user_id, viewed_products=viewed, n=8) if engine else products_df.nlargest(8,"rating")
        except: recs = products_df.nlargest(8,"rating")
        st.markdown(f'<div style="font-size:0.8rem;color:#6b7280;margin-bottom:1rem;">Showing <strong style="color:#7c3aed;">{len(recs)}</strong> personalized picks</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i,(_, p) in enumerate(recs.head(8).iterrows()):
            with cols[i%4]: rec_card(p, engine, i, "fy")

        st.markdown("""<div class="sr-divider"></div><div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">Because you viewed Samsung Galaxy S24 Ultra</div>""", unsafe_allow_html=True)
        bv = products_df[products_df["category"]=="Smartphones"].head(3)
        bvc = st.columns(3)
        for i,(_,p) in enumerate(bv.iterrows()):
            with bvc[i]: rec_card(p,engine,i+100,"bv")

        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin:1rem 0 0.8rem;">Customers Also Bought</div>""", unsafe_allow_html=True)
        cab = products_df.sample(min(3,len(products_df)), random_state=42)
        cabc = st.columns(3)
        for i,(_,p) in enumerate(cab.iterrows()):
            with cabc[i]: rec_card(p,engine,i+200,"ca")

    with tab2:
        st.markdown("**Find similar products to what you've viewed:**")
        viewed_list = st.session_state.get("viewed_products",[])
        names = products_df[products_df["product_id"].isin(viewed_list[:10])]["name"].tolist() if viewed_list else products_df["name"].head(10).tolist()
        sel = st.selectbox("Select a product:", names if names else ["No products viewed yet"], key="sim_sel")
        if sel and sel != "No products viewed yet":
            sp = products_df[products_df["name"]==sel]
            if not sp.empty and engine:
                try:
                    similar = engine.recommend_similar(sp.iloc[0]["product_id"], n=8)
                    sc = st.columns(4)
                    for i,(_,p) in enumerate(similar.head(8).iterrows()):
                        with sc[i%4]: rec_card(p,engine,i+300,"si")
                except Exception as e: st.error(str(e))

    with tab3:
        try: tr = engine.get_trending(n=12) if engine else products_df.nlargest(12,"purchases")
        except: tr = products_df.nlargest(12,"purchases")
        t3c = st.columns(3)
        for i,(_,p) in enumerate(tr.head(3).iterrows()):
            with t3c[i]:
                icon = CATEGORY_ICONS.get(p.get("category",""),"🛍️")
                st.markdown(f"""
                <div class="sr-card" style="text-align:center;">
                  <div style="font-size:1.5rem;">{'🥇🥈🥉'[i]}</div>
                  <div style="font-size:2.5rem;margin:0.3rem 0;">{icon}</div>
                  <div style="font-weight:700;color:#1e1b4b;font-size:0.85rem;">{truncate_text(str(p.get('name','')),35)}</div>
                  <div style="color:#f59e0b;font-size:0.82rem;">⭐ {p.get('rating',4.0):.1f}</div>
                  <div style="font-weight:700;color:#7c3aed;font-size:1rem;">{format_naira(p.get('price',0))}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Product", key=f"top3_{p['product_id']}_{i}", use_container_width=True):
                    st.session_state.current_product = p.to_dict()
                    st.session_state.current_page = "Search"; st.rerun()
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        trc = st.columns(4)
        for i,(_,p) in enumerate(tr.iloc[3:11].iterrows()):
            with trc[i%4]: rec_card(p,engine,i+400,"tr")

    with tab4:
        try: na = engine.get_new_arrivals(n=12) if engine else products_df.tail(12)
        except: na = products_df.tail(12)
        nac = st.columns(4)
        for i,(_,p) in enumerate(na.head(12).iterrows()):
            with nac[i%4]: rec_card(p,engine,i+500,"na")
