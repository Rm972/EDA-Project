# 🎮 Gaming & Mental Health: EDA and Interactive Dashboard

**Are gamers sad and isolated?** This project explores how gaming habits relate to anxiety, life satisfaction and social phobia, using a survey of more than 13,000 gamers. It includes data cleaning, exploratory data analysis (EDA) in a Jupyter Notebook, and an interactive Streamlit dashboard.

---

## 📁 Project Structure

```
gaming_dashboard/
├── app.py                    # Entry point: data loading, sidebar filters, page navigation
├── requirements.txt
├── README.md
├── EDA_Project.ipynb         # The analysis notebook
├── GamingStudy_Survey.pdf    # The original survey questionnaire
├── .streamlit/
│   └── config.toml           # Theme (colors, fonts)
├── data/
│   └── GamingStudy_data.csv  # Raw survey data (cleaned automatically by the app)
├── core/
│   ├── data.py               # Cleaning pipeline (same steps as the notebook)
│   ├── filters.py            # Sidebar filters and filter logic
│   ├── insights.py           # Summary tables and findings calculated from the data
│   ├── charts.py             # Plotly charts with one consistent style
│   └── ui.py                 # Layout helpers (KPI cards, headers, empty states)
└── views/                    # One file per dashboard page
    ├── overview.py
    ├── explore.py
    ├── addiction.py
    ├── mental_health.py
    ├── habits.py
    └── findings.py
```

---

## 📊 Dataset

