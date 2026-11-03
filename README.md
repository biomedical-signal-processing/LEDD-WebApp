# Levodopa Equivalent Daily Dose Calculator

<p align="left">
  <strong>A Streamlit web application for calculating Parkinson's medication doses using updated conversion factors</strong>
</p>

---

## 📋 Overview

The **LEDD Calculator** is an interactive web application built with Streamlit that estimates the **Levodopa Equivalent Daily Dose (LEDD)** for a list of Parkinson's medications. Its conversion rules follow the 2020 proposal by Schade et al., including rules for **opicapone** and **safinamide**.

### Key Features

- ✅ Swiss medication catalogue
- ✅ Real-time LEDD calculation with category breakdown
- ✅ Interactive dosage schedule input (Morning, Noon, Evening, Night)
- ✅ Visual pie chart representation of medication categories
- ✅ Export results as CSV or PDF
- ✅ Session state management for multi-step workflow

The catalogue currently contains Swiss products only. The app uses the product's ingredient strengths from `config_Switzerland.json`; it does not look up prescriptions or verify a patient's regimen.

---

## 📚 Scientific Background

This calculator is based on the peer-reviewed publication:

**Schade S, Mollenhauer B, Trenkwalder C.** "Levodopa Equivalent Dose Conversion Factors: An Updated Proposal Including Opicapone and Safinamide." *Movement Disorders Clinical Practice*. 2020 Mar 16;7(3):343.

