import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Config halaman
st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}

/* App background */
.stApp, .stAppHeader, .stColumn p{
    background-color: #DCEBEC;
    color: #0B2E30;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #105E62 !important;
    border-right: 1px solid #2F7F83;
}

section[data-testid="stSidebar"] * {
    color: white;
}
            
section[data-testid="stSidebar"] svg{
    fill: black
}

/* Selected tags (the pills) */
[data-baseweb="tag"] {
    background-color: #2F7F83 !important;
    color: #F4A261 !important;
}

/* Checkbox tick color in dropdown */
[data-baseweb="checkbox"] svg {
    fill: #F4A261 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #DCEBEC 0%, #2F7F83 100%);
    border: 1px solid #2F7F83;
    border-radius: 12px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #105E62 0%, #F4A261 100%);
}
[data-testid="metric-container"] label {
    color: #0B2E30 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0B2E30 !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
}

/* Section headers */
.section-title {
    font-size: 2rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #105E62;
    margin-bottom: 4px;
}
.chart-title {
    font-size: 3rem;
    font-weight: 700;
    color: #0B2E30;
    margin-bottom: 20px;
}

/* Plotly chart containers */
.stPlotlyChart {
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #2F7F83 !important;
    margin: 28px 0;
}

/* Warning / info */
.stAlert {
    background-color: #DCEBEC !important;
    border: 1px solid #2F7F83 !important;
    border-radius: 8px !important;
    color: #0B2E30 !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background-color: #DCEBEC !important;
    border: 1px dashed #2F7F83 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# Color Palette
ACCENT   = "#105E62"
ACCENT2  = "#2F7F83"
ACCENT3  = "#F4A261"
BG       = "#DCEBEC"
SURFACE  = "#DCEBEC"
SURFACE2 = "#DCEBEC"
BORDER   = "#2F7F83"
TEXT     = "#0B2E30"
TEXT_DIM = "#2F7F83"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Roboto, sans-serif", color=TEXT),
    margin=dict(l=12, r=12, t=36, b=12),
    xaxis=dict(
        gridcolor=BORDER, zerolinecolor=BORDER,
        tickfont=dict(color=TEXT_DIM, size=14),
        title_font=dict(color=TEXT_DIM),
    ),
    yaxis=dict(
        gridcolor=BORDER, zerolinecolor=BORDER,
        tickfont=dict(color=TEXT_DIM, size=14),
        title_font=dict(color=TEXT_DIM),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_DIM, size=14),
    ),
)

PALETTE = [
    "#105E62", "#2F7F83", "#F4A261", "#0B2E30",
    "#105E62", "#F4A261", "#2F7F83", "#0B2E30",
    "#105E62", "#2F7F83",
]

# Helper
def skill_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("skill_")]

def clean_label(col: str) -> str:
    return col.replace("skill_", "").replace("_", " ").title()

def header(section: str, title: str):
    st.markdown(f'<p class="section-title">{section}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="chart-title">{title}</p>', unsafe_allow_html=True)

df = pd.read_csv('main.csv')
skill_cols = skill_columns(df)

# Sidebar filters
with st.sidebar:
    st.markdown("### Filter")

    all_categories = sorted(df["job_category"].dropna().unique())
    sel_categories = st.multiselect(
        "Job Category", all_categories, default=all_categories,
        placeholder="Semua kategori"
    )

    all_levels = sorted(df["formatted_experience_level"].dropna().unique())
    sel_levels = st.multiselect(
        "Experience Level", all_levels, default=all_levels,
        placeholder="Semua level"
    )

# Apply filters
fdf = df.copy()
if sel_categories:
    fdf = fdf[fdf["job_category"].isin(sel_categories)]
if sel_levels:
    fdf = fdf[fdf["formatted_experience_level"].isin(sel_levels)]

