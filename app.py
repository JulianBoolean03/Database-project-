from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)
import psycopg2
import psycopg2.extras
from datetime import date

import predictor

app = Flask(__name__)
app.secret_key = 'farmers-market-dev-key-change-me'

DB_CONFIG = {
    'dbname': 'farmersmarket',
    'user': 'postgres',
    'password': 'newpassword',
    'host': 'localhost',
    'port': '5432',
}


def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


@app.context_processor
def inject_user():
    return {
        'current_user': session.get('customer_name'),
        'cart_count': sum(session.get('cart', {}).values()),
    }


# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('home.html')


# ---------- AUTH ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "SELECT CustomerID, Name FROM Customer WHERE LOWER(Email) = %s",
            (email,),
        )
        customer = cur.fetchone()
        cur.close()
        conn.close()
        if customer:
            session['customer_id'] = customer['customerid']
            session['customer_name'] = customer['name']
            flash(f"Welcome, {customer['name']}!", 'success')
            return redirect(url_for('products'))
        flash('No customer found with that email.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('home'))


# ---------- CUSTOMER STOREFRONT ----------
@app.route('/products')
def products():
    search = request.args.get('search', '')
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if search:
        cur.execute("""
            SELECT p.ProductID, p.Name, p.Current_Price, v.Name AS vendor
            FROM Product p JOIN Vendor v ON p.VendorID = v.VendorID
            WHERE p.Name ILIKE %s OR v.Name ILIKE %s
            ORDER BY p.Name
        """, (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT p.ProductID, p.Name, p.Current_Price, v.Name AS vendor
            FROM Product p JOIN Vendor v ON p.VendorID = v.VendorID
            ORDER BY p.Name
        """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products, search=search)


# ---------- CART ----------
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    if cart:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        product_ids = [int(pid) for pid in cart.keys()]
        cur.execute("""
            SELECT p.ProductID, p.Name, p.Current_Price, v.Name AS vendor
            FROM Product p JOIN Vendor v ON p.VendorID = v.VendorID
            WHERE p.ProductID = ANY(%s)
        """, (product_ids,))
        for p in cur.fetchall():
            qty = cart[str(p['productid'])]
            line = float(p['current_price']) * qty
            total += line
            items.append({
                'product_id': p['productid'],
                'name': p['name'],
                'vendor': p['vendor'],
                'price': float(p['current_price']),
                'qty': qty,
                'line_total': line,
            })
        cur.close()
        conn.close()
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    qty = int(request.form.get('qty', 1))
    cart = session.get('cart', {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    session['cart'] = cart
    flash('Added to cart.', 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/cart/checkout', methods=['POST'])
def checkout():
    if 'customer_id' not in session:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products'))

    conn = get_db()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT MarketID, Date FROM Market "
            "WHERE Date >= CURRENT_DATE ORDER BY Date LIMIT 1"
        )
        market = cur.fetchone()
        if not market:
            flash('No upcoming market to order for.', 'danger')
            conn.rollback()
            return redirect(url_for('cart'))
        market_id, market_date = market

        cur.execute(
            'INSERT INTO "Order" (CustomerID, MarketID, OrderDate, Status) '
            'VALUES (%s, %s, %s, %s) RETURNING OrderID',
            (session['customer_id'], market_id, date.today(), 'Pending'),
        )
        order_id = cur.fetchone()[0]

        product_ids = [int(pid) for pid in cart.keys()]
        cur.execute(
            "SELECT ProductID, Current_Price FROM Product "
            "WHERE ProductID = ANY(%s)",
            (product_ids,),
        )
        prices = {row[0]: float(row[1]) for row in cur.fetchall()}
        for pid_str, qty in cart.items():
            pid = int(pid_str)
            cur.execute(
                "INSERT INTO OrderItem (OrderID, ProductID, PurchasePrice, Qty) "
                "VALUES (%s, %s, %s, %s)",
                (order_id, pid, prices[pid], qty),
            )
        conn.commit()
        session['cart'] = {}
        predictor.reset_model()
        flash(f'Order #{order_id} placed for market on {market_date}.', 'success')
        return redirect(url_for('products'))
    except Exception as e:
        conn.rollback()
        flash(f'Checkout failed: {e}', 'danger')
        return redirect(url_for('cart'))
    finally:
        cur.close()
        conn.close()


# ---------- VENDOR DASHBOARD ----------
@app.route('/vendor/<int:vendor_id>')
def vendor_dashboard(vendor_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Vendor WHERE VendorID = %s", (vendor_id,))
    vendor = cur.fetchone()
    cur.execute("""
        SELECT ProductID, Name, Current_Price FROM Product
        WHERE VendorID = %s ORDER BY Name
    """, (vendor_id,))
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('vendor_dashboard.html', vendor=vendor, products=products)


@app.route('/vendor/<int:vendor_id>/add', methods=['POST'])
def add_product(vendor_id):
    name = request.form['name']
    price = request.form['price']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Product (VendorID, Name, Current_Price) VALUES (%s, %s, %s)",
        (vendor_id, name, price),
    )
    cur.close()
    conn.close()
    predictor.reset_model()
    return redirect(url_for('vendor_dashboard', vendor_id=vendor_id))


@app.route('/vendor/<int:vendor_id>/update/<int:product_id>', methods=['POST'])
def update_product(vendor_id, product_id):
    new_price = request.form['price']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Product SET Current_Price = %s "
        "WHERE ProductID = %s AND VendorID = %s",
        (new_price, product_id, vendor_id),
    )
    cur.close()
    conn.close()
    predictor.reset_model()
    flash('Price updated.', 'success')
    return redirect(url_for('vendor_dashboard', vendor_id=vendor_id))


@app.route('/vendor/<int:vendor_id>/delete/<int:product_id>', methods=['POST'])
def delete_product(vendor_id, product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM Product WHERE ProductID = %s AND VendorID = %s",
        (product_id, vendor_id),
    )
    cur.close()
    conn.close()
    predictor.reset_model()
    return redirect(url_for('vendor_dashboard', vendor_id=vendor_id))


# ---------- SMART RESTOCK (ML) ----------
@app.route('/vendor/<int:vendor_id>/restock')
def smart_restock(vendor_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Vendor WHERE VendorID = %s", (vendor_id,))
    vendor = cur.fetchone()
    cur.close()
    conn.close()

    upcoming = predictor.list_upcoming_markets()
    selected_id = request.args.get('market', type=int)
    market = None
    predictions = []
    model_info = None
    error = None

    if upcoming and selected_id is None:
        selected_id = upcoming[0]['marketid']

    if selected_id is not None:
        try:
            model = predictor.get_model()
            model_info = {'rows': model.training_rows, 'r2': model.r2}
            market, predictions = model.predict_for_vendor_market(
                vendor_id, selected_id
            )
        except Exception as e:
            error = str(e)

    return render_template(
        'smart_restock.html',
        vendor=vendor,
        upcoming=upcoming,
        selected_id=selected_id,
        market=market,
        predictions=predictions,
        model_info=model_info,
        error=error,
    )


# ---------- REPORTS (demo queries: JOIN + AGGREGATE) ----------
@app.route('/reports')
def reports():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Query 1 — Top 10 best-selling products (JOIN 3 tables + aggregate)
    cur.execute("""
        SELECT p.Name AS product, v.Name AS vendor,
               SUM(oi.Qty) AS units_sold,
               SUM(oi.Qty * oi.PurchasePrice) AS revenue
        FROM OrderItem oi
        JOIN Product p ON oi.ProductID = p.ProductID
        JOIN Vendor v  ON p.VendorID   = v.VendorID
        GROUP BY p.Name, v.Name
        ORDER BY units_sold DESC
        LIMIT 10
    """)
    best_sellers = cur.fetchall()

    # Query 2 — Revenue by weather condition (JOIN + aggregate + GROUP BY)
    cur.execute("""
        SELECT m.WeatherCondition AS weather,
               COUNT(DISTINCT o.OrderID) AS orders,
               SUM(oi.Qty) AS units,
               SUM(oi.Qty * oi.PurchasePrice) AS revenue,
               ROUND(AVG(oi.Qty * oi.PurchasePrice)::numeric, 2) AS avg_line_value
        FROM OrderItem oi
        JOIN "Order" o ON oi.OrderID = o.OrderID
        JOIN Market m  ON o.MarketID = m.MarketID
        GROUP BY m.WeatherCondition
        ORDER BY revenue DESC
    """)
    weather_breakdown = cur.fetchall()

    # Query 3 — Vendor revenue leaderboard (JOIN + aggregate)
    cur.execute("""
        SELECT v.Name AS vendor,
               COUNT(DISTINCT p.ProductID) AS product_count,
               SUM(oi.Qty) AS units_sold,
               SUM(oi.Qty * oi.PurchasePrice) AS revenue
        FROM Vendor v
        JOIN Product p   ON v.VendorID  = p.VendorID
        JOIN OrderItem oi ON p.ProductID = oi.ProductID
        GROUP BY v.Name
        ORDER BY revenue DESC
    """)
    vendor_leaderboard = cur.fetchall()

    cur.close()
    conn.close()
    return render_template(
        'reports.html',
        best_sellers=best_sellers,
        weather_breakdown=weather_breakdown,
        vendor_leaderboard=vendor_leaderboard,
    )


# ---------- VENDORS LIST ----------
@app.route('/vendors')
def vendors():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT VendorID, Name, ProfileInfo FROM Vendor ORDER BY Name")
    vendors = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('vendors.html', vendors=vendors)


if __name__ == '__main__':
    app.run(debug=True)
