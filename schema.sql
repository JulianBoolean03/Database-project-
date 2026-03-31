-- ============================================
-- Farmers Market Database Schema
-- Team: Database Demons
-- Julian Robinson & Aleesha Exantus
-- ============================================

DROP TABLE IF EXISTS OrderItem CASCADE;
DROP TABLE IF EXISTS "Order" CASCADE;
DROP TABLE IF EXISTS VendorMarket CASCADE;
DROP TABLE IF EXISTS Product CASCADE;
DROP TABLE IF EXISTS Market CASCADE;
DROP TABLE IF EXISTS Vendor CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;

-- Customers who shop at the market
CREATE TABLE Customer (
    CustomerID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(150) UNIQUE NOT NULL
);

-- Vendors who sell at the market
CREATE TABLE Vendor (
    VendorID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ProfileInfo TEXT
);

-- Each market day (date, location, conditions)
CREATE TABLE Market (
    MarketID SERIAL PRIMARY KEY,
    Date DATE NOT NULL,
    Location VARCHAR(200) NOT NULL,
    WeatherCondition VARCHAR(50),
    IsSpecialEvent BOOLEAN DEFAULT FALSE
);

-- Products each vendor sells
CREATE TABLE Product (
    ProductID SERIAL PRIMARY KEY,
    VendorID INT NOT NULL REFERENCES Vendor(VendorID),
    Name VARCHAR(100) NOT NULL,
    Current_Price NUMERIC(8,2) NOT NULL CHECK (Current_Price > 0)
);

-- Which vendors attend which markets
CREATE TABLE VendorMarket (
    VendorID INT REFERENCES Vendor(VendorID),
    MarketID INT REFERENCES Market(MarketID),
    PRIMARY KEY (VendorID, MarketID)
);

-- Customer orders placed at a market
CREATE TABLE "Order" (
    OrderID SERIAL PRIMARY KEY,
    CustomerID INT NOT NULL REFERENCES Customer(CustomerID),
    MarketID INT NOT NULL REFERENCES Market(MarketID),
    OrderDate DATE NOT NULL,
    Status VARCHAR(30) DEFAULT 'Pending'
);

-- Individual items within an order
CREATE TABLE OrderItem (
    ItemNo SERIAL,
    OrderID INT NOT NULL REFERENCES "Order"(OrderID),
    ProductID INT NOT NULL REFERENCES Product(ProductID),
    PurchasePrice NUMERIC(8,2) NOT NULL,
    Qty INT NOT NULL CHECK (Qty > 0),
    PRIMARY KEY (ItemNo, OrderID)
);
