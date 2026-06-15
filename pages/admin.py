"""SmartRecommend - Admin Panel (Light Theme)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import format_naira, CATEGORY_ICONS, CATEGORY_COLORS

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter",color="#6b7280",size=11),
    margin=dict(l=10,r=10,t=35,b=10),
    xaxis=dict(gridcolor="#f3f4f6",linecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#f3f4f6",linecolor="#e5e7eb"))

def render():
    products_df = st.session_state.get("products_df", pd.DataFrame())
    users_df    = st.session_state.get("users_df", pd.DataFrame())

    st.markdown("""
    <div style="font-size:1.3rem;font-weight:800;color:#1e1b4b;margin-bottom:0.2rem;">Admin Panel</div>
    <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1rem;">System overview, data management and model controls</div>
    """, unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["📊 Overview","🛍️ Products","👥 Users","🤖 ML Model"])

    with tab1:
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Products", f"{len(products_df):,}")
        with c2: st.metric("Total Users", f"{len(users_df):,}")
        with c3: st.metric("Interactions", "50,000+")
        with c4: st.metric("Categories", "7")
        st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)
        if not products_df.empty:
            ca,cb = st.columns(2)
            with ca:
                cnt = products_df["category"].value_counts()
                fig = go.Figure(go.Bar(x=cnt.index, y=cnt.values,
                    marker=dict(color="#7c3aed",line=dict(width=0)),
                    text=cnt.values, textposition="outside", textfont=dict(color="#6b7280")))
                fig.update_layout(**LAYOUT, title="Products per Category", title_font=dict(color="#1e1b4b",size=12))
                st.plotly_chart(fig, use_container_width=True)
            with cb:
                stk = products_df["in_stock"].value_counts()
                fig2 = go.Figure(go.Pie(labels=["In Stock","Out of Stock"], values=stk.values,
                    hole=0.55, marker=dict(colors=["#10b981","#ef4444"])))
                fig2.update_layout(**LAYOUT, title="Stock Status", title_font=dict(color="#1e1b4b",size=12))
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        s = st.text_input("Search products", placeholder="Search by name...", key="adm_s")
        cf = st.selectbox("Category", ["All"]+list(CATEGORY_ICONS.keys())[:-1], key="adm_cf")
        filt = products_df.copy()
        if s:  filt = filt[filt["name"].str.contains(s,case=False,na=False)]
        if cf != "All": filt = filt[filt["category"]==cf]
        if not filt.empty:
            cols = [c for c in ["product_id","name","category","price","rating","in_stock","views","purchases"] if c in filt.columns]
            show = filt[cols].head(50).copy()
            show["price"] = show["price"].apply(format_naira)
            st.dataframe(show, use_container_width=True, hide_index=True,
                column_config={"product_id":st.column_config.NumberColumn("ID",width="small"),
                               "name":st.column_config.TextColumn("Product Name",width="large"),
                               "in_stock":st.column_config.CheckboxColumn("In Stock"),
                               "rating":st.column_config.NumberColumn("Rating",format="%.1f ⭐")})
            st.caption(f"Showing {min(50,len(filt))} of {len(filt):,} products")
        st.markdown("""<div class="sr-divider"></div><div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">Add New Product</div>""", unsafe_allow_html=True)
        ac1,ac2 = st.columns(2)
        with ac1:
            new_name = st.text_input("Product Name", key="np_name")
            new_cat  = st.selectbox("Category", list(CATEGORY_ICONS.keys())[:-1], key="np_cat")
            new_price= st.number_input("Price (₦)", min_value=0, value=50000, key="np_price")
        with ac2:
            new_desc = st.text_area("Description", key="np_desc", height=100)
            new_rat  = st.slider("Initial Rating", 1.0, 5.0, 4.0, 0.1, key="np_rat")
        if st.button("Add Product", key="add_p"):
            st.success(f"✅ '{new_name}' added! (Demo mode)") if new_name else st.warning("Enter a product name.")

    with tab3:
        if not users_df.empty:
            dcols = [c for c in ["user_id","name","email","city","age","date_joined"] if c in users_df.columns]
            st.dataframe(users_df[dcols].head(100), use_container_width=True, hide_index=True)
            st.caption(f"Showing 100 of {len(users_df):,} users")

    with tab4:
        m1,m2,m3 = st.columns(3)
        for col,icon,title,desc,status in [
            (m1,"📝","Content-Based","TF-IDF + Cosine Similarity","Active"),
            (m2,"👥","Collaborative","KNN + Matrix Factorization","Active"),
            (m3,"⚡","Hybrid Engine","0.6 Content + 0.4 Collab","Active")]:
            with col:
                st.markdown(f"""
                <div class="sr-card" style="text-align:center;">
                  <div style="font-size:1.5rem;margin-bottom:0.4rem;">{icon}</div>
                  <div style="font-weight:700;color:#1e1b4b;font-size:0.88rem;">{title}</div>
                  <div style="font-size:0.75rem;color:#6b7280;margin:0.3rem 0;">{desc}</div>
                  <span class="badge badge-success">● {status}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("""<div class="sr-divider"></div><div style="font-weight:700;color:#1e1b4b;margin-bottom:0.8rem;">Model Configuration</div>""", unsafe_allow_html=True)
        cfg1,cfg2 = st.columns(2)
        with cfg1:
            cw = st.slider("Content-Based Weight", 0.0, 1.0, 0.6, 0.05, key="cfg_cw")
            st.caption(f"Collaborative weight: {1-cw:.2f}")
        with cfg2:
            st.slider("KNN Neighbors", 5, 50, 20, 5, key="cfg_nn")
            st.selectbox("TF-IDF Max Features", [500,1000,2000], index=1, key="cfg_mf")
        if st.button("🔄 Retrain Model", key="retrain"):
            import time; time.sleep(1); st.success("✅ Model retrained! (Demo mode)")
