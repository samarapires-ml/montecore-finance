# MonteCore Finance — Dataset Strategy

MonteCore Finance combines multiple datasets because financial anomaly detection, suspicious activity detection, and financial risk prediction represent different analytical problems.

Rather than treating unusual activity as confirmed fraud, the platform separates these signals and allows the AI investigation layer to analyze them together.

## Data Layer 1 — Transaction Anomaly Detection

**Dataset:** Bank Transaction Dataset for Fraud Detection  
**Source:** Kaggle  
**Purpose:** Identify transactions that deviate from normal customer behaviour.

The dataset contains contextual transaction information such as transaction amount, location, device, channel, account balance, transaction duration, and login attempts.

Because the dataset does not provide confirmed fraud labels, MonteCore Finance uses it for **unsupervised anomaly detection**, not supervised fraud classification.

Planned techniques include:

- Isolation Forest
- DBSCAN
- Customer/transaction segmentation
- Behavioural baseline analysis

**Primary output:** Transaction Anomaly Score

---

## Data Layer 2 — Suspicious Financial Activity Detection

**Dataset:** IBM Transactions for Anti-Money Laundering (AML)  
**Source:** IBM

**Purpose:** Analyze transaction patterns associated with suspicious financial activity.

Unlike the anomaly dataset, the IBM AML dataset includes labelled laundering activity, allowing MonteCore Finance to evaluate its ability to distinguish labelled suspicious transactions from legitimate activity.

This layer will support experimentation with supervised machine learning and financial-crime pattern detection.

**Primary output:** Suspicious Activity Risk Score

---

## Data Layer 3 — Financial Risk Prediction

**Dataset:** Default of Credit Card Clients  
**Source:** UCI Machine Learning Repository

**Purpose:** Estimate customer financial/default risk using historical credit and repayment behaviour.

Relevant information includes:

- Credit limits
- Historical repayment status
- Bill amounts
- Previous payment amounts
- Customer financial characteristics
- Default outcome

This dataset provides a labelled outcome and will support supervised financial-risk modelling.

**Primary output:** Financial Risk Score

---

## Combined MonteCore Intelligence

The three analytical layers represent different types of financial risk:

1. **Transaction Anomaly Score** — Is this activity unusual?
2. **Suspicious Activity Risk Score** — Does the activity resemble labelled suspicious financial behaviour?
3. **Financial Risk Score** — Is the customer showing elevated financial/default risk?

These signals will eventually be provided to the MonteCore AI investigation agent alongside relevant customer and transaction context.

The agent will investigate the available evidence, explain contributing risk signals, prioritize cases, and generate decision-support recommendations for human analysts.

MonteCore Finance does not treat an anomaly as proof of fraud and does not autonomously make consequential financial decisions.

## IBM AML Dataset Preparation Summary

For the initial AML modelling pipeline, MonteCore Finance uses the IBM HI-Small transaction dataset.

### Raw Dataset

- Total transactions: **5,078,345**
- Legitimate transactions: **5,073,168**
- Laundering transactions: **5,177**
- Laundering rate: approximately **0.102%**

The raw dataset is highly imbalanced, which reflects the rarity of labelled laundering transactions.

### Modelling Dataset

To create a manageable development dataset while preserving all known laundering examples:

- All **5,177 laundering transactions** were retained.
- **51,747 legitimate transactions** were randomly sampled.
- Final modelling dataset size: **56,924 transactions**

The modelling dataset is intentionally more balanced than the original dataset for development purposes. Final model evaluation will take the original class imbalance into account.

### Feature Engineering

The initial feature set includes:

- Transaction hour
- Day of week
- Weekend indicator
- Cross-currency indicator
- Same-bank indicator
- Same-account indicator
- Same-entity indicator
- Log-transformed transaction amount
- Amount difference
- Log-transformed amount difference
- Entity-level transaction activity features
- Entity-pair transaction frequency

The first baseline modelling pipeline uses a selected subset of leakage-safe transaction features.

### Train / Validation / Test Split

The modelling data was split using stratified sampling:

- **Training:** 39,846 transactions
- **Validation:** 8,539 transactions
- **Test:** 8,539 transactions

The laundering proportion is approximately **9.1%** in each development split.

### Preprocessing

- `Payment Format` is one-hot encoded.
- Numerical features are passed through directly.
- Preprocessing is fitted using the training dataset only.
- The target variable `Is Laundering` is kept separate from model features.
- Final baseline feature count after preprocessing: **15**

### Saved Artifacts

The following processed artifacts are generated for downstream modelling:

- `ibm_aml_model_data.csv`
- `X_train.npy`
- `X_val.npy`
- `X_test.npy`
- `y_train.npy`
- `y_val.npy`
- `y_test.npy`
- `feature_names.npy`
- `preprocessor.joblib`

These artifacts provide the input foundation for the Phase 3 AML detection models.