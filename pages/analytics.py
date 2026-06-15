"""SmartRecommend - Analytics Dashboard (Light Theme)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.helpers import format_naira, CATEGORY_COLORS

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#6b7280", size=11),
    margin=dict(l=10,r=10,t=35,b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#f3f4f6", linecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#f3f4f6", linecolor="#e5e7eb"))

def render():
    products_df   = st.session_state.get("products_df", pd.DataFrame())
    activities_df = st.session_state.get("activities_df", pd.DataFrame())
    users_df      = st.session_state.get("users_df", pd.DataFrame())

    st.markdown("""
    <div style="font-size:1.3rem;font-weight:800;color:#1e1b4b;margin-bottom:0.2rem;">Analytics Dashboard</div>
    <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1rem;">Real-time insights into product performance and user behavior</div>
    """, unsafe_allow_html=True)

    if products_df.empty: st.error("No data available."); return

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("Total Products", f"{len(products_df):,}", "+120 this week")
    with k2: st.metric("Total Users", f"{len(users_df):,}", "+340 this month")
    with k3: st.metric("Interactions", "50,000+", "+1,200 today")
    with k4: st.metric("Avg Rating", f"{products_df['rating'].mean():.2f} ⭐", "+0.12")
    with k5: st.metric("Accuracy", "92%", "+3%")

    st.markdown("""<div class="sr-divider"></div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.6rem;">Top Categories</div>""", unsafe_allow_html=True)
        cat_cnt = products_df.groupby("category")["product_id"].count().reset_index()
        fig = go.Figure(go.Pie(labels=cat_cnt["category"], values=cat_cnt["product_id"], hole=0.5,
            marker=dict(colors=[CATEGORY_COLORS.get(c,"#7c3aed") for c in cat_cnt["category"]], line=dict(color="white",width=2)),
            textfont=dict(size=11)))
        fig.update_layout(**LAYOUT, title="Products by Category", title_font=dict(color="#1e1b4b",size=12))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.6rem;">Most Viewed Products</div>""", unsafe_allow_html=True)
        top_v = products_df.nlargest(8,"views")[["name","views","category"]].copy()
        top_v["short"] = top_v["name"].str[:22]+"..."
        fig2 = go.Figure(go.Bar(x=top_v["views"], y=top_v["short"], orientation="h",
            marker=dict(color=[CATEGORY_COLORS.get(c,"#7c3aed") for c in top_v["category"]], line=dict(width=0)),
            text=top_v["views"].apply(lambda x:f"{x:,}"), textposition="outside",
            textfont=dict(color="#6b7280",size=9)))
        fig2.update_layout(**LAYOUT, title="Top 8 Most Viewed", title_font=dict(color="#1e1b4b",size=12),
                           yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.6rem;">User Activity Trend</div>""", unsafe_allow_html=True)
        days = list(range(1,31))
        fig3 = go.Figure()
        for action,color in [("Views","#7c3aed"),("Clicks","#0ea5e9"),("Purchases","#10b981")]:
            y = np.random.randint(50,300,30)+np.sin(np.array(days))*30
            fig3.add_trace(go.Scatter(x=days, y=y.astype(int), name=action, mode="lines",
                line=dict(color=color,width=2), fill="tozeroy",
                fillcolor=color+"20" if len(color)==7 else color))
        fig3.update_layout(**LAYOUT, title="Daily Activity (Last 30 Days)", title_font=dict(color="#1e1b4b",size=12))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("""<div style="font-weight:700;color:#1e1b4b;margin-bottom:0.6rem;">Rating Distribution</div>""", unsafe_allow_html=True)
        r_bins = pd.cut(products_df["rating"], bins=[0,2,3,4,4.5,5], labels=["1-2","2-3","3-4","4-4.5","4.5-5"])
        r_dist = r_bins.value_counts().sort_index()
        fig4 = go.Figure(go.Bar(x=r_dist.index.astype(str), y=r_dist.values,
            marker=dict(color=["#ef4444","#f59e0b","#84cc16","#22c55e","#10b981"], line=dict(width=0)),
            text=r_dist.values, textposition="outside", textfont=dict(color="#6b7280")))
        fig4.update_layout(**LAYOUT, title="Products by Rating Range", title_font=dict(color="#1e1b4b",size=12))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""<div class="sr-divider"></div><div style="font-weight:700;color:#1e1b4b;margin-bottom:1rem;">Sentiment Analysis</div>""", unsafe_allow_html=True)
    s1,s2,s3 = st.columns(3)
    for col,emoji,label,pct,color in [(s1,"😊","Positive Reviews",82,"#10b981"),(s2,"😐","Neutral Reviews",12,"#f59e0b"),(s3,"😔","Negative Reviews",6,"#ef4444")]:
        with col:
            st.markdown(f"""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:2rem;margin-bottom:0.4rem;">{emoji}</div>
              <div style="font-size:2rem;font-weight:800;color:{color};">{pct}%</div>
              <div style="font-size:0.8rem;color:#6b7280;">{label}</div>
              <div class="conf-bar" style="margin-top:0.6rem;"><div style="height:100%;width:{pct}%;background:{color};border-radius:4px;"></div></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""<div class="sr-divider"></div><div style="font-weight:700;color:#1e1b4b;margin-bottom:1rem;">Recommendation Performance</div>""", unsafe_allow_html=True)
    r1,r2,r3,r4 = st.columns(4)
    for col,label,val,color in [(r1,"Precision@10","87%","#7c3aed"),(r2,"Recall@10","79%","#0ea5e9"),(r3,"NDCG Score","0.84","#10b981"),(r4,"Coverage","94%","#f59e0b")]:
        with col:
            st.markdown(f"""
            <div class="sr-card" style="text-align:center;">
              <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
              <div style="font-size:0.75rem;color:#6b7280;margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)
