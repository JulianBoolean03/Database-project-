# Report Outline — Farmers Market Platform

**Team:** Database Demons (Julian Robinson, Aleesha Exantus)
**Target:** 5–10 single-column pages
**Delivery:** fill in the bullets below, paste into Word/Google Docs, add screenshots

---

## 1. Introduction (~1 page)

### What is the application?
- A digital platform for a local farmers market with two user roles:
  - **Customers** browse products, search, add to cart, and place orders for upcoming market days
  - **Vendors** manage their product catalogue and use a "Smart Restock" forecasting tool to decide how much inventory to bring to each market

### Why this application (motivation)?
- Local food systems are underserved by tech — most vendors still operate on spreadsheets or nothing at all
- Weather and seasonality have outsized effects on sales but are rarely formalized into planning
- Combines **transactional CRUD** (bread-and-butter DB work) with **predictive analytics** (stretches the course material into ML territory)
- Our two-sided design means the same database powers both a consumer-facing UI and an analyst-facing tool

### Key components
- PostgreSQL 16 relational database (7 tables)
- Flask web backend (Python)
- HTML / Bootstrap 5 frontend with session-based auth, cart, and checkout
- **Advanced function:** Smart Restock demand forecaster using pandas + scikit-learn Linear Regression

---

## 2. Database Details (~2 pages)

### ER Diagram
**TODO:** draw in dbdiagram.io or draw.io, export PNG, insert here.
Entities: Customer, Vendor, Market, Product, Order, OrderItem
Relationships:
- Customer 1—N Order
- Market  1—N Order
- Order   1—N OrderItem
- Product 1—N OrderItem
- Vendor  1—N Product
- Vendor  M—N Market (through VendorMarket associative entity)

### Relational Model
```
Customer     (CustomerID PK, Name, Email UNIQUE)
Vendor       (VendorID PK, Name, ProfileInfo)
Market       (MarketID PK, Date, Location, WeatherCondition, IsSpecialEvent)
Product      (ProductID PK, VendorID FK→Vendor, Name, Current_Price)
Order        (OrderID PK, CustomerID FK→Customer, MarketID FK→Market, OrderDate, Status)
OrderItem    (ItemNo, OrderID FK→Order, ProductID FK→Product, PurchasePrice, Qty)
              PRIMARY KEY (ItemNo, OrderID)
VendorMarket (VendorID FK→Vendor, MarketID FK→Market)
              PRIMARY KEY (VendorID, MarketID)
```

### Functional Dependencies & Normalization
Walk through each table:

- **Customer:** `CustomerID → Name, Email`; `Email → CustomerID` (Email is a superkey by UNIQUE constraint). In **BCNF**.
- **Vendor:** `VendorID → Name, ProfileInfo`. Single non-key attribute group, no partial deps. **BCNF**.
- **Market:** `MarketID → Date, Location, WeatherCondition, IsSpecialEvent`. Only the PK determines all attributes. **BCNF**.
- **Product:** `ProductID → VendorID, Name, Current_Price`. **BCNF** (VendorID is a foreign key, not a determinant of other Product attributes).
- **Order:** `OrderID → CustomerID, MarketID, OrderDate, Status`. **BCNF**.
- **OrderItem:** `(ItemNo, OrderID) → ProductID, PurchasePrice, Qty`. Composite PK, every attribute determined by the whole key. **BCNF**. Note: `PurchasePrice` is intentionally denormalized — it captures the price at the time of sale, not the current price (which can change).
- **VendorMarket:** Pure associative entity, PK = both FKs. **BCNF**.

### Other Constraints
- `Customer.Email UNIQUE NOT NULL`
- `Product.Current_Price > 0` (CHECK)
- `OrderItem.Qty > 0` (CHECK)
- All foreign keys enforce referential integrity
- `Market.IsSpecialEvent DEFAULT FALSE`, `Order.Status DEFAULT 'Pending'`

---

## 3. Functionality Details (~2 pages)

### Basic Functions
| # | Function | How it's implemented |
|---|---|---|
| 1 | **Insert** — Customer places order | `POST /cart/checkout` wraps Order + OrderItem inserts in a transaction; rolls back on failure |
| 1b | **Insert** — Vendor adds product | `POST /vendor/<id>/add` |
| 2 | **Search** | `GET /products?search=` using ILIKE with JOIN to Vendor |
| 3 | **Interesting Queries** | `/reports` page — 3 queries, see SQL below |
| 4 | **Update** | `POST /vendor/<id>/update/<pid>` — inline price edit |
| 5 | **Delete** | `POST /vendor/<id>/delete/<pid>` |

Paste the 3 report queries here verbatim (from `app.py:reports()`) and explain each:
1. **Best-sellers** — 3-way JOIN + SUM aggregate
2. **Revenue by weather** — 3-way JOIN + GROUP BY categorical + COUNT DISTINCT
3. **Vendor leaderboard** — 3-way JOIN + multiple aggregates

### Advanced Function — Smart Restock
**Goal:** predict per-product demand for each upcoming market given weather, location, event status, and month, then flag vendors' inventory as High Demand / Normal / Potential Overstock.

