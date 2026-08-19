import os
from typing import List, Optional

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from .schemas import InvestigationCase, InvestigationResult

PRIMARY_MODEL_ID = "mistralai/mistral-small-3-1-24b-instruct-2503"
REVIEW_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

_SYSTEM_PROMPT = """\
You are an AI assistant supporting a financial-crime analyst at a regulated \
financial institution.

Your role is to help the analyst review an investigation case by producing a \
clear, structured assessment based solely on the evidence and deterministic \
findings supplied to you.

Rules you must follow without exception:
- Use only the evidence, risk signals, findings, and recommended actions \
provided in this message. Do not invent transactions, identities, amounts, \
motives, counterparties, dates, or any other facts.
- Clearly distinguish observed evidence (what the models detected) from \
interpretation (what that evidence may suggest).
- Do not make a final fraud or AML determination. You are providing decision \
support, not a verdict.
- The final investigation decision belongs to the human analyst. Your \
assessment is one input into that decision.
- Keep your response concise and structured. Do not repeat the raw input data \
verbatim.

Return your response in exactly this format:

## Case Summary
<Two to three sentences summarising the case, its priority, and the signals \
that drove it.>

## Key Risk Indicators
<Bullet list of the most significant risk signals and evidence items.>

## Recommended Next Steps
<Bullet list of suggested analyst actions, drawn from the deterministic \
recommendations and your reading of the evidence.>

## Analyst Caution
<One to two sentences reminding the analyst of the limitations of this \
AI-generated assessment and that the final decision is theirs.>\
"""


def _build_case_prompt(
    case: InvestigationCase,
    deterministic_result: InvestigationResult,
) -> str:
    """Render the grounded case context that is sent as the user message."""
    lines: List[str] = []

    lines.append(f"CASE ID: {case.case_id}")
    if case.customer_id:
        lines.append(f"Customer ID: {case.customer_id}")
    if case.transaction_id:
        lines.append(f"Transaction ID: {case.transaction_id}")
    lines.append(f"Priority: {case.priority}")
    lines.append(f"Status: {case.status}")

    lines.append("\n--- Risk Signals ---")
    for signal in case.risk_signals:
        parts = [f"[{signal.source}] {signal.signal_type}"]
        if signal.level:
            parts.append(f"level={signal.level}")
        if signal.score is not None:
            parts.append(f"score={signal.score:.3f}")
        if signal.description:
            parts.append(f'"{signal.description}"')
        lines.append("  " + "  ".join(parts))

    lines.append("\n--- Supporting Evidence ---")
    for item in case.evidence:
        lines.append(f"  [{item.evidence_type}] {item.description}")

    lines.append("\n--- Deterministic Findings ---")
    for finding in deterministic_result.key_findings:
        lines.append(f"  - {finding}")

    lines.append("\n--- Deterministic Recommended Actions ---")
    for action in deterministic_result.recommended_actions:
        lines.append(f"  - {action}")

    lines.append(
        "\nPlease produce a structured analyst assessment using only the "
        "information above."
    )

    return "\n".join(lines)


_REVIEW_SYSTEM_PROMPT = """\
You are an independent AI reviewer supporting a financial-crime analyst at a \
regulated financial institution.

Your task is to critically evaluate a primary AI-generated investigation \
assessment. You will be given:
  1. The original case evidence, risk signals, deterministic findings, and \
deterministic recommended actions — this is the GROUND TRUTH.
  2. The primary AI assessment to review.

You must check the primary assessment strictly against the ground truth and \
identify every place it goes beyond the supplied evidence. Specifically, \
detect and flag:
- Invented facts: any transaction detail, amount, date, counterparty, \
identity, or event not present in the ground-truth evidence.
- Unsupported motives or intent: claims about why a customer or party acted \
in a certain way that are not stated in the evidence.
- Unsupported security-compromise claims: statements that an account was \
hacked, credentials were stolen, or a device was compromised unless that is \
explicitly stated in the evidence.
- Unsupported identities, dates, transactions, or counterparties: any named \
or implied party or event not traceable to the ground-truth evidence.
- Conclusions stronger than the evidence supports: language implying \
confirmed fraud, confirmed laundering, or confirmed criminal activity when \
the evidence only shows elevated risk signals.
- Final fraud or AML determinations: any statement that this IS fraud or IS \
money laundering rather than a signal requiring further investigation.
- Recommendations not grounded in the deterministic case: action items that \
go beyond the deterministic recommended actions or the supplied evidence.

Rules you must follow without exception:
- Base your review solely on the ground-truth case context provided.
- Be specific: quote or closely paraphrase each problematic statement.
- If no issues are found, say so clearly.
- Do not invent new evidence or introduce external knowledge.
- The final investigation decision belongs to the human analyst.

Return your response in exactly this format:

## Review Status
<Either the single word PASS if the primary assessment is fully grounded, \
or NEEDS_CORRECTION if any unsupported or overstated claims were found.>

## Unsupported or Overstated Claims
<If Review Status is PASS, write "None identified." \
Otherwise provide a bullet list. For each item: quote or paraphrase the \
problematic statement, then explain why it is not supported by the \
ground-truth evidence.>

## Corrected Investigation Assessment
<If Review Status is PASS, write "The primary assessment is acceptable \
as written." \
Otherwise rewrite the full investigation assessment — Case Summary, Key \
Risk Indicators, Recommended Next Steps, and Analyst Caution — using only \
the ground-truth evidence and deterministic findings. Do not include any \
claim that was not present in the ground-truth context.>

## Human Review Note
<One to two sentences addressed to the human analyst, noting whether the \
primary assessment was accepted or corrected, and reminding them that this \
review is itself AI-generated and that final judgement is theirs.>\
"""


