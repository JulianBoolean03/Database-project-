import random
import psycopg2

#Connect to the database
conn = psycopg2.connect("dbname=farmersmarket host=localhost")
cur = conn.cursor()

#Get market info: ID, Date, Weather, Special Event
cur.execute("SELECT MarketID, Date, WeatherCondition, isSpecialEvent FROM Market")
markets = cur.fetchall()

#Get product info:ID and Price
cur.execute("SELECT ProductID, Current_Price, Name FROM Product")
products = cur.fetchall()

all_sql = []

#Loop through all markets
for market in markets:
    m_id = market[0]
    m_date = market[1]
    weather = market[2]
    is_event = market[3]

    #Set num orders based on weather
    if weather == 'Sunny':
        num_orders = random.randint(8, 10)
    else:
        num_orders = random.randint(2, 4)

    #If special event double the orders
    if is_event:
        num_orders = num_orders * 2

    #Create orders
    for _ in range(num_orders):
        customer_id = random.randint(1, 15)
        
        #Add the Order 
        all_sql.append(f"INSERT INTO \"Order\" (CustomerID, MarketID, OrderDate, Status) VALUES ({customer_id}, {m_id}, '{m_date}', 'Completed');")
        
        #Add 1 to 5 items to this order
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            prod = random.choice(products)
            p_id = prod[0]
            price = prod[1]
            p_name = prod[2]
            
            qty = random.randint(1, 3)
            
            #Seasonal Pattern: More fruit or berries in summer months 
            if m_date.month in [6, 7, 8] and ("Berry" in p_name or "Fruit" in p_name):
                qty = qty + 2
            
            #Save the OrderItem
            all_sql.append(f"INSERT INTO OrderItem (OrderID, ProductID, PurchasePrice, Qty) VALUES (currval('\"Order_orderid_seq\"'), {p_id}, {price}, {qty});")

#Save everything to the file
with open("seed_orders.sql", "w") as f:
    for line in all_sql:
        f.write(line + "\n")

print("Done! Created seed_orders.sql with patterned data.")

cur.close()
conn.close()

