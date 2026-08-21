from pathlib import Path
import math
import sys

import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PROJECT SETUP
# ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH    = PROJECT_ROOT / "assets" / "montecore_logo.png"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.case_agent.case_manager import (
    load_case_sources,
    build_investigation_case,
)
from agents.investigation_agent.orchestrator import (
    run_agentic_investigation,
)

from agents.case_agent.case_manager import (
    load_case_sources,
    build_investigation_case,
)

from agents.investigation_agent.orchestrator import (
    run_agentic_investigation,
)

from agents.investigation_agent.investigator import (
    build_deterministic_investigation_result,
)

from agents.investigation_agent.watsonx_client import (
    WatsonxClient,
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MonteCore Finance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────
# MINIMAL CSS  — styles Streamlit's own elements only
# ─────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Darker text inside sidebar form controls */
section[data-testid="stSidebar"] input {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    color: #172033 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #172033 !important;
}

/* Keep placeholder text slightly lighter */
section[data-testid="stSidebar"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}
    /* App background */
    .stApp { background: #F6F8FB; }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
        max-width: 1500px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06111F 0%, #0B1C31 100%);
        border-right: 1px solid #102a47;
    }
    [data-testid="stSidebar"] * { color: #DCE8F5; }
    [data-testid="stSidebar"] label {
        color: #E7EEF8 !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.10);
    }

    /* ── KPI metric cards ── */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A;
        font-weight: 700;
    }

    /* ── Dataframe ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"]  { gap: 16px; }
    .stTabs [data-baseweb="tab"]       { font-size: 12px; font-weight: 600; }
    .stTabs [aria-selected="true"]     { color: #168BFF !important; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        min-height: 38px;
        font-weight: 600;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

_PRIORITY_COLOURS = {
    "Critical": ("🔴", "#DC2626"),
    "High":     ("🟠", "#EA580C"),
    "Medium":   ("🟡", "#D97706"),
    "Low":      ("🟢", "#16A34A"),
}

def priority_icon(level: str) -> str:
    return _PRIORITY_COLOURS.get(level, ("⚪", "#64748B"))[0]

def priority_colour(level: str) -> str:
    return _PRIORITY_COLOURS.get(level, ("⚪", "#64748B"))[1]

def priority_badge_style(level: str) -> str:
    """Inline CSS used only inside st.markdown badge spans."""
    palette = {
        "Critical": ("Fee2e2", "#DC2626"),
        "High":     ("#FFEDD5", "#EA580C"),
        "Medium":   ("#FEF3C7", "#D97706"),
        "Low":      ("#DCFCE7", "#16A34A"),
    }
    bg, fg = palette.get(level, ("#F1F5F9", "#64748B"))
    return (
        f"display:inline-block;"
        f"background:{bg};"
        f"color:{fg};"
        f"border-radius:6px;"
        f"padding:2px 10px;"
        f"font-size:11px;"
        f"font-weight:700;"
        f"letter-spacing:.5px;"
    )


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    return load_case_sources()

sources          = load_data()
queue            = sources["queue"]
financial_results = sources["financial"]


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────

if "investigation_results" not in st.session_state:
    st.session_state.investigation_results = {}

if "page_number" not in st.session_state:
    st.session_state.page_number = 1

if "case_chats" not in st.session_state:
    st.session_state.case_chats = {}

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

with st.sidebar:

    # ── Branding ──────────────────────────────────
    if LOGO_PATH.exists():
        # Three-column trick: pad left/right to visually centre
        # the logo without using HTML. Middle column = logo width.
        _sb_l, _sb_m, _sb_r = st.columns([1, 3, 1])
        with _sb_m:
            st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown(
        "<p style='color:#FFFFFF;font-size:14px;font-weight:700;"
        "margin:6px 0 2px;text-align:center;line-height:1.3;'>"
        "MonteCore Finance</p>"
        "<p style='color:#7FA8C9;font-size:11px;margin:0 0 14px;"
        "text-align:center;line-height:1.4;'>"
        "Financial Intelligence Console</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Filters ────────────────────────────────────
    st.markdown(
        "<p style='color:#168BFF;font-size:13px;font-weight:700;"
        "letter-spacing:.8px;margin-bottom:4px;'>⚙ FILTERS</p>",
        unsafe_allow_html=True,
    )

    source_filter = st.selectbox(
        "Risk source",
        ["All"] + sorted(queue["CaseSource"].unique().tolist()),
    )

    priority_filter = st.selectbox(
        "Priority",
        ["All", "Critical", "High", "Medium"],
    )

    search = st.text_input(
        "Search",
        placeholder="Case ID, source ID or entity",
    )

    st.divider()

    st.caption(
        "🛡️  AI outputs support analyst investigations.\n\n"
        "Final investigation decisions remain with human analysts."
    )


# ─────────────────────────────────────────────────────────────
# FILTERING
# ─────────────────────────────────────────────────────────────

filtered = queue.copy()

if source_filter != "All":
    filtered = filtered[filtered["CaseSource"] == source_filter]

if priority_filter != "All":
    filtered = filtered[filtered["RiskLevel"] == priority_filter]

if search.strip():
    term = search.strip().lower()
    mask = (
        filtered["CaseID"].astype(str).str.lower().str.contains(term, regex=False)
        | filtered["EntityID"].astype(str).str.lower().str.contains(term, regex=False)
        | filtered["SourceRecordID"].astype(str).str.lower().str.contains(term, regex=False)
    )
    filtered = filtered[mask]

if len(filtered) == 0:
    st.session_state.page_number = 1


# ─────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────

k1, k2, k3, k4 = st.columns(4)

k1.metric("Open Cases",     f"{len(queue):,}",
          help="Total active investigation cases")
k2.metric("Critical",       f"{(queue['RiskLevel'] == 'Critical').sum():,}",
          help="Critical priority cases")
k3.metric("High Priority",  f"{(queue['RiskLevel'] == 'High').sum():,}",
          help="High priority cases")
k4.metric("Early Warnings", f"{int(financial_results['EarlyWarningFlag'].sum()):,}",
          help="Financial early-warning alerts")

st.write("")


# ─────────────────────────────────────────────────────────────
# MAIN LAYOUT  — 55 / 45
# ─────────────────────────────────────────────────────────────

left, right = st.columns([1.2, 0.88], gap="medium")


# ═════════════════════════════════════════════════════════════
# LEFT — INVESTIGATION QUEUE
# ═════════════════════════════════════════════════════════════

with left:

    st.subheader("☷  Investigation Queue")
    st.caption(f"{len(filtered):,} cases shown")

    # ── Pagination ──
    PAGE_SIZE   = 10
    total_pages = max(1, math.ceil(len(filtered) / PAGE_SIZE))

    if st.session_state.page_number > total_pages:
        st.session_state.page_number = total_pages

    start   = (st.session_state.page_number - 1) * PAGE_SIZE
    end     = start + PAGE_SIZE
    page_df = filtered.iloc[start:end].copy()

    # ── Build display frame ──
    queue_view = page_df[
        ["CaseID", "CaseSource", "RiskLevel", "RiskScore", "EntityID"]
    ].copy()
    queue_view.columns = ["Case", "Source", "Priority", "Score", "Entity"]

    def _priority_cell_style(v):
        styles = {
            "Critical": "background-color:#FEE2E2;color:#DC2626;font-weight:600;",
            "High":     "background-color:#FFEDD5;color:#EA580C;font-weight:600;",
            "Medium":   "background-color:#FEF3C7;color:#D97706;font-weight:600;",
        }
        return styles.get(v, "")

    styled_queue = queue_view.style.map(_priority_cell_style, subset=["Priority"])

    st.dataframe(
        styled_queue,
        use_container_width=True,
        hide_index=True,
        height=390,
        column_config={
            "Score": st.column_config.NumberColumn(format="%.3f"),
        },
    )

    # ── Pagination controls ──
    nav_l, nav_c, nav_r = st.columns([0.3, 0.4, 0.3])

    with nav_l:
        if st.button("← Previous",
                     disabled=(st.session_state.page_number <= 1),
                     use_container_width=True):
            st.session_state.page_number -= 1
            st.rerun()

    with nav_c:
        st.caption(
            f"Page {st.session_state.page_number} of {total_pages}",
        )

    with nav_r:
        if st.button("Next →",
                     disabled=(st.session_state.page_number >= total_pages),
                     use_container_width=True):
            st.session_state.page_number += 1
            st.rerun()

    shown_end = min(end, len(filtered))
    st.caption(f"Showing {start + 1:,}–{shown_end:,} of {len(filtered):,} cases")


# ═════════════════════════════════════════════════════════════
# RIGHT — CASE INTELLIGENCE
# ═════════════════════════════════════════════════════════════

with right:

    st.subheader("▣  Case Intelligence")

    if filtered.empty:
        st.info("No cases match the current filters.")
        st.stop()

    selected_case_id = st.selectbox(
        "Select case",
        filtered["CaseID"].tolist(),
    )

    selected_row = filtered[filtered["CaseID"] == selected_case_id].iloc[0]
    risk_level   = str(selected_row["RiskLevel"])

    # Build the case object once and reuse across tabs
    case = build_investigation_case(selected_case_id)

    # ── Case header ──
    badge_style = priority_badge_style(risk_level)
    st.markdown(
        f"<span style='font-size:24px;font-weight:700;color:#0F172A;'>"
        f"{selected_case_id}</span>&nbsp;&nbsp;"
        f"<span style='{badge_style}'>{risk_level.upper()}</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"**Priority:** {selected_row['RiskLevel']} &nbsp;·&nbsp; "
        f"**Source:** {selected_row['CaseSource']} &nbsp;·&nbsp; "
        f"**Risk Score:** {selected_row['RiskScore']:.3f}"
    )
    st.caption(
        f"Entity: {selected_row['EntityID']}  ·  "
        f"Source record: {selected_row['SourceRecordID']}"
    )

    # ── Tabs ──
    
    overview_tab, evidence_tab, ai_tab, chat_tab = st.tabs(
    [
        "Overview",
        "Evidence",
        "AI Review",
        "💬 Ask MonteCore",
    ]
)

    # ─────────────────────────────────────────
    # OVERVIEW TAB
    # ─────────────────────────────────────────
    with overview_tab:

        st.markdown("#### Case reason")
        st.info(selected_row["CaseReason"])

        st.markdown("#### Risk signals")

        for signal in case.risk_signals:
            with st.container(border=True):
                col_icon, col_body = st.columns([0.08, 0.92])
                with col_icon:
                    st.markdown(
                        f"<div style='font-size:20px;padding-top:4px;'>"
                        f"{priority_icon(signal.level)}</div>",
                        unsafe_allow_html=True,
                    )
                with col_body:
                    st.markdown(
                        f"**{signal.signal_type}**"
                    )
                    st.caption(
                        f"Source: {signal.source}  ·  "
                        f"Level: {signal.level}  ·  "
                        f"Score: {signal.score:.3f}"
                    )
                    st.write(signal.description)


    # ─────────────────────────────────────────
    # EVIDENCE TAB
    # ─────────────────────────────────────────
    with evidence_tab:

        st.markdown("#### Grounded evidence")
        st.caption(
            "Evidence loaded directly from the source risk-engine output."
        )

        for item in case.evidence:
            with st.container(border=True):
                st.caption(item.evidence_type)
                st.write(item.description)
                st.caption(f"Source: {item.source}")


    # ─────────────────────────────────────────
    # AI REVIEW TAB
    # ─────────────────────────────────────────
    with ai_tab:

        st.caption(
            "Mistral Small generates the primary investigation assessment.  "
            "Llama 3.3 independently reviews it for unsupported claims."
        )

        if st.button(
            "🔍  Run AI Investigation",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Running MonteCore investigation agents…"):
                result = run_agentic_investigation(case)
                st.session_state.investigation_results[selected_case_id] = result

        result = st.session_state.investigation_results.get(selected_case_id)

        if result is None:
            st.info("No AI investigation has been run for this case yet.")

        else:

            # ── Deterministic assessment ──────────────
            st.markdown("### Deterministic Assessment")
            det = result.deterministic_result

            st.write(det.summary)

            st.markdown("**Key findings**")
            for finding in det.key_findings:
                st.write(f"• {finding}")

            st.markdown("**Recommended actions**")
            for action in det.recommended_actions:
                st.write(f"• {action}")

            st.divider()

            # ── Primary investigation (Mistral) ───────
            st.markdown("### Primary Investigation")
            st.caption("Mistral Small · IBM watsonx.ai")

            if result.primary_error:
                st.warning(result.primary_error)
            else:
                st.markdown(result.primary_summary)

            st.divider()

            # ── Second-look review (Llama) ────────────
            st.markdown("### Independent Second Look")
            st.caption("Llama 3.3 · IBM watsonx.ai")

            if result.review_error:
                st.warning(result.review_error)
            else:
                review_upper = result.review_output.upper()
                if "NEEDS_CORRECTION" in review_upper:
                    st.warning("Second-look status: corrections required.")
                elif "PASS" in review_upper:
                    st.success("Second-look status: PASS")

                st.markdown(result.review_output)

            st.divider()

            st.info(
                "⚖️  AI-generated decision support. "
                "Final investigation decisions remain with human analysts."
            )

    # ─────────────────────────────────────────
    # ASK MONTECORE TAB
    # ─────────────────────────────────────────
    with chat_tab:

        st.markdown("### 💬 Ask MonteCore")

        st.caption(
            "Ask questions about the selected case. "
            "Responses are grounded in this case's evidence "
            "and deterministic investigation findings."
        )

        # Create a separate conversation for each case
        if selected_case_id not in st.session_state.case_chats:
            st.session_state.case_chats[selected_case_id] = []

        chat_history = st.session_state.case_chats[selected_case_id]

        st.info(
            f"Case Copilot is currently grounded to **{selected_case_id}**."
        )

        # Display previous messages
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        question = st.chat_input(
            "Ask about this case...",
            key=f"case_chat_input_{selected_case_id}",
        )

        if question:

            # Store and display analyst question
            chat_history.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user"):
                st.markdown(question)

            # Build deterministic context
            deterministic_result = (
                build_deterministic_investigation_result(case)
            )

            client = WatsonxClient()

            # The current question is passed separately,
            # so only send earlier messages as history
           

            try:
                with st.chat_message("assistant"):

                    with st.spinner(
                        "MonteCore is reviewing the case evidence..."
                    ):
                        draft_answer = client.chat_about_case(
                        case=case,
                        deterministic_result=deterministic_result,
                        question=question,
                        chat_history=None,
                    )

                    answer = client.review_case_chat_answer(
                     case=case,
                     deterministic_result=deterministic_result,
                     question=question,
                     draft_answer=draft_answer,
                    )

                    st.markdown(answer)

                # Save assistant response
                chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as exc:
                st.error(
                    "MonteCore could not generate a response. "
                    f"{exc}"
                )

        st.divider()

        clear_col, note_col = st.columns([0.35, 0.65])

        with clear_col:
            if st.button(
                "Clear conversation",
                key=f"clear_chat_{selected_case_id}",
                use_container_width=True,
            ):
                st.session_state.case_chats[selected_case_id] = []
                st.rerun()

        with note_col:
            st.caption(
                "AI-generated decision support. "
                "Final investigation decisions remain "
                "with human analysts."
            )