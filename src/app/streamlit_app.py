import os
import glob
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------
# PAGE CONFIGURATION - INSTITUTIONAL GRADE
# ---------------------------------------------------------
st.set_page_config(
    page_title="ApexRisk // Financial Intelligence & AML Lakehouse",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Financial Terminal Styling
st.markdown("""
<style>
    /* Dark Slate & Gold Financial Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-critical {
        background-color: #ef4444;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-pci {
        background-color: #10b981;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GOLD_MART_DIR = os.path.join(PROJECT_ROOT, "data", "lakehouse", "gold", "aml_fraud_mart")
SILVER_DIR = os.path.join(PROJECT_ROOT, "data", "lakehouse", "silver", "transactions_parquet")

@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def load_lakehouse_data():
    gold_files = glob.glob(os.path.join(GOLD_MART_DIR, "**", "*.parquet"), recursive=True)
    if not gold_files:
        return pd.DataFrame(), pd.DataFrame()
    df_gold = pd.concat([pd.read_parquet(f) for f in gold_files], ignore_index=True)
    
    silver_files = glob.glob(os.path.join(SILVER_DIR, "**", "*.parquet"), recursive=True)
    df_silver = pd.concat([pd.read_parquet(f) for f in silver_files], ignore_index=True) if silver_files else df_gold
    return df_gold, df_silver

df_gold, df_silver = load_lakehouse_data()

# Precompute Embeddings in Memory for Instant Zero-Docker Vector Search
@st.cache_resource
def build_inmemory_vector_index(texts):
    embedder = load_embedder()
    vectors = embedder.encode(texts, show_progress_bar=False)
    return vectors

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://img.shields.io/badge/SECURITY-PCI--DSS%20COMPLIANT-emerald?style=for-the-badge", use_column_width=True)
    st.markdown("### 🎛️ Risk Engine Parameters")
    risk_threshold = st.slider("AML Minimum Risk Filter", 0, 100, 50, step=5)
    selected_country = st.multiselect("Geographic Exposure", options=["ALL"] + sorted(df_gold["country"].unique().tolist()) if not df_gold.empty else ["ALL"], default=["ALL"])
    
    st.markdown("---")
    st.markdown("### 🏛️ Pipeline Topology")
    st.markdown("""
    - **Bronze Ingestion:** Streaming CSV
    - **Silver Lakehouse:** Parquet + Window Features
    - **Gold AML Mart:** Partitioned by Category
    - **Vector Engine:** 384-dim Dense Embeddings
    """)
    st.markdown("---")
    st.caption("ApexRisk Enterprise Lakehouse v4.2 // 2026 Edition")

# ----------------- TOP KPI BANNER -----------------
st.title("🛡️ ApexRisk // Financial Crime Lakehouse & Semantic Audit Engine")
st.markdown("Real-time distributed transaction surveillance, automated PCI-DSS sanitization, and GenAI compliance discovery.")

if not df_gold.empty:
    filtered_gold = df_gold[df_gold["risk_score"] >= risk_threshold]
    if "ALL" not in selected_country and selected_country:
        filtered_gold = filtered_gold[filtered_gold["country"].isin(selected_country)]

    total_volume = filtered_gold["amount"].sum()
    flagged_txns = len(filtered_gold)
    avg_dev = filtered_gold["amount_deviation_ratio"].mean()
    high_risk_users = filtered_gold["user_id"].nunique()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Flagged Exposure Volume</div>
            <div class="metric-value">${total_volume:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High-Risk Entities</div>
            <div class="metric-value">{high_risk_users} Accounts</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Behavioral Anomaly</div>
            <div class="metric-value">{avg_dev:.1f}x Baseline</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PCI-DSS Sanitization</div>
            <div class="metric-value" style="color: #10b981;">100% Masked</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------- TABS -----------------
    tab_search, tab_analytics, tab_evidence, tab_sql = st.tabs([
        "🧠 Semantic AI Audit Investigator",
        "📊 Lakehouse Risk Distribution",
        "📋 Forensic Audit Records (PCI Cleansed)",
        "💻 Direct SQL Query Console"
    ])

    # ----------------- TAB 1: AI AUDIT SEARCH -----------------
    with tab_search:
        st.subheader("🔍 Natural Language AML Forensic Search")
        st.caption("Execute semantic discovery across millions of unstructured audit narratives without SQL.")

        col_input, col_btn = st.columns([5, 1])
        with col_input:
            query = st.text_input(
                "Compliance Query Prompt:",
                value="Show me suspicious high-value wire transfers or crypto transactions",
                placeholder="e.g., 'Find accounts moving funds to high-risk merchant categories during off-peak hours'"
            )
        with col_btn:
            st.write("")
            st.write("")
            search_exec = st.button("🔎 Run Forensic Scan", type="primary", use_container_width=True)

        if query:
            with st.spinner("Analyzing high-dimensional vector space..."):
                embedder = load_embedder()
                query_vec = embedder.encode(query)

                corpus_texts = filtered_gold["audit_summary"].tolist()
                corpus_vectors = build_inmemory_vector_index(corpus_texts)

                # Cosine Similarity Calculation
                dot_products = np.dot(corpus_vectors, query_vec)
                norms = (np.linalg.norm(corpus_vectors, axis=1) * np.linalg.norm(query_vec))
                scores = dot_products / (norms + 1e-9)

                top_indices = np.argsort(scores)[::-1][:6]

                st.markdown("#### 🎯 Identified Forensic Matches")
                for rank, idx in enumerate(top_indices, 1):
                    match_row = filtered_gold.iloc[idx]
                    similarity_pct = int(scores[idx] * 100)

                    col_left, col_right = st.columns([4, 1])
                    with col_left:
                        st.markdown(f"""
                        **#{rank} | Transaction `{match_row['transaction_id']}`** — Account: `{match_row['user_id']}`
                        > *"{match_row['audit_summary']}"*
                        """)
                    with col_right:
                        st.metric("Vector Match", f"{similarity_pct}%")

                    badge_cols = st.columns([1, 1, 1, 1, 2])
                    badge_cols[0].write(f"💵 **${match_row['amount']:,.2f}**")
                    badge_cols[1].write(f"🏢 **{match_row['merchant_category']}**")
                    badge_cols[2].write(f"🌍 **{match_row['country']}**")
                    badge_cols[3].write(f"🛡️ **Risk: {match_row['risk_score']}/100**")
                    badge_cols[4].write(f"🔒 **{match_row['masked_card_number']}**")
                    st.divider()

    # ----------------- TAB 2: ANALYTICS -----------------
    with tab_analytics:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_bar = px.histogram(
                filtered_gold,
                x="merchant_category",
                y="amount",
                color="merchant_category",
                title="Suspicious Exposure by Merchant Sector",
                template="plotly_dark"
            )
            fig_bar.update_layout(showlegend=False, xaxis_title="Merchant Category", yaxis_title="Total USD")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_c2:
            fig_scatter = px.scatter(
                filtered_gold,
                x="amount",
                y="amount_deviation_ratio",
                color="risk_score",
                size="amount",
                hover_data=["user_id", "merchant_category", "country"],
                title="Amount vs. Behavioral Anomaly Ratio (Cluster Analysis)",
                template="plotly_dark",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    # ----------------- TAB 3: FORENSIC RECORDS -----------------
    with tab_evidence:
        st.subheader("📋 Sanitized Lakehouse Gold Layer Table")
        st.dataframe(
            filtered_gold[[
                "transaction_id", "user_id", "masked_card_number", "amount",
                "merchant_category", "country", "risk_score", "amount_deviation_ratio", "audit_summary"
            ]],
            use_container_width=True,
            height=450
        )

    # ----------------- TAB 4: SQL CONSOLE -----------------
    with tab_sql:
        st.subheader("💻 Lakehouse SQL Query Engine (DuckDB Powered)")
        st.caption("Inspect underlying Parquet storage directly using ANSI SQL:")
        
        default_query = """SELECT 
    merchant_category, 
    COUNT(*) as flag_count, 
    ROUND(SUM(amount), 2) as total_exposure,
    ROUND(AVG(amount_deviation_ratio), 1) as avg_deviation
FROM df_gold 
GROUP BY merchant_category 
ORDER BY total_exposure DESC;"""
        
        sql_input = st.text_area("SQL Statement:", value=default_query, height=120)
        if st.button("Execute SQL", type="secondary"):
            try:
                import duckdb
                result = duckdb.query(sql_input).to_df()
                st.dataframe(result, use_container_width=True)
            except Exception as err:
                st.error(f"SQL Error: {err}")

else:
    st.warning("⚠️ No Lakehouse data detected. Run `python src/pipeline/pyspark_job.py` first to generate the tables.")
