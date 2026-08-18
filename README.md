# MonteCore Finance

> **See the Risk Before It Becomes the Problem.**

MonteCore Finance is an agentic AI platform for financial anomaly detection, emerging-risk monitoring, and intelligent investigation.

The platform is designed to act as an AI financial investigation co-worker, helping analysts detect suspicious activity, investigate unusual financial behaviour, prioritize cases, and make faster, evidence-based decisions.

## The Problem

Financial institutions process large volumes of transactions and customer activity every day. Identifying suspicious transactions is only one part of the challenge — analysts must also determine why activity is unusual, assess whether broader financial risk is emerging, prioritize cases, and decide what action should be taken.

Traditional workflows can require analysts to manually review transaction histories, account behaviour, login activity, financial patterns, and other risk indicators across multiple systems.

MonteCore Finance explores how AI can support this workflow by combining anomaly detection, behavioural risk monitoring, and agentic investigation into a single decision-support system.

## The Solution

MonteCore Finance is an AI-powered financial investigation platform designed to help analysts identify and investigate potentially risky financial activity.

The system combines:

- **Transaction anomaly detection** to identify unusual or potentially suspicious transactions.
- **Financial behaviour monitoring** to detect emerging signs of customer financial stress.
- **AI-powered investigation** to gather and analyze relevant evidence behind flagged activity.
- **Explainable risk insights** to communicate why a customer or transaction was flagged.
- **Case prioritization** to help analysts focus on higher-risk investigations first.
- **Decision-support recommendations** to suggest appropriate next steps while keeping final decisions with human analysts.

Rather than replacing financial analysts, MonteCore Finance is designed to operate as an **AI co-worker** that reduces repetitive investigation work and helps analysts reach informed decisions faster.

## Core Capabilities

MonteCore Finance is being developed around four core capabilities:

### 1. Transaction Anomaly Detection

Detect unusual transaction behaviour using an ensemble of unsupervised machine learning techniques.

The implemented anomaly detection pipeline includes:

- **Isolation Forest** for isolation-based anomaly detection
- **DBSCAN** for density-based anomaly detection
- **Behavioural feature engineering** using account-level transaction patterns
- **Model agreement analysis** to identify consensus anomalies
- **Anomaly confidence levels** (Low, Medium, High)
- **Investigation queue generation** for downstream AI investigation

Current results on the transaction anomaly dataset:

- 2,512 transactions analyzed
- 126 transactions flagged by Isolation Forest
- 66 transactions identified as DBSCAN noise
- 49 transactions flagged by both models
- 143 Medium/High-confidence transactions prioritized for investigation

Anomaly detection identifies unusual behavioural patterns and should not be interpreted as confirmed fraud.

### 2. Emerging Financial Risk Monitoring
Analyze changes in customer financial behaviour over time to identify early warning signals before financial risk escalates.

### 3. Agentic AI Investigation
Use an AI investigation agent to gather relevant customer and transaction evidence, analyze detected risk signals, and generate an explainable case assessment.

### 4. Human-Centered Decision Support
Prioritize investigation cases and recommend appropriate next steps while keeping financial analysts in control of final decisions.

## AI & Machine Learning Approach

MonteCore Finance combines machine learning and agentic AI to support financial investigation workflows.

### Machine Learning
- **Isolation Forest** — transaction anomaly detection
- **DBSCAN** — density-based identification of unusual transaction patterns
- **Customer Segmentation** — analysis of customer behavioural patterns
- **Behavioural Risk Scoring** — identification of emerging financial stress signals over time

### Agentic AI
The AI investigation layer will analyze outputs from the machine learning models alongside customer and transaction context to:

1. Gather relevant evidence.
2. Investigate why activity was flagged.
3. Identify contributing risk signals.
4. Generate an explainable case summary.
5. Recommend appropriate next steps for human review.

### Human-in-the-Loop
MonteCore Finance is designed as a decision-support system. AI-generated assessments and recommendations assist financial analysts, while final investigation and intervention decisions remain under human control.

## Current Development Status

MonteCore Finance is being developed incrementally as a modular financial
risk and investigation platform.

The machine-learning foundation currently contains three complementary
risk-detection components:

1. Supervised AML classification
2. Unsupervised transaction anomaly detection
3. Financial risk and early-warning scoring

These signals will ultimately feed into an agentic investigation layer
that gathers evidence, explains risk signals, and supports analyst review.

---

### Phase 1 — Project Foundation ✅

- Project repository and Python environment configured
- Modular project structure established
- Core dependencies and development tooling configured
- Git-based version control workflow established

---

### Phase 2 — AML Data Foundation & Feature Engineering ✅

The AML pipeline uses IBM's synthetic Anti-Money Laundering dataset.

#### Dataset

- **5,078,345** raw financial transactions
- **5,073,168** legitimate transactions
- **5,177** labelled laundering transactions
- Original laundering prevalence: approximately **0.102%**
- Account and entity metadata incorporated for investigation context

#### Modelling Dataset

A development dataset was constructed by retaining all laundering
transactions and randomly sampling legitimate transactions:

- **56,924 total transactions**
- **51,747 legitimate**
- **5,177 laundering**

The development dataset intentionally contains a higher laundering
prevalence than the original dataset.

#### Feature Engineering

Candidate features include:

- Transaction time and day characteristics
- Weekend activity
- Cross-currency transactions
- Same-bank transfers
- Same-account transfers
- Same-entity transfers
- Log-transformed transaction amounts
- Amount differences
- Entity activity
- Entity-pair transaction frequency

The leakage-safe baseline uses **15 processed ML features** after
categorical encoding.

#### Data Split

| Dataset | Transactions |
| --- | ---: |
| Training | 39,846 |
| Validation | 8,539 |
| Test | 8,539 |

