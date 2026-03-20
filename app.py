from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from resume_screening.main import load_resumes
from resume_screening.ranking import rank_candidates


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_uploaded_resume_text(file) -> str:
    suffix = Path(file.name).suffix.lower()
    if suffix == ".txt":
        return file.read().decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError:
            st.error("PDF support needs pypdf. Install it with: python -m pip install --user pypdf")
            return ""

        reader = PdfReader(file)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()

    return ""


def _split_skills(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def _style_chart(chart: alt.Chart) -> alt.Chart:
    """Apply a consistent medium dark-blue visual theme to charts."""
    return (
        chart.configure(background="#1f3b5b")
        .configure_view(fill="#1f3b5b", stroke="#35506d")
        .configure_axis(
            labelColor="#dbeafe",
            titleColor="#dbeafe",
            gridColor="#35506d",
            labelFontSize=11,
            titleFontSize=12,
        )
        .configure_legend(labelColor="#dbeafe", titleColor="#dbeafe", labelFontSize=11, titleFontSize=12)
        .configure_title(fontSize=13, color="#dbeafe")
    )


st.set_page_config(page_title="Resume Screening System", page_icon="RS", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 20% 20%, #1f2937 0%, #111827 45%, #020617 100%);
            color: #39ff14;
            font-weight: 700;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
            border-right: 1px solid #374151;
        }

        .stMarkdown, .stCaption, label, .stTextInput, .stTextArea {
            color: #39ff14;
            font-weight: 700;
        }

        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #39ff14;
            font-weight: 700;
        }

        p,
        span,
        li,
        a,
        div,
        label,
        .stDataFrame,
        .stSelectbox,
        .stMultiSelect,
        .stRadio,
        .stCheckbox {
            color: #39ff14 !important;
            font-weight: 700 !important;
            text-shadow: 0 0 6px rgba(57, 255, 20, 0.45);
        }

        [data-testid="stDataFrame"],
        [data-testid="stExpander"],
        [data-testid="stVerticalBlock"] > div:has(> .stAltairChart),
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stDataFrame"]) {
            background: rgba(17, 24, 39, 0.72);
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 8px;
        }

        [data-testid="stTable"],
        [data-testid="stTable"] *,
        [data-testid="stTable"] th,
        [data-testid="stTable"] td {
            color: #000000 !important;
            font-weight: 700 !important;
            text-shadow: none !important;
            font-size: 12px !important;
        }

        div[data-baseweb="select"] > div,
        .stTextInput > div > div,
        .stTextArea textarea {
            background: #0f172a;
            color: #39ff14;
            border: 1px solid #334155;
            font-weight: 700;
        }

        .stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #39ff14;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            text-shadow: 0 0 6px rgba(57, 255, 20, 0.45);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        h1, h2, h3 {
            color: #39ff14;
            font-weight: 800;
            text-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Resume / Candidate Screening System")
st.caption("NLP-based screening, scoring, ranking, and skill-gap analysis")

default_job_file = ROOT / "data" / "job_descriptions" / "software_engineer.txt"
default_resumes_dir = ROOT / "data" / "resumes"

with st.sidebar:
    st.header("Inputs")
    use_sample_data = st.checkbox("Use sample data", value=True)
    required_skills_input = st.text_input(
        "Required skills (comma-separated)",
        "python,sql,aws,docker,kubernetes,machine learning,nlp,communication,api,git",
    )

if use_sample_data:
    job_description = _read(default_job_file)
    resumes = load_resumes(default_resumes_dir)
else:
    job_description = st.text_area("Paste job description", height=220)
    uploads = st.file_uploader("Upload resume .txt or .pdf files", type=["txt", "pdf"], accept_multiple_files=True)
    resumes: Dict[str, str] = {}
    for file in uploads or []:
        extracted = _extract_uploaded_resume_text(file)
        if extracted:
            resumes[Path(file.name).stem] = extracted

run = st.button("Rank Candidates", type="primary", use_container_width=True)

if "results_table" not in st.session_state:
    st.session_state["results_table"] = None
if "required_skills" not in st.session_state:
    st.session_state["required_skills"] = []

if run:
    required_skills = [s.lower() for s in _split_skills(required_skills_input)]
    if not job_description.strip():
        st.error("Job description is empty.")
    elif not resumes:
        st.error("No resumes found.")
    elif not required_skills:
        st.error("Please provide at least one required skill.")
    else:
        results = rank_candidates(job_description=job_description, resumes=resumes, required_skills=required_skills)

        table = pd.DataFrame(
            [
                {
                    "Rank": idx,
                    "Candidate": item.candidate_id,
                    "Final Score": item.final_score,
                    "Text Similarity": item.text_similarity,
                    "Skill Match": item.skill_match,
                    "Matched Skills": ", ".join(item.matched_skills),
                    "Missing Skills": ", ".join(item.missing_skills),
                    "Matched Count": len(item.matched_skills),
                    "Missing Count": len(item.missing_skills),
                }
                for idx, item in enumerate(results, start=1)
            ]
        )

        st.session_state["results_table"] = table
        st.session_state["required_skills"] = required_skills

table = st.session_state["results_table"]
required_skills = st.session_state["required_skills"]

