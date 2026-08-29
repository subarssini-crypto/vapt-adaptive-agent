
import streamlit as st
import plotly.graph_objects as go
from agent import app
from state import initial_state


st.set_page_config(
    page_title="Adaptive AI Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #06101c;
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background: #050b14;
    border-right: 1px solid #17283b;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

h1, h2, h3 {
    color: #ffffff;
}

.card {
    background: #0b1726;
    border: 1px solid #1b3047;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
}

.card-title {
    color: #8fa7bf;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.card-value {
    color: #ffffff;
    font-size: 27px;
    font-weight: 700;
    margin-top: 5px;
}

.green {
    color: #00e676;
}

.red {
    color: #ff5252;
}

.orange {
    color: #ffab00;
}

.purple {
    color: #b388ff;
}

.blue {
    color: #40a9ff;
}

.muted {
    color: #8fa7bf;
}

.module {
    background: #0a1625;
    border: 1px solid #20364d;
    border-radius: 9px;
    padding: 12px 15px;
    margin: 7px 0;
}

.module:hover {
    border-color: #40a9ff;
}

.chain {
    background: #151027;
    border: 1px solid #9c6cff;
    border-radius: 9px;
    padding: 12px;
    margin: 8px 0;
    text-align: center;
    color: #c7a7ff;
}

.finding {
    background: #0b1726;
    border-radius: 8px;
    padding: 13px;
    margin: 8px 0;
    border-left: 4px solid #ff5252;
}

.success-box {
    background: #071b14;
    border: 1px solid #00e676;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 12px;
}

.project-title {
    text-align: center;
    padding: 8px 3px 18px 3px;
}

.project-icon {
    font-size: 42px;
    margin-bottom: 8px;
}

.project-name {
    color: #00e676;
    font-size: 18px;
    font-weight: 700;
    line-height: 1.25;
}

.project-subtitle {
    color: #9aadc1;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 7px;
}

.ai-step {
    background: #0a1625;
    border: 1px solid #1d3146;
    border-radius: 8px;
    padding: 11px;
    margin: 6px 0;
}

.key-result {
    background: #10102a;
    border: 1px solid #8c63d9;
    border-radius: 10px;
    padding: 18px;
    margin-top: 15px;
}

div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="project-title">

        <div class="project-icon">🛡️</div>

        <div class="project-name">
            ADAPTIVE AI AGENT
        </div>

        <div class="project-subtitle">
            FOR MULTISTEP<br>
            WEB APPLICATION<br>
            PEN TESTING
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Navigation")

    st.markdown("🏠 **Overview**")
    st.markdown("🔍 **Reconnaissance**")
    st.markdown("🚨 **Vulnerabilities**")
    st.markdown("🤖 **AI Agent**")
    st.markdown("📊 **Comparison**")
    st.markdown("📄 **Report**")

    st.divider()

    st.markdown("### Scan Control")

    target = st.text_input(
        "Target URL",
        value="http://localhost:3000"
    )

    start_scan = st.button(
        "▶  START NEW SCAN",
        use_container_width=True
    )

    clear_results = st.button(
        "↻  CLEAR RESULTS",
        use_container_width=True
    )

    st.divider()

    st.markdown("### System Status")

    st.success("● Agent Ready")

    st.caption("AI Model: Llama 3.1 8B")
    st.caption("Framework: LangGraph")
    st.caption("Runtime: Ollama")


# =========================================================
# SESSION STATE
# =========================================================

if "result" not in st.session_state:
    st.session_state.result = None


if clear_results:
    st.session_state.result = None
    st.rerun()


# =========================================================
# START SCAN
# =========================================================

if start_scan:

    with st.spinner("Adaptive AI Agent is performing assessment..."):

        try:

            state = initial_state(
                target,
                chaining_enabled=True
            )

            result = app.invoke(state)

            st.session_state.result = result

            st.success("Security assessment completed.")

        except Exception as e:

            st.error(f"Scan failed: {e}")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    "# Adaptive AI Agent"
)

st.markdown(
    '<span class="muted">Multistep Web Application Penetration Testing</span>',
    unsafe_allow_html=True
)

st.write("")


# =========================================================
# WAITING SCREEN
# =========================================================

