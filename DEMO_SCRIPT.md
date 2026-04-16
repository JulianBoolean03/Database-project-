 wl
 # Demo Script — Farmers Market (Database Demons)

**Length target:** 20 minutes
**Presenters:** Julian Robinson, Aleesha Exantus
**URL:** http://127.0.0.1:5000

---

## Pre-demo setup (do this BEFORE hitting record)

```bash
# 1. Start Postgres if not running
sudo service postgresql start

# 2. Reset data to a clean state (optional but recommended)
PGPASSWORD=newpassword psql -U postgres -h localhost -d farmersmarket -f schema.sql
PGPASSWORD=newpassword psql -U postgres -h localhost -d farmersmarket -f seed_data.sql
PGPASSWORD=newpassword psql -U postgres -h localhost -d farmersmarket -f seed_orders.sql

# 3. Start the app
source venv/bin/activate
python app.py

# 4. Open two browser tabs side by side:
#    Tab A: http://127.0.0.1:5000
#    Tab B: a terminal running `psql` for the SQL-level demos
```

---

## Roles

- **[J] Julian** — code walkthrough: schema.sql, app.py, predictor.py. Explains *how it works*.
- **[A] Aleesha** — app walkthrough: clicking through the browser. Demonstrates *what the user sees*.

The pattern for each section: **[J] shows the code for ~30 sec → [A] demos the feature live**. This keeps the audience from getting code-fatigued.

## Timing breakdown

| Section | Time | Rubric coverage | Lead |
|---|---|---|---|
| 1. Introduction & schema | 2 min | — | [J] |
| 2. Basic: INSERT | 3 min | Insert records | [J] → [A] |
| 3. Basic: SEARCH | 2 min | Search + list | [J] → [A] |
| 4. Basic: JOIN + AGGREGATE queries | 4 min | Interesting queries | [J] → [A] |
| 5. Basic: UPDATE | 1 min | Update records | [J] → [A] |
| 6. Basic: DELETE | 1 min | Delete records | [A] (code already shown) |
| 7. Advanced: Smart Restock | 6 min | Advanced function | [J] → [A] |
| 8. Wrap-up | 1 min | — | both |

---

## 1. Introduction (2 min) — [J] leads

### Opening line — [A]
> "Hi, we're Database Demons — I'm Aleesha, this is Julian. Our project is a farmers market platform with two sides: a customer storefront and a vendor dashboard. The database is PostgreSQL, the backend is Flask, and the advanced function is a Smart Restock assistant powered by scikit-learn linear regression. Julian's going to walk through the code, I'll walk through the app."

### Schema walkthrough — [J]
Open `schema.sql` in neovim. Tip: `:set number` to show line numbers, then `30G` to jump to line 30, etc.

**Lines 16–20 — Customer**
> "Customer is simple — ID, name, email. Email is UNIQUE because customers log in with it."

**Lines 23–27 — Vendor**
> "Vendors have a name and a free-text profile description shown on their dashboard."

**Lines 30–36 — Market** ← spend a beat here
> "Market is the most important table for our advanced function. Each row is one market day, and crucially we store **WeatherCondition** and **IsSpecialEvent** — those two columns are the features our ML model uses to predict demand."

**Lines 39–44 — Product**
> "Products belong to a vendor. The CHECK constraint on Current_Price forces it to be positive — that's one of our integrity constraints."

**Lines 47–51 — VendorMarket**
> "VendorMarket is our associative entity for the many-to-many relationship — not every vendor attends every market. Composite primary key is both foreign keys."

**Lines 54–60 — Order**
> "An Order ties a Customer to a Market on a specific date, with a Status column we default to 'Pending'."

**Lines 63–70 — OrderItem** ← spend a beat here too
> "OrderItem has a composite primary key — (ItemNo, OrderID) — and stores **PurchasePrice** separately from Product.Current_Price. That's intentional denormalization: if a vendor raises prices tomorrow, yesterday's sales records stay accurate."

### Closing line for Section 1
> "That whole chain — OrderItem joins back to Order joins back to Market's weather and event columns — is the JOIN path our machine learning pipeline uses to build training data."

---

## 2. Basic Function #1 — INSERT (3 min)

