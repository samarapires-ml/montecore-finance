from agents.case_agent.case_manager import build_investigation_case
from agents.investigation_agent.investigator import (
    build_deterministic_investigation_result,
)
from agents.investigation_agent.watsonx_client import WatsonxClient


def main():
    print("Building case...")
    case = build_investigation_case("MC-01220")

    print(f"Case loaded: {case.case_id}")

    print("Running deterministic investigation...")
    deterministic_result = build_deterministic_investigation_result(case)

    print("Creating Watsonx client...")
    client = WatsonxClient()

    print("Sending question to AI...")
    answer = client.chat_about_case(
        case=case,
        deterministic_result=deterministic_result,
        question=(
            "Why was this case flagged and what evidence "
            "supports the risk level?"
        ),
    )

    print("\n--- AI ANSWER ---\n")
    print(answer)


if __name__ == "__main__":
    main()