Preprocessing is fitted on training data only to prevent information
leakage.

---

### Phase 3 — AML Detection Model ✅

A supervised AML screening pipeline was developed using the IBM synthetic
AML dataset.

Three approaches were evaluated:

- Logistic Regression
- Random Forest
- Class-balanced Random Forest

The standard **Random Forest** was selected based on validation
performance.

#### AML Threshold Optimization

Rather than using the default classification threshold of 0.50, the
operating threshold was tuned using the validation dataset.

Selected prototype threshold:

**0.21**

This increases laundering recall while accepting additional false-positive
alerts for analyst review.

#### Held-Out AML Test Performance

| Metric | Score |
| --- | ---: |
| Precision | 0.510 |
| Recall | **0.763** |
| F1-score | **0.611** |
| PR-AUC | **0.620** |

On the untouched test set, the model detected:

**592 of 776 labelled laundering transactions.**

Model interpretation was performed using Random Forest feature importance
and permutation importance.

Full methodology and evaluation details are documented in:

`docs/aml_model.md`

---

### Phase 4 — Transaction Anomaly Detection ✅

An unsupervised transaction anomaly-detection pipeline was developed to
identify unusual behavioural patterns without relying on fraud labels.

The pipeline combines:

- **Isolation Forest**
- **DBSCAN**
- Account-level behavioural feature engineering
- Model agreement analysis
- Confidence-based anomaly prioritization

#### Results

From **2,512 transactions**:

- Isolation Forest flagged **126 transactions**
- DBSCAN identified **66 transactions** as noise
- **49 transactions** were flagged by both models
- **77 transactions** were flagged only by Isolation Forest
- **17 transactions** were flagged only by DBSCAN
- **143 Medium/High-confidence transactions** were prioritized for investigation

The resulting investigation dataset is exported to:

`data/processed/transaction_anomaly_results.csv`

Anomaly detection identifies unusual behavioural patterns and should not
be interpreted as confirmed fraud.

Full methodology is documented in:

`docs/anomaly_detection.md`

---

### Phase 5 — Financial Risk & Early-Warning Engine ✅

A supervised financial-risk model was developed to identify customers
showing elevated risk of default in the following month.

The pipeline uses a **30,000-customer credit-default dataset** and combines
repayment history with engineered financial-stress indicators.

#### Financial Behaviour Features

Features include:

- Credit utilization
- Average bill amount
- Average payment amount
- Payment-to-bill ratio
- Number of delayed-payment months
- Maximum payment delay
- Recent payment delinquency
- Repayment deterioration
- Bill balance trend
- Payment trend
- Combined financial-stress indicators

#### Model Comparison

Logistic Regression was used as an interpretable baseline and compared
against a class-balanced Random Forest.

| Metric | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Accuracy | **0.815** | 0.778 |
| Default Precision | **0.649** | 0.499 |
| Default Recall | 0.352 | **0.589** |
| Default F1 | 0.456 | **0.541** |
| ROC-AUC | 0.754 | **0.778** |
| PR-AUC | 0.518 | **0.558** |

The **Random Forest** was selected because the early-warning objective
prioritizes detection of genuinely risky customers rather than overall
classification accuracy.

#### Early-Warning Threshold

The prototype operating threshold was selected as:

**0.45**

At this threshold:

- Precision: **0.461**
- Recall: **0.642**
- F1-score: **0.536**
- True positives: **852**
- False negatives: **475**
- **1,850 of 6,000 test customers** were flagged for investigation

#### Risk Stratification

Customers are assigned operational risk levels:

| Risk Level | Customers | Observed Default Rate |
| --- | ---: | ---: |
| Low | 2,460 | **8.09%** |
| Medium | 1,690 | **16.33%** |
| High | 1,850 | **46.05%** |

High-Risk customers therefore showed substantially greater observed
default risk than Low-Risk customers.

The model also generates interpretable financial-stress indicators such as:

- Severe historical payment delay
- Recent payment delinquency
- Repeated delayed payments
- Low payment-to-bill ratio
- High credit utilization
- Worsening repayment behaviour
- Multiple simultaneous financial-stress indicators

Raw Random Forest scores are used for ranking and thresholding and should
not be interpreted as perfectly calibrated probabilities.

Full methodology, limitations, threshold analysis, and evaluation results
are documented in:

`docs/financial_risk_engine.md`

---

## ML Components Completed

MonteCore Finance currently contains three complementary machine-learning
signals:

| Component | Approach | Purpose |
| --- | --- | --- |
| AML Detection | Supervised Random Forest | Identify transactions resembling labelled laundering activity |
| Transaction Anomaly Detection | Isolation Forest + DBSCAN | Identify unusual transaction behaviour without labels |
| Financial Risk Engine | Class-balanced Random Forest | Identify customers showing emerging default risk |

Together, these components provide different perspectives on financial risk.

A transaction may be suspicious because it resembles known laundering
patterns, because it is behaviourally unusual, because the customer is
showing broader financial stress, or because several signals occur
simultaneously.

---

## Next Phase — Agentic Investigation Layer 🚧

The next major development phase will connect the machine-learning outputs
to an AI-powered investigation workflow.

The investigation layer is planned to:

1. Receive flagged transactions and customers from the ML components.
2. Gather relevant transaction and customer evidence.
3. Compare AML, anomaly, and financial-risk signals.
4. Identify the strongest contributing risk indicators.
5. Generate a structured investigation summary.
6. Prioritize cases based on combined risk evidence.
7. Recommend appropriate next steps for human review.

The goal is not autonomous financial decision-making.

MonteCore Finance is designed as a **human-in-the-loop decision-support
system**, where AI assists investigation while analysts retain control over
final decisions.
