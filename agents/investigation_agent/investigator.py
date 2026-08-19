from typing import Optional


from .schemas import (
    InvestigationCase,
    InvestigationResult,
    RiskSignal,
)

def determine_priority(risk_signals):
    high_count = sum(
        1
        for signal in risk_signals
        if signal.level == "High"
    )

    medium_count = sum(
        1
        for signal in risk_signals
        if signal.level == "Medium"
    )

    if high_count >= 2:
        return "Critical"

    if high_count == 1:
        return "High"

    if medium_count >= 2:
        return "Medium"

    return "Low"

def create_investigation_case(
    case_id: str,
    customer_id: Optional[str] = None,
    transaction_id: Optional[str] = None,
    aml_score: Optional[float] = None,
    aml_level: Optional[str] = None,
    anomaly_score: Optional[float] = None,
    anomaly_level: Optional[str] = None,
    financial_risk_score: Optional[float] = None,
    financial_risk_level: Optional[str] = None,
) -> InvestigationCase:

    risk_signals = []

    if aml_score is not None or aml_level is not None:
        risk_signals.append(
            RiskSignal(
                source="AML Model",
                signal_type="AML Risk",
                score=aml_score,
                level=aml_level,
                description="AML screening signal for the transaction."
            )
        )

    if anomaly_score is not None or anomaly_level is not None:
        risk_signals.append(
            RiskSignal(
                source="Anomaly Engine",
                signal_type="Transaction Anomaly",
                score=anomaly_score,
                level=anomaly_level,
                description="Unsupervised transaction anomaly signal."
            )
        )

    if financial_risk_score is not None or financial_risk_level is not None:
        risk_signals.append(
            RiskSignal(
                source="Financial Risk Engine",
                signal_type="Financial Risk",
                score=financial_risk_score,
                level=financial_risk_level,
                description="Customer financial early-warning signal."
            )
        )

    priority = determine_priority(risk_signals)

    return InvestigationCase(
    case_id=case_id,
    customer_id=customer_id,
    transaction_id=transaction_id,
    risk_signals=risk_signals,
    priority=priority,
)

def generate_findings(case: InvestigationCase):
    findings = []

    # Risk-signal findings
    for signal in case.risk_signals:
        if signal.level == "High":
            findings.append(
                f"High {signal.signal_type.lower()} signal "
                f"from {signal.source}."
            )

    # Context-based findings
    context_values = {
        item.metadata["context_key"]: item.value
        for item in case.evidence
        if item.evidence_type == "Context"
        and "context_key" in item.metadata
    }

    transaction_amount = context_values.get("TransactionAmount")
    account_balance = context_values.get("AccountBalance")
    login_attempts = context_values.get("LoginAttempts")
    delayed_months = context_values.get("DelayedPaymentMonths")

    if (
        transaction_amount is not None
        and account_balance is not None
        and account_balance > 0
        and transaction_amount > account_balance
    ):
        findings.append(
            "Transaction amount exceeds the current account balance."
        )

    if login_attempts is not None and login_attempts >= 3:
        findings.append(
            "Multiple login attempts were associated with the transaction."
        )

    if delayed_months is not None and delayed_months >= 2:
        findings.append(
            "Customer has repeated delayed-payment behaviour."
        )

    if not findings:
        findings.append(
            "No major deterministic investigation finding was identified."
        )

    return findings


def generate_recommended_actions(
    case: InvestigationCase,
    findings: list[str]
):
    actions = []

    if case.priority == "Critical":
        actions.append(
            "Escalate the case for immediate analyst review."
        )

    if any(
        "transaction anomaly" in finding.lower()
        for finding in findings
    ):
        actions.append(
            "Review recent transaction history for related unusual activity."
        )

    if any(
        "login attempts" in finding.lower()
        for finding in findings
    ):
        actions.append(
            "Review authentication and login activity associated with the account."
        )

    if any(
        "delayed-payment" in finding.lower()
        for finding in findings
    ):
        actions.append(
            "Review recent repayment behaviour and financial stress indicators."
        )

    if any(
        signal.signal_type == "AML Risk"
        for signal in case.risk_signals
    ):
        actions.append(
            "Review AML-related transaction evidence and linked account activity."
        )

    if not actions:
        actions.append(
            "Perform standard analyst review of the available case evidence."
        )

    return actions

def build_deterministic_investigation_result(
    case: InvestigationCase
):
    findings = generate_findings(case)

    actions = generate_recommended_actions(
        case,
        findings
    )

    supporting_evidence = [
        item.description
        for item in case.evidence
    ]

    summary = (
        f"Case {case.case_id} is classified as "
        f"{case.priority} priority based on "
        f"{len(case.risk_signals)} risk signals and "
        f"{len(case.evidence)} supporting evidence items."
    )

    return InvestigationResult(
        case_id=case.case_id,
        summary=summary,
        key_findings=findings,
        recommended_actions=actions,
        overall_risk_level=case.priority,
        confidence="Deterministic",
        supporting_evidence=supporting_evidence
    )