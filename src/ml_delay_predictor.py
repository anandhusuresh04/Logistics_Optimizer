import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress warnings for clean terminal output
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from imblearn.over_sampling import SMOTE

def main():
    print("Loading data for Machine Learning...")
    df = pd.read_csv('data/processed/master_orders.csv')
    
    # 1. Select ONLY pre-dispatch features
    features = ['customer_state', 'seller_state', 'estimated_shipping_days', 'product_weight_g', 'freight_value']
    target = 'is_late'
    
    ml_df = df[features + [target]].copy()
    
    # Handle missing numerical values gracefully (fill weight/freight with 0 instead of dropping rows)
    ml_df['product_weight_g'] = ml_df['product_weight_g'].fillna(0)
    ml_df['freight_value'] = ml_df['freight_value'].fillna(0)
    ml_df = ml_df.dropna(subset=['estimated_shipping_days', target])
    
    X = ml_df[features]
    y = ml_df[target]
    
    # 2. Train/Test Split (Do this BEFORE encoding to prevent Data Leakage)
    # stratify=y ensures the 7% late rate is maintained in both train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Encode categorical variables (Fit on Train, Transform on Test)
    le_cust = LabelEncoder()
    le_sell = LabelEncoder()
    
    X_train['customer_state'] = le_cust.fit_transform(X_train['customer_state'])
    X_train['seller_state'] = le_sell.fit_transform(X_train['seller_state'])
    
    # For the test set, we must handle any unseen states by mapping them to a default (e.g., -1)
    # This prevents the code from crashing if a rare state appears only in the test set
    X_test['customer_state'] = X_test['customer_state'].map(lambda s: le_cust.transform([s])[0] if s in le_cust.classes_ else -1)
    X_test['seller_state'] = X_test['seller_state'].map(lambda s: le_sell.transform([s])[0] if s in le_sell.classes_ else -1)
    
    # 4. Apply SMOTE to the TRAINING data only
    print(f"Original training set shape: {y_train.value_counts().to_dict()}")
    print("Applying SMOTE to balance classes (this may take a few seconds)...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"Resampled training set shape: {y_train_resampled.value_counts().to_dict()}")
    
    # 5. Train Random Forest Model
    print("\nTraining Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_resampled, y_train_resampled)
    
    # 6. Predictions & Evaluation
    y_pred = rf_model.predict(X_test)
    y_proba = rf_model.predict_proba(X_test)[:, 1]
    
    auc_score = roc_auc_score(y_test, y_proba)
    
    print("\n======================================================")
    print("RESEARCH QUESTION 3: PREDICTIVE MODELING (RQ3)")
    print("======================================================")
    print(f"AUC-ROC Score: {auc_score:.4f}")
    
    if auc_score > 0.65:
        print("Result: REJECT the null hypothesis. The model successfully predicts delays (AUC > 0.65).")
    else:
        print("Result: FAIL to reject the null hypothesis.")
        
    print("\nClassification Report (Test Set):")
    print(classification_report(y_test, y_pred))
    
    # 7. Feature Importance (The Business Story)
    importances = rf_model.feature_importances_
    feat_imp = pd.Series(importances, index=features).sort_values(ascending=False)
    print("Feature Importances (What causes delays?):")
    print(feat_imp)
    
    # Visualization 3: Feature Importance
    plt.figure(figsize=(8, 5))
    sns.barplot(x=feat_imp.values, y=feat_imp.index, hue=feat_imp.index, palette='viridis', legend=False)
    plt.title('What Drives Late Deliveries? (Feature Importance)', fontsize=14, fontweight='bold')
    plt.xlabel('Importance Score', fontsize=12)
    plt.ylabel('Features (Known at Checkout)', fontsize=12)
    plt.tight_layout()
    plt.savefig('visualizations/fig3_feature_importance.png', dpi=300)
    print("\nSaved visualization: visualizations/fig3_feature_importance.png")
    plt.close()

    # Visualization 4: ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    plt.figure(figsize=(6, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve: Predicting Late Deliveries', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig('visualizations/fig4_roc_curve.png', dpi=300)
    print("Saved visualization: visualizations/fig4_roc_curve.png")
    plt.close()

if __name__ == "__main__":
    main()