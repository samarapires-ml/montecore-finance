# MonteCore Finance — Evaluation Report

## Overview

MonteCore Finance was evaluated as an end-to-end financial risk investigation system rather than only as a collection of individual machine-learning models.

The evaluation covers five system layers:

1. Unified case and evidence pipeline
2. Deterministic investigation engine
3. Agentic AI investigation workflow
4. Conversational Case Copilot
5. Failure handling and application-level behaviour

Representative cases from all three MonteCore risk sources were included:

- AML detection
- Transaction anomaly detection
- Financial risk / early warning

---

## 1. End-to-End Pipeline Validation

The pipeline validation verifies that outputs from each risk engine can be transformed into structured investigation cases.

### Queue

The unified investigation queue contained:

**4,844 cases**

### Representative Cases

| Risk Source | Case ID | Priority | Evidence Items |
| --- | --- | --- | ---: |
| AML | MC-00008 | Critical | 12 |
| Transaction Anomaly | MC-01162 | Critical | 13 |
| Financial Risk | MC-03612 | High | 11 |

The tests verified:

- Case retrieval
- Priority propagation
- Transaction/customer identifier mapping
- Risk-signal construction
- Supporting evidence construction
- Compatibility with the downstream investigation engine

**Result: PASS**

---

## 2. Deterministic Investigation Engine

The deterministic layer was tested independently of generative AI.

Tests covered representative AML, anomaly, and financial-risk cases.

The evaluation verified that the engine can generate:

- Investigation summaries
- Key deterministic findings
- Recommended analyst actions
- Critical-case escalation
- AML-specific review actions
- Financial-risk findings

All three representative cases completed deterministic validation successfully.

| Risk Source | Result |
| --- | --- |
| AML | PASS |
| Transaction Anomaly | PASS |
| Financial Risk | PASS |

**Overall result: PASS**

---

## 3. Agentic AI Evaluation

MonteCore uses a two-model investigation workflow:

```text
Structured Case Evidence
        ↓
Deterministic Investigation
        ↓
Primary AI Investigator — Mistral Small
        ↓
Independent Reviewer — Llama 3.3
        ↓
Analyst-Facing Assessment
```

The primary model generates an investigation assessment from the supplied case evidence.

The second-look model independently compares that assessment with the original case and deterministic investigation context.

### Review Objective

The reviewer checks for:

- Unsupported factual claims
- Invented identities or relationships
- Unsupported fraud or AML conclusions
- Unsupported account-compromise claims
- Causal claims not established by evidence
- Recommendations extending beyond available evidence
- Overstatement of probabilistic model signals

### Evaluation Findings

Across representative AML, anomaly, and financial-risk investigations, the second-look reviewer identified instances where the primary model introduced interpretations beyond the supplied evidence.

Examples included:

- Treating anomalous activity as potentially fraudulent without sufficient evidence
- Inferring account-takeover implications
- Extending recommendations beyond deterministic actions
- Introducing causal interpretations not established by the case context

The reviewer returned `NEEDS_CORRECTION` where appropriate and generated corrected assessments constrained to the available evidence.

This behaviour demonstrates the purpose of the second-look architecture: the primary model is not assumed to be correct simply because it generated a plausible investigation narrative.

**Agentic evaluation result: PASS**

---

## 4. Case Copilot Evaluation

Case Copilot was evaluated using three question types for each risk source:

1. Why was the case flagged?
2. Does the available signal prove the suspected outcome?
3. What additional evidence would be useful?

This produced **9 reviewed responses**.

| Risk Source | Questions Tested | Passed |
| --- | ---: | ---: |
| AML | 3 | 3 |
| Transaction Anomaly | 3 | 3 |
| Financial Risk | 3 | 3 |
| **Total** | **9** | **9** |

### Leading-Question Tests

The evaluation intentionally included questions designed to test whether the system would overstate model evidence.

Examples included:

> Does this prove money laundering?

> Does this prove fraud or account takeover?

> Does this prove the customer will default?

The reviewed responses correctly distinguished risk signals from confirmed outcomes.

The system did not treat:

- An AML model flag as proof of money laundering
- An anomaly signal as proof of fraud or account takeover
- A high financial-risk score as proof of future default

**Case Copilot result: 9 / 9 PASS**

---

## 5. Robustness & Failure Testing

MonteCore was tested under controlled failure conditions.

### Invalid Case ID

Input:

```text
MC-99999
```

Expected behaviour:

The system should reject the request with an explicit error rather than returning an incorrect case.

Observed behaviour:

```text
Case ID not found: MC-99999
```

**Result: PASS**

### Missing watsonx Credentials

The test environment temporarily removed:

```text
IBM_CLOUD_API_KEY
IBM_PROJECT_ID
IBM_WATSONX_URL
```

MonteCore correctly detected the missing configuration and produced an explicit credentials error.

**Result: PASS**

### AI Failure Fallback

The orchestration layer was tested with the AI configuration unavailable.

The system:

- Preserved the deterministic investigation result
- Recorded the primary AI failure
- Safely skipped the second-look stage
- Avoided failure of the complete investigation pipeline

**Result: PASS**

---

## 6. Application Acceptance Testing

The Streamlit application was manually tested as an integrated analyst workflow.

Validated functionality included:

- Risk-source filtering
- Priority filtering
- Case search
- Investigation queue pagination
- Case selection
- Case overview
- Evidence inspection
- AI Review
- Case Copilot
- Switching between cases
- Conversation clearing
- Dashboard rendering and layout

**Application acceptance result: PASS**

---

## Evaluation Summary

| Evaluation Area | Result |
| --- | --- |
| End-to-End Pipeline | PASS |
| Deterministic Investigation | PASS |
| Agentic AI Workflow | PASS |
| Case Copilot | **9 / 9 PASS** |
| Invalid Case Handling | PASS |
| Missing Credential Handling | PASS |
| AI Failure Fallback | PASS |
| Application Acceptance | PASS |

---

## Interpretation

These evaluations demonstrate that MonteCore's prototype pipeline operates across all three supported financial-risk sources and that its generative-AI layer is surrounded by deterministic evidence, independent review, and explicit failure handling.

The tests do **not** establish that the system is suitable for production financial decision-making.

In particular, successful grounding tests do not guarantee that a language model will never generate an unsupported statement. The second-look reviewer is itself an AI system and can also fail.

MonteCore therefore maintains a human-in-the-loop design in which model scores and AI-generated assessments remain decision-support signals rather than final financial or regulatory determinations.