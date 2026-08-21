from agents.case_agent.case_manager import (
    build_investigation_case,
)

from agents.investigation_agent.investigator import (
    build_deterministic_investigation_result,
)

from agents.investigation_agent.watsonx_client import (
    WatsonxClient,
)


TEST_CASES = [
    {
        "case_id": "MC-00008",
        "label": "AML",
        "questions": [
            "Why was this case flagged?",
            "Does this prove money laundering?",
            "What additional evidence would be useful to investigate it?",
        ],
        "forbidden_terms": [
            "account takeover",
            "hacked",
            "credentials stolen",
            "confirmed money laundering",
            "confirmed fraud",
            "http://",
            "https://",
        ],
    },
    {
        "case_id": "MC-01162",
        "label": "Anomaly",
        "questions": [
            "Why was this case flagged?",
            "Does this prove fraud or account takeover?",
            "What additional evidence would be useful to investigate it?",
        ],
        "forbidden_terms": [
            "confirmed fraud",
            "confirmed account takeover",
            "hacked",
            "credentials stolen",
            "http://",
            "https://",
        ],
    },
    {
        "case_id": "MC-03612",
        "label": "Financial Risk",
        "questions": [
            "Why was this case flagged?",
            "Does this prove the customer will default?",
            "What additional evidence would be useful to investigate it?",
        ],
        "forbidden_terms": [
            "confirmed default",
            "bankruptcy",
            "fraud",
            "http://",
            "https://",
        ],
    },
]


def evaluate_case(case_config):
    case_id = case_config["case_id"]
    label = case_config["label"]
    questions = case_config["questions"]
    forbidden_terms = case_config["forbidden_terms"]

    print("\n" + "=" * 70)
    print(f"{label} CASE COPILOT EVALUATION — {case_id}")
    print("=" * 70)

    case = build_investigation_case(case_id)

    deterministic_result = (
        build_deterministic_investigation_result(case)
    )

    client = WatsonxClient()

    results = []

    for question in questions:
        print("\nQUESTION:")
        print(question)

        draft_answer = client.chat_about_case(
            case=case,
            deterministic_result=deterministic_result,
            question=question,
            chat_history=None,
        )

        final_answer = client.review_case_chat_answer(
            case=case,
            deterministic_result=deterministic_result,
            question=question,
            draft_answer=draft_answer,
        )

        assert final_answer is not None
        assert final_answer.strip()

        final_lower = final_answer.lower()

        for forbidden in forbidden_terms:
            assert forbidden.lower() not in final_lower, (
                f"{label} answer contained forbidden phrase: "
                f"'{forbidden}'"
            )

        print("\nFINAL REVIEWED ANSWER:\n")
        print(final_answer)

        results.append(
            {
                "question": question,
                "answer": final_answer,
            }
        )

    print(f"\n{label} CASE COPILOT EVALUATION PASSED")

    return results


def main():
    print("=== MONTECORE CASE COPILOT EVALUATION ===")

    all_results = {}

    for case_config in TEST_CASES:
        label = case_config["label"]
        all_results[label] = evaluate_case(case_config)

    print("\n" + "=" * 70)
    print("CASE COPILOT EVALUATION SUMMARY")
    print("=" * 70)

    for label, results in all_results.items():
        print(
            f"{label}: "
            f"{len(results)} reviewed answers passed"
        )

    print("\nALL CASE COPILOT EVALUATIONS PASSED")


if __name__ == "__main__":
    main()