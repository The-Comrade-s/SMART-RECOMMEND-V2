# SmartRecommend 🛍️
**AI-Powered Product Recommendation Engine**

A production-style e-commerce recommendation platform built with Streamlit and Machine Learning.

---

## Features

- 🔐 User Registration & Login (SQLite auth)
- 🏠 Personalized Home Page with Hero Banner
- 🔍 Search & Filter Products (category, price, rating)
- 📦 Product Detail Page with Explainable AI
- ✨ Hybrid Recommendation Engine (TF-IDF + Collaborative Filtering)
- ❤️ Wishlist Management with Order Summary
- 👤 User Profile with Preference Breakdown
- 📊 Analytics Dashboard with Plotly Charts
- 🤖 Recommendation Accuracy Gauge

---

## ML Architecture

```
Hybrid Score = 0.6 × Content Similarity + 0.4 × Collaborative Score
```

- **Content-Based**: TF-IDF vectorization + Cosine Similarity on descriptions/tags/categories
- **Collaborative**: K-Nearest Neighbors on User×Product rating matrix
- **Explainable AI**: Every recommendation shows why it was suggested

---

## Project Structure

```
smartrecommend/
├── app.py                  # Main entry point + Auth pages
├── pages/
│   ├── home.py             # Home page with recommendations
│   ├── search.py           # Search & browse products
│   ├── product_detail.py   # Product detail + rating
│   ├── recommendations.py  # Full recommendations page
│   ├── wishlist.py         # User wishlist
│   ├── profile.py          # User profile & preferences
│   └── analytics.py        # Analytics dashboard
├── database/
│   └── db_setup.py         # SQLite schema + seeder
├── models/
│   └── recommendation_engine.py  # ML recommendation engine
├── utils/
│   ├── helpers.py          # Shared utility functions
│   └── styles.py           # Shared CSS
├── .streamlit/
│   └── config.toml         # Streamlit theme config
└── requirements.txt
```

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Demo login: `oluwavictor@gmail.com` / `demo123`

---

## Deploy to Streamlit Cloud

1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Click **Deploy**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit + Custom CSS |
| Database | SQLite |
| ML | scikit-learn (TF-IDF, KNN, Cosine Similarity) |
| Charts | Plotly |
| Auth | SHA-256 password hashing |

---

## Nigerian E-Commerce Context

- Prices displayed in Nigerian Naira (₦)
- Products relevant to Nigerian market (Tecno, Infinix included)
- Delivery and support features tailored for local context
