# What To Do Next — Aleesha

## Setup
1. Pull the project folder
2. Create your venv and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install flask psycopg2-binary
   ```
3. Make sure PostgreSQL is running and the database exists:
   ```
   sudo -u postgres psql -c "CREATE DATABASE farmersmarket;"
   ```
4. Load the schema and seed data:
   ```
   psql -U postgres -h localhost -d farmersmarket -f schema.sql
   psql -U postgres -h localhost -d farmersmarket -f seed_data.sql
   ```
5. Run the app with `python app.py` and check localhost:5000 works

## Your Main Task: Create Order & OrderItem Seed Data

We need fake historical sales data so the predictive model has something to train on.

Create a file called `seed_orders.sql` with:

- **~150-200 Orders** spread across MarketIDs 1-25 (the past markets)
- Each Order picks a random CustomerID (1-15) and set Status to 'Completed'
- OrderDate should match the Market's date

- **1-5 OrderItems per Order** with:
  - ProductID from products that vendor actually sells
  - Qty between 1 and 6
  - PurchasePrice matching the product's Current_Price

### Make the data show patterns (this is important for the AI model):
- **Sunny days** = more sales than Rainy days
- **Special events** (Fall Festival, Holiday Market, etc.) = big spikes in sales
- **Seasonal stuff** — more fruit sold in fall, more seedlings in spring

This is the data that feeds into the Smart Restock predictions later.

## What's Already Done
- schema.sql — all 7 tables
- seed_data.sql — Customers, Vendors, Markets, Products, VendorMarket
- app.py — Flask app with basic routes
- templates/ — home page, product listing with search, vendor dashboard with add/delete
