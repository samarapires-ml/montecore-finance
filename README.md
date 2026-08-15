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
Detect unusual transaction behaviour using machine learning techniques such as Isolation Forest and density-based anomaly detection.

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

MonteCore Finance is being developed incrementally, with the initial implementation focused on building a reliable AML transaction-risk detection foundation.

### Phase 1 — Project Foundation ✅

- Project repository and Python environment configured
- Modular project structure established
- Core dependencies and development tooling configured
- Git-based version control workflow established

### Phase 2 — Data Foundation & Feature Engineering ✅

The initial AML pipeline uses IBM's synthetic Anti-Money Laundering dataset.

#### Dataset

- **5,078,345** raw financial transactions
- **5,073,168** legitimate transactions
- **5,177** labelled laundering transactions
- Original laundering prevalence: approximately **0.102%**
- Account and entity metadata incorporated for investigation context

#### Modelling Dataset

A development dataset was constructed by retaining all laundering transactions and randomly sampling legitimate transactions:

- **56,924 total transactions**
- **51,747 legitimate**
- **5,177 laundering**

The development dataset intentionally contains a higher laundering prevalence than the original dataset. Model evaluation will therefore distinguish development-set performance from performance under the original class distribution.

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

The initial leakage-safe baseline uses **15 processed ML features** after categorical encoding.

#### Data Split

Stratified train/validation/test datasets were created:

| Dataset | Transactions |
| --- | ---: |
| Training | 39,846 |
| Validation | 8,539 |
| Test | 8,539 |

Preprocessing is fitted on the training data only to prevent information leakage.

### Phase 3 — AML Detection Models 🚧

The next development phase will focus on:

- Establishing baseline classification performance
- Training and comparing AML detection models
- Evaluating precision, recall, F1-score and PR-AUC
- Addressing severe class imbalance
- Selecting an appropriate decision threshold
- Model explainability and feature importance
- Saving the selected AML model for integration with the investigation layer