import pandas as pd
import os

def main():
    # 1. Define file paths
    RAW_DATA_PATH = 'data/raw/'
    PROCESSED_DATA_PATH = 'data/processed/'
    
    print("Loading raw data...")
    
    # Load core tables (Notice we added products)
    orders = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_orders_dataset.csv'))
    reviews = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_order_reviews_dataset.csv'))
    customers = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_customers_dataset.csv'))
    items = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_order_items_dataset.csv'))
    sellers = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_sellers_dataset.csv'))
    products = pd.read_csv(os.path.join(RAW_DATA_PATH, 'olist_products_dataset.csv'))

    print(f"Initial orders: {len(orders)}")

    # 2. Filter for valid, delivered orders only (per our methodology)
    orders = orders[orders['order_status'] == 'delivered'].copy()
    orders = orders.dropna(subset=['order_delivered_customer_date', 'order_estimated_delivery_date'])
    
    print(f"Valid delivered orders: {len(orders)}")

    # 3. Convert date columns to datetime objects
    date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])

    # 4. Feature Engineering on Orders
    # Delay in days (actual - estimated)
    orders['delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
    orders['is_late'] = (orders['delay_days'] > 0).astype(int)
    
    # Estimated shipping window (in days) - Needed for RQ3
    orders['estimated_shipping_days'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']).dt.days

    # 5. Prepare Items, Sellers, and Products for merging
    # Merge items with sellers to get seller_state
    items_sellers = items.merge(sellers[['seller_id', 'seller_state']], on='seller_id', how='left')
    # Merge with products to get weight
    items_full = items_sellers.merge(products[['product_id', 'product_weight_g']], on='product_id', how='left')
    
    # Aggregate to one row per order (Sum weights, sum freight, take first seller state)
    # This prevents row duplication when an order has multiple items
    order_agg = items_full.groupby('order_id').agg({
        'seller_state': 'first',
        'product_weight_g': 'sum',
        'freight_value': 'sum'
    }).reset_index()

    # 6. Prepare Reviews (Keep only the latest review per order to avoid duplicates)
    reviews_clean = reviews.drop_duplicates(subset=['order_id'], keep='last')

    # 7. Merge everything into our Master DataFrame
    print("Merging tables...")
    
    master_df = orders.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')
    master_df = master_df.merge(reviews_clean[['order_id', 'review_score']], on='order_id', how='left')
    master_df = master_df.merge(order_agg, on='order_id', how='left')

    # 8. Create the 'Route' column
    master_df['route'] = master_df['seller_state'].astype(str) + ' -> ' + master_df['customer_state'].astype(str)

    # 9. Select final columns for the analytical dataset
    final_cols = [
        'order_id', 'customer_state', 'seller_state', 'route',
        'order_purchase_timestamp', 'order_delivered_customer_date', 
        'order_estimated_delivery_date', 'estimated_shipping_days',
        'product_weight_g', 'freight_value', 'delay_days', 'is_late', 'review_score'
    ]
    master_df = master_df[final_cols]

    # 10. Save to processed folder
    output_file = os.path.join(PROCESSED_DATA_PATH, 'master_orders.csv')
    master_df.to_csv(output_file, index=False)
    
    print(f"\nSuccess! Master dataset saved to {output_file}")
    print(f"Final row count: {len(master_df)}")
    print("\nSample of the merged data:")
    print(master_df[['route', 'delay_days', 'is_late', 'review_score', 'product_weight_g']].head())

if __name__ == "__main__":
    main()