**Pipeline:**
1. **SQL feature extraction** — aggregate `SUM(Qty)` per (product, past market) joining OrderItem ⋈ Order ⋈ Market
2. **Feature engineering (pandas)** — one-hot encode weather (3 cols), location (2 cols), boolean for is_special_event, numeric month, one-hot product_id
3. **Model training (scikit-learn)** — `LinearRegression` fit on ~400 training rows; R² reported to the user
4. **Prediction** — for each product in the selected vendor's catalogue, build a synthetic row with the upcoming market's features, predict Qty
5. **Flagging** — compare prediction to historical per-product average; `> 1.3×` → High Demand, `< 0.7×` → Potential Overstock, else Normal
6. **Auto-retrain** — model invalidates and retrains when new orders, products, or price changes land

**Why it qualifies as advanced:**
- **Technical depth:** multi-stage ETL → ML → integration (not something you build in an afternoon)
- **Real utility:** solves a concrete vendor pain point (over/under-stocking)
- **Novelty for the domain:** most farmers-market apps are static catalogues

---

## 4. Implementation Details (~2 pages)

### Languages & Platform
- **Database:** PostgreSQL 16
- **Backend:** Python 3.12 + Flask 3
- **Frontend:** HTML5, Bootstrap 5 (CDN), vanilla JS
- **ML:** pandas 3, scikit-learn 1.8
- **DB driver:** psycopg2-binary

### Architecture
```
Browser ──HTTP──▶ Flask (app.py) ──psycopg2──▶ PostgreSQL
                       │
                       └─calls─▶ predictor.py ──psycopg2──▶ PostgreSQL
                                      │
                                      └──uses──▶ pandas + scikit-learn
```

### Frontend ↔ Backend interaction
- Jinja2 templates rendered server-side for every route
- Cart state persisted in Flask's signed session cookie
- Login is email-only (lookup against Customer table) — no passwords, since this is a classroom project. Production would add hashed passwords.
- Forms POST HTML, backend returns 302 redirects to avoid double-submit

### Repository
`https://github.com/JulianBoolean03/Database-project-`

### Directory layout
```
app.py                 — Flask routes
predictor.py           — Smart Restock ML module
schema.sql             — Table definitions
seed_data.sql          — Customers/Vendors/Markets/Products seed
seed_orders.sql        — Historical orders/items (ML training data)
generate_orders.py     — Script that produced seed_orders.sql
templates/             — Jinja2 HTML
requirements.txt       — pip deps
```

### Running locally
(Paste the setup block from DEMO_SCRIPT.md)

---

## 5. Evaluation of Group Members

**TODO — fill this honestly.** Keep it short: one sentence per person + a score.

### Julian Robinson — Score: ?/10
- Built: [what you built]
- Contributed to: [what you helped with]
- Strengths: [what you brought to the team]

### Aleesha Exantus — Score: ?/10
- Built: schema.sql table design, seed_data.sql (customers/vendors/markets/products/vendor-market), generate_orders.py with weather/event/seasonality patterning, seed_orders.sql generated output
- Contributed to: historical data design that made the ML model work
- Strengths: [fill in]

---

## 6. Experiences (~1 page)

### What we learned
- Designing a schema up front saves painful migrations later
- Postgres quoted-identifier rules (`"Order"` vs `order_orderid_seq`) are a real source of bugs
- ML quality depends far more on data quality than model choice — Linear Regression worked fine because the seed data had clean weather/event patterns

### Hard problems we solved
- **Sequence name case-sensitivity bug:** the first `seed_orders.sql` used `currval('order_orderid_seq')` but Postgres auto-generated `"Order_orderid_seq"` (capital O, quoted) because our Order table name was quoted. Fix: update both `seed_orders.sql` and `generate_orders.py` to use the correctly quoted sequence name.
- **Feature engineering for Smart Restock:** early model with just weather + month had R² near zero. Adding product_id one-hot features let the regression learn per-product baselines, giving the model something to adjust up/down based on conditions.
- **Session-based cart state** across login redirects — needed to carefully order the auth check before the empty-cart check.
- **Model staleness** after a vendor edits a product — solved with a `reset_model()` call on every write route.

### Future extensions
- Proper password-hashed authentication (werkzeug.security or bcrypt)
- Swap Linear Regression for a Gradient Boosted Tree (XGBoost) for nonlinear interactions
- Add a `Product.Stock` column and surface true "running out" warnings
- Historical accuracy tracking: after each market, compare predicted vs actual and display MAE
- Vendor-specific fine-tuning: train one model per vendor once enough data accumulates
- Mobile-first redesign for in-market use

---

## 7. References

- Flask documentation — https://flask.palletsprojects.com
- psycopg2 — https://www.psycopg.org/docs/
- scikit-learn Linear Regression — https://scikit-learn.org/stable/modules/linear_model.html
- Bootstrap 5 — https://getbootstrap.com/docs/5.3/
- PostgreSQL 16 — https://www.postgresql.org/docs/16/
- USDA food pricing data (reference for realistic prices in seed_data.sql)
- Course slides on normalization (BCNF / 3NF)