if table is not None and not table.empty:
    st.subheader("Ranking Results")
    styled_table = table.style.set_table_styles(
        [
            {"selector": "", "props": [("background-color", "#1f3b5b")]},
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "#1f3b5b"),
                    ("color", "#000000"),
                    ("font-weight", "700"),
                    ("font-size", "12px"),
                ],
            },
            {
                "selector": "tbody td",
                "props": [
                    ("background-color", "#1f3b5b"),
                    ("color", "#000000"),
                    ("font-weight", "700"),
                    ("font-size", "12px"),
                ],
            },
        ]
    )
    st.table(styled_table)

    winner = table.iloc[0]
    st.success(f"Top candidate: {winner['Candidate']} with final score {winner['Final Score']:.4f}")

    st.subheader("Score Overview")
    score_col, component_col = st.columns(2)

    with score_col:
        st.markdown("**Final Score by Candidate**")
        score_chart = (
            alt.Chart(table)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Candidate:N", sort=alt.EncodingSortField(field="Final Score", op="sum", order="descending")),
                y=alt.Y("Final Score:Q", scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("Final Score:Q", scale=alt.Scale(scheme="blues"), legend=None),
                tooltip=["Rank", "Candidate", "Final Score", "Text Similarity", "Skill Match"],
            )
            .properties(height=320)
        )
        st.altair_chart(_style_chart(score_chart), use_container_width=True)

    with component_col:
        st.markdown("**Component Breakdown**")
        component_df = table.melt(
            id_vars=["Candidate"],
            value_vars=["Text Similarity", "Skill Match"],
            var_name="Metric",
            value_name="Score",
        )
        component_chart = (
            alt.Chart(component_df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("Candidate:N", title="Candidate"),
                y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 1])),
                xOffset="Metric:N",
                color=alt.Color("Metric:N", scale=alt.Scale(range=["#1f77b4", "#ff7f0e"])),
                tooltip=["Candidate", "Metric", "Score"],
            )
            .properties(height=320)
        )
        st.altair_chart(_style_chart(component_chart), use_container_width=True)

    st.subheader("Skill Gap Analysis")
    gap_col, heatmap_col = st.columns(2)

    with gap_col:
        gap_chart = (
            alt.Chart(table)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Candidate:N", sort=alt.EncodingSortField(field="Missing Count", op="sum", order="ascending")),
                y=alt.Y("Missing Count:Q"),
                color=alt.Color("Missing Count:Q", scale=alt.Scale(scheme="orangered"), legend=None),
                tooltip=["Candidate", "Missing Count", "Missing Skills"],
            )
            .properties(height=320)
        )
        st.altair_chart(_style_chart(gap_chart), use_container_width=True)

    with heatmap_col:
        if required_skills:
            heatmap_rows = []
            for _, row in table.iterrows():
                matched = set(_split_skills(row["Matched Skills"]))
                for skill in required_skills:
                    heatmap_rows.append(
                        {
                            "Candidate": row["Candidate"],
                            "Skill": skill,
                            "Matched": 1 if skill in matched else 0,
                        }
                    )

            heatmap_df = pd.DataFrame(heatmap_rows)
            heatmap_chart = (
                alt.Chart(heatmap_df)
                .mark_rect(cornerRadius=2)
                .encode(
                    x=alt.X("Skill:N", sort=required_skills),
                    y=alt.Y("Candidate:N", sort=table["Candidate"].tolist()),
                    color=alt.Color("Matched:Q", scale=alt.Scale(domain=[0, 1], range=["#f6d5d2", "#1b9e77"])),
                    tooltip=["Candidate", "Skill", "Matched"],
                )
                .properties(height=320)
            )
            st.altair_chart(_style_chart(heatmap_chart), use_container_width=True)

    st.subheader("Visual Candidate Comparison")
    candidates = table["Candidate"].tolist()
    left, right = st.columns(2)
    with left:
        candidate_a = st.selectbox("Candidate A", options=candidates, index=0)
    with right:
        default_b = 1 if len(candidates) > 1 else 0
        candidate_b = st.selectbox("Candidate B", options=candidates, index=default_b)

    subset = table[table["Candidate"].isin([candidate_a, candidate_b])]
    compare_df = subset.melt(
        id_vars=["Candidate"],
        value_vars=["Final Score", "Text Similarity", "Skill Match"],
        var_name="Metric",
        value_name="Value",
    )

    compare_chart = (
        alt.Chart(compare_df)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("Metric:N", title="Metric"),
            y=alt.Y("Value:Q", scale=alt.Scale(domain=[0, 1])),
            xOffset="Candidate:N",
            color=alt.Color("Candidate:N", scale=alt.Scale(scheme="tableau10")),
            tooltip=["Candidate", "Metric", "Value"],
        )
        .properties(height=320)
    )
    st.altair_chart(_style_chart(compare_chart), use_container_width=True)

    compare_left, compare_right = st.columns(2)
    with compare_left:
        row_a = subset[subset["Candidate"] == candidate_a].iloc[0]
        st.markdown(f"**{candidate_a}**")
        st.write(f"Matched Skills: {row_a['Matched Skills'] or 'None'}")
        st.write(f"Missing Skills: {row_a['Missing Skills'] or 'None'}")
    with compare_right:
        row_b = subset[subset["Candidate"] == candidate_b].iloc[0]
        st.markdown(f"**{candidate_b}**")
        st.write(f"Matched Skills: {row_b['Matched Skills'] or 'None'}")
        st.write(f"Missing Skills: {row_b['Missing Skills'] or 'None'}")