# Financial Risk & Early-Warning Engine

## Overview

MonteCore Finance includes a supervised financial-risk and early-warning
component designed to identify customers showing elevated risk of default
in the following month.

This component complements the AML classifier and transaction anomaly
detector by focusing on broader financial stress and repayment behaviour.

## Dataset

The model uses the UCI Default of Credit Card Clients dataset.

Dataset characteristics:

- 30,000 customers
- 23 predictive variables plus ID and target
- Target: default payment in the following month
- 23,364 non-default customers
- 6,636 default customers
- Default prevalence: 22.12%

No missing values, duplicate rows, or duplicate IDs were found.

Rare or undocumented demographic codes were consolidated:

- EDUCATION values 0, 5, and 6 → Other
- MARRIAGE value 0 → Other

The model itself intentionally excludes demographic features such as
SEX, EDUCATION, and MARRIAGE so that the prototype focuses on financial
and behavioural evidence.

## Feature Engineering

The model includes both raw repayment history and engineered financial
behaviour features.

### Financial Summary Features

- AverageBillAmount
- AveragePaymentAmount
- CreditUtilization
- PaymentToBillRatio

### Repayment Behaviour Features

- DelayedPaymentMonths
- MaxPaymentDelay
- RecentPaymentDelay
- RepaymentDeterioration

### Trend Features

- BillAmountTrend
- PaymentAmountTrend

### Financial Stress Feature

- FinancialStressIndicatorCount

This indicator combines several warning conditions such as:

- high credit utilization
- low payment-to-bill ratio
- repeated payment delays
- recent delinquency
- worsening repayment behaviour

Default rates increased substantially as multiple warning indicators
accumulated.

For example:

- 0 indicators → 11.52% default rate
- 1 indicator → 13.73%
- 2 indicators → 20.22%
- 3 indicators → 51.24%
- 4 indicators → 59.73%
- 5 indicators → 54.05%

The indicator is exploratory and should not be interpreted as a calibrated
default probability.

## Model Features

The final model uses 19 features:

1. LIMIT_BAL
2. AGE
3. PAY_0
4. PAY_2
5. PAY_3
6. PAY_4
7. PAY_5
8. PAY_6
9. AverageBillAmount
10. AveragePaymentAmount
11. CreditUtilization
12. PaymentToBillRatio
13. DelayedPaymentMonths
14. MaxPaymentDelay
15. RecentPaymentDelay
16. RepaymentDeterioration
17. BillAmountTrend
18. PaymentAmountTrend
19. FinancialStressIndicatorCount

## Data Split

The dataset was divided using stratified sampling:

- Training: 24,000 customers
- Test: 6,000 customers

Both splits preserved the original 22.12% default prevalence.

## Baseline Model

Logistic Regression was used as an interpretable baseline.

Test results:

- Accuracy: 0.815
- Default precision: 0.649
- Default recall: 0.352
- Default F1: 0.456
- ROC-AUC: 0.754
- PR-AUC: 0.518

The model achieved reasonable overall accuracy but detected only 35.2%
of actual defaults.

## Random Forest Model

A class-balanced Random Forest was trained using:

- 300 trees
- max depth = 10
- minimum leaf size = 10
- balanced class weights

At the default 0.50 threshold:

- Accuracy: 0.778
- Default precision: 0.499
- Default recall: 0.589
- Default F1: 0.541
- ROC-AUC: 0.778
- PR-AUC: 0.558

Random Forest was selected because it provided stronger minority-class
detection, higher F1, and better ROC-AUC and PR-AUC despite lower overall
accuracy.

## Threshold Optimization

Multiple operating thresholds were evaluated to balance:

- default recall
- false-positive investigations
- F1-score
- investigation volume

The prototype operating threshold was selected as:

**0.45**

At this threshold:

- True negatives: 3,675
- False positives: 998
- False negatives: 475
- True positives: 852
- Precision: 0.461
- Recall: 0.642
- F1: 0.536
- Customers flagged: 1,850 of 6,000 test customers

The threshold is a prototype operating decision rather than a universally
optimal default-risk cutoff.

## Risk Levels

Model scores were translated into operational risk bands:

- Low: score < 0.30
- Medium: 0.30 ≤ score < 0.45
- High: score ≥ 0.45

Distribution:

- Low: 2,460 customers
- Medium: 1,690 customers
- High: 1,850 customers

Observed default rates:

- Low: 8.09%
- Medium: 16.33%
- High: 46.05%

The risk bands therefore provided useful risk stratification.

## Calibration Limitation

Raw Random Forest scores were not treated as perfectly calibrated
probabilities.

For example, the High-Risk group had an average model score of approximately
68.97%, while its observed default rate was 46.05%.

The score should therefore be interpreted as a model risk score for ranking
and thresholding rather than a literal probability of default.

## Feature Importance

The strongest Random Forest features included:

1. DelayedPaymentMonths
2. MaxPaymentDelay
3. FinancialStressIndicatorCount
4. PAY_0
5. RecentPaymentDelay
6. AveragePaymentAmount
7. AverageBillAmount
8. CreditUtilization

Repayment history and delinquency behaviour were the dominant predictive
signals.

## Risk Indicators

High-risk customers were also assigned interpretable rule-based warning
indicators.

Common indicators among High-Risk customers included:

- Severe historical payment delay: 77.14%
- Low payment-to-bill ratio: 70.38%
- Recent payment delinquency: 63.41%
- Multiple financial stress indicators: 62.49%
- Repeated delayed payments: 57.41%
- Repayment behaviour deteriorating: 53.57%
- High credit utilization: 27.03%

These indicators are contextual explanations and should not be interpreted
as exact causal explanations of the Random Forest prediction.

## Investigation Output

The financial-risk pipeline exports:

`data/processed/financial_risk_results.csv`

The file contains:

- 6,000 test customers
- 13 output fields
- unique CustomerIDs
- risk score
- risk level
- early-warning flag
- financial stress indicators
- validation target for historical evaluation

In production, the ground-truth `ActualDefault` field would not be available
at prediction time.

## Saved Artifacts

The pipeline generates:

- `financial_risk_random_forest.joblib`
- `financial_risk_features.json`
- `financial_risk_policy.json`

The feature JSON records the exact 19-feature contract.

The policy JSON stores the early-warning threshold and Low/Medium/High risk
bands separately from the trained model.

Reload testing confirmed that the persisted model reproduces identical
risk scores and early-warning flags.

## Role Within MonteCore Finance

MonteCore now contains three complementary ML signals:

1. Supervised AML classification
2. Unsupervised transaction anomaly detection
3. Financial risk / early-warning scoring

These outputs can later be combined by the MonteCore investigation agent
to prioritize cases, gather evidence, and generate human-readable
investigation summaries.

## Limitations

The current model is a prototype based on a benchmark credit-default dataset.

Important limitations include:

- Risk scores are not probability-calibrated.
- Thresholds are prototype operating choices.
- Data does not represent every type of financial institution or customer.
- Historical default prediction is not the same as real-time intervention.
- Rule-based warning reasons do not provide causal explanations.
- Production use would require fairness review, temporal validation,
  monitoring, calibration, governance, and human oversight.