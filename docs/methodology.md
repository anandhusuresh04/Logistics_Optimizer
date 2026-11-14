#  Methodology & Business Logic

**Project Title:** Delivery Delay Analytics: An Empirical Study of E-Commerce Logistics Bottlenecks

This document outlines the statistical approach, data engineering pipeline, and business definitions used in this project to ensure transparency and reproducibility.

---

## 1. Research Questions & Business Objectives

### RQ1: Customer Impact (Statistical Hypothesis Testing)
*   **Business Question:** Is late delivery significantly associated with lower customer review scores?
*   **Objective:** To quantify the exact drop in customer satisfaction caused by late deliveries to justify investment in logistics.
*   **Statistical Test:** **Mann-Whitney U Test** (chosen because review scores are ordinal 1–5 data, not normally distributed).
*   **Effect Size:** **Cliff's Delta** (used to measure the magnitude of the difference, not just the p-value).

### RQ2: Route & Geographic Bottlenecks
*   **Business Question:** Do delivery delay rates vary significantly across different shipping routes (Seller State -> Customer State)?
*   **Objective:** To identify specific geographic bottlenecks where the company is failing to meet its delivery promises.
*   **Statistical Test:** **Chi-Square Test of Independence** on a contingency table of the top 20 highest-volume routes.
*   **Effect Size:** **Cramér's V**.
*   **Analysis:** Ranking routes by both percentage of delays and absolute volume to find the most financially damaging bottlenecks.

### RQ3: Predictive Modeling (Pre-Dispatch)
*   **Business Question:** Can delivery delays be predicted *before* an order is dispatched using only checkout-time data?
*   **Objective:** To build an early-warning system that flags high-risk orders so customer service can intervene (e.g., upgrade shipping) before a delay occurs.
*   **Model:** **Random Forest Classifier**.
*   **Data Imbalance Handling:** **SMOTE** (Synthetic Minority Over-sampling Technique) applied strictly to the training data to handle the 93/7 class imbalance.
*   **Evaluation Metric:** **AUC-ROC** (Area Under the Curve) to evaluate how well the model distinguishes late vs. on-time orders.
*   **Data Leakage Prevention:** The model was strictly trained on features known *at checkout* (e.g., customer state, seller state, estimated shipping days, freight value). Actual delivery dates were excluded.

---

## 2. Operational Definitions (Business Logic)

To ensure reproducible data analysis, the following business rules were strictly applied:

| Term | Operational Definition |
| :--- | :--- |
| **Valid Order** | An order where `order_status` == 'delivered' AND both actual/estimated delivery dates are not null. |
| **Late Order** | An order where `order_delivered_customer_date` > `order_estimated_delivery_date`. |
| **On-Time Order** | An order where `order_delivered_customer_date` <= `order_estimated_delivery_date` (includes early deliveries). |
| **Delay Days** | The difference in days between actual and estimated delivery (Positive = Late, Negative = Early). |
| **Severe Delay** | An order delayed by more than 7 days (Threshold chosen based on industry standards for triggering refunds/churn). |
| **Shipping Route** | The directional pair of `seller_state` to `customer_state` (e.g., SP -> RJ). |
| **Bad Review** | A review score of 1 or 2 out of 5 stars. |

---

## 3. Data Processing & Engineering Strategy

1.  **Filtering:** The raw `orders` table was filtered to include only `delivered` orders to isolate logistics performance from cancellations or lost packages.
2.  **Relational Joins:** The `orders` table was merged with `order_items`, `order_reviews`, `customers`, and `sellers` using SQL-style joins to create a single analytical dataset (`master_orders.csv`).
3.  **Feature Engineering:** New columns were created, including `delay_days`, `is_late` (Target Variable), `estimated_shipping_days`, and `route`.
4.  **Handling Missing Data:** Records missing critical delivery dates or review scores were excluded to prevent bias in the statistical tests.

---

## 4. Financial Impact Methodology

To translate statistical findings into business value, the following assumptions were used in the ROI simulation:

*   **Cost of a Bad Review:** Estimated at **R$ 400** per bad review (R$ 150 for refund processing/return shipping + R$ 250 for lost Customer Lifetime Value).
*   **ROI Simulation:** If management implements a targeted 25% reduction in delays for the worst route, the model calculates the exact number of bad customer experiences prevented and the resulting financial savings.

---

## 5. Methodological Limitations

*   **Observational Data:** This study uses historical observational data; therefore, correlation does not imply causation (e.g., a late delivery might co-occur with a damaged product, both contributing to a bad review).
*   **Synthetic Financials:** The financial impact relies on assumed refund costs and CLV figures, as exact proprietary company data is unavailable.
*   **Temporal Scope:** The dataset spans 2016–2018. While the statistical relationships remain valid, absolute delivery times may not reflect current post-pandemic logistics realities.