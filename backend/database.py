import os
import sqlite3
from sqlite3 import Connection
from typing import List

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")
DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
OFFICIAL_DATA_FILE = os.path.join(DATA_DIR, "Online Retail.xlsx")
PRODUCTS_CSV = os.path.join(DATA_DIR, "IntelliCart_product_catalog.csv")
USER_HISTORY_CSV = os.path.join(DATA_DIR, "IntelliCart_user_history.csv")


def _load_official_dataset() -> tuple[List[dict], List[dict], List[dict], List[dict]]:
    if not os.path.exists(OFFICIAL_DATA_FILE):
        return [], [], [], []

    df = pd.read_excel(OFFICIAL_DATA_FILE, engine="openpyxl")
    df = df.dropna(subset=["CustomerID", "StockCode", "Description"]).copy()
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Quantity"] = df["Quantity"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    product_groups = df.groupby(["StockCode", "Description"], as_index=False).agg(
        total_quantity=("Quantity", "sum"),
        avg_price=("UnitPrice", "mean"),
        sales=("Quantity", "sum"),
        country=("Country", "first"),
    )
    product_groups["product_id"] = range(1, len(product_groups) + 1)
    q_mean = product_groups["total_quantity"].mean()
    q_std = product_groups["total_quantity"].std() if product_groups["total_quantity"].std() > 0 else 1.0
    product_groups["rating"] = (
        ((product_groups["total_quantity"] - q_mean) / q_std) * 0.5 + 3.5
    ).clip(1.0, 5.0).round(2)
    product_groups["price"] = product_groups["avg_price"].round(2)
    product_groups["category"] = product_groups["country"].fillna("General")
    products = product_groups[
        ["product_id", "Description", "category", "Description", "price", "rating", "sales"]
    ].copy()
    products.columns = ["product_id", "name", "category", "description", "price", "rating", "sales"]
    products = products.to_dict(orient="records")

    users = []
    for user_id, group in df.groupby("CustomerID"):
        top_items = group["Description"].value_counts().head(3).index.tolist()
        preferences = ", ".join(top_items)
        users.append(
            {
                "user_id": int(user_id),
                "name": f"Customer {user_id}",
                "preferences": preferences,
            }
        )

    code_to_product_id = {
        code: pid
        for code, pid in zip(product_groups["StockCode"], product_groups["product_id"])
    }

    ratings = []
    rating_id = 1
    quantity_by_user_product = (
        df.groupby(["CustomerID", "StockCode"], as_index=False)["Quantity"].sum()
    )
    for _, row in quantity_by_user_product.iterrows():
        pid = code_to_product_id.get(row["StockCode"])
        if pid is None:
            continue
        rating_value = min(5, max(1, int(1 + row["Quantity"] // 5)))
        ratings.append(
            {
                "rating_id": rating_id,
                "user_id": int(row["CustomerID"]),
                "product_id": int(pid),
                "rating": rating_value,
            }
        )
        rating_id += 1

    views = []
    view_id = 1
    for _, row in df.sort_values("InvoiceDate").iterrows():
        pid = code_to_product_id.get(row["StockCode"])
        if pid is None:
            continue
        views.append(
            {
                "view_id": view_id,
                "user_id": int(row["CustomerID"]),
                "product_id": int(pid),
            }
        )
        view_id += 1

    return products, users, ratings, views

PRODUCTS = [
    {
        "product_id": 101,
        "name": "Wireless Gaming Mouse",
        "category": "Electronics",
        "description": "Ergonomic gaming mouse with RGB lighting and programmable buttons.",
        "price": 39.99,
        "rating": 4.6,
        "sales": 430,
    },
    {
        "product_id": 102,
        "name": "Noise Cancelling Headphones",
        "category": "Electronics",
        "description": "Over-ear headphones with active noise cancellation and long battery life.",
        "price": 129.99,
        "rating": 4.8,
        "sales": 335,
    },
    {
        "product_id": 103,
        "name": "4K Ultra HD Smart TV",
        "category": "Electronics",
        "description": "55-inch smart TV with streaming apps and voice control.",
        "price": 499.99,
        "rating": 4.5,
        "sales": 210,
    },
    {
        "product_id": 104,
        "name": "Running Shoes",
        "category": "Sportswear",
        "description": "Lightweight running shoes with breathable mesh and cushioned soles.",
        "price": 79.99,
        "rating": 4.4,
        "sales": 290,
    },
    {
        "product_id": 105,
        "name": "Smartphone Stand",
        "category": "Accessories",
        "description": "Adjustable desk phone stand for video calls and charging.",
        "price": 19.99,
        "rating": 4.3,
        "sales": 520,
    },
    {
        "product_id": 106,
        "name": "Laptop Sleeve",
        "category": "Accessories",
        "description": "Protective padded laptop sleeve for 13- to 15-inch notebooks.",
        "price": 24.99,
        "rating": 4.2,
        "sales": 225,
    },
    {
        "product_id": 107,
        "name": "Stainless Steel Water Bottle",
        "category": "Home",
        "description": "Insulated water bottle keeps drinks cold for 24 hours.",
        "price": 22.99,
        "rating": 4.7,
        "sales": 389,
    },
    {
        "product_id": 108,
        "name": "Bluetooth Speaker",
        "category": "Electronics",
        "description": "Portable Bluetooth speaker with deep bass and waterproof design.",
        "price": 59.99,
        "rating": 4.5,
        "sales": 310,
    },
    {
        "product_id": 109,
        "name": "Fitness Tracker",
        "category": "Wearables",
        "description": "Activity tracker with heart rate monitoring and sleep analytics.",
        "price": 49.99,
        "rating": 4.1,
        "sales": 260,
    },
    {
        "product_id": 110,
        "name": "Coffee Maker",
        "category": "Home",
        "description": "Automatic drip coffee maker with programmable timer.",
        "price": 89.99,
        "rating": 4.6,
        "sales": 175,
    },
]

USERS = [
    {"user_id": 1, "name": "Sophia", "preferences": "Electronics, Accessories"},
    {"user_id": 2, "name": "Noah", "preferences": "Sportswear, Home"},
    {"user_id": 3, "name": "Ava", "preferences": "Wearables, Electronics"},
    {"user_id": 4, "name": "Liam", "preferences": "Home, Accessories"},
    {"user_id": 5, "name": "Emma", "preferences": "Electronics, Home"},
]

RATINGS = [
    {"rating_id": 1, "user_id": 1, "product_id": 101, "rating": 5},
    {"rating_id": 2, "user_id": 1, "product_id": 102, "rating": 4},
    {"rating_id": 3, "user_id": 1, "product_id": 105, "rating": 5},
    {"rating_id": 4, "user_id": 2, "product_id": 104, "rating": 4},
    {"rating_id": 5, "user_id": 2, "product_id": 110, "rating": 5},
    {"rating_id": 6, "user_id": 3, "product_id": 109, "rating": 4},
    {"rating_id": 7, "user_id": 3, "product_id": 108, "rating": 4},
    {"rating_id": 8, "user_id": 4, "product_id": 106, "rating": 4},
    {"rating_id": 9, "user_id": 4, "product_id": 105, "rating": 5},
    {"rating_id": 10, "user_id": 5, "product_id": 103, "rating": 5},
    {"rating_id": 11, "user_id": 5, "product_id": 101, "rating": 4},
    {"rating_id": 12, "user_id": 5, "product_id": 108, "rating": 5},
]

VIEWS = [
    {"view_id": 1, "user_id": 1, "product_id": 101},
    {"view_id": 2, "user_id": 1, "product_id": 105},
    {"view_id": 3, "user_id": 2, "product_id": 104},
    {"view_id": 4, "user_id": 2, "product_id": 110},
    {"view_id": 5, "user_id": 3, "product_id": 109},
    {"view_id": 6, "user_id": 4, "product_id": 106},
    {"view_id": 7, "user_id": 5, "product_id": 103},
]


def _load_products_from_csv() -> List[dict]:
    if os.path.exists(PRODUCTS_CSV):
        df = pd.read_csv(PRODUCTS_CSV)
        return df.to_dict(orient="records")
    return PRODUCTS


def _load_history_from_csv() -> tuple[List[dict], List[dict]]:
    if os.path.exists(USER_HISTORY_CSV):
        df = pd.read_csv(USER_HISTORY_CSV)
        ratings = []
        views = []
        rating_id = 1
        view_id = 1
        for _, row in df.iterrows():
            event_type = str(row["event_type"]).lower()
            if event_type == "rating":
                ratings.append(
                    {
                        "rating_id": rating_id,
                        "user_id": int(row["user_id"]),
                        "product_id": int(row["product_id"]),
                        "rating": int(row["rating"]),
                    }
                )
                rating_id += 1
            if event_type in ["view", "click", "purchase"]:
                views.append(
                    {
                        "view_id": view_id,
                        "user_id": int(row["user_id"]),
                        "product_id": int(row["product_id"]),
                    }
                )
                view_id += 1
        return ratings, views
    return RATINGS, VIEWS


def create_connection() -> Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def initialize_database(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, description TEXT, price REAL, rating REAL, sales INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, preferences TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS ratings (rating_id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, rating INTEGER, FOREIGN KEY(user_id) REFERENCES users(user_id), FOREIGN KEY(product_id) REFERENCES products(product_id))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS views (view_id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, viewed_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(user_id), FOREIGN KEY(product_id) REFERENCES products(product_id))"
    )
    conn.commit()


def seed_data(conn: Connection) -> None:
    cursor = conn.cursor()
    existing = cursor.execute("SELECT COUNT(1) FROM products").fetchone()[0]
    if existing > 0:
        return

    if os.path.exists(OFFICIAL_DATA_FILE):
        products, users, ratings, views = _load_official_dataset()
    elif os.path.exists(PRODUCTS_CSV) or os.path.exists(USER_HISTORY_CSV):
        products = _load_products_from_csv()
        ratings, views = _load_history_from_csv()
        users = USERS
    else:
        products = PRODUCTS
        ratings = RATINGS
        views = VIEWS
        users = USERS

    cursor.executemany(
        "INSERT INTO products (product_id, name, category, description, price, rating, sales) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (p["product_id"], p["name"], p["category"], p["description"], p["price"], p["rating"], p["sales"])
            for p in products
        ],
    )
    cursor.executemany(
        "INSERT INTO users (user_id, name, preferences) VALUES (?, ?, ?)",
        [(u["user_id"], u["name"], u["preferences"]) for u in users],
    )
    cursor.executemany(
        "INSERT INTO ratings (rating_id, user_id, product_id, rating) VALUES (?, ?, ?, ?)",
        [(r["rating_id"], r["user_id"], r["product_id"], r["rating"]) for r in ratings],
    )
    cursor.executemany(
        "INSERT INTO views (view_id, user_id, product_id) VALUES (?, ?, ?)",
        [(v["view_id"], v["user_id"], v["product_id"]) for v in views],
    )
    conn.commit()


def load_table(conn: Connection, table_name: str) -> pd.DataFrame:
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def get_sample_data() -> None:
    conn = create_connection()
    initialize_database(conn)
    seed_data(conn)
    conn.close()
