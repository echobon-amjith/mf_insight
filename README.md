# Mutual Fund Portfolio Overview

Gives you the detailed current valuation and performane analysis of all your mutual fund portfolio holding by just adding your CAS pdf.

## Features
- Safest way to view and analyse the mutual fund portfolio without disclosing any personal details
- Get portfolio specific charts, graphs and metric by fetching the nav history and the fact sheets from AMFI

## Project Structure
```text
├── code/
│   ├── features/
│   │   ├── __init__.py
│   │   ├── amfi_navhistory.py  # AMFI data fetch module
│   │   ├── config.py           # AMFI URL and NAV file directory stored
│   │   ├── pdf_process.py      # Extract CAS data module
│   │   ├── pofo_data.py        # CAS data and AMFI data joining module
│   │   └── streamlit_view.py   # Main Streamlit application
│   └── tests/
│       └──
├── data/
│   └── daily_cache/            # Downloaded NAV files directory
├── README.md                   # This documentation file
└── requirements.txt            # Python package dependencies
```
---

## Getting Started

Follow these steps to set up and run the application locally on your machine.

### 1. Prerequisites
Make sure you have **Python 3.8+** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/echobon-amjith/amfi_mf_portfolio_insight_from_cas.git
```

### 3. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Start the Streamlit local server:
```bash
streamlit run code\features\streamlit_view.py
```
The app should automatically open in your default web browser at `http://localhost:8501`.

---