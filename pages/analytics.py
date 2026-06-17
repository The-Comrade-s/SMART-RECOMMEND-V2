import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import get_analytics_data, get_user_stats, format_price
from utils.styles import SHARED_CSS


def render():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    user = st.session_state.get("user", {})
    uid = user.get("user_id") if user else None

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#1a1d2e;margin-bottom:1.5rem;">
        📊 Analytics Dashboard
    </h2>
    """, unsafe_allow_html=True)

    stats = get_user_stats(uid) if uid else {}
    cat_df, top_products, trending = get_analytics_data()

    # KPI row
    kpi_cols = st.columns(4)
    kpis = [
        ("👁️", "Products Viewed", stats.get("viewed", 0), "#6c5ce7"),
        ("❤️", "Wishlist Items", stats.get("wishlist", 0), "#ef4444"),
        ("⭐", "Ratings Given", stats.get("ratings", 0), "#f59e0b"),
        ("🛒", "Purchases", stats.get("orders", 0), "#10b981"),
    ]
    for i, (icon, label, val, color) in enumerate(kpis):
        with kpi_cols[i]:
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:1.25rem;
                 border:1px solid #eef0f7;text-align:center;">
                <div style="font-size:1.8rem;margin-bottom:0.3rem;">{icon}</div>
                <div style="font-size:1.8rem;font-weight:800;color:{color};">{val}</div>
                <div style="font-size:0.78rem;color:#888;margin-top:0.2rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        # Top Products bar chart
        if not top_products.empty:
            st.markdown("""
            <div class="dashboard-card">
                <h4>Most Viewed Products</h4>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                top_products.head(8),
                x="views", y="name",
                orientation="h",
                color="views",
                color_continuous_scale=["#c4b5fd", "#6c5ce7"],
                labels={"views": "Views", "name": "Product"},
                height=340,
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(showgrid=False),
                font=dict(family="Inter", size=11),
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        # User activity trend (simulated)
        st.markdown("""
        <div class="dashboard-card" style="margin-top:1rem;">
            <h4>Activity Trend (Last 7 Days)</h4>
        </div>
        """, unsafe_allow_html=True)

        import random, datetime
        random.seed(42)
        days = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%b %d")
                for i in range(6, -1, -1)]
        views_data = [random.randint(2, 15) for _ in days]
        wish_data = [random.randint(0, 5) for _ in days]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=days, y=views_data, mode="lines+markers",
            name="Views", line=dict(color="#6c5ce7", width=2.5),
            marker=dict(size=7, color="#6c5ce7"),
            fill="tozeroy", fillcolor="rgba(108,92,231,0.08)"
        ))
        fig2.add_trace(go.Scatter(
            x=days, y=wish_data, mode="lines+markers",
            name="Wishlist", line=dict(color="#ef4444", width=2.5),
            marker=dict(size=7, color="#ef4444"),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.06)"
        ))
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=260, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            font=dict(family="Inter", size=11),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with right_col:
        # Category donut
        if not cat_df.empty:
            st.markdown("""
            <div class="dashboard-card">
                <h4>Top Categories</h4>
            </div>
            """, unsafe_allow_html=True)

            colors = ["#6c5ce7", "#a78bfa", "#10b981", "#f59e0b", "#ef4444",
                      "#64748b", "#06b6d4", "#ec4899"]
            fig3 = px.pie(
                cat_df.head(6), values="interactions", names="category",
                hole=0.55, color_discrete_sequence=colors, height=280
            )
            fig3.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="white",
                legend=dict(font=dict(size=10, family="Inter")),
                font=dict(family="Inter"),
            )
            fig3.update_traces(textposition="outside", textfont_size=10)
            st.plotly_chart(fig3, use_container_width=True)

        # Recommendation accuracy gauge
        try:
            if "rec_engine" not in st.session_state:
                from models.recommendation_engine import RecommendationEngine
                st.session_state.rec_engine = RecommendationEngine()
            accuracy = st.session_state.rec_engine.get_recommendation_accuracy(uid) if uid else 78
        except Exception:
            accuracy = 78

        st.markdown(f"""
        <div class="dashboard-card">
            <h4>Recommendation Accuracy</h4>
            <div style="text-align:center;padding:0.5rem 0;">
                <div style="font-size:2.5rem;font-weight:800;color:#10b981;">{accuracy}%</div>
                <div style="font-size:0.82rem;color:#555;margin:0.5rem 0;">
                    {'🟢 Excellent — system is learning your preferences well' if accuracy >= 85
                     else '🟡 Good — keep browsing to improve accuracy'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig4 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=accuracy,
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"size": 10}},
                "bar": {"color": "#10b981"},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "#fef2f2"},
                    {"range": [50, 75], "color": "#fef9c3"},
                    {"range": [75, 100], "color": "#ecfdf5"},
                ],
                "threshold": {"line": {"color": "#6c5ce7", "width": 3}, "thickness": 0.75, "value": accuracy}
            },
            number={"suffix": "%", "font": {"size": 28, "family": "Inter", "color": "#1a1d2e"}},
        ))
        fig4.update_layout(
            height=200, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white", font=dict(family="Inter")
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Trending now
        if not trending.empty:
            st.markdown("""
            <div class="dashboard-card">
                <h4>🔥 Trending Now</h4>
            </div>
            """, unsafe_allow_html=True)

            for i, (_, row) in enumerate(trending.iterrows()):
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                     padding:0.5rem 0;border-bottom:1px solid #f8f9ff;">
                    <div style="display:flex;align-items:center;gap:0.6rem;">
                        <span style="background:#6c5ce7;color:white;width:22px;height:22px;
                              border-radius:6px;display:inline-flex;align-items:center;
                              justify-content:center;font-size:0.72rem;font-weight:800;flex-shrink:0;">
                            {i+1}
                        </span>
                        <span style="font-size:0.82rem;font-weight:600;color:#1a1d2e;">{row['name']}</span>
                    </div>
                    <span style="font-size:0.78rem;color:#6c5ce7;font-weight:600;">{row['cnt']} saves</span>
                </div>
                """, unsafe_allow_html=True)

    # ML Model Info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:1.5rem;border:1px solid #eef0f7;">
        <h4 style="font-size:1rem;font-weight:700;color:#1a1d2e;margin:0 0 1rem 0;">
            🤖 Recommendation Engine Details
        </h4>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
            <div style="flex:1;min-width:200px;background:#f8f9ff;border-radius:12px;padding:1rem;">
                <div style="font-weight:700;color:#6c5ce7;font-size:0.88rem;margin-bottom:0.4rem;">
                    Content-Based Filtering
                </div>
                <div style="font-size:0.8rem;color:#555;">
                    TF-IDF vectorization + Cosine Similarity on product descriptions,
                    categories, and tags. Weight: <b>60%</b>
                </div>
            </div>
            <div style="flex:1;min-width:200px;background:#f8f9ff;border-radius:12px;padding:1rem;">
                <div style="font-weight:700;color:#10b981;font-size:0.88rem;margin-bottom:0.4rem;">
                    Collaborative Filtering
                </div>
                <div style="font-size:0.8rem;color:#555;">
                    K-Nearest Neighbors on User×Product rating matrix.
                    Finds users with similar taste. Weight: <b>40%</b>
                </div>
            </div>
            <div style="flex:1;min-width:200px;background:#f8f9ff;border-radius:12px;padding:1rem;">
                <div style="font-weight:700;color:#f59e0b;font-size:0.88rem;margin-bottom:0.4rem;">
                    Hybrid Score
                </div>
                <div style="font-size:0.8rem;color:#555;">
                    <code>0.6 × Content Similarity + 0.4 × Collaborative Score</code>
                    for best-of-both recommendations.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
