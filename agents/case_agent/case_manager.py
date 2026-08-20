from pathlib import Path

import pandas as pd

from agents.investigation_agent.schemas import (
    InvestigationCase,
    RiskSignal,
    EvidenceItem,
)


# Resolve paths relative to this file so the module works
# from notebooks, Streamlit, tests, or the terminal.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_case_sources(processed_dir=None):
    """
    Load the processed outputs from all MonteCore risk engines
    plus the unified case queue.
    """
    if processed_dir is None:
        processed_dir = DEFAULT_PROCESSED_DIR

    processed_dir = Path(processed_dir)

    aml_results = pd.read_csv(
        processed_dir / "aml_risk_results.csv"
    )

    anomaly_results = pd.read_csv(
        processed_dir / "transaction_anomaly_results.csv"
    )

    financial_results = pd.read_csv(
        processed_dir / "financial_risk_results.csv"
    )

    unified_queue = pd.read_csv(
        processed_dir / "unified_case_queue.csv"
    )

    return {
        "aml": aml_results,
        "anomaly": anomaly_results,
        "financial": financial_results,
        "queue": unified_queue,
    }


def build_case_from_queue_row(row):
    """
    Convert one unified queue row into an InvestigationCase.
    """
    source = row["CaseSource"]

    risk_signals = []
    evidence = []

    if source == "AML":
        risk_signals.append(
            RiskSignal(
                source="AML Model",
                signal_type="AML Risk",
                score=float(row["RiskScore"]),
                level=row["RiskLevel"],
                description="AML model flagged transaction.",
            )
        )

    elif source == "Anomaly":
        risk_signals.append(
            RiskSignal(
                source="Anomaly Engine",
                signal_type="Transaction Anomaly",
                score=float(row["RiskScore"]),
                level=row["RiskLevel"],
                description=row["CaseReason"],
            )
        )

    elif source == "Financial Risk":
        risk_signals.append(
            RiskSignal(
                source="Financial Risk Engine",
                signal_type="Financial Risk",
                score=float(row["RiskScore"]),
                level=row["RiskLevel"],
                description=row["CaseReason"],
            )
        )

    else:
        raise ValueError(
            f"Unsupported CaseSource: {source}"
        )

    evidence.append(
        EvidenceItem(
            evidence_type="Queue Metadata",
            description=(
                f"Source record: {row['SourceRecordID']}"
            ),
            value=row["SourceRecordID"],
            source="Unified Case Queue",
        )
    )

    evidence.append(
        EvidenceItem(
            evidence_type="Queue Metadata",
            description=(
                f"Entity ID: {row['EntityID']}"
            ),
            value=row["EntityID"],
            source="Unified Case Queue",
        )
    )

    return InvestigationCase(
        case_id=row["CaseID"],
        customer_id=(
            str(row["EntityID"])
            if source == "Financial Risk"
            else None
        ),
        transaction_id=(
            str(row["SourceRecordID"])
            if source in ["AML", "Anomaly"]
            else None
        ),
        risk_signals=risk_signals,
        evidence=evidence,
        priority=row["RiskLevel"],
        status=row["CaseStatus"],
    )


def attach_source_evidence(
    case,
    queue_row,
    aml_results,
    anomaly_results,
    financial_results,
):
    """
    Attach source-specific evidence to an InvestigationCase.
    """
    source = queue_row["CaseSource"]
    source_id = queue_row["SourceRecordID"]

    if source == "AML":
        match = aml_results[
            aml_results["AMLTransactionID"] == source_id
        ]

        if not match.empty:
            row = match.iloc[0]

            context = {
                "Timestamp": row["Timestamp"],
                "FromAccount": row["From Account"],
                "ToAccount": row["To Account"],
                "AmountPaid": row["Amount Paid"],
                "PaymentCurrency": row["Payment Currency"],
                "PaymentFormat": row["Payment Format"],
                "CrossCurrency": row["Is Cross Currency"],
                "SameBank": row["Is Same Bank"],
                "SameAccount": row["Is Same Account"],
                "AMLScore": row["AMLScore"],
            }

            for key, value in context.items():
                case.evidence.append(
                    EvidenceItem(
                        evidence_type="AML Context",
                        description=f"{key}: {value}",
                        value=value,
                        source="AML Dataset",
                        metadata={"context_key": key},
                    )
                )

    elif source == "Anomaly":
        match = anomaly_results[
            anomaly_results["TransactionID"] == source_id
        ]

        if not match.empty:
            row = match.iloc[0]

            context = {
                "AccountID": row["AccountID"],
                "TransactionAmount":
                    row["TransactionAmount"],
                "AccountBalance":
                    row["AccountBalance"],
                "TransactionDuration":
                    row["TransactionDuration"],
                "LoginAttempts":
                    row["LoginAttempts"],
                "AmountDeviationZScore":
                    row["AmountDeviationZScore"],
                "TransactionToBalanceRatio":
                    row["TransactionToBalanceRatio"],
                "IsolationAnomalyScore":
                    row["IsolationAnomalyScore"],
                "IsolationForestFlag":
                    row["IsAnomaly_IF"],
                "DBSCANFlag":
                    row["IsAnomaly_DBSCAN"],
                "AnomalyConfidence":
                    row["AnomalyConfidence"],
            }

            for key, value in context.items():
                case.evidence.append(
                    EvidenceItem(
                        evidence_type="Anomaly Context",
                        description=f"{key}: {value}",
                        value=value,
                        source="Transaction Anomaly Dataset",
                        metadata={"context_key": key},
                    )
                )

    elif source == "Financial Risk":
        customer_id = int(queue_row["EntityID"])

        match = financial_results[
            financial_results["CustomerID"] == customer_id
        ]

        if not match.empty:
            row = match.iloc[0]

            context = {
                "CustomerID":
                    row["CustomerID"],
                "RiskScore":
                    row["RiskScore"],
                "DelayedPaymentMonths":
                    row["DelayedPaymentMonths"],
                "MaxPaymentDelay":
                    row["MaxPaymentDelay"],
                "RecentPaymentDelay":
                    row["RecentPaymentDelay"],
                "CreditUtilization":
                    row["CreditUtilization"],
                "PaymentToBillRatio":
                    row["PaymentToBillRatio"],
                "FinancialStressIndicatorCount":
                    row["FinancialStressIndicatorCount"],
                "RiskReasonSummary":
                    row["RiskReasonSummary"],
            }

            for key, value in context.items():
                case.evidence.append(
                    EvidenceItem(
                        evidence_type=(
                            "Financial Risk Context"
                        ),
                        description=f"{key}: {value}",
                        value=value,
                        source="Financial Risk Dataset",
                        metadata={"context_key": key},
                    )
                )

    return case


def build_investigation_case(
    case_id,
    processed_dir=None,
):
    """
    Build a fully enriched InvestigationCase from
    a MonteCore unified CaseID.
    """
    if processed_dir is None:
        processed_dir = DEFAULT_PROCESSED_DIR

    sources = load_case_sources(processed_dir)

    queue = sources["queue"]

    match = queue[
        queue["CaseID"] == case_id
    ]

    if match.empty:
        raise ValueError(
            f"Case ID not found: {case_id}"
        )

    queue_row = match.iloc[0]

    case = build_case_from_queue_row(
        queue_row
    )

    case = attach_source_evidence(
        case=case,
        queue_row=queue_row,
        aml_results=sources["aml"],
        anomaly_results=sources["anomaly"],
        financial_results=sources["financial"],
    )

    return case