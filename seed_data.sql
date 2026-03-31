-- ============================================
-- Seed Data: Foundational Tables
-- Customers, Vendors, Markets, Products, VendorMarket
-- ============================================

-- ---- CUSTOMERS ----
INSERT INTO Customer (Name, Email) VALUES
('Marcus Johnson', 'marcus.j@email.com'),
('Priya Patel', 'priya.p@email.com'),
('Sofia Reyes', 'sofia.r@email.com'),
('David Kim', 'david.k@email.com'),
('Amara Okafor', 'amara.o@email.com'),
('James Whitfield', 'james.w@email.com'),
('Nina Alvarez', 'nina.a@email.com'),
('Ethan Brooks', 'ethan.b@email.com'),
('Lily Chen', 'lily.c@email.com'),
('Omar Hassan', 'omar.h@email.com'),
('Rachel Thompson', 'rachel.t@email.com'),
('Carlos Mendez', 'carlos.m@email.com'),
('Aisha Williams', 'aisha.w@email.com'),
('Tyler Nguyen', 'tyler.n@email.com'),
('Grace Obi', 'grace.o@email.com');

-- ---- VENDORS ----
INSERT INTO Vendor (Name, ProfileInfo) VALUES
('Green Acres Farm', 'Family-owned organic vegetable farm, est. 2015. Specializes in leafy greens and root vegetables.'),
('Sunny Side Orchards', 'Local fruit orchard growing seasonal stone fruits and berries since 2010.'),
('Honeybee Apiaries', 'Small-batch raw honey and beeswax products from ethically managed hives.'),
('Bread & Butter Bakery', 'Artisan sourdough and pastries baked fresh every market morning.'),
('Herban Garden', 'Hydroponic herb farm offering year-round fresh herbs and microgreens.'),
('River Rock Ranch', 'Free-range eggs and pasture-raised poultry from a sustainable ranch.'),
('Pickle Palace', 'Handcrafted fermented vegetables, pickles, and kimchi using local produce.'),
('Roots & Shoots Nursery', 'Seedlings, potted herbs, and native plants for home gardeners.');

-- ---- MARKETS (historical + upcoming) ----
INSERT INTO Market (Date, Location, WeatherCondition, IsSpecialEvent) VALUES
-- Past markets (historical data for the model)
('2025-09-06', 'Downtown Plaza', 'Sunny', FALSE),
('2025-09-13', 'Downtown Plaza', 'Cloudy', FALSE),
('2025-09-20', 'Riverside Park', 'Sunny', FALSE),
('2025-09-27', 'Downtown Plaza', 'Rainy', FALSE),
('2025-10-04', 'Riverside Park', 'Sunny', TRUE),   -- Fall Festival
('2025-10-11', 'Downtown Plaza', 'Cloudy', FALSE),
('2025-10-18', 'Downtown Plaza', 'Sunny', FALSE),
('2025-10-25', 'Riverside Park', 'Rainy', FALSE),
('2025-11-01', 'Downtown Plaza', 'Cloudy', FALSE),
('2025-11-08', 'Riverside Park', 'Sunny', TRUE),   -- Harvest Fair
('2025-11-15', 'Downtown Plaza', 'Rainy', FALSE),
('2025-11-22', 'Downtown Plaza', 'Cloudy', FALSE),
('2025-12-06', 'Riverside Park', 'Sunny', TRUE),   -- Holiday Market
('2025-12-13', 'Downtown Plaza', 'Cloudy', FALSE),
('2025-12-20', 'Downtown Plaza', 'Sunny', TRUE),   -- Holiday Market
('2026-01-10', 'Downtown Plaza', 'Cloudy', FALSE),
('2026-01-17', 'Riverside Park', 'Rainy', FALSE),
('2026-01-24', 'Downtown Plaza', 'Sunny', FALSE),
('2026-02-07', 'Riverside Park', 'Cloudy', FALSE),
('2026-02-14', 'Downtown Plaza', 'Sunny', TRUE),   -- Valentine's Market
('2026-02-21', 'Downtown Plaza', 'Rainy', FALSE),
('2026-02-28', 'Riverside Park', 'Sunny', FALSE),
('2026-03-07', 'Downtown Plaza', 'Cloudy', FALSE),
('2026-03-14', 'Riverside Park', 'Sunny', FALSE),
('2026-03-21', 'Downtown Plaza', 'Sunny', FALSE),
-- Upcoming markets (for predictions)
('2026-04-04', 'Riverside Park', 'Sunny', FALSE),
('2026-04-11', 'Downtown Plaza', 'Cloudy', FALSE),
('2026-04-18', 'Riverside Park', 'Sunny', TRUE),   -- Spring Festival
('2026-04-25', 'Downtown Plaza', 'Sunny', FALSE);

