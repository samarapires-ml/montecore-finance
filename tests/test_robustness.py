import os
from unittest.mock import patch

from agents.case_agent.case_manager import (
    build_investigation_case,
)

from agents.investigation_agent.watsonx_client import (
    WatsonxClient,
)


def test_invalid_case_id():
    print("\nTesting invalid case ID handling...")

    try:
        build_investigation_case("MC-99999")

    except ValueError as exc:
        message = str(exc)

        assert "Case ID not found" in message

        print("Caught expected error:")
        print(message)
        print("Invalid case ID test PASSED")

        return

    raise AssertionError(
        "Expected ValueError for invalid Case ID"
    )


def test_missing_watsonx_credentials():
    print("\nTesting missing Watsonx credentials handling...")

    credential_names = [
        "IBM_CLOUD_API_KEY",
        "IBM_PROJECT_ID",
        "IBM_WATSONX_URL",
    ]

    fake_environment = {
        key: value
        for key, value in os.environ.items()
        if key not in credential_names
    }

    with patch.dict(
        os.environ,
        fake_environment,
        clear=True,
    ):
        client = WatsonxClient()

        try:
            client.get_primary_model()

        except ValueError as exc:
            message = str(exc)

            assert "Missing watsonx credentials" in message

            for credential in credential_names:
                assert credential in message

            print("Caught expected error:")
            print(message)
            print(
                "Missing Watsonx credentials test PASSED"
            )

            return

    raise AssertionError(
        "Expected ValueError when Watsonx "
        "credentials are missing"
    )

def test_orchestrator_ai_failure_fallback():
    print("\nTesting orchestrator AI failure fallback...")

    from agents.investigation_agent.orchestrator import (
        run_agentic_investigation,
    )

    case = build_investigation_case("MC-00008")

    credential_names = [
        "IBM_CLOUD_API_KEY",
        "IBM_PROJECT_ID",
        "IBM_WATSONX_URL",
    ]

    fake_environment = {
        key: value
        for key, value in os.environ.items()
        if key not in credential_names
    }

    with patch.dict(
        os.environ,
        fake_environment,
        clear=True,
    ):
        result = run_agentic_investigation(case)

    assert result.deterministic_result is not None

    assert result.primary_summary is None
    assert result.primary_error is not None

    assert (
        "Primary AI summarization unavailable"
        in result.primary_error
    )

    assert result.review_output is None
    assert result.review_error is not None

    assert (
        "Second-look review skipped"
        in result.review_error
    )

    print("Deterministic result preserved: YES")
    print("Primary AI failure recorded: YES")
    print("Second-look review skipped safely: YES")

    print(
        "Orchestrator AI failure fallback test PASSED"
    )

def main():
    print("=== MONTECORE ROBUSTNESS TESTS ===")

    test_invalid_case_id()
    test_missing_watsonx_credentials()
    test_orchestrator_ai_failure_fallback()

    print("\n================================")
    print("ROBUSTNESS TESTS 9E.1–9E.3 PASSED")
    print("================================")


if __name__ == "__main__":
    main()