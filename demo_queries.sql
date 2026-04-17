-- ============================================
-- DEMO QUERIES — Part 5, Interesting Queries
-- These are the exact queries running behind /reports.
-- Paste into psql, or run:  \i demo_queries.sql
-- ============================================


-- ---------- QUERY 1 — TOP 10 BEST-SELLING PRODUCTS ----------
-- Three-table JOIN (OrderItem, Product, Vendor) + SUM aggregate

SELECT p.Name AS product,
       v.Name AS vendor,
       SUM(oi.Qty) AS units_sold,
       SUM(oi.Qty * oi.PurchasePrice) AS revenue
FROM OrderItem oi
JOIN Product p ON oi.ProductID = p.ProductID
JOIN Vendor v  ON p.VendorID   = v.VendorID
GROUP BY p.Name, v.Name
ORDER BY units_sold DESC
LIMIT 10;


-- ---------- QUERY 2 — REVENUE BY WEATHER ----------
-- Three-table JOIN (OrderItem, Order, Market) + GROUP BY + multiple aggregates
-- This is the signal our Smart Restock model learns.

SELECT m.WeatherCondition AS weather,
       COUNT(DISTINCT o.OrderID) AS orders,
       SUM(oi.Qty) AS units,
       SUM(oi.Qty * oi.PurchasePrice) AS revenue,
       ROUND(AVG(oi.Qty * oi.PurchasePrice)::numeric, 2) AS avg_line_value
FROM OrderItem oi
JOIN "Order" o ON oi.OrderID = o.OrderID
JOIN Market m  ON o.MarketID = m.MarketID
GROUP BY m.WeatherCondition
ORDER BY revenue DESC;


-- ---------- QUERY 3 — VENDOR REVENUE LEADERBOARD ----------
-- Three-table JOIN (Vendor, Product, OrderItem) + aggregates

SELECT v.Name AS vendor,
       COUNT(DISTINCT p.ProductID) AS product_count,
       SUM(oi.Qty) AS units_sold,
       SUM(oi.Qty * oi.PurchasePrice) AS revenue
FROM Vendor v
JOIN Product p    ON v.VendorID  = p.VendorID
JOIN OrderItem oi ON p.ProductID = oi.ProductID
GROUP BY v.Name
ORDER BY revenue DESC;