# Overview
st.markdown("## Job Market Dashboard")
st.markdown("---")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Lowongan", f"{len(fdf):,}")
k2.metric("Job Categories", fdf["job_category"].nunique())
k3.metric(
    "Rata Rata gaji per tahun",
    f"${fdf['med_salary'].mean():,.0f}" if fdf["med_salary"].notna().any() else "N/A"
)
k4.metric(
    "Jumlah skill",
    len(skill_cols) if skill_cols else "—"
)

st.markdown("---")

# Distribusi lowongan per kategori
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    header("01", "Distribusi Lowongan per Kategori")
    cat_counts = (
        fdf["job_category"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Kategori", "job_category": "Jumlah"})
    )
    cat_counts.columns = ["Kategori", "Jumlah"]
    cat_total = cat_counts['Jumlah'].sum()

    # fig_cat = go.Figure(go.Bar(
    #     x=cat_counts["Jumlah"],
    #     y=cat_counts["Kategori"],
    #     orientation="h",
    #     marker=dict(
    #         color=cat_counts["Jumlah"],
    #         colorscale=[[0, ACCENT2], [1, ACCENT3]],
    #         showscale=False,
    #     ),
    #     text=cat_counts["Jumlah"].apply(lambda v: f"{v:,}"),
    #     textposition="outside",
    #     textfont=dict(color=TEXT_DIM, size=11, family="DM Mono"),
    #     hovertemplate="<b>%{y}</b><br>Jumlah: %{x:,}<extra></extra>",
    # ))

    fig_cat = go.Figure(go.Pie(
        labels=cat_counts["Kategori"],
        values=cat_counts["Jumlah"],
        hole=0.5,
        marker=dict(colors=PALETTE, line=dict(color=BG, width=2)),
        textinfo="percent",
        textfont=dict(size=11, family="DM Mono"),
        hovertemplate="<b>%{label}</b><br>%{value:,} lowongan (%{percent})<extra></extra>",
    ))
    
    # Apply base layout first
    # fig_cat.update_layout(**PLOTLY_LAYOUT)
    
    # Then apply specific overrides
    # fig_cat.update_layout(
    #     height=400,
    #     yaxis_autorange="reversed",  # Use dot notation for nested property
    #     bargap=0.3,
    # )

    fig_cat.update_traces(textposition='inside')

    fig_cat.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        annotations=[
            dict(
                text=f"<b>{cat_total:,}</b><br><span>total</span>",
                font=dict(size=24, color=TEXT, family="Syne"),
                showarrow=False, x=0.5, y=0.5,
            )
        ],
        uniformtext_minsize=12, uniformtext_mode="hide"
    )
    
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    header("02", "Distribusi Experience Level")
    exp_counts = (
        fdf["formatted_experience_level"]
        .value_counts()
        .reset_index()
    )
    exp_counts.columns = ["Level", "Jumlah"]
    exp_total = exp_counts["Jumlah"].sum()

    fig_exp = go.Figure(go.Pie(
        labels=exp_counts["Level"],
        values=exp_counts["Jumlah"],
        hole=0.5,
        marker=dict(colors=PALETTE, line=dict(color=BG, width=2)),
        textinfo="percent",
        textfont=dict(size=11, family="DM Mono"),
        hovertemplate="<b>%{label}</b><br>%{value:,} lowongan (%{percent})<extra></extra>",
    ))
    fig_exp.update_traces(textposition='inside')
    fig_exp.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        annotations=[
            dict(
                text=f"<b>{exp_total:,}</b><br><span>total</span>",
                font=dict(size=24, color=TEXT, family="Syne"),
                showarrow=False, x=0.5, y=0.5,
            )
        ],
        uniformtext_minsize=12, uniformtext_mode="hide"
    )

    # NaN count note
    nan_exp = fdf["formatted_experience_level"].isna().sum()
    if nan_exp:
        st.caption(f"ℹ️ {nan_exp:,} baris tanpa data experience level (tidak ditampilkan di chart).")
    st.plotly_chart(fig_exp, use_container_width=True)

st.markdown("---")