if st.session_state.result is None:

    st.markdown("""
    <div class="card">

        <h2>🛡️ Ready for Security Assessment</h2>

        <p class="muted">
        Enter the target URL from the sidebar and start a new scan.
        The adaptive agent will execute reconnaissance,
        authentication testing, vulnerability assessment,
        and chained security checks.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# GET RESULT
# =========================================================

state = st.session_state.result

findings = state.get("findings", [])
modules = state.get("modules_run", [])
decision_log = state.get("decision_log", [])
tech_stack = state.get("tech_stack", {})
pages = state.get("pages", [])


# =========================================================
# CONFIRMED VULNERABILITIES
# =========================================================

vulnerabilities = []

for finding in findings:

    data = finding.get("data", {})

    if isinstance(data, dict):

        if data.get("vulnerable") is True:
            vulnerabilities.append(finding)


# =========================================================
# TOP STATUS CARDS
# =========================================================

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Target URL</div>
        <div class="card-value green">
            {state.get("target_url", "N/A")}
        </div>
    </div>
    """, unsafe_allow_html=True)


with c2:

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Scan Status</div>
        <div class="card-value green">
            ● COMPLETED
        </div>
    </div>
    """, unsafe_allow_html=True)


with c3:

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Modules Completed</div>
        <div class="card-value">
            {len(modules)} / 6
        </div>
    </div>
    """, unsafe_allow_html=True)


with c4:

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Confirmed Vulnerabilities</div>
        <div class="card-value red">
            {len(vulnerabilities)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN DASHBOARD
# =========================================================

left, middle, right = st.columns([1, 1, 1.15])


# =========================================================
# MODULE EXECUTION FLOW
# =========================================================

with left:

    st.markdown(
        '<div class="section-title">🔄 Module Execution Flow</div>',
        unsafe_allow_html=True
    )

    module_names = {

        "fingerprint":
            "🔍 Fingerprinting",

        "crawl":
            "🕷️ Web Crawling",

        "auth_check":
            "🔐 Authentication Check",

        "idor_check":
            "🎯 IDOR Check",

        "sqli_check":
            "💉 SQL Injection Check",

        "xss_check":
            "🧪 XSS Check"
    }


    for i, module in enumerate(modules):

        name = module_names.get(
            module,
            module
        )


        if module == "idor_check":

            st.markdown("""
            <div class="chain">

                🔗 <b>AI CHAIN TRIGGERED</b>

                <br>

                <small>
                Valid authentication token
                → IDOR testing
                </small>

            </div>
            """, unsafe_allow_html=True)


        st.markdown(f"""
        <div class="module">

            <b>
                ✓ &nbsp; {i + 1}. {name}
            </b>

            <br>

            <small class="green">
                Completed
            </small>

        </div>
        """, unsafe_allow_html=True)


# =========================================================
# VULNERABILITY OVERVIEW
# =========================================================

with middle:

    st.markdown(
        '<div class="section-title">🚨 Vulnerability Overview</div>',
        unsafe_allow_html=True
    )


    severity_map = {

        "sqli":
            ("CRITICAL", "red", "💉"),

        "idor":
            ("HIGH", "orange", "🎯"),

        "xss":
            ("MEDIUM", "orange", "🧪"),

        "auth":
            ("LOW", "green", "🔐")
    }


    for finding in findings:

        finding_type = finding.get(
            "finding_type",
            "unknown"
        )

        data = finding.get(
            "data",
            {}
        )


        severity, color, icon = severity_map.get(
            finding_type,
            ("INFO", "blue", "ℹ️")
        )


        vulnerable = (
            isinstance(data, dict)
            and data.get("vulnerable") is True
        )


        status = (
            "VULNERABLE"
            if vulnerable
            else "PASSED"
        )


        if vulnerable:

            st.markdown(f"""
            <div class="finding">

                <b>
                    {icon} {finding_type.upper()}
                </b>

                <br>

                <span class="{color}">
                    {severity} — {status}
                </span>

                <br>

                <small class="muted">
                    {data.get("detail", "")}
                </small>

            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div class="success-box">

                <b>
                    {icon} {finding_type.upper()}
                </b>

                <br>

                <span class="green">
                    {severity} — PASSED
                </span>

            </div>
            """, unsafe_allow_html=True)


# =========================================================
# AI DECISION TRAIL
# =========================================================

with right:

    st.markdown(
        '<div class="section-title">🤖 AI Decision Trail</div>',
        unsafe_allow_html=True
    )


    for entry in decision_log:

        if "CHAINED" in entry:

            st.markdown(f"""
            <div class="ai-step">

                <span class="purple">
                    🔗 CHAIN
                </span>

                <br>

                <small>
                    {entry}
                </small>

            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div class="ai-step">

                <span class="green">
                    ● DECIDE
                </span>

                <br>

                <small>
                    {entry}
                </small>

            </div>
            """, unsafe_allow_html=True)


# =========================================================
# RECONNAISSANCE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🔍 Reconnaissance Results</div>',
    unsafe_allow_html=True
)


