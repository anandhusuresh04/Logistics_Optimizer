import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def main():
    # 1. Load the master dataset
    df = pd.read_csv('data/processed/master_orders.csv')
    
    print("======================================================")
    print("RESEARCH QUESTION 1: DELAYS vs CUSTOMER SATISFACTION")
    print("======================================================")
    
    # Drop missing reviews for RQ1
    rq1_df = df.dropna(subset=['review_score'])
    
    # Split into Late and On-Time
    late_reviews = rq1_df[rq1_df['is_late'] == 1]['review_score']
    on_time_reviews = rq1_df[rq1_df['is_late'] == 0]['review_score']
    
    print(f"Average Review Score (On-Time): {on_time_reviews.mean():.2f} (n={len(on_time_reviews)})")
    print(f"Average Review Score (Late):    {late_reviews.mean():.2f} (n={len(late_reviews)})")
    
    # Statistical Test: Mann-Whitney U
    stat, p_value = stats.mannwhitneyu(late_reviews, on_time_reviews, alternative='less')
    
    # Effect Size: Cliff's Delta calculated mathematically from U-statistic (FAST)
    n1, n2 = len(late_reviews), len(on_time_reviews)
    c_delta = (2 * stat) / (n1 * n2) - 1
    
    print(f"\nMann-Whitney U Test Results:")
    print(f"P-value: {p_value:.5e}")
    print(f"Cliff's Delta (Effect Size): {c_delta:.4f}")
    
    if p_value < 0.05:
        print("Result: REJECT the null hypothesis. Late deliveries have a significantly lower review score.")
    else:
        print("Result: FAIL to reject the null hypothesis.")
        
    # Visualization 1: Boxplot of Review Scores (Fixed Warning)
    plt.figure(figsize=(8, 5))
    sns.boxplot(x='is_late', y='review_score', data=rq1_df, hue='is_late', palette=['green', 'red'], legend=False)
    plt.title('Impact of Delivery Delays on Customer Review Scores', fontsize=14, fontweight='bold')
    plt.xlabel('Delivery Status', fontsize=12)
    plt.ylabel('Review Score (1-5)', fontsize=12)
    plt.xticks([0, 1], ['On-Time', 'Late'])
    plt.tight_layout()
    plt.savefig('visualizations/fig1_review_vs_delay.png', dpi=300)
    print("\nSaved visualization: visualizations/fig1_review_vs_delay.png")
    plt.close()

    print("\n======================================================")
    print("RESEARCH QUESTION 2: ROUTE BOTTLENECKS")
    print("======================================================")
    
    # Filter to routes with at least 50 orders to avoid statistical noise
    route_counts = df['route'].value_counts()
    valid_routes = route_counts[route_counts >= 50].index
    rq2_df = df[df['route'].isin(valid_routes)].copy()
    
    # Calculate delay rate per route
    route_stats = rq2_df.groupby('route').agg(
        total_orders=('is_late', 'count'),
        late_orders=('is_late', 'sum'),
        late_rate=('is_late', 'mean')
    ).reset_index()
    
    # Statistical Test: Chi-Square of Independence (Top 20 highest volume routes)
    top_20_volume_routes = route_stats.sort_values('total_orders', ascending=False).head(20)['route']
    chi_df = rq2_df[rq2_df['route'].isin(top_20_volume_routes)]
    
    contingency_table = pd.crosstab(chi_df['route'], chi_df['is_late'])
    chi2, p_val_chi, dof, expected = stats.chi2_contingency(contingency_table)
    
    # Effect Size: Cramér's V
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim))
    
    print(f"Chi-Square Test (Top 20 Volume Routes):")
    print(f"P-value: {p_val_chi:.5e}")
    print(f"Cramér's V (Effect Size): {cramers_v:.4f}")
    
    if p_val_chi < 0.05:
        print("Result: REJECT the null hypothesis. Delay rates vary significantly by route.")
    else:
        print("Result: FAIL to reject the null hypothesis.")

    # Get Top 10 Worst Routes by Late Rate
    worst_routes = route_stats.sort_values('late_rate', ascending=False).head(10)
    worst_routes['late_rate_pct'] = worst_routes['late_rate'] * 100
    
    print("\nTop 10 Worst Routes by Late Rate:")
    for index, row in worst_routes.iterrows():
        print(f"Route {row['route']}: {row['late_rate_pct']:.1f}% late ({row['late_orders']} out of {row['total_orders']} orders)")

    # Visualization 2: Bar chart of Worst Routes (Fixed Warning)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='late_rate_pct', y='route', data=worst_routes, hue='route', palette='Reds_r', legend=False)
    plt.title('Top 10 Worst Shipping Routes by Delay Rate', fontsize=14, fontweight='bold')
    plt.xlabel('Late Delivery Rate (%)', fontsize=12)
    plt.ylabel('Route (Seller State -> Customer State)', fontsize=12)
    
    # Add data labels to the bars
    for index, value in enumerate(worst_routes['late_rate_pct']):
        plt.text(value, index, f' {value:.1f}%', va='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('visualizations/fig2_worst_routes.png', dpi=300)
    print("\nSaved visualization: visualizations/fig2_worst_routes.png")
    plt.close()

if __name__ == "__main__":
    main()