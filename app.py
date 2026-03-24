from __future__ import annotations

import json
from json import JSONDecodeError

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import COMPARISON_PATH, SUMMARY_PATH
from src.pipeline import run_pipeline


st.set_page_config(
    page_title="Bolsa Família vs BPC por território",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #0b1020; color: #f4f7fb; }
    .stMetric { background: rgba(255,255,255,0.04); padding: 12px; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


REQUIRED_COLUMNS = {
    "municipio",
    "ano",
    "valor_bolsa_familia",
    "valor_bpc",
    "valor_total_transferencias",
    "participacao_bolsa_pct",
    "participacao_bpc_pct",
    "taxa_judicializacao_bpc_pct",
    "indice_pressao_assistencial",
    "alerta_prioritario",
}


def load_data() -> tuple[dict[str, object], pd.DataFrame]:
    if not SUMMARY_PATH.exists() or not COMPARISON_PATH.exists():
        run_pipeline()
    try:
        summary = json.loads(SUMMARY_PATH.read_text())
        comparison_df = pd.read_parquet(COMPARISON_PATH)
    except (FileNotFoundError, JSONDecodeError, ValueError, OSError):
        summary = run_pipeline()
        comparison_df = pd.read_parquet(COMPARISON_PATH)

    if not REQUIRED_COLUMNS.issubset(comparison_df.columns):
        summary = run_pipeline()
        comparison_df = pd.read_parquet(COMPARISON_PATH)

    return summary, comparison_df


summary, comparison_df = load_data()

st.title("Bolsa Família vs BPC por território")
st.caption(
    "Comparação territorial entre transferência de renda familiar e benefício assistencial individual, com foco em composição municipal, judicialização do BPC e priorização gerencial."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Municípios", summary["municipios_cobertos"])
col2.metric("Ano de referência", summary["ano_referencia"])
col3.metric("Total Bolsa Família", f"R$ {summary['valor_total_bolsa_familia']:,.0f}".replace(",", "."))
col4.metric("Total BPC", f"R$ {summary['valor_total_bpc']:,.0f}".replace(",", "."))

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Composição Municipal", "Judicialização e Priorização"])

with tab1:
    top_df = comparison_df.nlargest(15, "valor_total_transferencias").copy()
    fig = px.bar(
        top_df,
        x="municipio",
        y=["valor_bolsa_familia", "valor_bpc"],
        barmode="stack",
        title="15 municípios com maior volume combinado de transferências",
        labels={"value": "Valor (R$)", "variable": "Programa"},
    )
    fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(fig, use_container_width=True)

    treemap = px.treemap(
        comparison_df,
        path=["perfil_territorial", "municipio"],
        values="valor_total_transferencias",
        color="participacao_bpc_pct",
        color_continuous_scale="Tealgrn",
        title="Distribuição territorial por perfil de dependência",
    )
    treemap.update_layout(paper_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(treemap, use_container_width=True)

with tab2:
    scatter = px.scatter(
        comparison_df,
        x="participacao_bolsa_pct",
        y="participacao_bpc_pct",
        size="valor_total_transferencias",
        color="perfil_territorial",
        hover_data=["municipio", "taxa_judicializacao_bpc_pct"],
        title="Composição percentual do gasto social por município",
        labels={
            "participacao_bolsa_pct": "% Bolsa Família",
            "participacao_bpc_pct": "% BPC",
        },
    )
    scatter.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(scatter, use_container_width=True)

    st.dataframe(
        comparison_df[
            [
                "municipio",
                "valor_bolsa_familia",
                "valor_bpc",
                "valor_total_transferencias",
                "participacao_bolsa_pct",
                "participacao_bpc_pct",
                "perfil_territorial",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    risk_df = comparison_df.sort_values("indice_pressao_assistencial", ascending=False).head(20)
    risk_fig = px.bar(
        risk_df,
        x="municipio",
        y="indice_pressao_assistencial",
        color="alerta_prioritario",
        title="Municípios prioritários para análise gerencial",
        hover_data=["taxa_judicializacao_bpc_pct", "participacao_bpc_pct"],
    )
    risk_fig.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(risk_fig, use_container_width=True)

    judicial_scatter = px.scatter(
        comparison_df,
        x="taxa_judicializacao_bpc_pct",
        y="participacao_bpc_pct",
        size="valor_bpc",
        color="alerta_prioritario",
        hover_data=["municipio", "perfil_territorial"],
        title="Relação entre judicialização do BPC e participação do BPC no território",
        labels={
            "taxa_judicializacao_bpc_pct": "Taxa de judicialização do BPC (%)",
            "participacao_bpc_pct": "Participação do BPC no total (%)",
        },
    )
    judicial_scatter.update_layout(paper_bgcolor="#0b1020", plot_bgcolor="#0b1020", font_color="#f4f7fb")
    st.plotly_chart(judicial_scatter, use_container_width=True)

    st.dataframe(
        comparison_df[
            [
                "municipio",
                "taxa_judicializacao_bpc_pct",
                "participacao_bpc_pct",
                "indice_pressao_assistencial",
                "alerta_prioritario",
            ]
        ].sort_values("indice_pressao_assistencial", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
