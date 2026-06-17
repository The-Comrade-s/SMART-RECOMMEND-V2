import streamlit as st
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_setup import get_connection, hash_password


def login_user(email: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def register_user(name: str, email: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password) VALUES (?,?,?)",
            (name, email, hash_password(password))
        )
        conn.commit()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        return dict(user), None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Email already registered"


def get_products(category=None, search=None, min_price=None, max_price=None,
                 min_rating=None, sort_by="popular", limit=50):
    conn = get_connection()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if category and category != "All":
        query += " AND category=?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)"
        s = f"%{search}%"
        params += [s, s, s]
    if min_price is not None:
        query += " AND price>=?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price<=?"
        params.append(max_price)
    if min_rating:
        query += " AND rating>=?"
        params.append(min_rating)

    sort_map = {
        "popular": "review_count DESC",
        "rating": "rating DESC",
        "price_low": "price ASC",
        "price_high": "price DESC",
        "newest": "product_id DESC"
    }
    query += f" ORDER BY {sort_map.get(sort_by, 'review_count DESC')} LIMIT ?"
    params.append(limit)

    import pandas as pd
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_product_by_id(product_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def track_activity(user_id: int, product_id: int, action: str):
    if not user_id:
        return
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_activity (user_id, product_id, action) VALUES (?,?,?)",
        (user_id, product_id, action)
    )
    conn.commit()
    conn.close()


def toggle_wishlist(user_id: int, product_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT wishlist_id FROM wishlist WHERE user_id=? AND product_id=?",
              (user_id, product_id))
    existing = c.fetchone()
    if existing:
        c.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?",
                  (user_id, product_id))
        added = False
    else:
        c.execute("INSERT INTO wishlist (user_id, product_id) VALUES (?,?)",
                  (user_id, product_id))
        track_activity(user_id, product_id, "wishlist")
        added = True
    conn.commit()
    conn.close()
    return added


def is_in_wishlist(user_id: int, product_id: int):
    if not user_id:
        return False
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",
              (user_id, product_id))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_wishlist(user_id: int):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT p.*, w.timestamp as added_at FROM wishlist w
        JOIN products p ON w.product_id = p.product_id
        WHERE w.user_id=? ORDER BY w.timestamp DESC
    """, conn, params=(user_id,))
    conn.close()
    return df


def get_user_stats(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(DISTINCT product_id) FROM user_activity WHERE user_id=? AND action='view'",
              (user_id,))
    stats["viewed"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM wishlist WHERE user_id=?", (user_id,))
    stats["wishlist"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM ratings WHERE user_id=?", (user_id,))
    stats["ratings"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM user_activity WHERE user_id=? AND action='purchase'",
              (user_id,))
    stats["orders"] = c.fetchone()[0]

    conn.close()
    return stats


def get_viewed_product_ids(user_id: int, limit: int = 20):
    if not user_id:
        return []
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT product_id FROM user_activity
        WHERE user_id=? ORDER BY timestamp DESC LIMIT ?
    """, (user_id, limit))
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids


def format_price(price: float) -> str:
    return f"₦{price:,.0f}"


def render_stars(rating: float) -> str:
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty


def get_categories():
    return ["All", "Smartphones", "Laptops", "Electronics", "Fashion",
            "Home & Kitchen", "Books", "Gaming"]


def get_analytics_data():
    conn = get_connection()
    import pandas as pd

    cat_df = pd.read_sql_query("""
        SELECT p.category, COUNT(*) as interactions
        FROM user_activity ua JOIN products p ON ua.product_id = p.product_id
        GROUP BY p.category ORDER BY interactions DESC
    """, conn)

    top_products = pd.read_sql_query("""
        SELECT p.name, p.category, COUNT(*) as views, p.rating, p.price
        FROM user_activity ua JOIN products p ON ua.product_id = p.product_id
        WHERE ua.action = 'view'
        GROUP BY p.product_id ORDER BY views DESC LIMIT 10
    """, conn)

    trending = pd.read_sql_query("""
        SELECT p.name, COUNT(*) as cnt FROM user_activity ua
        JOIN products p ON ua.product_id = p.product_id
        WHERE ua.action IN ('like','wishlist','purchase')
        GROUP BY p.product_id ORDER BY cnt DESC LIMIT 5
    """, conn)

    conn.close()
    return cat_df, top_products, trending
