import sqlite3
import os
import hashlib

# On Streamlit Cloud, use /tmp which persists across reruns within same session.
# For true persistence across restarts, we also write to a fixed absolute path.
def _get_db_path():
    # Try to use a persistent location
    candidates = [
        "/tmp/smartrecommend.db",          # Streamlit Cloud / Linux servers
        os.path.expanduser("~/smartrecommend.db"),  # Local fallback
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "smartrecommend.db"),
    ]
    for path in candidates:
        try:
            # Test write access
            conn = sqlite3.connect(path)
            conn.close()
            return path
        except Exception:
            continue
    return candidates[-1]

DB_PATH = _get_db_path()


def get_connection():
    # timeout=15 makes SQLite retry for up to 15s instead of raising
    # "database is locked" immediately if another connection briefly
    # holds a write lock (belt-and-braces alongside the toggle_wishlist fix).
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # Better concurrent access
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            avatar_url TEXT DEFAULT '',
            date_joined TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            category        TEXT NOT NULL,
            subcategory     TEXT DEFAULT '',
            price           REAL NOT NULL,
            original_price  REAL DEFAULT 0,
            description     TEXT DEFAULT '',
            image_url       TEXT DEFAULT '',
            rating          REAL DEFAULT 0,
            review_count    INTEGER DEFAULT 0,
            tags            TEXT DEFAULT '',
            in_stock        INTEGER DEFAULT 1,
            is_featured     INTEGER DEFAULT 0,
            is_trending     INTEGER DEFAULT 0,
            is_new_arrival  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS ratings (
            rating_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            product_id  INTEGER,
            rating      REAL,
            review_text TEXT DEFAULT '',
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id)    REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS user_activity (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            product_id  INTEGER,
            action      TEXT,
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id)    REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );

        CREATE TABLE IF NOT EXISTS wishlist (
            wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            product_id  INTEGER,
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id),
            FOREIGN KEY(user_id)    REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
    """)
    conn.commit()
    conn.close()


def seed_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    products = [
        # Smartphones
        ("Samsung Galaxy S24 Ultra 5G", "Smartphones", "Android", 1350000, 1500000,
         "200MP camera, 5000mAh battery, S Pen included, titanium frame, AI-powered features",
         "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400", 4.8, 124,
         "samsung,android,5g,camera,stylus", 1, 1, 1, 0),
        ("Apple iPhone 15 Pro Max", "Smartphones", "iOS", 1650000, 1800000,
         "48MP main camera, A17 Pro chip, titanium design, Action button, USB-C",
         "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400", 4.7, 99,
         "apple,iphone,ios,camera,5g", 1, 1, 1, 0),
        ("Google Pixel 8 Pro", "Smartphones", "Android", 890000, 950000,
         "50MP camera with AI enhancements, 7 years of updates, temperature sensor",
         "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400", 4.5, 67,
         "google,pixel,android,ai,camera", 1, 0, 1, 0),
        ("Samsung Galaxy A54", "Smartphones", "Android", 350000, 400000,
         "50MP triple camera, 5000mAh, Super AMOLED display, IP67 water resistant",
         "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400", 4.3, 213,
         "samsung,android,budget,camera", 1, 0, 0, 1),
        ("Tecno Phantom X2 Pro", "Smartphones", "Android", 280000, 320000,
         "60MP retractable portrait lens, 5160mAh, 45W fast charging, Dimensity 9000",
         "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400", 4.2, 156,
         "tecno,android,portrait,fast-charge", 1, 0, 0, 1),
        ("Infinix Zero 30 5G", "Smartphones", "Android", 175000, 200000,
         "108MP selfie camera, 4K video, 68W fast charging, AMOLED curved display",
         "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400", 4.1, 89,
         "infinix,android,selfie,5g,budget", 1, 0, 0, 1),
        # Laptops
        ("HP EliteBook 840 G10", "Laptops", "Business", 850000, 950000,
         "Intel Core i7-1365U, 16GB RAM, 512GB SSD, 14-inch FHD, Windows 11 Pro",
         "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400", 4.6, 98,
         "hp,laptop,business,intel,windows", 1, 1, 0, 0),
        ("MacBook Pro 14-inch M3", "Laptops", "Apple", 1450000, 1600000,
         "Apple M3 chip, 18GB unified memory, 512GB SSD, Liquid Retina XDR display",
         "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400", 4.9, 187,
         "apple,macbook,m3,laptop,creative", 1, 1, 1, 0),
        ("Lenovo IdeaPad 3 15", "Laptops", "Student", 285000, 320000,
         "Intel Core i5, 8GB RAM, 256GB SSD, 15.6-inch FHD, Windows 11 Home",
         "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400", 4.2, 445,
         "lenovo,laptop,student,budget,intel", 1, 0, 0, 1),
        ("Dell XPS 15", "Laptops", "Premium", 1250000, 1400000,
         "Intel Core i9, 32GB RAM, 1TB SSD, 4K OLED touch display, NVIDIA RTX 4060",
         "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400", 4.7, 134,
         "dell,laptop,premium,4k,gaming", 1, 1, 1, 0),
        ("Asus ROG Zephyrus G14", "Laptops", "Gaming", 980000, 1100000,
         "AMD Ryzen 9, 16GB RAM, 1TB SSD, NVIDIA RTX 4060, 165Hz display",
         "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400", 4.6, 76,
         "asus,rog,laptop,gaming,ryzen", 1, 1, 0, 0),
        ("Sony WH-1000XM5 Headphones", "Electronics", "Audio", 250000, 300000,
         "Industry-leading noise cancellation, 30-hour battery, multipoint connection",
         "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400", 4.7, 267,
         "sony,headphones,noise-cancellation,wireless,audio", 1, 1, 1, 0),
        ("Apple AirPods Pro 2nd Gen", "Electronics", "Audio", 320000, 380000,
         "Active noise cancellation, Adaptive Audio, Personalized Spatial Audio, MagSafe charging",
         "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400", 4.6, 145,
         "apple,airpods,noise-cancellation,wireless", 1, 0, 1, 0),
        ("Samsung Galaxy Buds2 Pro", "Electronics", "Audio", 180000, 220000,
         "24-bit Hi-Fi audio, intelligent ANC, 360 Audio, 18 hours total battery",
         "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400", 4.5, 73,
         "samsung,earbuds,anc,wireless,hi-fi", 1, 0, 0, 0),
        ("JBL Charge 5 Bluetooth Speaker", "Electronics", "Audio", 150000, 180000,
         "20 hours playtime, IP67 waterproof, JBL PartyBoost, built-in powerbank",
         "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400", 4.5, 312,
         "jbl,speaker,bluetooth,waterproof,portable", 1, 0, 1, 0),
        ("Apple Watch Series 9 GPS", "Electronics", "Smartwatches", 550000, 620000,
         "Double tap gesture, S9 chip, Always-On Retina display, 18h battery, health sensors",
         "https://images.unsplash.com/photo-1434493907317-a46b5bbe7834?w=400", 4.7, 87,
         "apple,smartwatch,health,fitness,gps", 1, 1, 1, 0),
        ("Samsung Galaxy Watch 6", "Electronics", "Smartwatches", 280000, 330000,
         "Advanced sleep coaching, body composition analysis, sapphire crystal glass",
         "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400", 4.4, 54,
         "samsung,smartwatch,health,sleep,android", 1, 0, 0, 1),
        ("Canon EOS R50 Mirrorless", "Electronics", "Cameras", 780000, 900000,
         "24.2MP APS-C sensor, 4K video, eye-tracking AF, compact and lightweight design",
         "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400", 4.6, 92,
         "canon,camera,mirrorless,4k,photography", 1, 0, 1, 0),
        ("Sony PlayStation 5", "Electronics", "Gaming", 650000, 750000,
         "Custom AMD GPU, 825GB SSD, 4K gaming, DualSense haptic controller",
         "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400", 4.8, 431,
         "sony,ps5,gaming,console,4k", 1, 1, 1, 0),
        # Home & Kitchen
        ("Samsung 55-inch QLED 4K TV", "Home & Kitchen", "TVs", 650000, 750000,
         "Quantum Dot technology, 120Hz, Smart TV, Alexa built-in, slim bezel design",
         "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=400", 4.6, 178,
         "samsung,tv,4k,qled,smart-tv", 1, 1, 0, 0),
        ("Dyson V15 Detect Vacuum", "Home & Kitchen", "Appliances", 480000, 560000,
         "Laser dust detection, HEPA filtration, 60 min runtime, LCD screen",
         "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", 4.5, 64,
         "dyson,vacuum,cordless,cleaning,home", 1, 0, 0, 1),
        ("Nespresso Vertuo Next", "Home & Kitchen", "Kitchen", 185000, 220000,
         "Centrifusion technology, 5 cup sizes, quick 30-second heat-up, WiFi enabled",
         "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400", 4.4, 123,
         "nespresso,coffee,kitchen,appliance", 1, 0, 0, 1),
        # Fashion
        ("Nike Air Zoom Pegasus 40", "Fashion", "Footwear", 120000, 145000,
         "Responsive cushioning, breathable mesh upper, durable rubber outsole, versatile running shoe",
         "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400", 4.5, 64,
         "nike,running,shoes,sports,fitness", 1, 0, 1, 0),
        ("Adidas Ultraboost 23", "Fashion", "Footwear", 135000, 160000,
         "BOOST midsole, Primeknit+ upper, Continental rubber outsole, energy return",
         "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400", 4.4, 98,
         "adidas,running,shoes,ultraboost,sports", 1, 0, 0, 0),
        ("Louis Vuitton Neverfull MM", "Fashion", "Bags", 850000, 950000,
         "Iconic monogram canvas, spacious interior, removable pouch, signature LV hardware",
         "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400", 4.7, 34,
         "louis-vuitton,bag,luxury,fashion,handbag", 1, 0, 0, 0),
        ("Ray-Ban Aviator Classic", "Fashion", "Eyewear", 85000, 100000,
         "Iconic pilot-frame design, crystal lenses, gold metal frame, UV400 protection",
         "https://images.unsplash.com/photo-1508296695146-257a814070b4?w=400", 4.6, 156,
         "rayban,sunglasses,aviator,fashion,eyewear", 1, 0, 0, 1),
        # Books
        ("Atomic Habits by James Clear", "Books", "Self-Help", 8500, 12000,
         "Build good habits, break bad ones. Learn proven system for remarkable results",
         "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400", 4.8, 2341,
         "habits,productivity,self-help,psychology", 1, 0, 1, 0),
        ("Rich Dad Poor Dad", "Books", "Finance", 7500, 10000,
         "What the rich teach their kids about money that the poor and middle class do not",
         "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=400", 4.7, 1876,
         "finance,money,investing,wealth,business", 1, 0, 0, 0),
        # Gaming
        ("Xbox Series X Console", "Gaming", "Consoles", 620000, 700000,
         "12 teraflops GPU, 1TB SSD, 4K gaming at 60fps, Quick Resume, Xbox Game Pass",
         "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400", 4.7, 289,
         "xbox,gaming,console,4k,microsoft", 1, 1, 1, 0),
        ("Razer BlackWidow V4 Keyboard", "Gaming", "Peripherals", 95000, 115000,
         "Razer Yellow mechanical switches, Chroma RGB, aluminum top plate, macro support",
         "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=400", 4.5, 143,
         "razer,keyboard,mechanical,gaming,rgb", 1, 0, 0, 1),
        ("Logitech G Pro X Superlight 2", "Gaming", "Peripherals", 65000, 80000,
         "Ultra-lightweight 60g mouse, HERO 2 sensor, 70 hour battery, PTFE feet",
         "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400", 4.8, 234,
         "logitech,mouse,gaming,wireless,lightweight", 1, 0, 1, 0),
        ("Samsung 45W Power Adapter", "Electronics", "Accessories", 35000, 45000,
         "Super Fast Charging 3.0, USB-C, compatible with Galaxy S series and Note series",
         "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400", 4.5, 39,
         "samsung,charger,fast-charge,usb-c,accessories", 1, 0, 0, 0),
        ("Spigen Tough Armor Case", "Electronics", "Accessories", 15000, 20000,
         "Dual layer protection, Air Cushion Technology, kickstand, military-grade tested",
         "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400", 4.5, 27,
         "spigen,case,protection,phone-case,accessories", 1, 0, 0, 0),
    ]

    c.executemany("""
        INSERT INTO products (name, category, subcategory, price, original_price,
            description, image_url, rating, review_count, tags, in_stock,
            is_featured, is_trending, is_new_arrival)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, products)

    # Seed demo user
    c.execute("""
        INSERT OR IGNORE INTO users (name, email, password)
        VALUES (?, ?, ?)
    """, ("Oluwa Victor", "oluwavictor@gmail.com", hash_password("demo123")))

    conn.commit()
    conn.close()


