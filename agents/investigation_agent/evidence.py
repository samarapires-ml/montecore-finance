from typing import List

from .schemas import (
    InvestigationCase,
    EvidenceItem,
)


def build_signal_evidence(
    case: InvestigationCase
) -> List[EvidenceItem]:

    evidence_items = []

    for signal in case.risk_signals:

        if signal.score is not None:
            score_description = (
                f"{signal.signal_type} score: "
                f"{signal.score:.3f}"
            )
        else:
            score_description = (
                f"{signal.signal_type} level: "
                f"{signal.level}"
            )

        evidence_items.append(
            EvidenceItem(
                evidence_type="Model Signal",
                description=score_description,
                value=signal.score
                if signal.score is not None
                else signal.level,
                source=signal.source,
                metadata={
                    "signal_type": signal.signal_type,
                    "risk_level": signal.level,
                },
            )
        )

    return evidence_items


def attach_signal_evidence(
    case: InvestigationCase
) -> InvestigationCase:

    existing_sources = {
        item.source
        for item in case.evidence
        if item.evidence_type == "Model Signal"
    }

    new_items = [
        item for item in build_signal_evidence(case)
        if item.source not in existing_sources
    ]

    case.evidence.extend(new_items)

    return case


def attach_context_evidence(
    case: InvestigationCase,
    context: dict
) -> InvestigationCase:

    for key, value in context.items():
        case.evidence.append(
            EvidenceItem(
                evidence_type="Context",
                description=f"{key}: {value}",
                value=value,
                source="Case Context",
                metadata={"context_key": key},
            )
        )

    return case