-- ---- PRODUCTS (priced from USDA-realistic ranges) ----
-- Green Acres Farm (VendorID 1)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(1, 'Organic Kale (bunch)', 3.50),
(1, 'Romaine Lettuce (head)', 2.75),
(1, 'Carrots (1 lb)', 3.00),
(1, 'Sweet Potatoes (1 lb)', 2.50),
(1, 'Beets (bunch)', 4.00),
(1, 'Swiss Chard (bunch)', 3.25);

-- Sunny Side Orchards (VendorID 2)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(2, 'Honeycrisp Apples (1 lb)', 4.00),
(2, 'Strawberries (pint)', 5.50),
(2, 'Blueberries (pint)', 6.00),
(2, 'Peaches (1 lb)', 4.50),
(2, 'Blackberries (half pint)', 4.00);

-- Honeybee Apiaries (VendorID 3)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(3, 'Wildflower Honey (16 oz)', 12.00),
(3, 'Clover Honey (8 oz)', 7.50),
(3, 'Honeycomb (piece)', 9.00),
(3, 'Beeswax Candle', 8.00);

-- Bread & Butter Bakery (VendorID 4)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(4, 'Sourdough Loaf', 7.00),
(4, 'Croissant', 3.50),
(4, 'Cinnamon Roll', 4.00),
(4, 'Baguette', 5.00),
(4, 'Blueberry Muffin', 3.00);

-- Herban Garden (VendorID 5)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(5, 'Fresh Basil (bunch)', 2.50),
(5, 'Cilantro (bunch)', 2.00),
(5, 'Rosemary (bunch)', 2.50),
(5, 'Microgreens Mix (box)', 5.00),
(5, 'Mint (bunch)', 2.00);

-- River Rock Ranch (VendorID 6)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(6, 'Free-Range Eggs (dozen)', 6.50),
(6, 'Whole Chicken (avg 4 lb)', 18.00),
(6, 'Duck Eggs (half dozen)', 8.00);

-- Pickle Palace (VendorID 7)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(7, 'Classic Dill Pickles (jar)', 8.00),
(7, 'Spicy Kimchi (jar)', 9.00),
(7, 'Pickled Jalapeños (jar)', 7.00),
(7, 'Sauerkraut (jar)', 7.50);

-- Roots & Shoots Nursery (VendorID 8)
INSERT INTO Product (VendorID, Name, Current_Price) VALUES
(8, 'Tomato Seedling', 4.00),
(8, 'Basil Plant (potted)', 5.00),
(8, 'Lavender Plant', 7.00),
(8, 'Succulent Trio', 12.00);

-- ---- VENDORMARKET (which vendors attend which markets) ----
-- Not every vendor attends every market
INSERT INTO VendorMarket (VendorID, MarketID) VALUES
-- Green Acres Farm attends most markets
(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),
(1,11),(1,12),(1,13),(1,14),(1,15),(1,16),(1,17),(1,18),(1,19),(1,20),
(1,21),(1,22),(1,23),(1,24),(1,25),(1,26),(1,27),(1,28),(1,29),
-- Sunny Side Orchards (seasonal, mostly fall)
(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(2,10),
(2,26),(2,27),(2,28),(2,29),
-- Honeybee Apiaries (every other week roughly)
(3,1),(3,3),(3,5),(3,7),(3,9),(3,11),(3,13),(3,15),(3,17),(3,19),
(3,21),(3,23),(3,25),(3,27),(3,29),
-- Bread & Butter Bakery (attends all)
(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10),
(4,11),(4,12),(4,13),(4,14),(4,15),(4,16),(4,17),(4,18),(4,19),(4,20),
(4,21),(4,22),(4,23),(4,24),(4,25),(4,26),(4,27),(4,28),(4,29),
-- Herban Garden
(5,1),(5,2),(5,4),(5,6),(5,8),(5,10),(5,12),(5,14),(5,16),(5,18),
(5,20),(5,22),(5,24),(5,26),(5,28),
-- River Rock Ranch
(6,1),(6,3),(6,5),(6,7),(6,9),(6,11),(6,13),(6,15),(6,17),(6,19),
(6,21),(6,23),(6,25),(6,27),(6,29),
-- Pickle Palace (weekends at Riverside mostly)
(7,3),(7,5),(7,8),(7,10),(7,13),(7,15),(7,17),(7,19),(7,22),(7,24),
(7,26),(7,28),
-- Roots & Shoots Nursery (spring + special events)
(8,5),(8,10),(8,13),(8,15),(8,20),(8,24),(8,25),(8,26),(8,27),(8,28),(8,29);
