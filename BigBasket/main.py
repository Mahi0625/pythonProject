import os
import sqlite3
import pandas as pd
import xlsxwriter
from scraper import scrape_products  # Import your scraper function
from notifier import send_notification
from utils import load_inserted_products, update_inserted_products
from datetime import datetime
from notification_formatter import format_notification_table
from notification_formatter import format_notification_table_np
import pytz

# Define a function to create an Excel file with multiple sheets
def create_excel_file(categories):
    workbook = xlsxwriter.Workbook('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products.xlsx')

    for _, category_name in categories:
        workbook.add_worksheet(category_name)

    workbook.close()

# Define a function to create a database for historical price records
def create_database():
    conn_products = sqlite3.connect('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products_database.db')
    c_products = conn_products.cursor()

    # Create products table if not exists
    c_products.execute('''CREATE TABLE IF NOT EXISTS products (
        product_name TEXT,
        original_price TEXT,
        discounted_price TEXT,
        discount TEXT,
        category TEXT,
        quantity TEXT,
        timestamp TEXT  -- Change the data type to TEXT
    )''')
    conn_products.commit()
    conn_products.close()

    conn_history = sqlite3.connect('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_price_history.db')
    c_history = conn_history.cursor()

    # Create price history table if not exists
    c_history.execute('''CREATE TABLE IF NOT EXISTS price_history (
        product_name TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        price TEXT
    )''')
    conn_history.commit()
    conn_history.close()

# Define the main function to scrape, process, and store data
def main_function(url, category_name, existing_df):
    # Scrape the website
    bigbasket_product_cards = scrape_products(url)

    # Set up SQLite database connection for products
    conn_products = sqlite3.connect('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products_database.db')
    c_products = conn_products.cursor()

    # Set up SQLite database connection for price history
    conn_history = sqlite3.connect('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_price_history.db')
    c_history = conn_history.cursor()

    # Load the set of inserted products from the file
    inserted_products = load_inserted_products('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_inserted_products.txt')

    # Lists to keep track of new and updated products
    new_products = []
    updated_products = []

    # Process and store data
    for card in bigbasket_product_cards:
        product_name_elem = card.find("h3", class_="text-base")
        original_price_elem = card.find("span", class_="Label-sc-15v1nk5-0 Pricing___StyledLabel2-sc-pldi2d-2 gJxZPQ hsCgvu")
        discounted_price_elem = card.find("span", class_="Label-sc-15v1nk5-0 Pricing___StyledLabel-sc-pldi2d-1 gJxZPQ AypOi")
        discount_elem = card.find("span", class_="font-semibold lg:text-xs xl:text-sm leading-xxl xl:leading-md")
        quantity_elem = card.find("span", class_=["Label-sc-15v1nk5-0 PackChanger___StyledLabel-sc-newjpv-1 gJxZPQ cWbtUx", "Label-sc-15v1nk5-0 gJxZPQ truncate"])

        # Check if the elements are found, and get their text if found, or assign "N/A" if not found
        product_name = product_name_elem.text.strip() if product_name_elem else "N/A"
        original_price = original_price_elem.text.strip() if original_price_elem else "N/A"
        discounted_price = discounted_price_elem.text.strip() if discounted_price_elem else "N/A"
        discount = discount_elem.text.strip() if discount_elem else "N/A"
        quantity = quantity_elem.text.strip() if quantity_elem else "N/A"
        
        # Set the timezone to IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

        # Check if the product is new or updated
        if product_name not in inserted_products:
            new_products.append((product_name, original_price, discounted_price, quantity))
            inserted_products.add(product_name)
        else:
            # Get the most recent price from the price history
            c_history.execute("SELECT price FROM price_history WHERE product_name=? ORDER BY timestamp DESC LIMIT 1", (product_name,))
            last_price = c_history.fetchone()

            if last_price is not None and last_price[0] != discounted_price:
                updated_products.append((product_name, last_price[0], discounted_price, quantity))

        # Record the current price in the price history
        c_history.execute("INSERT INTO price_history (product_name, price) VALUES (?, ?)", (product_name, discounted_price))

        # Update or insert the product details in the database
        c_products.execute('''INSERT OR REPLACE INTO products (product_name, original_price, discounted_price, discount, quantity, category, timestamp) VALUES (?,?,?,?,?,?,?)''',
                          (product_name, original_price, discounted_price, discount, quantity, category_name, current_time))

    # Commit changes and close the database connections
    conn_products.commit()
    conn_products.close()
    conn_history.commit()
    conn_history.close()

    # Update the inserted products file
    update_inserted_products('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_inserted_products.txt', inserted_products)

    return new_products, updated_products

if __name__ == "__main__":
    # Create the historical price database
    create_database()

    categories = [
        ('https://www.bigbasket.com/pc/fruits-vegetables/fresh-vegetables/?nc=ct-fa', 'Fresh Vegetables'),
        ('https://www.bigbasket.com/pc/fruits-vegetables/fresh-fruits/?nc=ct-fa', 'Fresh Fruits'),
    ]

    # Create Excel file with sheets if it doesn't exist
    if not os.path.isfile('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products.xlsx'):
        create_excel_file(categories)

    all_new_products = {}
    all_updated_products = {}
    existing_df = pd.DataFrame()  # Initialize an empty DataFrame to store existing data

    for url, category in categories:
        new_category_products, updated_category_products = main_function(url, category, existing_df)
        all_new_products[category] = new_category_products
        all_updated_products[category] = updated_category_products

    # Concatenate the existing DataFrame with new data
    for category in categories:
        category_name = category[1]
        conn = sqlite3.connect('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products_database.db')
        df = pd.read_sql_query(f"SELECT * FROM products WHERE category='{category_name}'", conn)
        conn.close()
        existing_df = pd.concat([existing_df, df], ignore_index=True)
  
        # Remove duplicates from the combined DataFrame
        existing_df.drop_duplicates(subset=["product_name"], keep="last", inplace=True)

    # Update Excel file and sheets
    with pd.ExcelWriter('/home/mahima/Downloads/Vegease/BigBasket/Bigbasket_products.xlsx', engine='xlsxwriter') as writer:
        for category in categories:
            category_name = category[1]
            df_category = existing_df[existing_df["category"] == category_name]
            df_category.to_excel(writer, sheet_name=category_name, index=False)

    # Prepare notification messages for new and updated products
    new_products_notification_text = "\n".join([f"Category: {category}\n{format_notification_table_np(products)}" for category, products in all_new_products.items() if products])
    updated_products_notification_text = "\n".join([f"Category: {category}\n{format_notification_table(products)}" for category, products in all_updated_products.items() if products])

    recipients = ['amit.khanna@egreens.com', 'mahimatripathi0625@gmail.com','rprithvi786@gmail.com']  # Add the second email here

    # Send notifications for new and updated products
    if new_products_notification_text:
        send_notification("BigBasket: New Products Alert", f"New products added:\n{new_products_notification_text}\nCheck them out!", recipients)

    if updated_products_notification_text:
        send_notification("BigBasket: Price Changes Alert", f"Price changes detected:\n{updated_products_notification_text}\nTime to grab a deal!", recipients)

    # Print the DataFrame head for the last category
    print(f"Category: {category_name}\n{df_category.head()}")
