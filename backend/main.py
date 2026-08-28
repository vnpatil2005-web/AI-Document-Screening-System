from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pathlib import Path
import os
import uuid

from ocr import extract_text, extract_fields
from verification import verify_document
from expiry import check_expiry
from tampering import detect_tampering
from risk import calculate_risk


# ============================================================
# PROJECT PATHS
# ============================================================

# Project root:
# AI-Document-Screening/

BASE_DIR = Path(__file__).resolve().parent.parent

# Frontend folder:
# AI-Document-Screening/frontend/

FRONTEND_FOLDER = BASE_DIR / "frontend"

# Backend uploads folder:
# AI-Document-Screening/backend/uploads/

UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"

# Create uploads folder if it does not exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    description="SIH Prototype for AI-based document screening",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CHECK FRONTEND FOLDER
# ============================================================

print()
print("==========================================")
print("AI DOCUMENT SCREENING SYSTEM")
print("==========================================")

print("Project folder:", BASE_DIR)
print("Frontend folder:", FRONTEND_FOLDER)
print("Uploads folder:", UPLOAD_FOLDER)

if FRONTEND_FOLDER.exists():
    print("Frontend folder: FOUND")
else:
    print("Frontend folder: NOT FOUND")

if (FRONTEND_FOLDER / "index.html").exists():
    print("index.html: FOUND")
else:
    print("index.html: NOT FOUND")

if (FRONTEND_FOLDER / "script.js").exists():
    print("script.js: FOUND")
else:
    print("script.js: NOT FOUND")

if (FRONTEND_FOLDER / "style.css").exists():
    print("style.css: FOUND")
else:
    print("style.css: NOT FOUND")

