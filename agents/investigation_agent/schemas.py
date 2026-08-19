from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RiskSignal:
    source: str
    signal_type: str
    score: Optional[float] = None
    level: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    evidence_type: str
    description: str
    value: Any = None
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvestigationCase:
    case_id: str
    customer_id: Optional[str] = None
    transaction_id: Optional[str] = None

    risk_signals: List[RiskSignal] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)

    priority: Optional[str] = None
    status: str = "Open"


@dataclass
class InvestigationResult:
    case_id: str
    summary: str
    key_findings: List[str]
    recommended_actions: List[str]

    overall_risk_level: Optional[str] = None
    confidence: Optional[str] = None

    supporting_evidence: List[str] = field(default_factory=list)