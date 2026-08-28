// ============================================================
// AI DOCUMENT SCREENING SYSTEM
// FINAL FRONTEND JAVASCRIPT
// ============================================================

console.log("========================================");
console.log("AI DOCUMENT SCREENING - SCRIPT LOADED");
console.log("========================================");


// ============================================================
// BACKEND URL
// ============================================================

const API_URL = "http://127.0.0.1:8000";


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const fileInput = document.getElementById("fileInput");
const chooseBtn = document.getElementById("chooseBtn");
const screenBtn = document.getElementById("screenBtn");

const fileName = document.getElementById("fileName");

const previewContainer =
    document.getElementById("previewContainer");

const previewImage =
    document.getElementById("previewImage");

const loading =
    document.getElementById("loading");

const errorBox =
    document.getElementById("errorBox");

const errorMessage =
    document.getElementById("errorMessage");

const resultCard =
    document.getElementById("resultCard");


// ============================================================
// CHECK ELEMENTS
// ============================================================

console.log("fileInput:", fileInput);
console.log("chooseBtn:", chooseBtn);
console.log("screenBtn:", screenBtn);
console.log("resultCard:", resultCard);

if (!fileInput) {
    console.error("ERROR: fileInput not found!");
}

if (!chooseBtn) {
    console.error("ERROR: chooseBtn not found!");
}

if (!screenBtn) {
    console.error("ERROR: screenBtn not found!");
}

if (!resultCard) {
    console.error("ERROR: resultCard not found!");
}


// ============================================================
// CHOOSE FILE BUTTON
// ============================================================

if (chooseBtn && fileInput) {

    chooseBtn.addEventListener("click", function (event) {

        event.preventDefault();

        console.log("CHOOSE FILE BUTTON CLICKED");

        fileInput.click();

    });

}


// ============================================================
// FILE SELECTED
// ============================================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        console.log("FILE INPUT CHANGED");

        const file = fileInput.files[0];

        if (!file) {

            console.log("No file selected.");

            return;

        }


        console.log(
            "Selected file:",
            file.name
        );

        console.log(
            "File type:",
            file.type
        );

        console.log(
            "File size:",
            file.size,
            "bytes"
        );


        // ----------------------------------------------------
        // DISPLAY FILE NAME
        // ----------------------------------------------------

        if (fileName) {

            fileName.textContent =
                file.name;

        }


        // ----------------------------------------------------
        // IMAGE PREVIEW
        // ----------------------------------------------------

        if (
            previewImage &&
            previewContainer
        ) {

            const imageURL =
                URL.createObjectURL(file);

            previewImage.src =
                imageURL;

            previewContainer.style.display =
                "block";

            console.log(
                "IMAGE PREVIEW DISPLAYED"
            );

        }

    });

}


// // ============================================================
// SCREEN DOCUMENT BUTTON
// ============================================================

if (screenBtn) {

    screenBtn.addEventListener("click", function (event) {

        event.preventDefault();

        console.log("========================================");
        console.log("SCREEN DOCUMENT BUTTON CLICKED!");
        console.log("========================================");

        screenDocument();

    });

}


// ============================================================
// SCREEN DOCUMENT
// ============================================================

