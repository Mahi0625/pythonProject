import os
import sqlite3
import pandas as pd
import xlsxwriter
from scraper import scrape_products  # Import your scraper function
from notifier import send_notification
from utils import load_inserted_products, update_inserted_products
from datetime import datetime
from notification_formatter import format_notification_table

# Define a function to create an Excel file with multiple sheets
def create_excel_file(categories):
    workbook = xlsxwriter.Workbook(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_products.xlsx')

    for _, category_name in categories:
        workbook.add_worksheet(category_name)

    workbook.close()

# Define a function to create a database for historical price records
def create_database():
    conn = sqlite3.connect(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_price_history.db')
    c = conn.cursor()

    # Create a table to store price history
    c.execute('''CREATE TABLE IF NOT EXISTS price_history (
        product_name TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        price TEXT
    )''')

    conn.commit()
    conn.close()

# Define the main function to scrape, process, and store data
# Define the main function to scrape, process, and store data
def main_function(url, category_name, existing_df):
    # Scrape the website
    bigbasket_product_cards = scrape_products(url)

    # Set up SQLite database connection
    conn = sqlite3.connect(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_products_database.db')
    c = conn.cursor()

    # Create products table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        product_name TEXT,
        original_price TEXT,
        discounted_price TEXT,
        discount TEXT,
        previous_price TEXT,
        category TEXT,
        quantity TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Load the set of inserted products from the file
    inserted_products = load_inserted_products(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_inserted_products.txt')

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

        # Check if the product is new or updated
        if product_name not in inserted_products:
            new_products.append((product_name, original_price, discounted_price, discount))
            inserted_products.add(product_name)
        else:
            existing_product = c.execute("SELECT * FROM products WHERE product_name=?", (product_name,)).fetchone()
            if existing_product is not None:
                # Check for price change
                if existing_product[4] != discounted_price:
                    updated_products.append((product_name, existing_product[4], discounted_price, discount))
                else:
                    # If no price change, update the previous price in the database
                    discounted_price = existing_product[4]

            # Update or insert the product details in the database
            c.execute('''INSERT OR REPLACE INTO products (product_name, original_price, discounted_price, discount, quantity, category) VALUES (?,?,?,?,?,?)''',
                      (product_name, original_price, discounted_price, discount, quantity, category_name))

        # Record the price in the price history database
        conn_history = sqlite3.connect(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_price_history.db')
        c_history = conn_history.cursor()
        c_history.execute("INSERT INTO price_history (product_name, price) VALUES (?, ?)", (product_name, discounted_price))
        conn_history.commit()
        conn_history.close()

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    # Update the inserted products file
    update_inserted_products(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_inserted_products.txt', inserted_products)

    return new_products, updated_products


    # Update Excel file and sheets
    with pd.ExcelWriter(r'D:\Nidhi\Vegease\BigBasket\Bigbasket_products.xlsx', engine='xlsxwriter') as writer:
        for category in categories:
            category_name = category[1]
            df_category = existing_df[existing_df["category"] == category_name]
            df_category.to_excel(writer, sheet_name=category_name, index=False)

    # Prepare notification messages for new and updated products
    new_products_notification_text = "\n".join([f"Category: {category}\n{format_notification_table(products)}" for category, products in all_new_products.items() if products])
    updated_products_notification_text = "\n".join([f"Category: {category}\n{format_notification_table(products)}" for category, products in all_updated_products.items() if products])

    # Send notifications for new and updated products
    if new_products_notification_text:
        send_notification("BigBasket: New Products Alert", f"New products added:\n{new_products_notification_text}\nCheck them out!", 'kdhini2807@gmail.com')

    if updated_products_notification_text:
        send_notification("BigBasket: Price Changes Alert", f"Price changes detected:\n{updated_products_notification_text}\nTime to grab a deal!", 'kdhini2807@gmail.com')