recon_left, recon_right = st.columns(2)


with recon_left:

    st.markdown("""
    <div class="card">

        <h3>Technology & Server</h3>

    """, unsafe_allow_html=True)


    if tech_stack:

        st.write(
            "**HTTP Status:**",
            tech_stack.get(
                "status_code",
                "N/A"
            )
        )

        st.write(
            "**Server:**",
            tech_stack.get(
                "server_header",
                "N/A"
            )
        )

        st.write(
            "**Powered By:**",
            tech_stack.get(
                "powered_by",
                "N/A"
            )
        )

    else:

        st.info("No fingerprint data available.")


    st.markdown("</div>", unsafe_allow_html=True)


with recon_right:

    st.markdown("""
    <div class="card">

        <h3>Security Headers</h3>

    """, unsafe_allow_html=True)


    headers = tech_stack.get(
        "security_headers_present",
        {}
    )


    if headers:

        for header, present in headers.items():

            if present:
                st.success(
                    f"✓ {header}"
                )
            else:
                st.error(
                    f"✗ {header}"
                )

    else:

        st.info(
            "No security header information."
        )


    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# UNUSUAL HEADERS
# =========================================================

unusual_headers = tech_stack.get(
    "unusual_headers",
    []
)


if unusual_headers:

    with st.expander(
        "⚠️ View Unusual / Leaked Headers"
    ):

        for header in unusual_headers:

            st.code(header)


# =========================================================
# DISCOVERED PAGES
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🕷️ Discovered Pages & Resources</div>',
    unsafe_allow_html=True
)


crawl_finding = next(
    (
        f
        for f in findings
        if f.get("finding_type") == "crawl"
    ),
    None
)


if crawl_finding:

    discovered = crawl_finding.get(
        "data",
        {}
    ).get(
        "discovered_pages",
        []
    )

else:

    discovered = pages


if discovered:

    page_cols = st.columns(3)

    for i, page in enumerate(discovered):

        with page_cols[i % 3]:

            st.markdown(
                f"""
                <div class="module">
                    📄 {page}
                </div>
                """,
                unsafe_allow_html=True
            )

else:

    st.info(
        "No pages/resources discovered."
    )


# =========================================================
# AI CHAIN VISUALIZATION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🔗 Adaptive AI Chain</div>',
    unsafe_allow_html=True
)


idor_ran = "idor_check" in modules


if idor_ran:

    chain1, chain2, chain3, chain4 = st.columns(
        [1, 0.3, 1, 1]
    )


    with chain1:

        st.markdown("""
        <div class="card">
            <h3>🔐 Authentication</h3>
            <span class="green">
                Session obtained
            </span>
        </div>
        """, unsafe_allow_html=True)


    with chain2:

        st.markdown(
            "<h1 style='text-align:center'>→</h1>",
            unsafe_allow_html=True
        )


    with chain3:

        st.markdown("""
        <div class="chain">
            🔑 TOKEN<br>
            <small>Valid session</small>
        </div>
        """, unsafe_allow_html=True)


    with chain4:

        st.markdown("""
        <div class="card">
            <h3>🎯 IDOR</h3>
            <span class="red">
                Automatically Triggered
            </span>
        </div>
        """, unsafe_allow_html=True)


    st.success(
        "The agent detected a valid session and automatically "
        "chained the IDOR module."
    )