print("==========================================")
print()


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
async def home():

    index_file = FRONTEND_FOLDER / "index.html"

    if not index_file.exists():

        return {
            "success": False,
            "message": "Frontend index.html not found",
            "frontend_folder": str(FRONTEND_FOLDER)
        }

    return FileResponse(
        index_file
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():

    return {
        "success": True,
        "status": "Running",
        "message": "AI Document Screening System is working"
    }


# ============================================================
# DOCUMENT SCREENING
# ============================================================

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...)
):

    print()
    print("==========================================")
    print("DOCUMENT SCREENING STARTED")
    print("==========================================")


    # ========================================================
    # 1. CHECK FILE
    # ========================================================

    if not file.filename:

        return {
            "success": False,
            "message": "No file selected"
        }


    print("Original File:", file.filename)


    # ========================================================
    # 2. CHECK FILE TYPE
    # ========================================================

    allowed_types = {
        "image/jpeg",
        "image/png"
    }

    if file.content_type not in allowed_types:

        return {
            "success": False,
            "message":
                "Unsupported file type. "
                "Please upload JPG, JPEG or PNG."
        }


    print("File Type:", file.content_type)


    # ========================================================
    # 3. SAVE FILE
    # ========================================================

    extension = Path(file.filename).suffix.lower()

    unique_filename = (
        str(uuid.uuid4()) + extension
    )

    filepath = UPLOAD_FOLDER / unique_filename


    try:

        content = await file.read()

        with open(filepath, "wb") as f:

            f.write(content)


    except Exception as e:

        print("FILE SAVE ERROR:", e)

        return {
            "success": False,
            "message": "Could not save uploaded document",
            "error": str(e)
        }


    print("File saved:", filepath)


    # ========================================================
    # 4. OCR
    # ========================================================

    try:

        detected_text = extract_text(
            str(filepath)
        )

    except Exception as e:

        print("OCR ERROR:", e)

        return {
            "success": False,
            "message": "OCR extraction failed",
            "error": str(e)
        }


    print()
    print("Detected Text:")
    print("------------------------------------------")

    for line in detected_text:

        print(line)


    # ========================================================
    # 5. EXTRACT INFORMATION
    # ========================================================

    try:

        fields = extract_fields(
            detected_text
        )

        if fields is None:
            fields = {}


    except Exception as e:

        print("FIELD EXTRACTION ERROR:", e)

        return {
            "success": False,
            "message": "Information extraction failed",
            "error": str(e)
        }


    print()
    print("Extracted Information:")
    print("------------------------------------------")

    for key, value in fields.items():

        print(
            f"{key}: {value}"
        )


    # ========================================================
    # 6. DOCUMENT NUMBER
    # ========================================================

    document_number = fields.get(
        "document_number"
    )

    print()
    print(
        "Document Number:",
        document_number
    )


    # ========================================================
    # 7. DATABASE VERIFICATION
    # ========================================================

    try:

        verification = verify_document(
            document_number
        )

        if verification is None:

            verification = {

                "verified": False,

                "status": "NOT_FOUND",

                "message":
                    "Document could not be verified",

                "data": {}

            }


    except Exception as e:

        print(
            "VERIFICATION ERROR:",
            e
        )

        verification = {

            "verified": False,

            "status": "ERROR",

            "message":
                "Database verification failed",

            "error":
                str(e),

            "data": {}

        }


    print()
    print("Verification Result:")
    print(verification)


    # ========================================================
    # 8. EXPIRY CHECK
    # ========================================================

    try:

        expiry_result = check_expiry(
            fields.get(
                "date_of_expiry"
            )
        )

        if expiry_result is None:

            expiry_result = {

                "expired": None,

                "status": "UNKNOWN",

                "message":
                    "Expiry status unavailable"

            }


    except Exception as e:

        print(
            "EXPIRY ERROR:",
            e
        )

        expiry_result = {

            "expired": None,

            "status": "ERROR",

            "message":
                "Expiry check failed",

            "error":
                str(e)

        }


    print()
    print("Expiry Result:")
    print(expiry_result)


    # ========================================================
    # 9. TAMPERING ANALYSIS
    # ========================================================

    try:

        tampering_result = detect_tampering(
            str(filepath)
        )

        if tampering_result is None:

            tampering_result = {

                "status": "UNKNOWN",

                "message":
                    "Tampering analysis unavailable"

            }


    except Exception as e:

        print(
            "TAMPERING ERROR:",
            e
        )

        tampering_result = {

            "status": "ERROR",

            "message":
                "Tampering analysis failed",

            "error":
                str(e)

        }


    print()
    print("Tampering Result:")
    print(tampering_result)


    # ========================================================
    # 10. RISK INPUTS
    # ========================================================

    database_verified = (
        verification.get(
            "verified",
            False
        ) is True
    )


    document_expired = (
        expiry_result.get(
            "expired",
            False
        ) is True
    )


    tampering_status = str(
        tampering_result.get(
            "status",
            "UNKNOWN"
        )
    ).upper()


    tampering_detected = (
        tampering_status not in [
            "PASS",
            "PASSED",
            "CLEAR"
        ]
    )


    print()
    print("Risk Inputs:")

    print(
        "Database Verified:",
        database_verified
    )

    print(
        "Document Expired:",
        document_expired
    )

    print(
        "Tampering Detected:",
        tampering_detected
    )


    # ========================================================
    # 11. RISK ASSESSMENT
    # ========================================================

    try:

        risk_result = calculate_risk(

            database_verified=
                database_verified,

            document_expired=
                document_expired,

            tampering_detected=
                tampering_detected

        )

        if risk_result is None:

            risk_result = {

                "risk_level":
                    "UNKNOWN",

                "risk_score":
                    0,

                "decision":
                    "UNAVAILABLE",

                "reasons": []

            }


    except Exception as e:

        print(
            "RISK ERROR:",
            e
        )

        risk_result = {

            "risk_level":
                "UNKNOWN",

            "risk_score":
                0,

            "decision":
                "UNAVAILABLE",

            "reasons": [],

            "error":
                str(e)

        }


    print()
    print("Risk Assessment:")
    print(risk_result)


    # ========================================================
    # 12. DOCUMENT DATA
    # ========================================================

    document_data = {

        "filename":
            file.filename,

        "document_number":
            fields.get(
                "document_number"
            ),

        "name":
            fields.get(
                "name"
            ),

        "gender":
            fields.get(
                "gender"
            ),

        "date_of_birth":
            fields.get(
                "date_of_birth"
            ),

        "nationality":
            fields.get(
                "nationality"
            ),

        "date_of_issue":
            fields.get(
                "date_of_issue"
            ),

        "date_of_expiry":
            fields.get(
                "date_of_expiry"
            )

    }


    # ========================================================
    # 13. FINAL RESPONSE
    # ========================================================

    final_response = {

        "success":
            True,

        "message":
            "Document processed successfully",

        "detected_text":
            detected_text,

        "document":
            document_data,

        "verification":
            verification,

        "expiry_check":
            expiry_result,

        "tampering_analysis":
            tampering_result,

        "risk_assessment":
            risk_result

    }


    # ========================================================
    # 14. PRINT FINAL RESULT
    # ========================================================

    print()
    print("==========================================")
    print("FINAL SCREENING RESULT")
    print("==========================================")

    print(final_response)

    print("==========================================")
    print("DOCUMENT SCREENING COMPLETED")
    print("==========================================")


    # ========================================================
    # 15. SEND RESULT TO FRONTEND
    # ========================================================

    return final_response


# ============================================================
# SERVE FRONTEND STATIC FILES
# ============================================================

# IMPORTANT:
# This must come AFTER the API routes above.

if FRONTEND_FOLDER.exists():

    app.mount(
        "/",
        StaticFiles(
            directory=str(FRONTEND_FOLDER),
            html=True
        ),
        name="frontend"
    )

    print("Frontend mounted successfully.")

else:

    print(
        "WARNING: Frontend folder does not exist."
    )