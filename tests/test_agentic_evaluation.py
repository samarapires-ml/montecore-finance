from agents.case_agent.case_manager import (
    build_investigation_case,
)

from agents.investigation_agent.orchestrator import (
    run_agentic_investigation,
)


TEST_CASES = [
    ("MC-00008", "AML"),
    ("MC-01162", "Anomaly"),
    ("MC-03612", "Financial Risk"),
]


def evaluate_case(case_id, label):
    print("\n" + "=" * 60)
    print(f"{label} — {case_id}")
    print("=" * 60)

    case = build_investigation_case(case_id)

    result = run_agentic_investigation(case)

    assert result.deterministic_result is not None

    assert result.primary_error is None, (
        f"{label} primary AI failed: "
        f"{result.primary_error}"
    )

    assert result.primary_summary is not None
    assert result.primary_summary.strip()

    assert result.review_error is None, (
        f"{label} review AI failed: "
        f"{result.review_error}"
    )

    assert result.review_output is not None
    assert result.review_output.strip()

    review_upper = result.review_output.upper()

    assert (
        "PASS" in review_upper
        or "NEEDS_CORRECTION" in review_upper
    ), (
        f"{label} reviewer did not return "
        "PASS or NEEDS_CORRECTION"
    )

    if "NEEDS_CORRECTION" in review_upper:
        status = "NEEDS_CORRECTION"
    else:
        status = "PASS"

    print("Primary summary available: YES")
    print("Second-look review available: YES")
    print("Review status:", status)

    print("\n--- PRIMARY SUMMARY ---\n")
    print(result.primary_summary)

    print("\n--- SECOND-LOOK REVIEW ---\n")
    print(result.review_output)

    print(f"\n{label} AGENTIC EVALUATION PASSED")

    return status


def main():
    print("=== MONTECORE MULTI-SOURCE AGENTIC EVALUATION ===")

    statuses = {}

    for case_id, label in TEST_CASES:
        statuses[label] = evaluate_case(
            case_id,
            label,
        )

    print("\n========================================")
    print("AGENTIC AI EVALUATION SUMMARY")
    print("========================================")

    for label, status in statuses.items():
        print(f"{label}: {status}")

    print("\nALL AGENTIC AI EVALUATIONS PASSED")


if __name__ == "__main__":
    main()