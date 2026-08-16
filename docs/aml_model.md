# AML Detection Model

## Overview

MonteCore Finance includes a supervised machine-learning pipeline for identifying transactions that may warrant anti-money-laundering (AML) investigation.

The model is trained using a development sample derived from IBM's synthetic AML transaction dataset.

The objective of the model is not to make autonomous AML decisions. It acts as a screening mechanism that assigns transaction risk probabilities and identifies transactions for further investigation.

## Development Dataset

The AML modelling dataset contains:

- 56,924 transactions
- 51,747 legitimate transactions
- 5,177 labelled laundering transactions

The original IBM dataset contains approximately 0.102% labelled laundering transactions. The development dataset intentionally retains all laundering examples while sampling legitimate transactions to support efficient experimentation.

Therefore, performance on the development dataset should not be interpreted as production prevalence performance.

## Data Split

The modelling dataset was divided using stratified sampling:

| Split | Transactions |
| --- | ---: |
| Training | 39,846 |
| Validation | 8,539 |
| Test | 8,539 |

The test dataset remained untouched during model comparison and threshold selection.

## Baseline

A naive classifier predicting every transaction as legitimate achieves approximately 91% accuracy on the development data while detecting zero laundering transactions.

This demonstrates why accuracy alone is inappropriate for evaluating the AML detector.

Primary evaluation metrics therefore include:

- Precision
- Recall
- F1-score
- Precision-Recall AUC (PR-AUC)

## Model Comparison

Three initial classifiers were evaluated on the validation dataset:

| Model | Accuracy | Precision | Recall | F1 | PR-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.9232 | 0.6170 | 0.4106 | 0.4930 | 0.5491 |
| Random Forest | 0.9284 | 0.6322 | 0.5109 | 0.5651 | 0.6228 |
| Balanced Random Forest | 0.9291 | 0.6401 | 0.5058 | 0.5651 | 0.6198 |

The standard Random Forest provided the strongest overall validation performance, particularly for recall and PR-AUC.

## Threshold Selection

The default classification threshold of 0.50 was not assumed to be optimal for AML screening.

Thresholds were evaluated using the validation dataset to examine the trade-off between:

- laundering detection recall
- alert precision
- F1-score
- investigation workload

The highest validation F1-score was obtained at approximately:

**Threshold = 0.21**

At this threshold:

- Precision: approximately 0.522
- Recall: approximately 0.741
- F1: approximately 0.612
- Transactions flagged: 1,104 of 8,539 validation transactions

Lower thresholds increased laundering recall but also substantially increased the number of transactions requiring analyst review.

The threshold should therefore be interpreted as an operating point for the current prototype rather than a universally optimal AML threshold.

## Final Test Performance

After model and threshold selection using the validation dataset, the selected Random Forest was evaluated once on the untouched test dataset.

| Metric | Test Performance |
| --- | ---: |
| Accuracy | 0.9118 |
| Precision | 0.5099 |
| Recall | 0.7629 |
| F1-score | 0.6113 |
| PR-AUC | 0.6201 |

Final test confusion matrix:

| | Predicted Legitimate | Predicted Laundering |
| --- | ---: | ---: |
| Actual Legitimate | 7,194 | 569 |
| Actual Laundering | 184 | 592 |

The model therefore detected 592 of the 776 labelled laundering transactions in the held-out test dataset.

## Explainability

Random Forest built-in feature importance and permutation importance were examined.

Permutation importance using average precision identified several influential features, including:

1. Payment Format: ACH
2. Log Amount Paid
3. Transaction Hour
4. Is Same Entity
5. Payment Format: Cheque
6. Payment Format: Credit Card
7. Day of Week
8. Is Weekend

Feature importance describes predictive usefulness within this model and dataset. It should not be interpreted as evidence that these characteristics cause or independently indicate money laundering.

## Model Artifacts

The modelling pipeline produces:

- `aml_random_forest.joblib`
- `aml_threshold_config.joblib`

The threshold configuration stores the selected operating threshold separately from the classifier.

The preprocessing artifact created during the data phase is required to transform new transactions into the same feature representation used during model training.

## Limitations

The current model is a prototype trained on synthetic data.

Important limitations include:

- The development dataset intentionally changes the original class prevalence.
- Model performance may not generalize to real financial institutions.
- Synthetic transaction patterns may differ from real laundering behaviour.
- Feature importance should not be interpreted causally.
- Alert thresholds would require calibration against real investigation capacity, risk tolerance, and regulatory requirements.
- Human review remains necessary for any AML investigation or decision.

MonteCore Finance treats the AML model as a risk-screening component within a broader human-in-the-loop investigation system.