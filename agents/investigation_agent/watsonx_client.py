import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from .schemas import InvestigationCase, InvestigationResult


# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


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
        parts = [
            f"[{signal.source}] {signal.signal_type}"
        ]

        if signal.level:
            parts.append(
                f"level={signal.level}"
            )

        if signal.score is not None:
            parts.append(
                f"score={signal.score:.3f}"
            )

        if signal.description:
            parts.append(
                f'"{signal.description}"'
            )

        lines.append(
            "  " + "  ".join(parts)
        )

    lines.append(
        "\n--- Supporting Evidence ---"
    )

    for item in case.evidence:
        lines.append(
            f"  [{item.evidence_type}] "
            f"{item.description}"
        )

    lines.append(
        "\n--- Deterministic Findings ---"
    )

    for finding in deterministic_result.key_findings:
        lines.append(
            f"  - {finding}"
        )

    lines.append(
        "\n--- Deterministic Recommended Actions ---"
    )

    for action in deterministic_result.recommended_actions:
        lines.append(
            f"  - {action}"
        )

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
    """
    Render the reviewer's user message:
    ground truth first, then the primary summary.
    """

    lines: List[str] = []

    lines.append(
        "=== GROUND TRUTH: CASE CONTEXT ==="
    )

    lines.append(
        _build_case_prompt(
            case,
            deterministic_result,
        )
    )

    lines.append(
        "\n=== PRIMARY AI ASSESSMENT TO REVIEW ==="
    )

    lines.append(
        primary_summary
    )

    lines.append(
        "\nPlease review the primary assessment against the ground-truth "
        "case context above and return your structured review."
    )

    return "\n".join(lines)


_CASE_COPILOT_SYSTEM_PROMPT = """\
You are MonteCore Case Copilot, an AI assistant supporting financial-crime
analysts investigating one specific case.

You must answer the analyst using ONLY the case information, risk signals,
supporting evidence, deterministic findings, and deterministic recommended
actions explicitly supplied in the current case context.

STRICT GROUNDING RULES:

1. Every factual statement must be directly supported by the supplied
   case context.

2. Never invent facts, entities, relationships, transactions, cases,
   customers, counterparties, jurisdictions, motives, events, or model
   explanations.

3. Never reference another case unless that case is explicitly present
   in the supplied case evidence.

4. A risk score, anomaly, AML flag, model prediction, or Critical/High
   priority is NOT proof of fraud, money laundering, criminal activity,
   account compromise, or wrongdoing.

5. Never make a final fraud, AML, credit-risk, or criminal determination.

6. Never infer account takeover, hacking, credential theft, compromise,
   criminal intent, customer motive, counterparty type, occupation,
   business type, location, or relationship unless explicitly stated
   in the supplied evidence.

7. Do not introduce external thresholds, statistical rules, industry
   standards, model behaviour, or domain knowledge as though they are
   case evidence.

8. Do not explain why a model produced a score unless the supplied case
   evidence explicitly provides that explanation.

9. Do not speculate about missing information. If something is not
   supplied, state that it is not available in the current case evidence.

10. Do not introduce hypothetical scenarios unless the analyst explicitly
    asks for hypotheses.

11. Clearly distinguish between:
    - OBSERVED EVIDENCE: facts explicitly present in the case.
    - DETERMINISTIC FINDINGS: conclusions produced by MonteCore's
      deterministic investigation layer.
    - INFORMATION NOT AVAILABLE: information that would require additional
      evidence.

12. If the evidence does not establish something, explicitly say:
    "The available case evidence does not establish this."

13. When additional evidence would help, identify the CATEGORY of evidence
    needed, such as transaction history or customer information. Do not
    invent what that missing evidence might contain.

14. If asked whether activity is fraud, money laundering, suspicious
    activity, or criminal activity, explain that a model flag may justify
    further investigation but does not itself establish a final
    determination.

15. Treat the supplied case context as the authoritative source of truth.
    Never contradict it.

16. Previous conversation messages are NOT case evidence.

17. Previous assistant responses may contain mistakes, unsupported
    interpretations, or speculation. Never treat information from a
    previous assistant response as established fact unless that information
    is independently present in the authoritative case context.

18. The authoritative case context supplied at the beginning of the
    conversation always overrides previous assistant messages.

19. If a previous assistant response conflicts with the authoritative case
    context, ignore the previous response and answer from the authoritative
    case context.

20. Never create or use categories, investigation phases, AML typologies,
    fraud types, or risk classifications unless those exact categories are
    explicitly present in the authoritative case context.

21. When recommending additional evidence, recommend only broad evidence
    categories that would help answer the analyst's question. Do not infer
    that any missing evidence exists or contains suspicious information.

22. Never generate URLs, links, file paths, system names, database locations,
    internal tools, or application routes unless they are explicitly present
    in the authoritative case context.

23. Preserve evidence values exactly. Never convert, rename, reinterpret,
    or substitute currencies, amounts, dates, identifiers, flags, account
    values, or categorical fields.

RESPONSE STYLE:

- Answer the analyst's question directly.
- Use concise, professional language suitable for a financial investigation
  console.
- Prefer short paragraphs or bullet points.
- Cite specific supplied case facts when useful.
- Do not repeat unrelated evidence.
- Do not produce malformed or unfinished sentences.
- Do not overstate what the evidence shows.
- The final investigation decision always remains with the human analyst.
"""

