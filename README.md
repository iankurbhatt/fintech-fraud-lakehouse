# ApexRisk: Distributed Financial Surveillance & AML Compliance Lakehouse

ApexRisk is a distributed data lakehouse and semantic audit retrieval engine designed for real-time transaction surveillance, anti-money laundering (AML) detection, and automated regulatory compliance reporting. 

The system processes streaming and batch financial transaction logs, applies PCI-DSS Level 1 sanitization, computes rolling behavioral velocity metrics, materializes partitioned parquet lakehouse tables, and indexes audit narratives into a dense vector space for sub-second semantic forensic search.

---

## Architecture Overview

```
                                [ Ingestion Layer ]
                        Raw Transaction Feeds (CSV / JSON)
                                         │
                                         ▼
                        [ Medallion Processing Engine ]
                    PySpark / PyArrow Distributed Pipeline
                         ├── Schema Validation & Casting
                         ├── PCI-DSS Card Number Masking
                         └── 7-Day Rolling Window Analytics
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
         [ Silver Lakehouse ]                        [ Gold AML Mart ]
       Sanitized Transactions                   High-Risk Flagged Records
     (Parquet / S3 Object Store)             Partitioned by Merchant Category
                                                               │
                                                               ▼
                                                  [ AI Vector Indexer ]
                                              Dense Embeddings (384-dim)
                                              Qdrant Vector Database
                                                               │
                                                               ▼
                                              [ Forensic Surveillance UI ]
                                            Streamlit Compliance Terminal
                                            ANSI SQL Console (DuckDB)
```

---

## Core Capabilities

### 1. Regulatory Sanitization (PCI-DSS Compliance)
Primary Account Numbers (PANs) are intercepted and masked at the ingestion boundary using regex transformations:
```
Original: 4532-8921-4432-9012  ──►  Sanitized: ****-****-****-9012
```
Unmasked cardholder data is never persisted to downstream analytical tables or vector stores.

### 2. Behavioral Anomaly & Velocity Scoring
Static rule thresholds produce high false-positive rates. The pipeline calculates user-level baseline spending profiles using sliding window aggregations across transaction histories:
* **Deviation Ratio:** `current_amount / rolling_7d_average_amount`
* **Weighted Risk Calculation:** Combines transaction magnitude, high-risk merchant categories (Crypto Exchanges, Wire Transfers, Gambling), and historical deviation multipliers.
* Transactions exceeding risk thresholds are automatically tagged and routed to the **Gold AML Fraud Mart**.

### 3. Semantic Forensic Retrieval
Compliance analysts and auditors can query unstructured audit narratives using natural language. Transaction audit summaries are embedded into a 384-dimensional dense vector space (`all-MiniLM-L6-v2`) and indexed via cosine similarity in Qdrant, enabling discovery of cross-border fraud patterns without requiring complex SQL joins.

### 4. Hybrid Lakehouse Querying
The surveillance terminal exposes both semantic vector search and an embedded ANSI SQL engine (powered by DuckDB), allowing ad-hoc analytical queries directly against underlying parquet files.

---

## Repository Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated test suite and linting
├── src/
│   ├── pipeline/
│   │   ├── data_generator.py    # Synthetic financial transaction telemetry
│   │   ├── pyspark_job.py       # Lakehouse ingestion, masking & window features
│   │   └── dagster_pipeline.py  # Software-defined asset orchestration
│   ├── ai/
│   │   └── vector_indexer.py    # Vector generation and Qdrant ingestion
│   └── app/
│       └── streamlit_app.py     # Forensic surveillance terminal & dashboard
├── tests/
│   └── test_pipeline.py         # Unit tests for masking and risk algorithms
├── docker-compose.yml           # Local infrastructure (MinIO S3 & Qdrant)
├── requirements.txt             # Project dependencies
└── README.md
```

---

## Deployment & Setup

### Prerequisites
* Python 3.10+
* Docker & Docker Compose (optional, for MinIO and persistent vector store)

### 1. Environment Installation
```bash
# Clone the repository
git clone https://github.com/your-username/fintech-fraud-lakehouse.git
cd fintech-fraud-lakehouse

# Install required dependencies
pip install -r requirements.txt
```

### 2. Infrastructure Services (Optional)
To launch local S3 object storage (MinIO) and the persistent Qdrant vector database:
```bash
docker compose up -d
```
* **MinIO Console:** `http://localhost:9001` (`minioadmin` / `minioadminpassword`)
* **Qdrant Dashboard:** `http://localhost:6333/dashboard`

*(Note: The application includes an in-memory vector fallback if Docker is not running).*

### 3. Pipeline Execution

```bash
# Step 1: Generate transaction dataset
python src/pipeline/data_generator.py

# Step 2: Execute Lakehouse processing (Bronze -> Silver -> Gold)
python src/pipeline/pyspark_job.py

# Step 3: Materialize vector embeddings into Qdrant
python src/ai/vector_indexer.py
```

### 4. Surveillance Terminal
Launch the compliance analyst dashboard:
```bash
streamlit run src/app/streamlit_app.py
```
Access the application at `http://localhost:8501`.

---

## Testing & Quality Assurance

Run the test suite:
```bash
pytest tests/ -v
```

CI workflows are configured under `.github/workflows/ci.yml` to validate code formatting and test coverage on all pull requests and pushes to `main`.
