from datetime import datetime


def check_expiry(expiry_date):

    if not expiry_date:

        return {
            "expired": None,
            "status": "UNKNOWN",
            "message": "Expiry date could not be extracted"
        }

    try:

        expiry = datetime.strptime(
            expiry_date,
            "%d-%b-%Y"
        )

        today = datetime.now()

        if expiry < today:

            return {
                "expired": True,
                "status": "EXPIRED",
                "message": "Document has expired"
            }

        else:

            return {
                "expired": False,
                "status": "VALID",
                "message": "Document is not expired"
            }

    except ValueError:

        return {
            "expired": None,
            "status": "INVALID DATE",
            "message": "Expiry date format could not be verified"
        }


if __name__ == "__main__":

    result = check_expiry("19-MAR-2033")

    print("\nExpiry Check:")
    print(result)