# Top 10 skill bayaran tertinggi
header("03", "Top 10 Skill berdasarkan Salary")

if not skill_cols:
    st.warning("Kolom skill_ tidak ditemukan.")
elif fdf["med_salary"].isna().all():
    st.warning("Tidak ada data med_salary yang valid setelah filter.")
else:
    salary_df = fdf[fdf["med_salary"].notna()].copy()

    skill_salary = {}
    for sc in skill_cols:
        subset = salary_df[salary_df[sc] == 1]["med_salary"]
        if len(subset) >= 5:           # minimal sample guard
            skill_salary[sc] = subset.median()

    if not skill_salary:
        st.warning("Tidak cukup data skill + salary untuk ditampilkan.")
    else:
        top10_salary = (
            pd.Series(skill_salary)
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top10_salary.columns = ["skill_col", "median_salary"]
        top10_salary["Skill"] = top10_salary["skill_col"].apply(clean_label)
        top10_salary = top10_salary.sort_values("median_salary")

        fig_salary = go.Figure(go.Bar(
            x=top10_salary["median_salary"],
            y=top10_salary["Skill"],
            orientation="h",
            marker=dict(
                color=top10_salary["median_salary"],
                colorscale=[[0, "#3da17b"], [0.5, "#167f74"], [1, "#105e62"]],
                showscale=False,
            ),
            text=top10_salary["median_salary"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(color=TEXT_DIM, size=11, family="DM Mono"),
            hovertemplate="<b>%{y}</b><br>Median Salary: $%{x:,.0f}<extra></extra>",
        ))

        fig_salary.update_layout(**PLOTLY_LAYOUT)
        
        fig_salary.update_layout(
            height=420,
            xaxis=dict(
                tickprefix="$",
                tickformat=",",
                **PLOTLY_LAYOUT["xaxis"]
            ),
            bargap=0.4,
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_salary, use_container_width=True)

    # NaN note
    nan_sal = fdf["med_salary"].isna().sum()
    if nan_sal:
        st.caption(f"ℹTerdapat {nan_sal:,} baris tanpa data med_salary dari analisis salary.")

st.markdown("---")

# skill paling dicari
header("04", "Skill Paling Dicari")

if not skill_cols:
    st.warning("Kolom skill_ tidak ditemukan.")
else:
    col_top = 20
    skill_demand = {}
    for sc in skill_cols:
        count = fdf[sc].sum() if sc in fdf.columns else 0
        if count > 0:
            skill_demand[sc] = int(count)

    if not skill_demand:
        st.warning("Tidak ada data skill untuk remote IT jobs.")
    else:
        top_skills = (
            pd.Series(skill_demand)
            .sort_values(ascending=False)
            .head(col_top)
            .reset_index()
        )
        top_skills.columns = ["skill_col", "count"]
        top_skills["Skill"] = top_skills["skill_col"].apply(clean_label)
        top_skills["pct"] = (top_skills["count"] / len(df) * 100).round(1)
        top_skills = top_skills.sort_values("count")

        fig_remote = go.Figure()
        fig_remote.add_trace(go.Bar(
            x=top_skills["count"],
            y=top_skills["Skill"],
            orientation="h",
            marker=dict(
                color=top_skills["count"],
                colorscale=[[0, "#3da17b"], [0.5, "#167f74"], [1, "#105e62"]],
                showscale=False,
            ),
            text=top_skills.apply(lambda r: f"{r['count']:,}  ({r['pct']}%)", axis=1),
            textposition="outside",
            textfont=dict(color=TEXT_DIM, size=10, family="DM Mono"),
            hovertemplate="<b>%{y}</b><br>%{x:,} lowongan<extra></extra>",
        ))
        fig_remote.update_layout(
            **PLOTLY_LAYOUT,
            height=580,
            bargap=0.4,
        )
        fig_remote.update_layout(yaxis=dict(showgrid=False))

        st.plotly_chart(fig_remote, use_container_width=True)