async function screenDocument() {

    console.log("Starting document screening...");


    // ========================================================
    // CHECK FILE INPUT
    // ========================================================

    if (!fileInput) {

        showError(
            "File input was not found."
        );

        return;

    }


    // ========================================================
    // GET SELECTED FILE
    // ========================================================

    const file =
        fileInput.files[0];


    if (!file) {

        console.log(
            "NO FILE SELECTED"
        );

        showError(
            "Please select a document first."
        );

        return;

    }


    console.log(
        "File ready for screening:",
        file.name
    );


    // ========================================================
    // CHECK FILE TYPE
    // ========================================================

    const allowedTypes = [
        "image/jpeg",
        "image/png"
    ];


    if (!allowedTypes.includes(file.type)) {

        showError(
            "Please select a JPG, JPEG or PNG image."
        );

        return;

    }


    // ========================================================
    // DISABLE SCREEN BUTTON
    // ========================================================

    if (screenBtn) {

        screenBtn.disabled = true;

        screenBtn.textContent =
            "⏳ Analyzing...";

    }


    // ========================================================
    // SHOW LOADING
    // ========================================================

    if (loading) {

        loading.style.display =
            "block";

    }


    // ========================================================
    // HIDE OLD ERROR
    // ========================================================

    if (errorBox) {

        errorBox.style.display =
            "none";

    }


    // ========================================================
    // CREATE FORM DATA
    // ========================================================

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    // ========================================================
    // SEND IMAGE TO FASTAPI
    // ========================================================

    try {

        console.log(
            "Sending image to backend..."
        );

        console.log(
            "Backend URL:",
            API_URL + "/upload-document"
        );


        const response =
            await fetch(
                API_URL + "/upload-document",
                {
                    method: "POST",
                    body: formData
                }
            );


        // ====================================================
        // RESPONSE STATUS
        // ====================================================

        console.log(
            "Backend response status:",
            response.status
        );


        // ====================================================
        // GET RESPONSE
        // ====================================================

        let data;

        try {

            data =
                await response.json();

        }
        catch (jsonError) {

            throw new Error(
                "Backend did not return valid JSON."
            );

        }


        console.log("========================================");
        console.log("BACKEND RESPONSE:");
        console.log(data);
        console.log("========================================");


        // ====================================================
        // BACKEND ERROR
        // ====================================================

        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Backend returned an error."
            );

        }


        // ====================================================
        // SAVE RESULT
        // ====================================================

        try {

            sessionStorage.setItem(
                "screeningResult",
                JSON.stringify(data)
            );

            console.log(
                "Screening result saved."
            );

        }
        catch (storageError) {

            console.warn(
                "Could not save screening result:",
                storageError
            );

        }


        // ====================================================
        // DISPLAY RESULT
        // ====================================================

        displayResult(data);


    }
    catch (error) {

        console.error(
            "========================================"
        );

        console.error(
            "SCREENING ERROR:"
        );

        console.error(error);

        console.error(
            "========================================"
        );


        showError(
            "Could not process document: " +
            error.message
        );

    }
    finally {

        // ====================================================
        // HIDE LOADING
        // ====================================================

        if (loading) {

            loading.style.display =
                "none";

        }


        // ====================================================
        // ENABLE BUTTON
        // ====================================================

        if (screenBtn) {

            screenBtn.disabled =
                false;

            screenBtn.textContent =
                "🔍 Screen Document";

        }

    }

}


// ============================================================
// DISPLAY SCREENING RESULT
// ============================================================

