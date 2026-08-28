def calculate_risk(
    database_verified=True,
    document_expired=False,
    tampering_detected=False
):
    """
    Calculate a simple risk score for the prototype.

    Score:
    0-20   = LOW
    21-50  = MEDIUM
    51-100 = HIGH
    """

    risk_score = 0
    reasons = []

    # Database verification
    if not database_verified:
        risk_score += 50
        reasons.append("Document not found in database")

    # Expiry check
    if document_expired:
        risk_score += 30
        reasons.append("Document has expired")

    # Tampering check
    if tampering_detected:
        risk_score += 40
        reasons.append("Possible document tampering detected")

    # Maximum score = 100
    risk_score = min(risk_score, 100)

    # Risk level
    if risk_score <= 20:
        risk_level = "LOW"
        decision = "DOCUMENT CLEARED"

    elif risk_score <= 50:
        risk_level = "MEDIUM"
        decision = "MANUAL REVIEW REQUIRED"

    else:
        risk_level = "HIGH"
        decision = "DOCUMENT FLAGGED"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "reasons": reasons
    }

if __name__ == "__main__":
    result = calculate_risk(
        database_verified=True,
        document_expired=False,
        tampering_detected=False
    )

    print("Risk Result:")
    print(result)