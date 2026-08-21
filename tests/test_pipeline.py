from agents.case_agent.case_manager import (
    load_case_sources,
    build_investigation_case,
)


def check_case(
    case_id,
    expected_priority,
    expected_transaction_id=None,
    expected_customer_id=None,
):
    print(f"\nTesting {case_id}...")

    case = build_investigation_case(case_id)

    assert case.case_id == case_id
    assert case.priority == expected_priority

    if expected_transaction_id is not None:
        assert case.transaction_id == expected_transaction_id

    if expected_customer_id is not None:
        assert case.customer_id == expected_customer_id

    assert len(case.risk_signals) > 0
    assert len(case.evidence) > 0

    print("Priority:", case.priority)
    print("Transaction ID:", case.transaction_id)
    print("Customer ID:", case.customer_id)
    print("Risk signals:", len(case.risk_signals))
    print("Evidence items:", len(case.evidence))

    print(f"{case_id} PASSED")


def main():
    print("=== MONTECORE PIPELINE VALIDATION ===")

    print("\nLoading case sources...")

    sources = load_case_sources()
    queue = sources["queue"]

    assert len(queue) == 4844

    print("Unified queue rows:", len(queue))

    # AML
    check_case(
        case_id="MC-00008",
        expected_priority="Critical",
        expected_transaction_id="AML-51684",
    )

    # Anomaly
    check_case(
        case_id="MC-01162",
        expected_priority="Critical",
        expected_transaction_id="TX000899",
    )

    # Financial Risk
    check_case(
        case_id="MC-03612",
        expected_priority="High",
        expected_customer_id="27537",
    )

    print("\n================================")
    print("ALL PIPELINE VALIDATIONS PASSED")
    print("================================")


if __name__ == "__main__":
    main()