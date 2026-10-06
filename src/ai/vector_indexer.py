import os
import glob
import pandas as pd
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

COLLECTION_NAME = "fintech_aml_audit_logs"

def get_qdrant_client(host: str = "localhost", port: int = 6333) -> QdrantClient:
    """
    Initializes client connection to local Qdrant Vector Store.
    Falls back gracefully to in-memory mode if Docker is not active yet.
    """
    try:
        client = QdrantClient(host=host, port=port, timeout=3.0)
        client.get_collections()
        print("Connected to Qdrant Docker instance at localhost:6333")
        return client
    except Exception:
        print("Qdrant Docker not running. Falling back to local in-memory storage mode...")
        return QdrantClient(":memory:")

def index_gold_fraud_mart(gold_parquet_dir: str):
    """
    Reads PySpark Gold Layer Parquet files, generates local embeddings,
    and indexes them into the Vector Database with compliance metadata payloads.
    """
    print(f">>> Reading Gold Mart Parquet files from {gold_parquet_dir}...")
    
    # Read Parquet files into Pandas
    parquet_files = glob.glob(os.path.join(gold_parquet_dir, "**", "*.parquet"), recursive=True)
    if not parquet_files:
        print(f"No Parquet files found in {gold_parquet_dir}. Please run the PySpark pipeline first.")
        return
        
    df_gold = pd.concat([pd.read_parquet(f) for f in parquet_files], ignore_index=True)
    print(f">>> Loaded {len(df_gold)} high-risk transactions for AI Vector Indexing.")

    # Initialize SentenceTransformer (Free, local, lightweight model)
    print(">>> Loading local embedding model (all-MiniLM-L6-v2)...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    summaries = df_gold["audit_summary"].tolist()
    embeddings = embedder.encode(summaries, show_progress_bar=True, batch_size=64)

    # Initialize Qdrant Collection
    client = get_qdrant_client()
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=384,  # all-MiniLM-L6-v2 dimension
            distance=models.Distance.COSINE
        )
    )

    # Batch upsert points
    points = []
    for idx, row in df_gold.iterrows():
        payload = {
            "transaction_id": str(row["transaction_id"]),
            "user_id": str(row["user_id"]),
            "amount": float(row["amount"]),
            "merchant_category": str(row.get("merchant_category", "UNKNOWN")),
            "country": str(row["country"]),
            "risk_score": int(row["risk_score"]),
            "masked_card": str(row["masked_card_number"]),
            "audit_summary": str(row["audit_summary"])
        }
        
        points.append(
            models.PointStruct(
                id=idx,
                vector=embeddings[idx].tolist(),
                payload=payload
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f">>> Successfully indexed {len(points)} compliance audit vectors into Qdrant collection: '{COLLECTION_NAME}'")

def search_compliance_audit(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Searches compliance audit logs using semantic natural language.
    """
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = embedder.encode(query_text).tolist()
    
    client = get_qdrant_client()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    
    return [hit.payload for hit in results]

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    gold_dir = os.path.join(project_root, "data", "lakehouse", "gold", "aml_fraud_mart")
    index_gold_fraud_mart(gold_dir)
