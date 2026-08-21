from agents.case_agent.case_manager import (
    build_investigation_case,
)

from agents.investigation_agent.investigator import (
    build_deterministic_investigation_result,
)


def test_aml_case():
    case = build_investigation_case("MC-00008")
    result = build_deterministic_investigation_result(case)

    assert case.priority == "Critical"
    assert result.summary
    assert len(result.key_findings) > 0
    assert len(result.recommended_actions) > 0

    assert (
        "Escalate the case for immediate analyst review."
        in result.recommended_actions
    )

    assert (
        "Review AML-related transaction evidence and linked account activity."
        in result.recommended_actions
    )

    print("AML deterministic test PASSED")


def test_anomaly_case():
    case = build_investigation_case("MC-01162")
    result = build_deterministic_investigation_result(case)

    assert case.priority == "Critical"
    assert result.summary
    assert len(result.key_findings) > 0
    assert len(result.recommended_actions) > 0

    assert (
        "Escalate the case for immediate analyst review."
        in result.recommended_actions
    )

    print("Anomaly deterministic test PASSED")


def test_financial_risk_case():
    case = build_investigation_case("MC-03612")
    result = build_deterministic_investigation_result(case)

    assert case.priority == "High"
    assert result.summary
    assert len(result.key_findings) > 0
    assert len(result.recommended_actions) > 0

    assert (
        "High financial risk signal from Financial Risk Engine."
        in result.key_findings
    )

    assert (
        "Perform standard analyst review of the available case evidence."
        in result.recommended_actions
    )

    print("Financial Risk deterministic test PASSED")


def main():
    print("=== MONTECORE DETERMINISTIC ENGINE VALIDATION ===")

    test_aml_case()
    test_anomaly_case()
    test_financial_risk_case()

    print("\n========================================")
    print("ALL DETERMINISTIC ENGINE TESTS PASSED")
    print("========================================")


if __name__ == "__main__":
    main()