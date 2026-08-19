from dataclasses import dataclass, field
from typing import Optional

from .investigator import build_deterministic_investigation_result
from .schemas import InvestigationCase, InvestigationResult
from .watsonx_client import WatsonxClient


@dataclass
class AgenticInvestigationResult:
    """Container for the full output of run_agentic_investigation().

    The deterministic_result is always populated and is the authoritative
    grounded output.  primary_summary and review_output are populated only
    when the corresponding watsonx calls succeeded.  Error fields record
    failure reasons without hiding them.

    This is a decision-support output.  It does not constitute a fraud or
    AML determination.  Final judgement belongs to a human analyst.
    """

    # Always present — the rule-based grounded layer.
    deterministic_result: InvestigationResult

    # Populated when Mistral successfully produced an assessment.
    primary_summary: Optional[str] = None
    primary_error: Optional[str] = None

    # Populated when Llama successfully reviewed the Mistral assessment.
    review_output: Optional[str] = None
    review_error: Optional[str] = None


def run_agentic_investigation(
    case: InvestigationCase,
    watsonx_client: Optional[WatsonxClient] = None,
) -> AgenticInvestigationResult:
    """Run the full three-layer investigation pipeline for a single case.

    Layers
    ------
    1. Deterministic — always runs; produces the grounded InvestigationResult.
    2. Primary AI    — Mistral Small summarises and reasons over the
                       deterministic output.
    3. Second-Look   — Llama 3.3 70B independently reviews the Mistral
                       assessment for unsupported claims, invented facts, or
                       conclusions that exceed the evidence.

    The deterministic result is the source of truth at every stage.  The AI
    layers are decision-support only.  No output from this function should be
    treated as a final fraud or AML determination.

    Parameters
    ----------
    case:
        A fully populated InvestigationCase (risk signals and evidence already
        attached by the caller via attach_signal_evidence / attach_context_evidence).
    watsonx_client:
        Optional pre-configured WatsonxClient.  If None, one is created from
        environment variables (IBM_CLOUD_API_KEY, IBM_PROJECT_ID,
        IBM_WATSONX_URL).

    Returns
    -------
    AgenticInvestigationResult
        Always contains deterministic_result.  AI fields are None when the
        corresponding call failed; the matching *_error field explains why.

    Raises
    ------
    This function does not raise.  All watsonx failures are captured into
    primary_error / review_error so the caller always receives a usable result.
    """

    # ── Layer 1: deterministic (always runs) ──────────────────────────────
    deterministic_result = build_deterministic_investigation_result(case)

    client = watsonx_client or WatsonxClient()

    # ── Layer 2: Mistral primary summary ──────────────────────────────────
    primary_summary: Optional[str] = None
    primary_error: Optional[str] = None

    try:
        primary_summary = client.generate_investigation_summary(
            case, deterministic_result
        )
    except Exception as exc:
        primary_error = (
            f"Primary AI summarization unavailable: {type(exc).__name__}: {exc}"
        )

    # ── Layer 3: Llama second-look review ─────────────────────────────────
    review_output: Optional[str] = None
    review_error: Optional[str] = None

    if primary_summary is not None:
        try:
            review_output = client.review_investigation_summary(
                case, deterministic_result, primary_summary
            )
        except Exception as exc:
            review_error = (
                f"Second-look review unavailable: {type(exc).__name__}: {exc}"
            )
    else:
        review_error = "Second-look review skipped: primary summary was not produced."

    return AgenticInvestigationResult(
        deterministic_result=deterministic_result,
        primary_summary=primary_summary,
        primary_error=primary_error,
        review_output=review_output,
        review_error=review_error,
    )