function displayResult(data) {

    console.log(
        "DISPLAYING SCREENING RESULT..."
    );


    if (!resultCard) {

        console.error(
            "resultCard was not found!"
        );

        return;

    }


    // ========================================================
    // SAVE RESULT AGAIN
    // ========================================================

    try {

        sessionStorage.setItem(
            "screeningResult",
            JSON.stringify(data)
        );

    }
    catch (error) {

        console.warn(
            "Could not save result:",
            error
        );

    }


    // ========================================================
    // GET BACKEND DATA
    // ========================================================

    const documentData =
        data.document || {};

    const verification =
        data.verification || {};

    const expiry =
        data.expiry_check || {};

    const tampering =
        data.tampering_analysis || {};

    const risk =
        data.risk_assessment || {};


    // ========================================================
    // VALIDITY
    // ========================================================

    const isValid =
        verification.verified === true ||
        verification.status === "VALID";


    const validityText =
        isValid
            ? "VALID"
            : "INVALID";


    // ========================================================
    // RISK
    // ========================================================

    const riskLevel =
        risk.risk_level ||
        risk.level ||
        risk.status ||
        "UNKNOWN";


    const riskScore =
        risk.risk_score ??
        risk.score ??
        "-";


    // ========================================================
    // STATUS BADGE
    // ========================================================

    const statusBadge =
        document.getElementById(
            "statusBadge"
        );


    if (statusBadge) {

        statusBadge.textContent =
            validityText;

    }


    // ========================================================
    // VERIFICATION ICON
    // ========================================================

    const verificationIcon =
        document.getElementById(
            "verificationIcon"
        );


    if (verificationIcon) {

        verificationIcon.textContent =
            isValid
                ? "✅"
                : "⚠️";

    }


    // ========================================================
    // VERIFICATION STATUS
    // ========================================================

    const verificationStatus =
        document.getElementById(
            "verificationStatus"
        );


    if (verificationStatus) {

        verificationStatus.textContent =
            isValid
                ? "DOCUMENT VERIFIED"
                : "DOCUMENT NOT VERIFIED";

    }


    // ========================================================
    // VERIFICATION MESSAGE
    // ========================================================

    const verificationMessage =
        document.getElementById(
            "verificationMessage"
        );


    if (verificationMessage) {

        verificationMessage.textContent =
            verification.message ||
            "No verification message available.";

    }


    // ========================================================
    // DOCUMENT INFORMATION
    // ========================================================

    setValue(
        "documentNumber",
        documentData.document_number
    );

    setValue(
        "name",
        documentData.name
    );

    setValue(
        "gender",
        documentData.gender
    );

    setValue(
        "dob",
        documentData.date_of_birth
    );

    setValue(
        "nationality",
        documentData.nationality
    );

    setValue(
        "issueDate",
        documentData.date_of_issue
    );

    setValue(
        "expiryDate",
        documentData.date_of_expiry
    );


    // ========================================================
    // RISK LEVEL
    // ========================================================

    setValue(
        "riskLevel",
        riskLevel
    );


    // ========================================================
    // EXPIRY STATUS
    // ========================================================

    console.log(
        "Expiry result:",
        expiry
    );


    // ========================================================
    // OCR TEXT
    // ========================================================

    const ocrText =
        document.getElementById(
            "ocrText"
        );


    if (ocrText) {

        ocrText.textContent =
            data.detected_text ||
            data.ocr_text ||
            data.text ||
            "No OCR text returned.";

    }


    // ========================================================
    // SHOW RESULT CARD
    // ========================================================

    resultCard.style.display =
        "block";


    // ========================================================
    // SCROLL TO RESULT
    // ========================================================

    setTimeout(function () {

        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);


    console.log(
        "RESULT DISPLAYED SUCCESSFULLY"
    );

}


// ============================================================
// SET HTML VALUE
// ============================================================

function setValue(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {

        console.warn(
            "Element not found:",
            elementId
        );

        return;

    }


    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        element.textContent =
            "-";

    }
    else {

        element.textContent =
            value;

    }

}


// ============================================================
// SHOW ERROR
// ============================================================

function showError(message) {

    console.error(
        "ERROR:",
        message
    );


    if (errorBox) {

        errorBox.style.display =
            "block";

    }


    if (errorMessage) {

        errorMessage.textContent =
            message;

    }

}


// ============================================================
// RESTORE RESULT AFTER PAGE RELOAD
// ============================================================

window.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "PAGE LOADED"
        );


        const savedResult =
            sessionStorage.getItem(
                "screeningResult"
            );


        if (!savedResult) {

            console.log(
                "No previous screening result."
            );

            return;

        }


        try {

            const data =
                JSON.parse(
                    savedResult
                );


            console.log(
                "RESTORING PREVIOUS SCREENING RESULT..."
            );


            displayResult(data);

        }
        catch (error) {

            console.error(
                "Could not restore screening result:",
                error
            );


            sessionStorage.removeItem(
                "screeningResult"
            );

        }

    }
);


// ============================================================
// FINAL CONNECTION MESSAGE
// ============================================================

console.log("========================================");
console.log("ALL FRONTEND EVENT HANDLERS READY");
console.log("Choose File: READY");
console.log("Screen Document: READY");
console.log("Backend URL:", API_URL);
console.log("========================================");