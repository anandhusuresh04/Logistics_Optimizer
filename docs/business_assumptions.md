#  Financial Assumptions & ROI Simulation Logic

**Project:** Delivery Delay Analytics

This document outlines the financial assumptions used in `src/business_impact.py` to translate statistical findings (bad reviews caused by delays) into a simulated Return on Investment (ROI).

*Note: Because this project uses a public dataset (Olist), exact proprietary financial data from the company is unavailable. The figures below are modeled using standard e-commerce industry averages and can be easily adjusted in the Python script.*

---

## 1. Baseline Loss Assumptions (The Cost of a Bad Review)

When an order is delivered late, it causes immediate financial damage (refunds/returns) and long-term financial damage (customer churn). We assume that a late delivery resulting in a **1-star or 2-star review** represents a complete loss of that customer.

| Variable | Assumed Value | Business Justification |
| :--- | :--- | :--- |
| **Refund Processing Cost** | **R$ 150.00** | Covers the cost of return shipping, restocking, customer service agent time, and potential payment gateway fees for a refunded order. |
| **Customer Lifetime Value (CLV) Loss** | **R$ 250.00** | The estimated future net profit lost when a customer churns due to a poor delivery experience. (Conservative estimate for an e-commerce platform). |
| **Total Loss per Bad Review** | **R$ 400.00** | Combined immediate refund cost + lost future revenue. |

###  The Baseline Formula:
> **Total Estimated Loss = (Number of Late Orders with 1-2 Star Reviews) × R$ 400**
*   *Result from analysis:* 3,980 bad reviews × R$ 400 = **R$ 1,592,000.00** total estimated loss.

---

## 2. ROI Simulation Assumptions (The Solution)

To prove that investing in logistics is profitable, we simulate a targeted intervention on the worst-performing route (`SP -> RJ`). 

*   **The Intervention:** Renegotiating the carrier Service Level Agreement (SLA) or adding a warehouse buffer for the São Paulo to Rio de Janeiro route.
*   **Target Improvement:** **25% Reduction** in late deliveries on this specific route.
*   **Why 25%?** A 25% improvement is a realistic, achievable operational goal. It does not require a complete overhaul of the logistics network, but rather a targeted fix (e.g., switching to a faster local courier for that specific state line).

###  The ROI Formula:
> **Estimated Savings = (Bad Reviews on SP -> RJ × 25%) × R$ 400**
*   *Result from analysis:* 841 bad reviews × 25% = 210 bad reviews prevented.
*   210 × R$ 400 = **R$ 84,000.00 in estimated savings.**

---

## 3. Sensitivity Analysis (Scenario Modeling)

Because these figures are assumptions, a Business Analyst must model different scenarios. If the actual cost of a bad review is higher or lower, the savings scale linearly:

| Scenario | Assumed Cost per Bad Review | Total Baseline Loss | Estimated Savings (SP -> RJ fix) |
| :--- | :--- | :--- | :--- |
| **Low Estimate** | R$ 200 (Refund only) | R$ 796,000 | R$ 42,000 |
| **Base Estimate (Used)** | **R$ 400 (Refund + CLV)** | **R$ 1,592,000** | **R$ 84,000** |
| **High Estimate** | R$ 600 (Aggressive CLV loss) | R$ 2,388,000 | R$ 126,000 |

---

## 4. Limitations of this Model

1.  **Causation vs. Correlation:** The model assumes the bad review was *solely* due to the delivery delay. In reality, the customer might also have been unhappy with the product quality.
2.  **Static CLV:** The model assumes a flat R$ 250 loss per customer. In reality, some customers are high-value (e.g., R$ 2,000 CLV) and some are low-value (e.g., R$ 50 CLV).
3.  **Exclusion of Operational Costs:** The ROI simulation calculates *savings*, not *net profit*. The actual cost of implementing the 25% improvement (e.g., paying a faster carrier) would need to be subtracted to find the true Net ROI.