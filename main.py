from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL)

app = FastAPI(title="CodeVector Product Backend")


@app.get("/")
def root():
    return {"message": "Backend is running successfully"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    return {"database_connected": result == 1}


@app.get("/create-table")
def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price NUMERIC(10,2) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_table_query))

    return {"message": "products table created successfully"}


@app.get("/create-index")
def create_index():
    query = """
    CREATE INDEX IF NOT EXISTS idx_products_updated_id
    ON products (updated_at DESC, id DESC);
    """
    with engine.begin() as conn:
        conn.execute(text(query))
    return {"message": "index created successfully"}


@app.get("/clear-products")
def clear_products():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM products"))

    return {"message": "all products deleted successfully"}


@app.get("/products")
def get_products(
    limit: int = Query(20, le=100),
    cursor_updated_at: str | None = None,
    cursor_id: int | None = None
):
    base_query = """
    SELECT id, name, category, price, created_at, updated_at
    FROM products
    """

    params = {"limit": limit}
    where_clause = ""

    if cursor_updated_at and cursor_id:
        where_clause = """
        WHERE (updated_at, id) < (:cursor_updated_at, :cursor_id)
        """
        params["cursor_updated_at"] = cursor_updated_at
        params["cursor_id"] = cursor_id

    final_query = f"""
    {base_query}
    {where_clause}
    ORDER BY updated_at DESC, id DESC
    LIMIT :limit
    """

    with engine.connect() as conn:
        rows = conn.execute(text(final_query), params).mappings().all()

    products = [dict(row) for row in rows]

    next_cursor = None
    if products:
        last_product = products[-1]
        next_cursor = {
            "cursor_updated_at": str(last_product["updated_at"]),
            "cursor_id": last_product["id"]
        }

    return {
        "count": len(products),
        "products": products,
        "next_cursor": next_cursor
    }


@app.post("/simulate-updates")
def simulate_updates():
    update_query = """
    UPDATE products
    SET updated_at = NOW()
    WHERE id IN (
        SELECT id
        FROM products
        ORDER BY RANDOM()
        LIMIT 50
    )
    """

    insert_query = """
    INSERT INTO products (name, category, price, created_at, updated_at)
    SELECT
        'New Product ' || gs,
        (ARRAY['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty', 'Toys'])[floor(random() * 7 + 1)],
        round((random() * 4900 + 100)::numeric, 2),
        NOW(),
        NOW()
    FROM generate_series(1, 50) AS gs;
    """

    with engine.begin() as conn:
        conn.execute(text(update_query))
        conn.execute(text(insert_query))

    return {"message": "50 products updated and 50 new products inserted"}