### [J] — Code first (~45s)
Open `app.py` and jump to the `checkout()` function (search `def checkout`, around line 140).
> "Here's what happens when a customer places an order. We grab the next upcoming market, insert a row into the Order table with `RETURNING OrderID` so we know the new ID, then loop through the cart and insert each OrderItem. The whole thing is wrapped in a transaction — `conn.autocommit = False` up here, `conn.commit()` at the end — so a partial order can't leave orphaned rows. We also call `predictor.reset_model()` so the ML model retrains on the new data."

Then scroll to `add_product()` (around line 230).
> "Vendor insert is simpler — one INSERT, parameterized query to prevent SQL injection, done."

### [A] — Live demo (~2 min)

**Customer order:**
1. Click **Login** → enter `marcus.j@email.com` → submit
2. Click **Products** → search `honey` → add 2 jars of Wildflower Honey to cart
3. Search `bread` → add 1 Sourdough Loaf
4. Click **Cart** → Place Order
5. Point at the flash message: "Order #NNN placed for market on 2026-04-18"

Prove it in Postgres (Tab B):
```sql
SELECT OrderID, CustomerID, MarketID, Status FROM "Order"
WHERE Status = 'Pending';
SELECT * FROM OrderItem WHERE OrderID = (last_id_above);
```

**Vendor adds a product:**
1. Nav → Vendors → Green Acres Farm → Dashboard
2. Bottom form: add `Purple Heirloom Tomato` at `$4.75`
3. Row appears immediately

---

## 3. Basic Function #2 — SEARCH & LIST (2 min)

### [J] — Code (~20s)
Open `app.py`, jump to `def products()` (around line 80).
> "The search hits two columns with ILIKE for case-insensitive matching, and it joins to the Vendor table so users can search by product name OR vendor name. Parameterized — no injection risk."

### [A] — Demo (~1:30)
1. Nav → Products
2. Type `berry` → returns Strawberries, Blueberries, Blackberries
3. Clear, type `sunny` → returns all Sunny Side Orchards items (matched by vendor, not product)

---

## 4. Basic Function #3 — Interesting Queries (JOIN + AGGREGATE) (4 min)

### [J] — Code walkthrough (~1:30)
Open `app.py` and jump to `def reports()` (around line 260). Walk through each of the three SQL queries below, pointing at the actual code on screen. Call out the key pieces: FROM/JOIN lines, GROUP BY, aggregates.

### [A] — Demo (~2:30)
Click **Reports** in the nav. Walk through all three cards:

### Query 1 — Top 10 Best-Selling Products (JOIN 3 tables + aggregate)
```sql
SELECT p.Name, v.Name AS vendor, SUM(oi.Qty) AS units_sold,
       SUM(oi.Qty * oi.PurchasePrice) AS revenue
FROM OrderItem oi
JOIN Product p ON oi.ProductID = p.ProductID
JOIN Vendor  v ON p.VendorID   = v.VendorID
GROUP BY p.Name, v.Name
ORDER BY units_sold DESC LIMIT 10;
```
**Talking point:** "Three-table join plus aggregate — this answers 'which items move fastest across all markets?'"

### Query 2 — Revenue by Weather (JOIN + aggregate)
```sql
SELECT m.WeatherCondition, COUNT(DISTINCT o.OrderID) AS orders,
       SUM(oi.Qty * oi.PurchasePrice) AS revenue
FROM OrderItem oi
JOIN "Order" o ON oi.OrderID = o.OrderID
JOIN Market  m ON o.MarketID = m.MarketID
GROUP BY m.WeatherCondition
ORDER BY revenue DESC;
```
**Talking point:** "Sunny markets generate far more revenue than rainy ones. This is exactly the signal our ML model will exploit — keep this in mind for the advanced function."

### Query 3 — Vendor Leaderboard
```sql
SELECT v.Name, COUNT(DISTINCT p.ProductID), SUM(oi.Qty),
       SUM(oi.Qty * oi.PurchasePrice) AS revenue
FROM Vendor v
JOIN Product   p  ON v.VendorID  = p.VendorID
JOIN OrderItem oi ON p.ProductID = oi.ProductID
GROUP BY v.Name ORDER BY revenue DESC;
```

---

