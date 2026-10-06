import os
from dagster import asset, Definitions, AssetExecutionContext
from src.pipeline.data_generator import generate_fintech_transactions
from src.pipeline.pyspark_job import run_lakehouse_pipeline
from src.ai.vector_indexer import index_gold_fraud_mart

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "transactions.csv")
LAKEHOUSE_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse")
GOLD_MART_PATH = os.path.join(LAKEHOUSE_PATH, "gold", "aml_fraud_mart")

@asset(group_name="fintech_ingestion", description="Synthetic real-time transaction logs with PCI sensitive data")
def raw_transactions_data(context: AssetExecutionContext) -> str:
    context.log.info("Generating realistic transaction logs...")
    generate_fintech_transactions(RAW_PATH, num_records=5000)
    context.log.info(f"Generated raw transactions at {RAW_PATH}")
    return RAW_PATH

@asset(
    deps=[raw_transactions_data],
    group_name="lakehouse_processing",
    description="PySpark Medallion Lakehouse pipeline: PCI-DSS masking, rolling features, and Gold AML Mart"
)
def lakehouse_silver_and_gold_marts(context: AssetExecutionContext) -> str:
    context.log.info("Triggering distributed PySpark transformations...")
    run_lakehouse_pipeline(RAW_PATH, LAKEHOUSE_PATH)
    context.log.info("PySpark pipeline completed successfully.")
    return GOLD_MART_PATH

@asset(
    deps=[lakehouse_silver_and_gold_marts],
    group_name="ai_vector_store",
    description="Embeds Gold AML Fraud logs using SentenceTransformers and indexes into Qdrant"
)
def qdrant_vector_store(context: AssetExecutionContext):
    context.log.info("Generating embeddings and upserting into Qdrant Vector Store...")
    index_gold_fraud_mart(GOLD_MART_PATH)
    context.log.info("Compliance Audit Vectors successfully materialized in Qdrant!")

defs = Definitions(
    assets=[
        raw_transactions_data,
        lakehouse_silver_and_gold_marts,
        qdrant_vector_store
    ]
)
