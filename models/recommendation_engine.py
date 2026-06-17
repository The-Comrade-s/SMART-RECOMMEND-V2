import sqlite3
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_setup import get_connection


class RecommendationEngine:
    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words="english", max_features=500)
        self.content_matrix = None
        self.product_ids = []
        self.products_df = None
        self.collab_model = None
        self.user_product_matrix = None
        self._build()

    def _load_products(self):
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        return df

    def _build(self):
        self.products_df = self._load_products()
        if self.products_df.empty:
            return

        self.product_ids = self.products_df["product_id"].tolist()

        # Content features
        self.products_df["features"] = (
            self.products_df["name"].fillna("") + " " +
            self.products_df["category"].fillna("") + " " +
            self.products_df["subcategory"].fillna("") + " " +
            self.products_df["description"].fillna("") + " " +
            self.products_df["tags"].fillna("")
        )
        self.content_matrix = self.tfidf.fit_transform(self.products_df["features"])

        # Collaborative filtering
        conn = get_connection()
        try:
            ratings_df = pd.read_sql_query("SELECT user_id, product_id, rating FROM ratings", conn)
            conn.close()
            if len(ratings_df) > 5:
                pivot = ratings_df.pivot_table(
                    index="user_id", columns="product_id", values="rating", fill_value=0
                )
                self.user_product_matrix = pivot
                self.collab_model = NearestNeighbors(n_neighbors=5, metric="cosine")
                self.collab_model.fit(pivot.values)
        except Exception:
            conn.close()

    def get_content_recommendations(self, product_id: int, n: int = 6):
        if self.content_matrix is None or product_id not in self.product_ids:
            return self._get_popular(n)
        idx = self.product_ids.index(product_id)
        sim_scores = cosine_similarity(self.content_matrix[idx], self.content_matrix).flatten()
        sim_scores[idx] = 0
        top_indices = sim_scores.argsort()[-n:][::-1]
        recs = []
        for i in top_indices:
            row = self.products_df.iloc[i]
            recs.append({
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "image_url": row["image_url"],
                "rating": row["rating"],
                "review_count": row["review_count"],
                "score": float(sim_scores[i]),
                "reason": "Similar product features and category"
            })
        return recs

    def get_hybrid_recommendations(self, user_id: int, viewed_ids: list, n: int = 8):
        """Hybrid: 0.6 content + 0.4 collaborative."""
        if self.products_df is None or self.products_df.empty:
            return self._get_popular(n)

        n_products = len(self.products_df)
        content_scores = np.zeros(n_products)

        for pid in viewed_ids[-5:]:
            if pid in self.product_ids:
                idx = self.product_ids.index(pid)
                sims = cosine_similarity(self.content_matrix[idx], self.content_matrix).flatten()
                content_scores += sims

        if content_scores.max() > 0:
            content_scores = content_scores / content_scores.max()

        collab_scores = np.zeros(n_products)
        if self.collab_model and self.user_product_matrix is not None:
            try:
                if user_id in self.user_product_matrix.index:
                    user_vec = self.user_product_matrix.loc[user_id].values.reshape(1, -1)
                    distances, indices = self.collab_model.kneighbors(user_vec, n_neighbors=5)
                    for i, dist in zip(indices[0], distances[0]):
                        neighbor_vec = self.user_product_matrix.iloc[i].values
                        weight = 1 - dist
                        for j, val in enumerate(neighbor_vec):
                            pid = self.user_product_matrix.columns[j]
                            if pid in self.product_ids:
                                pos = self.product_ids.index(pid)
                                collab_scores[pos] += weight * val
                    if collab_scores.max() > 0:
                        collab_scores = collab_scores / collab_scores.max()
            except Exception:
                pass

        hybrid = 0.6 * content_scores + 0.4 * collab_scores

        # Zero out already viewed
        for pid in viewed_ids:
            if pid in self.product_ids:
                idx = self.product_ids.index(pid)
                hybrid[idx] = 0

        top_indices = hybrid.argsort()[-n:][::-1]
        recs = []
        for i in top_indices:
            if hybrid[i] <= 0:
                continue
            row = self.products_df.iloc[i]
            reasons = self._build_reasons(
                content_scores[i], collab_scores[i], viewed_ids, int(row["product_id"])
            )
            recs.append({
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "subcategory": row.get("subcategory", ""),
                "price": row["price"],
                "original_price": row.get("original_price", 0),
                "image_url": row["image_url"],
                "rating": row["rating"],
                "review_count": row["review_count"],
                "score": float(hybrid[i]),
                "confidence": min(95, int(50 + hybrid[i] * 50)),
                "reasons": reasons,
                "in_stock": row.get("in_stock", 1)
            })
        if len(recs) < n:
            recs += self._get_popular(n - len(recs), exclude=viewed_ids + [r["product_id"] for r in recs])
        return recs[:n]

    def _build_reasons(self, content_score, collab_score, viewed_ids, product_id):
        reasons = []
        if content_score > 0.3:
            reasons.append("You viewed similar products")
        if collab_score > 0.2:
            reasons.append("Users with similar interests bought this")
        if len(viewed_ids) > 2:
            reasons.append("Matches your browsing patterns")
        if not reasons:
            reasons.append("Trending in your preferred categories")
        return reasons

    def _get_popular(self, n: int, exclude: list = None):
        df = self.products_df.copy()
        if exclude:
            df = df[~df["product_id"].isin(exclude)]
        df = df.sort_values("review_count", ascending=False).head(n)
        result = []
        for _, row in df.iterrows():
            result.append({
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "subcategory": row.get("subcategory", ""),
                "price": row["price"],
                "original_price": row.get("original_price", 0),
                "image_url": row["image_url"],
                "rating": row["rating"],
                "review_count": row["review_count"],
                "score": 0.5,
                "confidence": 72,
                "reasons": ["Top rated by users like you", "High popularity"],
                "in_stock": row.get("in_stock", 1)
            })
        return result

    def get_user_preferences(self, user_id: int):
        conn = get_connection()
        try:
            df = pd.read_sql_query("""
                SELECT p.category, COUNT(*) as cnt
                FROM user_activity ua
                JOIN products p ON ua.product_id = p.product_id
                WHERE ua.user_id = ?
                GROUP BY p.category ORDER BY cnt DESC
            """, conn, params=(user_id,))
            conn.close()
            if df.empty:
                return {}
            total = df["cnt"].sum()
            return {row["category"]: round(row["cnt"] / total * 100) for _, row in df.iterrows()}
        except Exception:
            conn.close()
            return {}

    def get_recommendation_accuracy(self, user_id: int):
        """Simulated accuracy score based on user activity."""
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM user_activity WHERE user_id=?", (user_id,))
            activity_count = c.fetchone()[0]
            conn.close()
            base = 75
            bonus = min(20, activity_count * 0.5)
            return int(base + bonus)
        except Exception:
            conn.close()
            return 78
