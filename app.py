"""Streamlit user interface for the LEDD Calculator.

The UI collects marketed medications and daily schedules, delegates the medical
calculation to :mod:`ledd_calculator.core`, and presents downloadable summaries.
Keeping calculation logic outside this file makes the clinically relevant rules
independently testable.
"""

import json

import streamlit as st
import pandas as pd
import matplotlib

# Select a non-interactive renderer before importing pyplot. This is required for
# packaged/headless execution, where a desktop plotting window is unavailable.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF, XPos, YPos

from ledd_calculator.core import CATEGORIES, SCHEDULE_TIMES, compute_ledd
from ledd_calculator.paths import resource_path
from ledd_calculator.shutdown import exit_application

# Streamlit requires page configuration to be the first Streamlit command.
st.set_page_config(page_title="LEDD Calculator", layout="centered")


@st.cache_data
def load_medication_data(country: str = "Switzerland") -> dict[str, dict[str, float]]:
    """Load and cache the country-specific medication catalogue.

    ``resource_path`` resolves the same filename from a source checkout and from
    PyInstaller's temporary extraction directory.
    """
    path = resource_path(f"config_{country}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def export_pdf(total_ledd: float, category_ledd: dict[str, float]) -> bytes:
    """Create an in-memory PDF summary for Streamlit's download button."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Write the overall result first, followed by one row per drug category.
    pdf.cell(
        200,
        10,
        text="LEDD Calculation Summary",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="C",
    )
    pdf.ln(10)
    pdf.cell(
        200,
        10,
        text=f"Total LEDD: {total_ledd:.2f} mg",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(5)
    for cat, ledd in category_ledd.items():
        pdf.cell(
            200,
            10,
            text=f"{cat}: {ledd:.2f} mg",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    # fpdf2 returns a bytearray; normalize it to immutable bytes for Streamlit.
    return bytes(pdf.output())

# Session state keeps the medication list across Streamlit's automatic reruns.
if "medication_list" not in st.session_state:
    st.session_state.medication_list = []


# Shared typography for the title, instructions, and scientific reference.
st.markdown("""
    <style>
    .title-text {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .ref-text {
        font-size: 14px;
        font-style: italic;
    }
    .section-title {
        font-size: 20px;
        margin-bottom: 0.5em;
        font-weight: 600;
    }
    .section-desc {
        font-size: 16px;
        margin-bottom: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Apply the calculator's dark colour palette consistently to Streamlit widgets.
st.markdown("""
    <style>
    .stApp {
    background-color: black;
    color: #e0e0e0;
    }
    .title-text {
    color: white;
    }
    .section-title, .section-desc {
    color: #aaa !important;
    }
    .ref-text {
    color: #aaa;
    }
    button, .stDownloadButton, .stToggle label {
    color: #e0e0e0 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>LEDD Calculator</div>", unsafe_allow_html=True)

# Step 1 loads the only catalogue currently shipped with the application. The
# select box intentionally leaves room for additional country JSON files later.
st.markdown("---")
with st.container():
    st.markdown("<div class='section-title'>Step 1: Select Country</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Choose the country to load a list of medications available in that region. The system will use this to match the drug names and dosages correctly.</div>", unsafe_allow_html=True)
    country = st.selectbox("Country", ["Switzerland"], label_visibility="collapsed")
    medications = load_medication_data(country)

# Step 2 displays the active ingredients for the selected marketed product,
# grouped using the same category definitions used by the calculation engine.
st.markdown("---")
with st.container():
    st.markdown("<div class='section-title'>Step 2: Select Medication</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Pick a medication from the list to view its active ingredients and associated dosage information.</div>", unsafe_allow_html=True)
    selected_med = st.selectbox(
        "Medication", list(medications.keys()), label_visibility="collapsed"
    )
    st.markdown("<div class='section-desc'>Ingredient Dosages by Category:</div>", unsafe_allow_html=True)
    ingredients = medications.get(selected_med, {})
    for cat, items in CATEGORIES.items():
        line = ", ".join([f"{ing}: {ingredients[ing]} mg" for ing in items if ing in ingredients])
        st.text_input(f"{cat}:", value=line, disabled=True)

# Step 3 captures the number of units taken at each time of day. Schedules are
# stored as compact hyphen-separated strings to match the core API.
st.markdown("---")
with st.container():
    st.markdown("<div class='section-title'>Step 3: Enter Dosage Schedule</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Specify how many tablets or dosages are taken in each time slot (Morning, Noon, Evening, Night). You can enter fractional values if needed.</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    schedule = []
    for i, time in enumerate(SCHEDULE_TIMES):
        val = cols[i].number_input(f"{time}", min_value=0.0, step=0.25, value=0.0, key=f"schedule_{time}")
        schedule.append(val)

    schedule_str = "-".join(str(value) for value in schedule)

    if st.button("Add Medication to List"):
        # Reject an all-zero schedule because it cannot contribute to LEDD.
        if sum(schedule) > 0:
            st.session_state.medication_list.append((selected_med, schedule_str))
            st.success(f"Added {selected_med} with schedule {schedule_str}")
        else:
            st.warning("Please enter a valid dosage schedule.")

# Step 4 renders the persistent list. Deleting an item triggers a rerun so that
# the removed row disappears immediately.
st.markdown("---")
with st.container():
    st.markdown("<div class='section-title'>Step 4: Medication List</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Here you see all medications you've added so far along with their respective dosage schedules. You can remove entries individually if needed.</div>", unsafe_allow_html=True)
    for i, (med, sched) in enumerate(st.session_state.medication_list):
        cols = st.columns([6, 2])
        cols[0].markdown(f"- **{med}** → `{sched}`")
        if cols[1].button(f"🗑️ Delete", key=f"del_{i}"):
            st.session_state.medication_list.pop(i)
            st.rerun()

# Step 5 calculates the result only on request, then renders both a visual
# breakdown and portable CSV/PDF summaries.
st.markdown("---")
with st.container():
    st.markdown("<div class='section-title'>Step 5: Calculate, Visualize & Export</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Click 'Compute LEDD' to calculate the total Levodopa Equivalent Daily Dose. View visual breakdown and export results if needed.</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Compute LEDD"):
        if st.session_state.medication_list:
            total_ledd, cats, cat_ledd = compute_ledd(st.session_state.medication_list, medications)
            st.success(f"Total LEDD: **{total_ledd:.2f} mg**")
            if cats:
                st.info(f"Categories involved: {', '.join(sorted(cats))}")

            # A pie chart makes each drug category's share of the total visible.
            fig, ax = plt.subplots()
            ax.pie(cat_ledd.values(), labels=cat_ledd.keys(), autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
            # Explicitly release the figure during long-running local sessions.
            plt.close(fig)

            # Convert the category mapping into a simple two-column CSV export.
            df = pd.DataFrame.from_dict(cat_ledd, orient='index', columns=['LEDD'])
            csv = df.to_csv().encode('utf-8')
            st.download_button("📄 Export Category LEDD to CSV", data=csv, file_name="category_ledd.csv", mime="text/csv")

            # Generate the PDF in memory; no temporary user file is required.
            pdf_bytes = export_pdf(total_ledd, cat_ledd)
            st.download_button("📑 Export Summary as PDF", data=pdf_bytes, file_name="ledd_summary.pdf", mime="application/pdf")
        else:
            st.warning("No medications added.")

    # Clear keeps the rest of the widget state; reset removes all session keys.
    if col2.button("Clear All"):
        st.session_state.medication_list = []
        st.info("Cleared all medications.")

    if col3.button("Reset App"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    # Closing a browser tab does not stop Streamlit, so the packaged app exposes
    # an explicit action that terminates its local background process.
    if col4.button("Exit Calculator"):
        st.info("Calculator closed. You can now close this browser tab.")
        exit_application()
        st.stop()

# Credit the source publication for the conversion factors used by the app.
st.markdown("---")
st.caption("""
    Made with ❤️ by GAL  
    <span class='ref-text'>Schade S, Mollenhauer B, Trenkwalder C. Levodopa equivalent dose conversion factors: an updated proposal including opicapone and safinamide. *Mov Disord Clin Pract.* 2020 Mar 16;7(3):343.</span>
""", unsafe_allow_html=True)
st.markdown("---")