else:

    st.info(
        "No adaptive chain was triggered."
    )


# =========================================================
# FINDINGS CHART
# =========================================================

st.divider()

chart_col, summary_col = st.columns([1, 1])


with chart_col:

    st.markdown(
        '<div class="section-title">📊 Finding Distribution</div>',
        unsafe_allow_html=True
    )


    counts = {}


    for finding in findings:

        finding_type = finding.get(
            "finding_type",
            "unknown"
        )

        counts[finding_type] = (
            counts.get(finding_type, 0) + 1
        )


    if counts:

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        x.upper()
                        for x in counts.keys()
                    ],
                    values=list(
                        counts.values()
                    ),
                    hole=0.55
                )
            ]
        )


        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),

            height=320
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


with summary_col:

    st.markdown(
        '<div class="section-title">📋 Assessment Summary</div>',
        unsafe_allow_html=True
    )


    st.markdown(f"""
    <div class="card">

        <p>
            <span class="muted">
                Target
            </span>
            <br>
            <b>{state.get("target_url", "N/A")}</b>
        </p>

        <p>
            <span class="muted">
                Modules Executed
            </span>
            <br>
            <b>{len(modules)}</b>
        </p>

        <p>
            <span class="muted">
                Total Steps
            </span>
            <br>
            <b>{state.get("step_count", 0)}</b>
        </p>

        <p>
            <span class="muted">
                Total Findings
            </span>
            <br>
            <b>{len(findings)}</b>
        </p>

        <p>
            <span class="muted">
                Confirmed Vulnerabilities
            </span>
            <br>
            <b class="red">
                {len(vulnerabilities)}
            </b>
        </p>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# BASELINE VS CHAINING
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">⚖️ Baseline vs Adaptive Agent</div>',
    unsafe_allow_html=True
)


b1, b2, b3 = st.columns(3)


with b1:

    st.markdown("""
    <div class="card">

        <h3>BASELINE</h3>

        <span class="muted">
        Chaining Disabled
        </span>

        <hr>

        <p>Modules: <b>5</b></p>

        <p>IDOR Tested:
        <span class="red">✗ No</span>
        </p>

    </div>
    """, unsafe_allow_html=True)


with b2:

    st.markdown("""
    <div class="card">

        <h3>ADAPTIVE AGENT</h3>

        <span class="purple">
        Chaining Enabled
        </span>

        <hr>

        <p>Modules: <b class="green">6</b></p>

        <p>IDOR Tested:
        <span class="green">✓ Yes</span>
        </p>

    </div>
    """, unsafe_allow_html=True)


with b3:

    st.markdown("""
    <div class="card">

        <h3>KEY DIFFERENCE</h3>

        <span class="green">
        + Adaptive Follow-up
        </span>

        <hr>

        <p>
        Authentication discovered a valid
        session token.
        </p>

        <p>
        The agent automatically used that
        context to trigger IDOR testing.
        </p>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# KEY RESULT
# =========================================================

st.markdown("""
<div class="key-result">

    <h3>⭐ Key Project Result</h3>

    <p>
        The chaining-enabled agent can adapt its next action
        based on information discovered during previous modules.
        When authentication produces a valid session,
        the agent can automatically trigger IDOR testing.
    </p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# DETAILED FINDINGS
# =========================================================

st.divider()

with st.expander("📋 View Detailed Findings"):

    if findings:

        for finding in findings:

            st.json(finding)

    else:

        st.info("No findings recorded.")


# =========================================================
# COMPLETE AI DECISION LOG
# =========================================================

with st.expander("🧠 View Complete AI Decision Log"):

    if decision_log:

        for entry in decision_log:

            st.write(entry)

    else:

        st.info("No decision log available.")


# =========================================================
# REPORT
# =========================================================

with st.expander("📄 View Security Assessment Report"):

    try:

        from modules.report import generate_report

        report = generate_report(state)

        st.code(
            report,
            language="text"
        )

        st.download_button(
            "⬇️ Download Report",
            data=report,
            file_name="security_assessment_report.txt",
            mime="text/plain"
        )

    except Exception as e:

        st.error(
            f"Unable to generate report: {e}"
        )