- **Name:** Online Gaming Anxiety Data ([Kaggle](https://www.kaggle.com/datasets/divyansh22/online-gaming-anxiety-data))
- **Original data:** Sauter & Draschkow (2017), published on the [Open Science Framework](https://osf.io/vnbxk/)
- **Size:** 13,464 participants aged 18+, 55 columns → **12,668 players** after cleaning
- **Scales:** GAD-7 anxiety (0–21), Satisfaction With Life (5–35), Social Phobia Inventory (0–68)

**Definition used in this project:** a player is classified as **addicted** if they play **40+ hours per week** (a full-time job). This is an analytical label, **not a medical diagnosis**.

---

## ❓ Questions

1. Which age groups have the highest addiction rate, and does it differ by gender?
2. Does the addiction rate differ by work status and education level?
3. Do addicted players have higher anxiety, lower life satisfaction and higher social phobia?
4. How strong is the relationship between gaming hours and mental health?
5. How does the reason for playing relate to anxiety?
6. Is playing with friends associated with better life satisfaction than playing alone?

---

## 📝 Using the Original Survey in My Analysis

The column descriptions on Kaggle were not always clear, so I used the original survey questionnaire ([GamingStudy_Survey](GamingStudy_Survey.pdf)) to understand what each column really measures. This helped me find three things that changed my cleaning decisions:

1. **`Degree` was not really missing.** The survey had a **"None"** option (no degree), but pandas reads the text `"None"` as a missing value. The 1,577 "missing" values were people with no degree, so I restored them. This group has the **highest addiction rate** of all education levels.
2. **`GADE` missing values had a reason.** The question was optional and started with *"If you checked off any problems..."*. Most people who skipped it had 0 anxiety, and 96% of people with 0 anxiety who did answer chose *"Not difficult at all"*, so I filled the skipped answers with that value.
3. **Correct meaning of the columns.** `GADE` measures how much **anxiety** affects daily life, and `streams` is **hours per week**, which confirmed that removing values above 168 hours (a whole week) was correct.

---

## 🔍 Key Findings

- About **11%** of players play 40+ hours per week.
- The most addicted group is **young males (18–20)**, and addiction goes down with age.
- **Unemployed** players have almost **three times** the addiction rate of employed players.
- Addicted players have **higher anxiety, lower life satisfaction and higher social phobia**.
- **But gaming hours are only weakly related to mental health (|r| ≤ 0.13).**
- **Why** and **with whom** people play matter more: players who play **for fun** and **with real-life friends** have better scores, while players who play **to relax** or **alone** have worse scores.

All numbers in the dashboard are calculated from the data when the app runs; none are typed in by hand.

## ✅ Checking My Results Against Published Research

My analysis showed that gaming **hours** have only a **weak** relationship with mental health, while the **reason for playing** and **playstyle** showed clearer differences. After finishing my analysis, I searched for research using the same survey and found a peer-reviewed paper by the researcher who collected the data, based on the same 13,464 players (Sauter, Braun & Mack, 2021). According to its abstract, time played is a poor predictor of mental health, while social context and gaming motives predict it better. This matches my findings.

---

## 🚀 Run the Dashboard Locally

1. Install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/) (tick *Add python.exe to PATH* on Windows).
2. Open a terminal **inside the `gaming_dashboard` folder**.
3. (Optional) create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```
4. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
   On Windows, if `pip` is not recognised, use `py -m pip install -r requirements.txt`.
5. Start the app:
   ```
   streamlit run app.py
   ```
   (or `py -m streamlit run app.py`). The dashboard opens at `http://localhost:8501`.

The app reads the **raw** file `data/GamingStudy_data.csv` and applies the notebook's cleaning steps itself, so the notebook and the dashboard always use the same data.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Upload the whole `gaming_dashboard` folder to a **public GitHub repository**, keeping the same structure. Make sure `data/GamingStudy_data.csv` (4 MB) and the hidden `.streamlit/` folder are included.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Choose your repository and branch, and set **Main file path** to `app.py` (or `gaming_dashboard/app.py` if the folder is inside the repository).
5. Click **Deploy**. Streamlit installs `requirements.txt` automatically. You get a public link you can share or open during the presentation.

---

## 🧪 Testing Checklist

| Area | Test | Expected result |
|---|---|---|
| Missing file | Rename `data/GamingStudy_data.csv` and reload | Friendly message telling you where to put the file |
| Wrong file | Use a CSV without `SPIN_T` | Message listing the missing columns |
| Metrics | Open Overview with no filters | 12,668 participants · 21.5 average hours · 11.1% addicted |
| Notebook match | Compare with the notebook | Same values (e.g. Unemployed 22.7%, median anxiety 5 vs 4) |
| Filters | Select *Work status = Unemployed* | Overview shows 1,299 players and 22.7% addicted |
| Comparison charts | Keep *Unemployed* selected, open Gaming Addiction | The Work chart still shows all four groups (its own filter is ignored, and the caption says so) |
| Small groups | Select *Education = PhD* and *Age group = 31+* | Warning that fewer than 30 players are selected; grey bars for small groups |
| Empty result | Remove every option from *Gender* | Every page shows "No players match the current filters" |
| One group only | Filter to a group with no addicted players | Mental Health page explains it cannot compare |
| Reset | Change filters, click **Reset filters** | All 12,668 players selected again |
| Download | Explore the Data → Download | CSV of the filtered players |
| Charts | Hover any bar | Tooltip shows the value and the number of players |

---

## 🎨 Design and Implementation Decisions

- **One cleaning pipeline (`core/data.py`)** reproduces the notebook step by step, so results cannot drift apart. It was checked to give exactly the same 12,668 rows and values as the notebook's `clean_data.csv`.
- **Percentages within groups, with counts shown.** Every rate shows *n*, and groups with fewer than 30 players are drawn in light grey, because 94% of players are male and some groups are tiny.
- **Comparison charts ignore their own filter.** For example, the "by work status" chart uses every filter except Work status, so filtering never removes the groups being compared. The caption says when this happens.
- **Findings are calculated, not typed in.** The Overview and Findings pages generate their sentences from the data (full dataset), and the analysis pages describe the filtered data.
- **Plotly** gives tooltips and a built-in "download as PNG" button on every chart (camera icon).
- **One colour meaning per concept:** coral = addicted, slate = not addicted, indigo for everything else.

---

## ⚠️ Limitations

- Addiction is defined by **hours only**; it also counts the 45 players who **earn a living from gaming**, even though it is their job.
- The sample is not balanced: **94% male**, 98% PC players, mostly recruited through Reddit, all **18+**.
- `Hours` counts only the player's **main game**.
- The survey is **self-reported** and taken at one time point, so it shows **associations, not causes**.

### Data notes (kept as in the notebook)
- 11 players report a PhD while younger than 22, which is unlikely; they were kept to match the notebook.
- The notebook's "before cleaning" addiction rate (11.33%) counts the 30 rows with missing hours as not addicted; excluding them gives 11.35%, so the conclusion does not change.

---

## 📚 References

- Sauter, M., & Draschkow, D. (2017). *Are gamers sad and isolated? A database about the anxiety, life satisfaction and social phobia of over 13000 participants.* PsyArXiv. https://doi.org/10.31234/osf.io/mfajz
- Sauter, M., Braun, T., & Mack, W. (2021). *Social context and gaming motives predict mental health better than time played.* Cyberpsychology, Behavior, and Social Networking, 24(2), 94–100. https://doi.org/10.1089/cyber.2020.0234
- Kaggle: [Online Gaming Anxiety Data](https://www.kaggle.com/datasets/divyansh22/online-gaming-anxiety-data)
- Survey questionnaire: [GamingStudy_Survey](GamingStudy_Survey.pdf)
