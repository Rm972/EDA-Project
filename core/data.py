"""Data loading, cleaning and feature engineering.

This module reproduces the cleaning steps from EDA_Project.ipynb, in the same order,
so the dashboard and the notebook produce the same final dataset.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_FILE = DATA_DIR / "GamingStudy_data.csv"

# Project definition of "addicted" (from the notebook): 40+ hours of gaming per week
ADDICTION_THRESHOLD = 40
# Impossible values: a week has only 168 hours (7 x 24)
MAX_WEEKLY_HOURS = 168
# Free-text categories with fewer answers than this are grouped into "other" (notebook rule)
RARE_CATEGORY_MIN = 30

AGE_BINS = [17, 20, 25, 30, 100]
AGE_LABELS = ["18-20", "21-25", "26-30", "31+"]

COLUMNS_TO_DROP = [
    "S. No.", "Timestamp", "GAD1", "GAD2", "GAD3", "GAD4", "GAD5", "GAD6", "GAD7", "Platform",
    "SWL1", "SWL2", "SWL3", "SWL4", "SWL5", "SPIN1", "SPIN2", "SPIN3", "SPIN4", "SPIN5",
    "SPIN6", "SPIN7", "SPIN8", "SPIN9", "SPIN10", "SPIN11", "SPIN12", "SPIN13", "SPIN14",
    "SPIN15", "SPIN16", "SPIN17", "League", "highestleague", "Narcissism", "Game",
    "Birthplace", "Residence", "Birthplace_ISO3", "Residence_ISO3", "Reference", "accept",
]

REQUIRED_COLUMNS = [
    "GADE", "Hours", "earnings", "whyplay", "streams", "Gender", "Age", "Work",
    "Degree", "Playstyle", "GAD_T", "SWL_T", "SPIN_T",
]

RENAME_SCORES = {
    "GAD_T": "Anxiety",
    "SWL_T": "Life_Satisfaction",
    "SPIN_T": "Social_Phobia",
    "GADE": "Anxiety_Impact",
}

PLAYSTYLE_LABELS = {
    "multiplayer - online - with real life friends": "Real friends",
    "multiplayer - online - with strangers": "Strangers",
    "multiplayer - online - with online acquaintances or teammates": "Online friends",
    "multiplayer - offline (people in the same room)": "Offline (same room)",
    "singleplayer": "Singleplayer",
}

# Display-only labels (applied after cleaning; they do not change any values)
WORK_LABELS = {
    "Student at college / university": "University student",
    "Student at school": "School student",
    "Unemployed / between jobs": "Unemployed",
    "Employed": "Employed",
}
DEGREE_LABELS = {
    "None": "No degree",
    "High school diploma (or equivalent)": "High school",
    "Bachelor (or equivalent)": "Bachelor",
    "Master (or equivalent)": "Master",
    "Ph.D., Psy. D., MD (or equivalent)": "PhD",
}
EARNINGS_LABELS = {
    "i play for fun": "For fun",
    "i play mostly for fun but earn a little on the side (tournament winnings, streaming, etc)": "Fun + side income",
    "i earn a living by playing this game": "Earns a living",
    "other": "Other",
}

# Category orders used across the app
DEGREE_ORDER = ["No degree", "High school", "Bachelor", "Master", "PhD"]
WORK_ORDER = ["School student", "University student", "Employed", "Unemployed"]
IMPACT_ORDER = ["Not difficult at all", "Somewhat difficult", "Very difficult", "Extremely difficult"]
GENDER_ORDER = ["Male", "Female", "Other"]
ADDICTION_LABELS = {True: "Addicted", False: "Not addicted"}
ADDICTION_ORDER = ["Not addicted", "Addicted"]

SCORES = {
    "Anxiety": {"label": "Anxiety (GAD-7)", "range": "0–21", "better": "lower"},
    "Life_Satisfaction": {"label": "Life satisfaction (SWL)", "range": "5–35", "better": "higher"},
    "Social_Phobia": {"label": "Social phobia (SPIN)", "range": "0–68", "better": "lower"},
}


class DataLoadError(Exception):
    """Raised with a user-friendly message when the data cannot be loaded."""


def read_raw(path: Path = RAW_FILE) -> pd.DataFrame:
    """Read the raw survey file exactly as the notebook does."""
    if not path.exists():
        raise DataLoadError(
            f"The data file was not found. Place **{path.name}** inside the **data/** folder "
            "next to app.py and reload the page."
        )
    try:
        # ISO-8859-1: the file contains non-UTF-8 characters (UnicodeDecodeError otherwise)
        raw = pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)
    except Exception as exc:  # pragma: no cover - depends on the file
        raise DataLoadError(f"The data file **{path.name}** could not be read as a CSV file.") from exc

    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise DataLoadError(
            f"The data file is missing required columns: {', '.join(missing)}. "
            "Please use the original GamingStudy_data.csv from Kaggle."
        )
    return raw


def _group_rare(series: pd.Series) -> pd.Series:
    counts = series.value_counts()
    rare = counts[counts < RARE_CATEGORY_MIN].index
    return series.replace(list(rare), "other")


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Apply the notebook cleaning steps. Returns the clean data and a log of each step."""
    log: list[dict] = []

    def record(step: str, detail: str, frame: pd.DataFrame) -> None:
        log.append({"Step": step, "What was done": detail, "Rows": len(frame), "Columns": frame.shape[1]})

    df = raw.copy()
    record("Start", "Raw survey data", df)

    df = df.drop(columns=[c for c in COLUMNS_TO_DROP if c in df.columns])
    record("Drop columns", "Removed individual questions (totals kept), IDs, countries, game, platform and empty columns", df)

    # GADE was optional and starts with "If you checked off any problems...":
    # most people who skipped it have 0 anxiety, so missing means "no difficulty".
    gade_missing = int(df["GADE"].isna().sum())
    df["GADE"] = df["GADE"].fillna("Not difficult at all")
    record("Fill GADE", f"{gade_missing:,} skipped answers filled with 'Not difficult at all'", df)

    # The survey option "None" (no degree) is read by pandas as NaN by default.
    degree_missing = int(df["Degree"].isna().sum())
    df["Degree"] = df["Degree"].fillna("None")
    record("Restore Degree = None", f"{degree_missing:,} values were the answer 'None' (no degree), not missing", df)

    df = df.dropna()
    record("Drop missing rows", "Rows missing social phobia, hours, streams or work status (each < 5%)", df)

    df = df[(df["Hours"] <= MAX_WEEKLY_HOURS) & (df["streams"] <= MAX_WEEKLY_HOURS)]
    record("Remove impossible values", f"Hours or streams above {MAX_WEEKLY_HOURS} per week", df)

    for col in ["whyplay", "Playstyle", "earnings"]:
        df[col] = df[col].str.strip().str.lower()
        df[col] = _group_rare(df[col])
    df["Playstyle"] = df["Playstyle"].replace(PLAYSTYLE_LABELS)
    record("Standardize text", f"Lowercased free text; answers with < {RARE_CATEGORY_MIN} people grouped as 'other'", df)

    df = df.rename(columns=RENAME_SCORES)
    df["is_addicted"] = df["Hours"] >= ADDICTION_THRESHOLD
    df["age_group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS)
    record("New features", f"is_addicted (Hours >= {ADDICTION_THRESHOLD}) and age_group", df)

    return df.reset_index(drop=True), log


def add_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Readable labels for charts. Values are relabelled only, never changed."""
    out = df.copy()
    out["addiction_status"] = out["is_addicted"].map(ADDICTION_LABELS)
    out["Work"] = out["Work"].map(WORK_LABELS).fillna(out["Work"])
    out["Degree"] = out["Degree"].str.replace("\xa0", " ", regex=False)  # some labels use a non-breaking space
    out["Degree"] = out["Degree"].map(DEGREE_LABELS).fillna(out["Degree"])
    out["earnings"] = out["earnings"].map(EARNINGS_LABELS).fillna(out["earnings"])
    out["whyplay"] = out["whyplay"].str.capitalize()
    out["Playstyle"] = out["Playstyle"].replace({"other": "Other"})
    out["age_group"] = out["age_group"].astype(str)
    return out


def load_dataset(path: Path = RAW_FILE) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Return (raw data, clean data with display labels, cleaning log)."""
    raw = read_raw(path)
    cleaned, log = clean(raw)
    return raw, add_display_columns(cleaned), log
