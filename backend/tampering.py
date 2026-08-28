from PIL import Image
import os


def detect_tampering(image_path):

    result = {
        "status": "PASS",
        "risk": "LOW",
        "message": "No obvious image-level tampering indicators detected",
        "checks": []
    }

    # Check 1: File exists
    if not os.path.exists(image_path):

        return {
            "status": "ERROR",
            "risk": "HIGH",
            "message": "Document image not found",
            "checks": []
        }

    try:

        # Open image
        image = Image.open(image_path)

        # --------------------------------
        # Check image format
        # --------------------------------

        result["checks"].append({
            "check": "Image format",
            "result": image.format
        })


        # --------------------------------
        # Check image dimensions
        # --------------------------------

        width, height = image.size

        result["checks"].append({
            "check": "Image dimensions",
            "result": f"{width} x {height}"
        })


        # --------------------------------
        # Check image size
        # --------------------------------

        file_size = os.path.getsize(image_path)

        result["checks"].append({
            "check": "File size",
            "result": f"{file_size / 1024:.2f} KB"
        })


        # --------------------------------
        # Basic quality check
        # --------------------------------

        if width < 500 or height < 300:

            result["status"] = "REVIEW"

            result["risk"] = "MEDIUM"

            result["message"] = (
                "Image resolution is low; "
                "manual review recommended"
            )


        # --------------------------------
        # EXIF metadata check
        # --------------------------------

        exif_data = image.getexif()

        if exif_data:

            result["checks"].append({
                "check": "Metadata",
                "result": "Metadata present"
            })

        else:

            result["checks"].append({
                "check": "Metadata",
                "result": "No EXIF metadata"
            })


        image.close()

        return result


    except Exception as error:

        return {
            "status": "ERROR",
            "risk": "HIGH",
            "message": f"Could not analyze image: {error}",
            "checks": []
        }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    image_path = "uploads/test.jpg"

    print("\n==============================")
    print("     TAMPERING ANALYSIS")
    print("==============================")

    result = detect_tampering(image_path)

    print("\nStatus:", result["status"])
    print("Risk:", result["risk"])
    print("Message:", result["message"])

    print("\nChecks:")

    for check in result["checks"]:

        print(
            f"{check['check']}: "
            f"{check['result']}"
        )

    print("\n==============================")