def _build_review_prompt(
    case: InvestigationCase,
    deterministic_result: InvestigationResult,
    primary_summary: str,
) -> str:
    """Render the reviewer's user message: ground truth first, then the
    primary summary to be evaluated."""
    lines: List[str] = []

    lines.append("=== GROUND TRUTH: CASE CONTEXT ===")
    lines.append(_build_case_prompt(case, deterministic_result))

    lines.append("\n=== PRIMARY AI ASSESSMENT TO REVIEW ===")
    lines.append(primary_summary)

    lines.append(
        "\nPlease review the primary assessment against the ground-truth "
        "case context above and return your structured review."
    )

    return "\n".join(lines)


class WatsonxClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("IBM_CLOUD_API_KEY")
        self.project_id = project_id or os.getenv("IBM_PROJECT_ID")
        self.url = url or os.getenv("IBM_WATSONX_URL")

    def validate_config(self):
        missing = []

        if not self.api_key:
            missing.append("IBM_CLOUD_API_KEY")

        if not self.project_id:
            missing.append("IBM_PROJECT_ID")

        if not self.url:
            missing.append("IBM_WATSONX_URL")

        return missing

    def get_primary_model(self) -> ModelInference:
        """Return a ModelInference client for the primary investigation model
        (Mistral Small 3.1).  Raises ValueError if credentials are missing."""
        missing = self.validate_config()
        if missing:
            raise ValueError(
                f"Missing watsonx credentials: {', '.join(missing)}"
            )

        return ModelInference(
            model_id=PRIMARY_MODEL_ID,
            credentials=Credentials(
                url=self.url,
                api_key=self.api_key,
            ),
            project_id=self.project_id,
        )

    def generate_investigation_summary(
        self,
        case: InvestigationCase,
        deterministic_result: InvestigationResult,
    ) -> str:
        """Call Mistral Small via chat() to produce an analyst-facing
        investigation assessment grounded in the deterministic findings.

        The deterministic engine's findings and recommended actions are passed
        verbatim as context so the model cannot stray beyond the supplied
        evidence.  The returned string is the raw model response text; callers
        are responsible for presenting it alongside the deterministic result.

        Raises ValueError if credentials are missing.
        """
        model = self.get_primary_model()

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_case_prompt(
                case, deterministic_result
            )},
        ]

        response = model.chat(messages=messages)

        return response["choices"][0]["message"]["content"]

    def get_review_model(self) -> ModelInference:
        """Return a ModelInference client for the second-look review model
        (Llama 3.3 70B).  Raises ValueError if credentials are missing."""
        missing = self.validate_config()
        if missing:
            raise ValueError(
                f"Missing watsonx credentials: {', '.join(missing)}"
            )

        return ModelInference(
            model_id=REVIEW_MODEL_ID,
            credentials=Credentials(
                url=self.url,
                api_key=self.api_key,
            ),
            project_id=self.project_id,
        )

    def review_investigation_summary(
        self,
        case: InvestigationCase,
        deterministic_result: InvestigationResult,
        primary_summary: str,
    ) -> str:
        """Use Llama 3.3 70B to perform an independent second-look review of
        the Mistral primary summary.

        The reviewer receives the full ground-truth case context alongside the
        primary summary and checks it for invented facts, unsupported motives,
        security-compromise claims, or conclusions that exceed the evidence.

        Returns the raw review text containing Review Status,
        Unsupported or Overstated Claims, Corrected Investigation Assessment,
        and Human Review Note.

        Raises ValueError if credentials are missing.
        """
        model = self.get_review_model()

        messages = [
            {"role": "system", "content": _REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": _build_review_prompt(
                case, deterministic_result, primary_summary
            )},
        ]

        response = model.chat(messages=messages)

        return response["choices"][0]["message"]["content"]
