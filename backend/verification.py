from database import get_connection


def verify_document(document_number):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM documents
    WHERE document_number = %s
    """

    cursor.execute(query, (document_number,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return {
            "verified": False,
            "status": "NOT FOUND",
            "message": "Document number not found in database"
        }

    if result["status"] == "BLACKLISTED":
        return {
            "verified": False,
            "status": "BLACKLISTED",
            "message": "Document is blacklisted"
        }

    return {
        "verified": True,
        "status": "VALID",
        "message": "Document verified successfully",
        "data": result
    }


if __name__ == "__main__":

    document_number = "1234567"

    result = verify_document(document_number)

    print("\nVerification Result:")
    print(result)