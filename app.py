import streamlit as st

from bb84 import (
    assess_qber,
    ideal_intercept_resend_qber,
    run_bb84,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Q-SECURE | Odyssey",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "runs" not in st.session_state:
    st.session_state.runs = []


# ============================================================
# LIGHT, LOW-STRAIN STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .team-footer {
        color: #667085;
        text-align: center;
        font-size: 0.8rem;
        padding: 0.7rem 0 0.2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.title("🔐 Q-SECURE")

st.caption(
    "Interactive BB84 experiment for detecting eavesdropping "
    "through quantum disturbance"
)

with st.container(border=True):

    st.markdown("### The idea")

    st.write(
        "Alice and Bob want to create shared key material. "
        "Eve may intercept some qubits. We do not look for Eve "
        "directly; we look for the disturbance her measurements "
        "can leave behind, using QBER."
    )


# ============================================================
# SIMPLE STORY
# ============================================================

st.subheader("The experiment")

c1, c2, c3 = st.columns(3)


with c1:

    with st.container(border=True):

        st.markdown("### 👩 Alice")

        st.write(
            "Creates random bits and randomly chooses Z or X "
            "to prepare each quantum state."
        )


with c2:

    with st.container(border=True):

        st.markdown("### 🕵️ Eve")

        st.write(
            "Optional attacker. She intercepts selected qubits, "
            "measures them using a guessed basis, and resends."
        )


with c3:

    with st.container(border=True):

        st.markdown("### 👨 Bob")

        st.write(
            "Receives the qubits and independently chooses Z or X "
            "to measure them."
        )


# ============================================================
# CONTROLS
# ============================================================

st.subheader("🎛️ Experiment controls")

c1, c2, c3 = st.columns(
    [1.2, 1, 1.5]
)


with c1:

    n_qubits = st.slider(
        "Number of qubits",
        min_value=20,
        max_value=300,
        value=200,
        step=20,
    )


with c2:

    eve_enabled = st.toggle(
        "Enable Eve",
        value=False,
    )


with c3:

    intercept_rate = st.slider(
        "Eve interception rate (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        disabled=not eve_enabled,
    )


st.caption(
    "Change the settings first. The experiment runs only "
    "when you press the button."
)


run_experiment = st.button(
    "🚀 Run Q-SECURE Experiment",
    type="primary",
    width="stretch",
)


# ============================================================
# RUN EXPERIMENT
# ============================================================

if run_experiment:

    with st.spinner(
        "Running the BB84 experiment..."
    ):

        result = run_bb84(
            n_qubits=n_qubits,
            eve_enabled=eve_enabled,
            intercept_rate=(
                intercept_rate
                if eve_enabled
                else 0
            ),
            seed=None,
        )

    st.session_state.result = result

    st.session_state.runs.append(
        {
            "Run":
                len(st.session_state.runs) + 1,

            "Qubits":
                result.n_qubits,

            "Eve":
                (
                    "ON"
                    if result.eve_enabled
                    else "OFF"
                ),

            "Interception":
                (
                    f"{result.intercept_rate:.0f}%"
                    if result.eve_enabled
                    else "0%"
                ),

            "Sifted bits":
                len(result.sifted_indices),

            "QBER":
                f"{result.qber:.2f}%",

            # Internal values for chart
            "QBER_value":
                result.qber,

            "Rate_value":
                (
                    result.intercept_rate
                    if result.eve_enabled
                    else 0.0
                ),
        }
    )


# ============================================================
# CURRENT RESULT
# ============================================================

result = st.session_state.result


# ============================================================
# BEFORE FIRST RUN
# ============================================================

if result is None:

    st.divider()

    st.subheader("What will happen?")

    steps = st.columns(5)


    with steps[0]:

        st.markdown(
            "**1. Alice prepares**"
        )

        st.caption(
            "Random bit + random Z/X basis"
        )


    with steps[1]:

        st.markdown(
            "**2. Qubits travel**"
        )

        st.caption(
            "Quantum states move toward Bob"
        )


    with steps[2]:

        st.markdown(
            "**3. Eve may interfere**"
        )

        st.caption(
            "Intercept → measure → resend"
        )


    with steps[3]:

        st.markdown(
            "**4. Sifting**"
        )

        st.caption(
            "Matching bases are kept"
        )


    with steps[4]:

        st.markdown(
            "**5. QBER**"
        )

        st.caption(
            "Measure remaining disturbance"
        )


    st.info(
        "Recommended demonstration: Eve OFF → Eve ON at "
        "25% → 50% → 100% interception."
    )


# ============================================================
# RESULTS
# ============================================================

else:

    st.divider()

    st.header("📊 Experiment result")


    # ========================================================
    # MAIN METRICS
    # ========================================================

    m1, m2, m3, m4 = st.columns(4)


    with m1:

        st.metric(
            "Qubits sent",
            result.n_qubits,
        )


    with m2:

        st.metric(
            "Sifted bits",
            len(result.sifted_indices),
        )


    with m3:

        st.metric(
            "Observed QBER",
            f"{result.qber:.2f}%",
        )


    with m4:

        st.metric(
            "Eve",
            (
                "ON"
                if result.eve_enabled
                else "OFF"
            ),
        )


    # ========================================================
    # SECURITY ASSESSMENT
    # ========================================================

    title, explanation = assess_qber(
        result.qber,
        result.eve_enabled,
    )


    if result.eve_enabled and result.qber >= 5:

        st.warning(
            f"**{title}**\n\n{explanation}"
        )

    else:

        st.success(
            f"**{title}**\n\n{explanation}"
        )


    # ========================================================
    # QBER GRAPH
    # ========================================================

    st.subheader(
        "📈 QBER vs Eve interception"
    )

    st.caption(
        "The reference line represents the ideal intercept-resend "
        "trend. Points/line segments represent your measured runs."
    )


    chart_rows = []


    # --------------------------------------------------------
    # Ideal reference
    # --------------------------------------------------------

    for rate in range(
        0,
        101,
        5,
    ):

        chart_rows.append(
            {
                "Interception":
                    rate,

                "QBER":
                    ideal_intercept_resend_qber(
                        rate
                    ),

                "Series":
                    "Ideal reference",
            }
        )


    # --------------------------------------------------------
    # Measured experiments
    # --------------------------------------------------------

    measured_runs = sorted(
        st.session_state.runs,
        key=lambda run: run["Rate_value"],
    )


    for run in measured_runs:

        chart_rows.append(
            {
                "Interception":
                    run["Rate_value"],

                "QBER":
                    run["QBER_value"],

                "Series":
                    "Measured",
            }
        )


    st.line_chart(
        chart_rows,
        x="Interception",
        y="QBER",
        color="Series",
        x_label="Eve interception (%)",
        y_label="QBER (%)",
        width="stretch",
        height=320,
    )


    # ========================================================
    # STORY OF THIS RUN
    # ========================================================

    st.subheader(
        "1. What happened?"
    )

    a, e, b = st.columns(3)


    with a:

        st.markdown(
            "### 👩 Alice"
        )

        st.write(
            "Random bits and random Z/X bases were used "
            "to prepare the quantum states."
        )


    with e:

        st.markdown(
            "### 🕵️ Eve"
        )

        if result.eve_enabled:

            st.write(
                f"Eve intercepted about "
                f"{result.intercept_rate:.0f}% of the qubits, "
                "measured selected states using guessed bases, "
                "and resent new states."
            )

        else:

            st.write(
                "Eve was OFF. The quantum states travelled "
                "directly from Alice to Bob."
            )


    with b:

        st.markdown(
            "### 👨 Bob"
        )

        st.write(
            "Bob independently selected Z/X bases and "
            "measured the received states."
        )


    # ========================================================
    # SIFTING
    # ========================================================

    st.subheader(
        "2. Sifting: what do Alice and Bob keep?"
    )

    st.write(
        "After Bob measures, Alice and Bob reveal only their "
        "bases. Matching bases are kept; different bases are "
        "discarded. Their secret bit values are not publicly revealed."
    )

    s1, s2 = st.columns(2)


    with s1:

        st.success(
            "✅ Same basis → KEEP"
        )


    with s2:

        st.info(
            "↪ Different basis → DISCARD"
        )


    # ========================================================
    # TRANSMISSION TABLE
    # ========================================================

    st.subheader(
        "3. Trace the first rounds"
    )

    st.caption(
        "These rows are taken directly from the same experiment "
        "used for QBER."
    )

    rows = []


    for i in range(
        min(15, result.n_qubits)
    ):

        same_basis = (
            result.alice_bases[i]
            == result.bob_bases[i]
        )


        rows.append(
            {
                "Round":
                    i + 1,

                "Alice bit":
                    result.alice_bits[i],

                "Alice basis":
                    result.alice_bases[i],

                "Eve":
                    (
                        "Yes"
                        if result.intercepted[i]
                        else "No"
                    ),

                "Eve basis":
                    (
                        result.eve_bases[i]
                        if result.eve_bases[i]
                        is not None
                        else "—"
                    ),

                "Bob basis":
                    result.bob_bases[i],

                "Bob bit":
                    result.bob_bits[i],

                "Decision":
                    (
                        "KEEP ✓"
                        if same_basis
                        else "DISCARD"
                    ),
            }
        )


    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
    )


    # ========================================================
    # SIFTED KEY
    # ========================================================

    st.subheader(
        "4. What remains after sifting?"
    )

    st.caption(
        "Only the rounds marked KEEP contribute to the raw "
        "shared key material."
    )


    # --------------------------------------------------------
    # Show the first kept rounds separately so the displayed
    # key can be traced directly to actual table rows.
    # --------------------------------------------------------

    kept_rows = []


    for index in result.sifted_indices:

        kept_rows.append(
            {
                "Round":
                    index + 1,

                "Alice bit":
                    result.alice_bits[index],

                "Bob bit":
                    result.bob_bits[index],

                "Basis":
                    result.alice_bases[index],

                "Match":
                    (
                        "✓"
                        if result.alice_bits[index]
                        == result.bob_bits[index]
                        else "✗"
                    ),
            }
        )


    if kept_rows:

        st.caption(
            "First 12 KEEP rounds:"
        )

        st.dataframe(
            kept_rows[:12],
            width="stretch",
            hide_index=True,
        )


    k1, k2 = st.columns(2)


    alice_key = "".join(
        str(bit)
        for bit in result.sifted_alice
    )


    bob_key = "".join(
        str(bit)
        for bit in result.sifted_bob
    )


    with k1:

        st.markdown(
            "**Alice — sifted bits**"
        )

        st.code(
            alice_key[:100]
            or "No matching-basis bits"
        )


    with k2:

        st.markdown(
            "**Bob — sifted bits**"
        )

        st.code(
            bob_key[:100]
            or "No matching-basis bits"
        )


    st.caption(
        f"Matching sifted bits: "
        f"{result.matching_bits}  •  "
        f"Mismatched sifted bits: "
        f"{result.mismatched_bits}"
    )


    # ========================================================
    # QBER
    # ========================================================

    st.subheader(
        "5. Did Eve leave a trace?"
    )

    st.markdown(
        "**QBER = mismatched sifted bits ÷ "
        "total sifted bits × 100**"
    )


    if result.sifted_alice:

        st.write(
            f"QBER = "
            f"{result.mismatched_bits} ÷ "
            f"{len(result.sifted_alice)} × 100 = "
            f"**{result.qber:.2f}%**"
        )


    if result.eve_enabled:

        expected = ideal_intercept_resend_qber(
            result.intercept_rate
        )

        st.info(
            f"Ideal large-sample reference at "
            f"{result.intercept_rate:.0f}% interception: "
            f"approximately **{expected:.1f}% QBER**. "
            "The measured value can fluctuate because this "
            "is a finite random experiment."
        )

    else:

        st.info(
            "With Eve OFF and an ideal noiseless simulator, "
            "QBER should normally be very close to 0%."
        )


    # ========================================================
    # PLAIN-LANGUAGE INTERPRETATION
    # ========================================================

    st.subheader(
        "💡 What does this mean?"
    )


    if result.eve_enabled:

        st.write(
            "Eve has to guess Alice's basis while the qubit "
            "is travelling. When her basis is wrong, her "
            "measurement can disturb the state. Some of this "
            "disturbance can appear as mismatches in the sifted "
            "key. Therefore, a higher observed QBER indicates "
            "more disturbance in the channel."
        )

    else:

        st.write(
            "Without Eve, Alice and Bob's matching-basis "
            "measurements agree in the ideal simulator. "
            "This gives a very low observed QBER."
        )


# ============================================================
# EXPERIMENT COMPARISON
# ============================================================

if len(st.session_state.runs) >= 2:

    st.divider()

    st.subheader(
        "🔬 Compare your experiments"
    )

    display_runs = []


    for run in st.session_state.runs:

        display_runs.append(
            {
                "Run":
                    run["Run"],

                "Qubits":
                    run["Qubits"],

                "Eve":
                    run["Eve"],

                "Interception":
                    run["Interception"],

                "Sifted bits":
                    run["Sifted bits"],

                "QBER":
                    run["QBER"],
            }
        )


    st.dataframe(
        display_runs,
        width="stretch",
        hide_index=True,
    )


    st.caption(
        "For the clearest demonstration, run Eve OFF, "
        "then 25%, 50%, 75%, and 100% interception."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    "<div class='team-footer'>"
    "Odyssey • Vyshnavi • "
    "Jasmin • "
    "Rajiv Gandhi University of Knowledge Technologies, Nuzvid"
    "</div>",
    unsafe_allow_html=True,
)