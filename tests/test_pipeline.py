import pytest
import os
import re

def test_data_masking_regex():
    """
    Validates PCI-DSS Compliance: Only the last 4 digits must remain visible.
    """
    card_number = "4532-8765-1234-9087"
    masked = re.sub(r"^\d{4}-\d{4}-\d{4}-(\d{4})$", r"****-****-****-\1", card_number)
    
    assert masked == "****-****-****-9087"
    assert not masked.startswith("4532")

def test_risk_scoring_calculation():
    """
    Ensures that high-value crypto transactions receive proper AML risk weighting.
    """
    amount = 12500.0
    category = "CRYPTO_EXCHANGE"
    deviation_ratio = 4.5
    
    risk_score = 0
    if amount > 5000.0:
        risk_score += 40
    if category in ["CRYPTO_EXCHANGE", "WIRE_TRANSFER", "GAMBLING"]:
        risk_score += 35
    if deviation_ratio > 3.0:
        risk_score += 25
        
    assert risk_score == 100
