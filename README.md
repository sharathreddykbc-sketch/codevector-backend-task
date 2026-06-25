# CodeVector Backend Task

FastAPI + PostgreSQL backend for product listing with **cursor-based pagination** and **simulate updates** support.

## Features
- FastAPI backend
- PostgreSQL database connection using SQLAlchemy
- Create products table
- Create index for efficient pagination
- Clear all products
- Cursor-based pagination using `updated_at` and `id`
- Simulate updates by:
  - updating random products
  - inserting new products

## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Neon DB
- Uvicorn

## API Endpoints

### `GET /`
Check if backend is running.

### `GET /db-test`
Check database connection.

### `GET /create-table`
Create the `products` table.

### `GET /create-index`
Create index on `(updated_at, id)`.

### `GET /clear-products`
Delete all products from the table.

### `GET /products`
Fetch products with cursor-based pagination.

#### Query params:
- `limit` → number of products to fetch
- `cursor_updated_at` → timestamp cursor
- `cursor_id` → product id cursor

### `POST /simulate-updates`
- Updates 50 random products
- Inserts 50 new products

## Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