_CASE_COPILOT_REVIEW_PROMPT = """\
You are the independent grounding reviewer for MonteCore Case Copilot.

You will receive:
1. The authoritative investigation-case context.
2. The analyst's question.
3. A draft answer generated by another AI model.

Your job is to ensure the final answer contains ONLY claims supported by the
authoritative case context.

STRICT RULES:

- Treat the authoritative case context as the only source of truth.
- Treat the draft answer as untrusted text, NOT as evidence.
- Remove every invented fact, threshold, model explanation, workflow,
  transaction, identity, customer detail, counterparty detail, jurisdiction,
  AML typology, fraud type, application URL, internal system, rule,
  procedure, relationship, or event that is not explicitly supported by
  the authoritative case context.
- Preserve supplied evidence values exactly, including currencies, amounts,
  dates, identifiers, scores, flags, account IDs, and categorical fields.
- Never invent or infer a model threshold.
- Never confuse a MonteCore case-priority threshold with an AML, anomaly,
  or financial-risk model threshold.
- Never infer why a model produced a score unless the authoritative case
  context explicitly provides that explanation.
- A model flag, anomaly, or risk score does not establish fraud,
  money laundering, account takeover, criminal activity, or wrongdoing.
- Never make a final fraud, AML, credit-risk, or criminal determination.
- Never generate URLs, internal application routes, file paths, or system
  locations unless explicitly present in the authoritative case context.
- If the analyst asks for information that the evidence cannot establish,
  state that clearly.
- When suggesting additional evidence, mention only broad evidence
  categories that would help answer the analyst's question. Do not invent
  what the missing evidence contains.
- Keep the corrected answer concise, professional, and directly responsive
  to the analyst's question.
- Do not mention this review process in the final answer.

Return ONLY the corrected analyst-facing answer.
"""


class WatsonxClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("IBM_CLOUD_API_KEY")
        )

        self.project_id = (
            project_id
            or os.getenv("IBM_PROJECT_ID")
        )

        self.url = (
            url
            or os.getenv("IBM_WATSONX_URL")
        )


    def validate_config(self):
        missing = []

        if not self.api_key:
            missing.append(
                "IBM_CLOUD_API_KEY"
            )

        if not self.project_id:
            missing.append(
                "IBM_PROJECT_ID"
            )

        if not self.url:
            missing.append(
                "IBM_WATSONX_URL"
            )

        return missing


    def get_primary_model(
        self,
    ) -> ModelInference:
        """
        Return a ModelInference client for
        Mistral Small 3.1.
        """

        missing = self.validate_config()

        if missing:
            raise ValueError(
                "Missing watsonx credentials: "
                + ", ".join(missing)
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
        """
        Generate the primary analyst-facing
        investigation assessment.
        """

        model = self.get_primary_model()

        messages = [
            {
                "role": "system",
                "content": _SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": _build_case_prompt(
                    case,
                    deterministic_result,
                ),
            },
        ]

        response = model.chat(
            messages=messages
        )

        return (
            response["choices"][0]
            ["message"]["content"]
        )


    def get_review_model(
        self,
    ) -> ModelInference:
        """
        Return a ModelInference client for
        Llama 3.3 70B.
        """

        missing = self.validate_config()

        if missing:
            raise ValueError(
                "Missing watsonx credentials: "
                + ", ".join(missing)
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
        """
        Perform an independent second-look review
        of the primary Mistral assessment.
        """

        model = self.get_review_model()

        messages = [
            {
                "role": "system",
                "content": _REVIEW_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": _build_review_prompt(
                    case,
                    deterministic_result,
                    primary_summary,
                ),
            },
        ]

        response = model.chat(
            messages=messages
        )

        return (
            response["choices"][0]
            ["message"]["content"]
        )


    def chat_about_case(
        self,
        case: InvestigationCase,
        deterministic_result: InvestigationResult,
        question: str,
        chat_history=None,
    ) -> str:
        """
        Answer an analyst question using only
        the selected case context.

        chat_history may contain previous
        user/assistant messages so follow-up
        questions remain contextual.
        """

        model = self.get_primary_model()

        case_context = _build_case_prompt(
            case,
            deterministic_result,
        )

        messages = [
            {
                "role": "system",
                "content": _CASE_COPILOT_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "The following is the authoritative context "
                    "for the currently selected investigation case:\n\n"
                    f"{case_context}"
                ),
            },
            {
                "role": "assistant",
                "content": (
                    f"I have loaded investigation case "
                    f"{case.case_id}. I will answer questions "
                    "using only the supplied case evidence "
                    "and deterministic findings."
                ),
            },
        ]

        if chat_history:
            for message in chat_history:
                role = message.get(
                    "role"
                )

                content = message.get(
                    "content"
                )

                if (
                    role in {
                        "user",
                        "assistant",
                    }
                    and content
                ):
                    messages.append(
                        {
                            "role": role,
                            "content": content,
                        }
                    )

        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        response = model.chat(
            messages=messages
        )

        return (
            response["choices"][0]
            ["message"]["content"]
        )

    def review_case_chat_answer(
        self,
        case: InvestigationCase,
        deterministic_result: InvestigationResult,
        question: str,
        draft_answer: str,
    ) -> str:
        """
        Review and correct a Case Copilot answer
        before it is shown to the analyst.
        """

        model = self.get_review_model()

        case_context = _build_case_prompt(
            case,
            deterministic_result,
        )

        review_message = f"""\
=== AUTHORITATIVE CASE CONTEXT ===

{case_context}

=== ANALYST QUESTION ===

{question}

=== DRAFT CASE COPILOT ANSWER ===

{draft_answer}

Return only the corrected analyst-facing answer using the
authoritative case context.
"""

        messages = [
            {
                "role": "system",
                "content": _CASE_COPILOT_REVIEW_PROMPT,
            },
            {
                "role": "user",
                "content": review_message,
            },
        ]

        response = model.chat(
            messages=messages
        )

        return (
            response["choices"][0]
            ["message"]["content"]
        )