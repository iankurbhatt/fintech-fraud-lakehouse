# 💳 Fintech Fraud Intelligence Lakehouse & Compliance AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-orange.svg)](https://spark.apache.org/)
[![Orchestration](https://img.shields.io/badge/Dagster-SDAs-purple.svg)](https://dagster.io/)
[![Vector DB](https://img.shields.io/badge/Qdrant-Vector%20Store-red.svg)](https://qdrant.tech/)
[![Compliance](https://img.shields.io/badge/PCI--DSS-Masked-success.svg)](#)

An enterprise-grade, end-to-end **Data Engineering & AI Lakehouse** built for fintech transaction monitoring, AML (Anti-Money Laundering) risk detection, and natural language compliance auditing.

---

## 🏛️ System Architecture

```text
               [ Raw Fintech Transactions (CSV/JSON) ]
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │    PySpark Lakehouse Pipeline     │
               ├───────────────────────────────────┤
               │ • PCI-DSS Sensitive Data Masking  │
               │ • 7-Day Rolling Velocity Windows  │
               │ • AML Risk Deviation Scoring      │
               └───────────────────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
          [ Silver Layer ]              [ Gold AML Mart ]
          Cleaned Parquet               High-Risk Flagged
          (MinIO / S3)                  (Partitioned by Merchant)
                                               │
                                               ▼
                                  ┌─────────────────────────┐
                                  │   AI Vector Indexer     │
                                  ├─────────────────────────┤
                                  │ • SentenceTransformers  │
                                  │ • Dense Vector Payloads │
                                  │ • Qdrant Vector DB      │
                                  └─────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │  Streamlit Investigator Portal  │
                              ├─────────────────────────────────┤
                              │ • Real-time Risk Analytics      │
                              │ • Natural Language Audit Search │
                              └─────────────────────────────────┘
```

---

## 🛠️ The Free Local Tech Stack

| Category | Enterprise Production | Local $0 Free Equivalent |
| :--- | :--- | :--- |
| **Data Lake Storage** | AWS S3 / Databricks Delta | **MinIO** (Local S3 clone) |
| **Big Data Compute** | Databricks / EMR | **PySpark** (Local Distributed Mode) |
| **Orchestration** | Apache Airflow | **Dagster** (Software-Defined Assets) |
| **Vector Search Engine** | Pinecone / Milvus | **Qdrant** (Local Docker Container) |
| **Embedding Models** | OpenAI text-embedding-3 | **HuggingFace `all-MiniLM-L6-v2`** |
| **Analytics & UI** | Tableau / Retool | **Streamlit & Plotly** |

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Local Cloud Infrastructure (Docker)
Starts local S3 (**MinIO**) and Vector DB (**Qdrant**):
```bash
docker compose up -d
```
* **MinIO S3 Console:** `http://localhost:9001` (User: `minioadmin` / Pass: `minioadminpassword`)
* **Qdrant Vector Dashboard:** `http://localhost:6333/dashboard`

---

### 3. Run the Lakehouse Pipeline

**Option A: Run Directly via Python**
```bash
# 1. Generate 10,000 synthetic financial transactions
python src/pipeline/data_generator.py

# 2. Run PySpark Medallion Lakehouse transformations
python src/pipeline/pyspark_job.py

# 3. Index high-risk transactions into Qdrant Vector DB
python src/ai/vector_indexer.py
```

**Option B: Run via Dagster (Interactive Web UI)**
```bash
dagster dev -f src/pipeline/dagster_pipeline.py
```
Open `http://localhost:3000` to view the asset dependency graph and trigger pipeline runs.

---

### 4. Launch the Compliance & Fraud Dashboard
```bash
streamlit run src/app/streamlit_app.py
```
Open `http://localhost:8501` to query the audit assistant and explore transaction metrics.

---

## 🛡️ Key Engineering Highlights for Hiring Managers
1. **PCI-DSS Compliance:** Sensitive credit card numbers are masked (`****-****-****-1234`) during the PySpark Bronze-to-Silver transition.
2. **Window Aggregations:** Computes rolling average transaction amounts per user using PySpark Window specifications to catch behavioral anomalies.
3. **Partition Pruning:** Gold layers are partitioned by `merchant_category` for optimized analytical reads.
4. **Vector Retrieval (RAG Foundation):** Converts raw financial audits into vector spaces to allow non-technical compliance officers to query fraud patterns using plain English.
