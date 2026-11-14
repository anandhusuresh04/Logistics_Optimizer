import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Suppress warnings for clean terminal output
warnings.filterwarnings('ignore')

def main():
    print("Loading data for Business Impact Analysis...")
    df = pd.read_csv('data/processed/master_orders.csv')
    
    # =========================================================
    # 1. BUSINESS ASSUMPTIONS (State these in your report)
    # =========================================================
    # Cost of processing a refund/return for a late item (Brazilian Real)
    REFUND_COST = 150.00 
    # Estimated lost future revenue (Customer Lifetime Value) per bad review
    CLV_LOSS = 250.00
    # Total loss per bad customer experience
    TOTAL_LOSS_PER_BAD_REVIEW = REFUND_COST + CLV_LOSS
    
    # Target reduction scenario (e.g., fixing logistics reduces delays by 25%)
    REDUCTION_TARGET = 0.25 
    
    print("\n======================================================")
    print("BUSINESS IMPACT ANALYSIS & ROI SIMULATION")
    print("======================================================")
    
    # 2. Calculate Baseline Financial Loss
    # We only care about late orders that resulted in a bad review (1 or 2 stars)
    # We assume a bad review on a late order indicates a refund request or lost CLV.
    late_df = df[(df['is_late'] == 1) & (df['review_score'] <= 2)].copy()
    
    total_late_orders = df['is_late'].sum()
    bad_review_late_orders = len(late_df)
    total_financial_loss = bad_review_late_orders * TOTAL_LOSS_PER_BAD_REVIEW
    
    print(f"Current State (The Problem):")
    print(f"- Total Late Orders: {total_late_orders:,}")
    print(f"- Late Orders resulting in Bad Reviews (1-2 stars): {bad_review_late_orders:,}")
    print(f"- Estimated Financial Loss: R$ {total_financial_loss:,.2f}")
    
    # 3. Dynamic Route Analysis (Find the biggest financial bleed)
    # Group by route to find absolute number of bad reviews caused by delays
    route_loss = late_df.groupby('route').agg(
        bad_reviews=('review_score', 'count')
    ).reset_index()
    
    # Calculate the financial loss per route
    route_loss['financial_loss'] = route_loss['bad_reviews'] * TOTAL_LOSS_PER_BAD_REVIEW
    route_loss = route_loss.sort_values('financial_loss', ascending=False)
    
    # The worst route is the one at the top
    worst_route = route_loss.iloc[0]
    target_route_name = worst_route['route']
    target_route_loss = worst_route['financial_loss']
    target_route_bad_reviews = worst_route['bad_reviews']
    
    print(f"\nBottleneck Analysis (Highest Absolute Financial Loss):")
    print(f"- Worst Route: {target_route_name}")
    print(f"- Bad Reviews due to delays on this route: {target_route_bad_reviews:,}")
    print(f"- Financial Loss on this route alone: R$ {target_route_loss:,.2f}")
    
    # 4. The ROI Simulation
    # We simulate fixing this specific route
    orders_saved = int(target_route_bad_reviews * REDUCTION_TARGET)
    money_saved = orders_saved * TOTAL_LOSS_PER_BAD_REVIEW
    
    print("\n======================================================")
    print("ROI SIMULATION: WHAT IF WE FIX THIS ROUTE?")
    print("======================================================")
    print(f"Scenario: Reduce delays on {target_route_name} by {REDUCTION_TARGET*100}%.")
    print(f"- Number of bad customer experiences prevented: {orders_saved:,}")
    print(f"- Estimated Financial Savings: R$ {money_saved:,.2f}")
    
    print("\nRecommendation for Management:")
    print(f"Prioritize renegotiating carrier SLAs or adjusting estimated delivery dates for the {target_route_name} route.")
    print("This single intervention will directly save future revenue and protect brand reputation.")
    
    # 5. Visualization: Top 5 Worst Routes by Financial Loss
    top_5_routes = route_loss.head(5)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='financial_loss', y='route', data=top_5_routes, hue='route', palette='Reds_r', legend=False)
    plt.title('Top 5 Shipping Routes by Estimated Financial Loss', fontsize=14, fontweight='bold')
    plt.xlabel('Estimated Financial Loss (R$)', fontsize=12)
    plt.ylabel('Route (Seller -> Customer)', fontsize=12)
    
    # Format x-axis to show millions/thousands clearly
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    # Add data labels
    for index, value in enumerate(top_5_routes['financial_loss']):
        plt.text(value, index, f' R$ {value:,.0f}', va='center', fontweight='bold', fontsize=10)
        
    plt.tight_layout()
    plt.savefig('visualizations/fig5_financial_impact.png', dpi=300)
    print("\nSaved visualization: visualizations/fig5_financial_impact.png")
    plt.close()

if __name__ == "__main__":
    main()