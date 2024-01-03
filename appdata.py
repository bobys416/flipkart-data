#importing libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import pymongo

Product_name=[]
Prices = []
Description = []
Reviews = []

#scrape data
for i in range(2, 20):
    url = "https://www.flipkart.com/search?q=5000000+mobile&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_13_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_13_na_na_na&as-pos=1&as-type=RECENT&suggestionId=5000000+mobile%7CMobiles&requestId=66e38645-4ed2-44d8-8cc2-8f13a16146e6&as-searchtext=mobile%20500000" + str(i)
    
    try:
        r = requests.get(url)
        r.raise_for_status()  # Check for errors in the HTTP response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        continue
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        continue

    soup = BeautifulSoup(r.text, 'html.parser')
    
    box = soup.find("div", class_="_1YokD2 _3Mn1Gg")
    if box is None:
        print("Box not found. Skipping...")
        continue
    
    names = box.find_all("div", class_="_4rR01T")
    
    for name in names:
        Product_name.append(name.text.strip())

    prices = box.find_all("div", class_="_30jeq3 _1_WHN1")

    for price in prices:
        Prices.append(price.text.strip())
    
    desc = box.find_all("ul", class_="_1xgFaf")

    for description in desc:
        Description.append(description.text.strip())
    
    reviews = box.find_all("div", class_="_3LWZlK")

    for review in reviews:
        Reviews.append(review.text.strip())

df = pd.DataFrame({"Product Name": Product_name, "Prices": Prices, "Description": Description, "Reviews": Reviews})
df.to_csv("flipkart_mobiles_data.csv", index=False)
print("Data saved to flipkart_mobiles_data.csv")

conn = sqlite3.connect('flipkart_mobiles.db')
# connecting sql
cursor = conn.cursor()
# Create a table to store the data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mobiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        price TEXT,
        description TEXT,
        review TEXT
    )
''')

# Insert data into the table
for i in range(len(Product_name)):
    cursor.execute('''
        INSERT INTO mobiles (product_name, price, description, review)
        VALUES (?, ?, ?, ?)
    ''', (Product_name[i], Prices[i], Description[i], Reviews[i]))

# Commit the changes and close the connection
conn.commit()
conn.close()


# conneting mongodb
client = pymongo.MongoClient("mongodb+srv://bobys416:brksdanger@flipka.lwlihgu.mongodb.net/?retryWrites=true&w=majority")
db = client["flipkart_mobiles_db"]
# Create a collection to store the data
collection = db["mobiles"]

# Insert data into the collection
for i in range(len(Product_name)):
    mobile_data = {
        "product_name": Product_name[i],
        "price": Prices[i],
        "description": Description[i],
        "review": Reviews[i]
    }
    collection.insert_one(mobile_data)

print("Data saved to MongoDB")
print('Data saved to flipkart_mobiles.db')