## 5. Basic Function #4 — UPDATE (1 min)

### [J] — Code (~15s)
Point at `update_product()` in `app.py`.
> "Parameterized UPDATE, filtered by both ProductID and VendorID so one vendor can't edit another's products. Retrains the model after the write."

### [A] — Demo (~45s)
1. Vendor dashboard for Green Acres Farm
2. On any row, change price in the inline input → click **Update**
3. Flash confirms, row reflects new price
4. **Tab B:** `SELECT Current_Price FROM Product WHERE ProductID = X;` — matches

---

## 6. Basic Function #5 — DELETE (1 min) — [A] leads (code is one-liner)

1. Same vendor dashboard
2. Delete the "Purple Heirloom Tomato" we added in Section 2
3. Row disappears
4. **Tab B:** `SELECT COUNT(*) FROM Product WHERE Name = 'Purple Heirloom Tomato';` returns 0

> "[A] Same pattern as UPDATE — parameterized DELETE filtered by vendor. Julian already showed you the shape of these write routes."

---

## 7. Advanced Function — Smart Restock (6 min)

This is where you earn the advanced-function points. Spend real time here.

### 7a. Frame the problem — [A] (30s)
> "Vendors need to know how much to bring to each market. Bringing too little means lost sales; bringing too much means spoilage. Currently they guess based on experience. We built a predictive model that ingests their sales history and upcoming market conditions to recommend stock levels."

### 7b. Show the data pipeline — [J] (2 min)
Open `predictor.py`. Walk through in this order:
- **`_load_history()`** (line ~30) → "This is the SQL aggregation — joins OrderItem to Order to Market, groups by product and market, sums the quantities. Only pulls past markets."
- **`_featurize()`** (line ~55) → "Feature engineering in pandas. Weather becomes 3 one-hot columns, location becomes 2, we add is_event, month, and one-hot encode the product. The model learns per-product baselines adjusted by conditions."
- **`DemandModel.train()`** (line ~85) → "Standard scikit-learn fit. We also cache the historical average per product so we can compute the High Demand / Overstock flags."
- **`predict_for_vendor_market()`** (line ~100) → "For each of the vendor's products we build a synthetic row with the upcoming market's conditions, run predict, and flag it."

### 7c. Run predictions live — [A] (2 min)
1. Nav → Vendors → Green Acres Farm → **Smart Restock →**
2. Market dropdown shows 4 upcoming markets
3. Select **2026-04-18 — Riverside Park (Sunny, Special Event)**
4. Point at badges: **High Demand** (red), **Normal** (grey), **Potential Overstock** (yellow)
5. Note the R² and training row count at the top

### 7d. Prove the model learns weather — [A] (1 min)
Switch the dropdown:
- **2026-04-11 — Downtown Plaza (Cloudy)** → predictions drop across the board
- Back to **04-18 (Sunny + Special Event)** → numbers jump

> "[A] The model learned the pattern we saw in Query 2 — Sunny markets and special events move more product. Same vendor, same products, only the market conditions changed."

### 7e. Make the case for "advanced" — [J] (30s)
Explicitly tick the rubric boxes:
- **Useful for users** — vendors save money by not over-packing or under-stocking
- **Technically challenging** — multi-stage pipeline: SQL aggregation → pandas feature engineering → sklearn training → Flask integration with auto-retrain on data changes
- **Novel for the domain** — most farmers market apps are static storefronts; ML-driven restock is uncommon at this scale

---

## 8. Wrap-up (1 min)

- **[J]** "GitHub link is in the report: `github.com/JulianBoolean03/Database-project-`"
- **[A]** "Team split: Julian handled the backend, database, and ML pipeline; I designed the schema and built the seed data that made the model trainable."
- **Both:** "Thanks — happy to answer questions."

---

## Recovery if something breaks on camera

| Problem | Quick fix |
|---|---|
| DB connection refused | `sudo service postgresql start` |
| Smart Restock shows error "No historical sales" | `psql -f seed_orders.sql` |
| R² looks different each run | Expected — seed data was randomly generated once and is now fixed |
| Cart won't checkout | Check you're logged in (top-right says "Hi, ...") |
| Port 5000 busy | `kill $(lsof -ti:5000)` then restart |
