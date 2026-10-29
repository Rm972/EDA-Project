import streamlit as st

from core.data import ADDICTION_THRESHOLD
from core.insights import key_findings
from core.ui import Context, finding, page_header


def render(ctx: Context) -> None:
    page_header("Key Findings and Limitations",
                "What the analysis shows, how far the results can be trusted, and what they do not prove.")
    full, raw = ctx.full, ctx.raw
    f = key_findings(full)
    st.caption(f"All findings on this page use the full cleaned dataset ({len(full):,} players) and ignore the sidebar filters.")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Who is addicted?")
        for k in ["rate", "age", "work", "degree"]:
            if k in f:
                finding(f[k])
    with c2:
        st.subheader("Mental health and habits")
        for k in ["mental", "corr", "why", "style"]:
            if k in f:
                finding(f[k])

    st.subheader("Conclusion")
    st.success(
        "**Are gamers sad and isolated? Not all of them.** Players who play a lot, play alone, or play to relax "
        "(possibly to escape stress) report worse mental health, while players who play for fun with real-life "
        "friends are doing better. The number of hours on its own is only weakly related to mental health. "
        "This agrees with Sauter, Braun & Mack (2021), who found that social context and gaming motives predict "
        "mental health better than time played."
    )

    st.subheader("Definition used in this project")
    st.info(
        f"A player is classified as **addicted** if they report **{ADDICTION_THRESHOLD} or more hours of gaming per week** "
        "(the length of a full-time job). This is a project-specific analytical label based on hours only. "
        "It is **not a medical diagnosis**: clinical gaming disorder is defined by symptoms such as loss of control "
        "and harm to daily life, not by hours alone."
    )

    st.subheader("Limitations")
    male = (full["Gender"] == "Male").mean() * 100
    pc = (raw["Platform"] == "PC").mean() * 100 if "Platform" in raw else None
    reddit = (raw["Reference"] == "Reddit").mean() * 100 if "Reference" in raw else None
    earners = full[full["earnings"] == "Earns a living"]
    sample_bits = [f"{male:.0f}% male"]
    if pc is not None:
        sample_bits.append(f"{pc:.0f}% PC players")
    if reddit is not None:
        sample_bits.append(f"{reddit:.0f}% recruited through Reddit")
    st.markdown(
        f"- **Sampling bias:** the sample is not representative of all gamers ({', '.join(sample_bits)}, "
        f"aged 18+, mostly League of Legends players). Results may not apply to other groups.\n"
        "- **Self-reported data:** answers come from an online survey, so people may misremember or exaggerate "
        "(two clearly joking answers, e.g. 8,000 hours per week, were removed).\n"
        "- **Correlation is not causation:** the survey was taken at one point in time, so it cannot show whether "
        "gaming affects mental health or mental health affects gaming.\n"
        f"- **Hours-based definition:** it also counts the {len(earners)} players who earn a living from gaming "
        f"({earners['is_addicted'].mean() * 100:.0f}% of them play 40+ hours), even though gaming is their job.\n"
        "- **Hours measure one game only:** the survey asked about the player's main game, so total gaming time may be higher.\n"
        "- **Game genre:** the survey did not include genres such as horror games, so their effect could not be studied."
    )

    st.subheader("Sources")
    st.markdown(
        "- Sauter, M., & Draschkow, D. (2017). *Are gamers sad and isolated? A database about the anxiety, life "
        "satisfaction and social phobia of over 13000 participants.* PsyArXiv. https://doi.org/10.31234/osf.io/mfajz\n"
        "- Sauter, M., Braun, T., & Mack, W. (2021). *Social context and gaming motives predict mental health better "
        "than time played.* Cyberpsychology, Behavior, and Social Networking, 24(2), 94–100. "
        "https://doi.org/10.1089/cyber.2020.0234\n"
        "- Kaggle: [Online Gaming Anxiety Data](https://www.kaggle.com/datasets/divyansh22/online-gaming-anxiety-data)"
    )
