from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.case_agent.case_manager import (
    load_case_sources,
    build_investigation_case,
)

from agents.investigation_agent.orchestrator import (
    run_agentic_investigation,
)


st.set_page_config(
    page_title="MonteCore Finance",
    page_icon="📊",
    layout="wide",
)


st.title("MonteCore Finance")

st.caption(
    "AI-powered financial risk monitoring and investigation console"
)


@st.cache_data
def load_dashboard_data():
    return load_case_sources()


sources = load_dashboard_data()

queue = sources["queue"]

st.success(
    f"Unified investigation queue loaded successfully: "
    f"{len(queue):,} cases"
)

st.dataframe(
    queue.head(20),
    use_container_width=True,
)