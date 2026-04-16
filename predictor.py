"""Smart Restock demand forecasting.

Trains a Linear Regression model on historical OrderItem data joined with
Market conditions (weather, special event, location, month). Used by the
vendor dashboard to predict demand for upcoming markets.
"""

import psycopg2
import psycopg2.extras
import pandas as pd
from sklearn.linear_model import LinearRegression

DB_CONFIG = {
    'dbname': 'farmersmarket',
    'user': 'postgres',
    'password': 'newpassword',
    'host': 'localhost',
    'port': '5432',
}

WEATHER_VALUES = ['Sunny', 'Cloudy', 'Rainy']
LOCATION_VALUES = ['Downtown Plaza', 'Riverside Park']


def _get_conn():
    return psycopg2.connect(**DB_CONFIG)


def _load_history():
    """Per (product, past market) row with summed quantity sold."""
    conn = _get_conn()
    query = """
        SELECT
            oi.ProductID       AS product_id,
            m.MarketID         AS market_id,
            m.Date             AS date,
            m.WeatherCondition AS weather,
            m.IsSpecialEvent   AS is_event,
            m.Location         AS location,
            SUM(oi.Qty)        AS total_qty
        FROM OrderItem oi
        JOIN "Order" o ON oi.OrderID = o.OrderID
        JOIN Market m  ON o.MarketID = m.MarketID
        WHERE m.Date < CURRENT_DATE
        GROUP BY oi.ProductID, m.MarketID, m.Date, m.WeatherCondition,
                 m.IsSpecialEvent, m.Location
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def _featurize(df, product_ids, feature_columns=None):
    """Turn raw rows into the numeric matrix the model was trained on."""
    out = pd.DataFrame(index=range(len(df)))
    for w in WEATHER_VALUES:
        out[f'weather_{w}'] = (df['weather'].values == w).astype(int)
    for loc in LOCATION_VALUES:
        key = loc.replace(' ', '_')
        out[f'loc_{key}'] = (df['location'].values == loc).astype(int)
    out['is_event'] = df['is_event'].astype(int).values
    out['month'] = pd.to_datetime(df['date']).dt.month.values
    for pid in product_ids:
        out[f'prod_{pid}'] = (df['product_id'].values == pid).astype(int)
    if feature_columns is not None:
        for col in feature_columns:
            if col not in out.columns:
                out[col] = 0
        out = out[feature_columns]
    return out


class DemandModel:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.product_avg = {}
        self.training_rows = 0
        self.r2 = None

    def train(self):
        df = _load_history()
        if df.empty:
            raise ValueError(
                "No historical sales found. Run seed_orders.sql first."
            )
        product_ids = sorted(df['product_id'].unique().tolist())
        X = _featurize(df, product_ids)
        y = df['total_qty'].astype(float).values
        self.model = LinearRegression()
        self.model.fit(X, y)
        self.feature_columns = X.columns.tolist()
        self._product_ids = product_ids
        self.product_avg = df.groupby('product_id')['total_qty'].mean().to_dict()
        self.training_rows = len(df)
        self.r2 = float(self.model.score(X, y))
        return {'training_rows': self.training_rows, 'r2': self.r2}

    def predict_for_vendor_market(self, vendor_id, market_id):
        if self.model is None:
            self.train()
        conn = _get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "SELECT MarketID, Date, WeatherCondition, IsSpecialEvent, Location "
            "FROM Market WHERE MarketID = %s",
            (market_id,),
        )
        market = cur.fetchone()
        cur.execute(
            "SELECT ProductID, Name, Current_Price FROM Product "
            "WHERE VendorID = %s ORDER BY Name",
            (vendor_id,),
        )
        products = cur.fetchall()
        cur.close()
        conn.close()
        if not market or not products:
            return None, []

        rows = pd.DataFrame([
            {
                'product_id': p['productid'],
                'date': market['date'],
                'weather': market['weathercondition'],
                'is_event': market['isspecialevent'],
                'location': market['location'],
            }
            for p in products
        ])
        X = _featurize(rows, self._product_ids, self.feature_columns)
        preds = self.model.predict(X)

        results = []
        for p, raw in zip(products, preds):
            predicted = max(0, round(float(raw)))
            avg = self.product_avg.get(p['productid'], float(predicted))
            if avg > 0 and predicted > avg * 1.3:
                flag, flag_class = 'High Demand', 'danger'
            elif avg > 0 and predicted < avg * 0.7:
                flag, flag_class = 'Potential Overstock', 'warning'
            else:
                flag, flag_class = 'Normal', 'secondary'
            results.append({
                'product_id': p['productid'],
                'name': p['name'],
                'price': float(p['current_price']),
                'predicted_demand': predicted,
                'historical_avg': round(avg, 1),
                'flag': flag,
                'flag_class': flag_class,
            })
        return dict(market), results


_model = None


def get_model():
    global _model
    if _model is None:
        _model = DemandModel()
        _model.train()
    return _model


def reset_model():
    """Force a retrain on next call (e.g. after new orders land)."""
    global _model
    _model = None


def list_upcoming_markets():
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT MarketID, Date, Location, WeatherCondition, IsSpecialEvent "
        "FROM Market WHERE Date >= CURRENT_DATE ORDER BY Date"
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
