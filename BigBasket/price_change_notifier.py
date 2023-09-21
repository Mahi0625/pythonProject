# price_change_notifier.py

# import pandas as pd
# from notifier import send_notification

# def send_price_change_notifications(existing_df, all_updated_products):
#     if existing_df.empty:
#         return  # No previous data, cannot send price change notifications

#     for category, updated_products in all_updated_products.items():
#         if not updated_products:
#             continue  # No updated products in this category

#         # Create a DataFrame for the new products in this category
#         new_df = pd.DataFrame(updated_products, columns=["product_name", "original_price", "discounted_price", "discount"])

#         # Merge the new DataFrame with the existing DataFrame based on product_name
#         merged_df = pd.merge(existing_df, new_df, on='product_name', suffixes=('_prev', '_cur'))

#         # Find rows where the discounted_price has changed
#         price_changed_rows = merged_df[merged_df['discounted_price_prev'] != merged_df['discounted_price_cur']]

#         # Check if there are any price changes in this category
#         if not price_changed_rows.empty:
#             # Prepare and send notifications for price changes in this category
#             price_change_notification_text = price_changed_rows.to_string(index=False)
#             send_notification("Price Changes Alert", f"Price changes detected in '{category}':\n{price_change_notification_text}\nTime to grab a deal!", 'kdhini2807@gmail.com')



# price_change_notifier.py

# price_change_notifier.py

# price_change_notifier.py

import pandas as pd
from notifier import send_notification
from notification_formatter import format_notification_table  # Import the formatter function

def send_price_change_notifications(existing_df, all_updated_products):
    if existing_df.empty:
        return  # No previous data, cannot send price change notifications

    # Initialize a string to store the notifications for both categories
    notification_text = ""

    for category, updated_products in all_updated_products.items():
        if not updated_products:
            continue  # No updated products in this category

        # Create a DataFrame for the updated products in this category
        updated_df = pd.DataFrame(updated_products, columns=["product_name_cur", "original_price_cur", "discounted_price_cur", "discount_cur"])

        # Merge the new DataFrame with the existing DataFrame based on product_name
        merged_df = pd.merge(existing_df, updated_df, left_on='product_name', right_on='product_name_cur', suffixes=('_prev', '_cur'))

        # Find rows where the discounted_price has changed
        price_changed_rows = merged_df[merged_df['discounted_price_prev'] != merged_df['discounted_price_cur']]

        # Check if there are any price changes in this category
        if not price_changed_rows.empty:
            # Prepare and append notifications for price changes in this category
            category_notification_text = f"Price changes detected in '{category}':\n"
            category_notification_text += format_notification_table(price_changed_rows[["product_name_cur", "original_price_prev", "discounted_price_prev", "discount_prev", "original_price_cur", "discounted_price_cur", "discount_cur"]].values.tolist())
            notification_text += category_notification_text

    # Send a single email containing notifications for both categories, if there are any
    if notification_text:
        send_notification("Price Changes Alert", notification_text, 'kdhini2807@gmail.com')
