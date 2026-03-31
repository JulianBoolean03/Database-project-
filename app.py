from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# Update these with your actual PostgreSQL credentials
DB_CONFIG = {
    'dbname': 'farmersmarket',
    'user': 'postgres',
    'password': 'newpassword',
    'host': 'localhost',
    'port': '5432'
}

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('home.html')

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

# ---------- VENDOR: ADD PRODUCT ----------
@app.route('/vendor/<int:vendor_id>/add', methods=['POST'])
def add_product(vendor_id):
    name = request.form['name']
    price = request.form['price']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Product (VendorID, Name, Current_Price) VALUES (%s, %s, %s)",
        (vendor_id, name, price)
    )
    cur.close()
    conn.close()
    return redirect(url_for('vendor_dashboard', vendor_id=vendor_id))

# ---------- VENDOR: DELETE PRODUCT ----------
@app.route('/vendor/<int:vendor_id>/delete/<int:product_id>', methods=['POST'])
def delete_product(vendor_id, product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Product WHERE ProductID = %s AND VendorID = %s", (product_id, vendor_id))
    cur.close()
    conn.close()
    return redirect(url_for('vendor_dashboard', vendor_id=vendor_id))

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