def seed_interactions():
    """Seed realistic user interactions for ML model."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_activity")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    import random
    random.seed(42)
    c.execute("SELECT user_id FROM users")
    users = [r[0] for r in c.fetchall()]
    c.execute("SELECT product_id FROM products")
    products = [r[0] for r in c.fetchall()]

    if not users or not products:
        conn.close()
        return

    actions = ["view", "click", "like", "wishlist", "purchase"]
    weights = [0.4, 0.25, 0.15, 0.12, 0.08]
    activities = []
    for uid in users:
        n = random.randint(5, 30)
        chosen = random.sample(products, min(n, len(products)))
        for pid in chosen:
            action = random.choices(actions, weights=weights)[0]
            activities.append((uid, pid, action))

    c.executemany(
        "INSERT INTO user_activity (user_id, product_id, action) VALUES (?,?,?)",
        activities
    )

    ratings_data = []
    for uid in users:
        n = random.randint(3, 15)
        chosen = random.sample(products, min(n, len(products)))
        for pid in chosen:
            rating = round(random.uniform(2.5, 5.0), 1)
            ratings_data.append((uid, pid, rating))

    c.executemany(
        "INSERT OR IGNORE INTO ratings (user_id, product_id, rating) VALUES (?,?,?)",
        ratings_data
    )

    conn.commit()
    conn.close()