DOI: [10.1002/mdc3.12921](https://doi.org/10.1002/mdc3.12921)

### Updated Conversion Factors

The app implements the following LEDD conversion factors:

| Medication | Conversion Factor |
|------------|-------------------|
| **Levodopa** (IR) | 1 |
| Levodopa CR | 0.75 |
| Levodopa ER | 0.5 |
| Duodopa | 1.11 |
| **COMT Inhibitors** | |
| Entacapone | 0.33 |
| Tolcapone | 0.5 |
| Opicapone | 0.5 |
| **MAO-B Inhibitors** | |
| Selegiline oral | 10 |
| Selegiline sublingual | 80 |
| Rasagiline | 100 |
| Safinamide | 100 (fixed, regardless of the 50/100 mg strength) |
| **Dopamine Agonists** | |
| Apomorphine | 10 |
| Piribedil | 1 |
| Pramipexole | 100 |
| Ropinirole | 20 |
| Rotigotine | 30 |
| **Other** | |
| Amantadine | 1 |

---


### Configuration Files

The app uses JSON configuration files to store medication data by country. Each medication entry contains active ingredients and their dosages in mg:

```json
{
  "Medication Name": {
    "Levodopa": 100,
    "Entacapone": 200
  }
}
```

---

## 🚀 Download and Run

End users do not need to open Python, Git, or a terminal. Download the file for your
computer from the repository's [Releases page](https://github.com/biomedical-signal-processing/LEDD-WebApp/releases/latest):

- **Windows:** download [LEDD-Calculator-Windows-x64-Setup.exe](https://github.com/biomedical-signal-processing/LEDD-WebApp/releases/latest/download/LEDD-Calculator-Windows-x64-Setup.exe), run it, and
  launch **LEDD Calculator** from the Start menu or desktop shortcut.
- **Windows portable fallback:** if the installer is blocked by organization
  policy, download [LEDD-Calculator-Windows-x64-Portable.zip](https://github.com/biomedical-signal-processing/LEDD-WebApp/releases/latest/download/LEDD-Calculator-Windows-x64-Portable.zip), choose
  **Extract All**, open the extracted `LEDD Calculator` folder, and double-click
  `LEDD Calculator.exe`.

The current release provides Windows downloads. On macOS and Linux, use the
developer setup below to run the Streamlit application from source. A macOS
desktop release is planned for later.

The application starts a private web server on `127.0.0.1`, opens the default
browser automatically, and keeps all entered medication information on the
local computer. Use **Exit Calculator** inside the page before closing the
browser tab so the background application also stops.

### Force Quit

If the browser was closed before **Exit Calculator** was selected:

- **Windows:** press `Ctrl+Shift+Esc`, open Task Manager, select
  **LEDD Calculator**, and choose **End task**.
- **macOS:** open **Activity Monitor**, search for **LEDD Calculator**, select
  it, choose the stop button, and then choose **Quit** or **Force Quit**.

## Developer Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate it on Windows PowerShell:**
   ```bash
   .\.venv\Scripts\Activate.ps1
   ```

   Or on macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   python -m streamlit run app.py
   ```

Open the local URL printed by Streamlit. To run the same local launcher used by the desktop build, use `python launcher.py`; it opens the browser automatically. `python launcher.py --no-browser` suppresses that action, and `--port 8501` selects a port. The equivalent environment settings are `LEDD_NO_BROWSER=1` and `LEDD_PORT=8501`. The launcher binds only to `127.0.0.1`.

Run the tests from the repository root with `python -m unittest discover -s tests`. The tests cover the calculation rules and a Streamlit UI smoke test. Install `requirements.txt` first.

### Building Desktop Files

Maintainers can run `build_windows.ps1` on Windows. Pushing a tag such as
`v1.0.0` triggers the GitHub Actions release workflow and attaches the Windows
installer and portable archive to a GitHub Release. `build_macos.command` is
available for local macOS builds, but the release workflow does not publish a
Mac download yet. PyInstaller builds are platform-specific; a Mac build cannot
be produced on Windows.

---

## 📦 Dependencies

The `requirements.txt` file includes:

| Package | Purpose |
|---------|---------|
| `streamlit` | Web framework for the UI |
| `pandas` | Data manipulation and CSV export |
| `matplotlib` | Pie chart visualization |
| `fpdf2` | PDF generation for exports |

---

## 📖 How to Use the App

The LEDD Calculator follows a **5-step workflow**:

### Step 1: Select Country

Choose the country to load the appropriate medication list. Currently supported:

- **Switzerland** - Products listed in `config_Switzerland.json`

The system uses this to match drug names and dosages correctly for your region.

### Step 2: Select Medication

Pick a medication from the dropdown list. The app displays:

- Active ingredients by category
- Dosage information in mg
- Category breakdown (L-Dopa, COMT inhibitors, MAO-B inhibitors, Dopamine Agonists, Other)

### Step 3: Enter Dosage Schedule

Specify the number of tablets/doses for each time slot:

| Time Slot | Description |
|-----------|-------------|
| Morning | First dose of the day |
| Noon | Midday dose |
| Evening | Evening dose |
| Night | Bedtime dose |

**Features:**
- Accepts fractional values (step: 0.25)
- Minimum value: 0.0
- Click **"Add Medication to List"** to save

### Step 4: Medication List

View all added medications with their schedules:

- Format: `Medication Name → Morning-Noon-Evening-Night`
- Example: `Levodopa 100mg → 1-0.5-1-0`
- Click **🗑️ Delete** to remove individual entries

### Step 5: Calculate, Visualize & Export

#### Compute LEDD
Click **"Compute LEDD"** to:
- Calculate total LEDD in mg
- Show involved medication categories
- Display pie chart with percentage breakdown

#### Export Options

| Button | Format | Description |
|--------|--------|-------------|
| 📄 Export Category LEDD to CSV | CSV | Category-wise LEDD breakdown |
| 📑 Export Summary as PDF | PDF | Total and category totals |

Exports contain category totals only. They do not include the entered medication schedule or patient identifiers. Downloads are generated in memory; the app does not save a local report automatically.

#### Management Buttons

- **Clear All** - Remove all medications from the list
- **Reset App** - Clear all session state and restart

---

## 🔧 Technical Implementation

### Core Functions

| Function | Purpose |
|----------|---------|
| `load_medication_data(country)` | Loads country-specific JSON config (cached) |
| `get_category(ingredient)` | Maps ingredient to medication category |
| `compute_ledd(medication_list, medication_data)` | Calculates total LEDD and category breakdown |
| `export_pdf(total_ledd, category_ledd)` | Generates PDF summary report |

### Session State Management

The app uses `st.session_state` to persist:

```python
st.session_state.medication_list = [(medication_name, schedule_string), ...]
```

Schedule format: `"Morning-Noon-Evening-Night"` (e.g., `"1-0.5-1-0"`)

### LEDD Calculation Formula

For each medication:

\[
\text{LEDD} = \sum (\text{daily\_dose} \times \text{ingredient\_amount} \times \text{conversion\_factor})
\]

Where:
- `daily_dose` = sum of all schedule time slots
- `ingredient_amount` = mg per tablet from config
- `conversion_factor` = the conversion factor defined in `ledd_calculator/core.py`

Safinamide is the documented exception: each selected product containing it contributes a fixed 100 mg LEDD when its schedule is nonzero, independently of the marketed 50 mg or 100 mg strength or number of units. Entering the same product more than once creates separate list entries and counts each entry. Ingredients without a conversion factor, such as carbidopa, contribute zero.

---

## 🌍 Adding New Countries

To support a new country:

1. Create `config_[CountryName].json`
2. Add medications available in that region
3. Update the country selectbox in `app.py`:
   ```python
   country = st.selectbox("Country", ["Switzerland", "YourCountry"])
   ```
4. Ensure ingredient names match the definitions in `ledd_calculator/core.py`

Each JSON value is the ingredient strength in mg **per unit**, not the daily amount. Keep product names unique and use the exact ingredient spelling and capitalization in `ledd_calculator/core.py`. An unrecognized ingredient contributes zero; the app does not warn about it. Before distributing a changed catalogue or conversion rule, review its clinical source and run the tests.

### JSON Template

```json
{
  "Medication Name": {
    "Levodopa": 100,
    "Entacapone": 200,
    "Rasagiline": 1
  }
}
```

---

## ⚠️ Important Disclaimers

### License

Copyright © 2026 Luigi Fiorillo, PhD. This project is available under the
[PolyForm Noncommercial License 1.0.0](LICENSE.txt). It permits noncommercial
use, modification, and distribution under its terms. Commercial use requires
separate permission from the copyright holder.
The license applies to this project; its third-party dependencies retain their
own licenses.

### Medical Disclaimer

> **This app is for informational and research purposes only.**

- ❌ Not a substitute for professional medical advice
- ❌ Not for making clinical decisions alone
- ✅ Should be used in consultation with Parkinson's specialists
- ✅ Verify all calculations with pharmacy teams

### Accuracy Notice

- Always verify medication dosages with prescribing information
- Conversion factors are based on the [Schade et al. proposal](https://doi.org/10.1002/mdc3.12921)
- Individual patient responses may vary
- Do not change a prescribed regimen based on this estimate alone

---

## 📊 Example Usage

### Scenario: Patient on Multiple Medications

**Medication 1:** Levodopa 100mg
- Schedule: 1 (Morning) - 0.5 (Noon) - 1 (Evening) - 0 (Night)
- Daily dose: 2.5 tablets

**Medication 2:** Rasagiline 1mg
- Schedule: 1 (Morning) - 0 - 0 - 0 (Night)
- Daily dose: 1 tablet

**Calculation:**
- Levodopa LEDD: 2.5 × 100 × 1 = 250 mg
- Rasagiline LEDD: 1 × 1 × 100 = 100 mg
- **Total LEDD: 350 mg**

---

## 🛠️ Development Notes

### Code Highlights

- **Caching**: `@st.cache_data` decorator for config loading
- **Input Handling**: The UI rejects an all-zero schedule; the core rejects schedules without four values
- **File Export**: In-memory PDF generation
- **UI/UX**: Custom CSS for dark theme styling

### Constants Dictionary

```python
CATEGORIES = {
    "L-Dopa": ["Levodopa", "Levodopa CR", "Levodopa ER"],
    "COMT inhibitors": ["Entacapone", "Opicapone", "Tolcapone"],
    "MAO-B inhibitors": ["Selegiline oral", "Selegiline sublingual", "Rasagiline", "Safinamide"],
    "Dopamine Agonists": ["Rotigotine", "Ropinirole", "Pramipexole", "Piribedil", "Apomorphine"],
    "Other": ["Amantadine"]
}
```

## 🔄 Future Enhancements

Potential improvements for future versions:

- [ ] Add more country-specific medication databases
- [ ] Include medication interaction warnings
- [ ] Add historical LEDD tracking over time
- [ ] Implement patient profile management
- [ ] Add dosage adjustment recommendations
- [ ] Multi-language support (English, Spanish, French, German)
- [ ] Mobile-responsive design improvements

---

## 📞 Support & Feedback

For issues, suggestions, or questions email the developer: [luigi.fiorillo@eoc.ch](mailto:luigi.fiorillo@eoc.ch) or [luigi.fiorillo@supsi.ch](mailto:luigi.fiorillo@supsi.ch)
