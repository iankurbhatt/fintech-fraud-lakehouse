import csv
import random
import os
from datetime import datetime, timedelta

def generate_fintech_transactions(output_path: str, num_records: int = 10000):
    """
    Generates realistic financial transaction logs with intentional fraud signals
    and PCI-sensitive fields (card numbers) to demonstrate data masking.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    users = [f"USR_{1000 + i}" for i in range(200)]
    merchant_categories = ["GROCERY", "RETAIL", "TRAVEL", "GAMBLING", "CRYPTO_EXCHANGE", "ELECTRONICS", "WIRE_TRANSFER"]
    countries = ["US", "IN", "GB", "CA", "SG", "NG", "RU"]
    device_types = ["MOBILE_IOS", "MOBILE_ANDROID", "WEB_CHROME", "ATM", "POS_TERMINAL"]

    start_time = datetime.now() - timedelta(days=7)
    
    headers = [
        "transaction_id", "timestamp", "user_id", "card_number", "amount", 
        "currency", "merchant_category", "merchant_id", "country", "device_type", "is_flagged_initially"
    ]
    
    print(f"Generating {num_records} realistic financial transactions -> {output_path}...")
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(num_records):
            txn_id = f"TXN_{1000000 + i}"
            txn_time = (start_time + timedelta(seconds=i * random.randint(30, 180))).isoformat()
            user_id = random.choice(users)
            
            # Simulated 16-digit card number (to show PCI-DSS masking in PySpark)
            card_num = f"{random.randint(4000, 4999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            category = random.choice(merchant_categories)
            country = random.choice(countries)
            device = random.choice(device_types)
            
            # Normal transactions vs Anomalous/Fraud spikes
            is_anomaly = random.random() < 0.05  # 5% anomalous
            if is_anomaly:
                amount = round(random.uniform(3500.0, 25000.0), 2)
                category = random.choice(["CRYPTO_EXCHANGE", "WIRE_TRANSFER", "GAMBLING"])
                initially_flagged = True
            else:
                amount = round(random.uniform(5.0, 600.0), 2)
                initially_flagged = False
                
            writer.writerow([
                txn_id, txn_time, user_id, card_num, amount, 
                "USD", category, f"MERCH_{random.randint(100, 999)}", country, device, initially_flagged
            ])
            
    print(f"Dataset successfully created at: {output_path}")

if __name__ == "__main__":
    default_target = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "transactions.csv"))
    generate_fintech_transactions(default_target, num_records=10000)
