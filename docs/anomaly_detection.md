# Transaction Anomaly Detection

## Overview

MonteCore Finance includes an unsupervised transaction anomaly detection
pipeline designed to identify unusual financial activity without requiring
labelled fraud examples.

The pipeline complements the supervised AML detection model by identifying
transactions whose behavioural characteristics differ substantially from
normal transaction patterns.

## Dataset

The transaction anomaly dataset contains:

- 2,512 transactions
- 495 unique accounts
- 16 original attributes
- No missing values
- No duplicate rows
- No duplicate TransactionIDs

During validation, `PreviousTransactionDate` was found to occur after
`TransactionDate` for 100% of records. Because this temporal relationship
was logically inconsistent, the feature was excluded from downstream
modelling.

## Feature Engineering

The anomaly detection pipeline uses transaction-level, account-level,
behavioural, and ratio-based features.

### Temporal Features

- TransactionHour
- DayOfWeek

`IsWeekend` was initially created but excluded from modelling because the
dataset contained no weekend transactions, resulting in zero variance.

### Account Behaviour Features

- AccountAvgTransactionAmount
- AccountStdTransactionAmount
- AccountTransactionCount
- AmountDeviationFromAccountAvg
- AmountDeviationZScore

These features compare individual transactions with the historical behaviour
represented by other transactions belonging to the same account in the
available dataset.

### Financial Ratio Features

- TransactionToBalanceRatio
- TransactionToAccountAvgRatio

These features help identify transactions that are unusually large relative
to the account balance or the account's typical transaction size.

### Login Behaviour

- MultipleLoginAttempts

This feature captures transactions associated with elevated login activity.

## Feature Matrix

The final Isolation Forest and DBSCAN feature matrix contains 14 features:

1. LogTransactionAmount
2. TransactionDuration
3. LoginAttempts
4. AccountBalance
5. TransactionHour
6. DayOfWeek
7. AccountAvgTransactionAmount
8. AccountStdTransactionAmount
9. AccountTransactionCount
10. AmountDeviationFromAccountAvg
11. AmountDeviationZScore
12. TransactionToBalanceRatio
13. TransactionToAccountAvgRatio
14. MultipleLoginAttempts

Features were standardized before anomaly modelling.

## Isolation Forest

Isolation Forest was used as the first unsupervised anomaly detector.

The model identified:

- 126 anomalous transactions
- 2,386 normal transactions
- Approximately 5.02% of transactions as anomalous

Isolation Forest detects unusual observations by measuring how easily
individual observations can be isolated from the rest of the dataset.

## DBSCAN

DBSCAN was used as a second anomaly detection method.

A k-distance plot and parameter comparison were used to select an
`eps` value of 3.0.

DBSCAN identified:

- 2 clusters
- 66 noise transactions
- Approximately 2.63% of transactions as anomalies/noise

DBSCAN identifies anomalies differently from Isolation Forest by detecting
observations that do not belong to sufficiently dense regions of the
feature space.

## Model Agreement

The two anomaly detectors produced the following agreement:

- Flagged by both: 49
- Isolation Forest only: 77
- DBSCAN only: 17
- Flagged by neither: 2,369

Approximately 74.2% of DBSCAN noise points were also identified as
anomalous by Isolation Forest.

Agreement between the models represents stronger anomaly evidence, but it
does not imply that a transaction is fraudulent.

## Consensus Anomaly Characteristics

Transactions flagged by both models showed several notable behavioural
differences relative to the overall dataset.

Consensus anomalies had approximately:

- 2.04x higher transaction amounts
- 2.72x more login attempts
- 1.96x greater deviation from account-average transaction amounts
- 1.46x higher amount-deviation z-scores
- 6.36x higher transaction-to-balance ratios
- 1.68x higher transaction-to-account-average ratios

Average account balances were similar between consensus anomalies and the
overall dataset, suggesting that anomaly detection was capturing unusual
transaction behaviour rather than simply identifying high- or low-balance
accounts.

## Anomaly Confidence

Outputs from Isolation Forest and DBSCAN were combined into an anomaly
confidence layer.

- Low: neither detector flags the transaction
- Medium: exactly one detector flags the transaction
- High: both detectors flag the transaction

Distribution:

- Low: 2,369 transactions (94.31%)
- Medium: 94 transactions (3.74%)
- High: 49 transactions (1.95%)

These confidence levels represent confidence in anomalous behaviour and
should not be interpreted as probabilities of fraud.

## Investigation Queue

Transactions with Medium or High anomaly confidence are exported to:

`data/processed/transaction_anomaly_results.csv`

The final investigation queue contains:

- 143 transactions
- 16 investigation attributes
- 0 duplicate TransactionIDs
- 0 missing values

This structured artifact can be consumed by downstream investigation and
agentic components of MonteCore Finance.

## Role Within MonteCore Finance

The anomaly detection pipeline provides a complementary signal to the
supervised AML model.

The intended architecture is:

Transaction Data
→ Feature Engineering
→ AML / Anomaly Models
→ Risk Evidence
→ Investigation Queue
→ Agentic Investigation Layer

The anomaly models identify unusual behavioural patterns, while downstream
components can combine these signals with additional financial-risk evidence
to prioritize and explain investigation cases.

## Limitations

The anomaly dataset is relatively small and contains synthetic or
benchmark-style behavioural patterns.

Anomaly detection identifies unusual observations rather than confirmed
fraud.

The contamination parameter used by Isolation Forest influences the number
of transactions flagged, while DBSCAN results depend on parameters such as
`eps` and `min_samples`.

The invalid `PreviousTransactionDate` field was excluded because it was
temporally inconsistent across all observations.

Future work could incorporate larger transaction histories, richer temporal
behaviour, graph-based account relationships, and validated fraud outcomes.