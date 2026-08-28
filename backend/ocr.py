import re
import easyocr


# ============================================================
# EASY OCR INITIALIZATION
# ============================================================

print("Loading EasyOCR...")

reader = easyocr.Reader(
    ['en'],
    gpu=False
)

print("EasyOCR loaded successfully.")


# ============================================================
# OCR TEXT EXTRACTION
# ============================================================

def extract_text(image_path):

    print()
    print("==========================================")
    print("STARTING OCR")
    print("==========================================")

    print("Image:", image_path)

    results = reader.readtext(
        str(image_path),
        detail=1
    )

    text_lines = []

    for result in results:

        if not result or len(result) < 2:
            continue

        text = str(result[1]).strip()

        if text:
            text_lines.append(text)

    print("OCR lines detected:", len(text_lines))

    print()
    print("OCR TEXT:")
    print("------------------------------------------")

    for line in text_lines:
        print(line)

    print("------------------------------------------")

    return text_lines


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_value(value):

    if value is None:
        return None

    value = str(value).strip()

    value = re.sub(
        r'\s+',
        ' ',
        value
    )

    return value if value else None


# ============================================================
# NORMALIZE OCR LINES
# ============================================================

def normalize_lines(text):

    if not text:
        return []

    # If OCR returns one string
    if isinstance(text, str):

        lines = text.splitlines()

    # If OCR returns list
    else:

        lines = text

    result = []

    for line in lines:

        line = clean_value(line)

        if line:
            result.append(line)

    return result


# ============================================================
# DATE DETECTION
# ============================================================

def is_date(value):

    if not value:
        return False

    value = clean_value(value)

    if not value:
        return False

    patterns = [

        # 01/01/1990
        r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$',

        # 01-JAN-1990
        r'^\d{1,2}[/-][A-Za-z]{3,9}[/-]\d{2,4}$',

        # 01 JAN 1990
        r'^\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}$',

        # JAN 01 1990
        r'^[A-Za-z]{3,9}\s+\d{1,2}\s+\d{2,4}$'
    ]

    for pattern in patterns:

        if re.match(
            pattern,
            value,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# DATE NORMALIZATION
# ============================================================

def normalize_date(value):

    if not value:
        return None

    value = clean_value(value)

    # Remove accidental spaces around separators
    value = re.sub(
        r'\s*[-/]\s*',
        '-',
        value
    )

    return value


# ============================================================
# LABEL CHECK
# ============================================================

def is_label(line):

    if not line:
        return False

    value = line.lower().strip()

    labels = [

        "name",
        "full name",
        "surname",
        "given name",

        "sex",
        "gender",

        "date of birth",
        "dob",
        "birth date",

        "nationality",
        "citizenship",

        "date of issue",
        "issue date",
        "date issued",
        "issued",

        "date of expiry",
        "expiry date",
        "expiration date",
        "expires",
        "valid until",

        "document number",
        "document no",
        "document no.",
        "passport number",
        "passport no",
        "passport no.",
        "id number",
        "id no",
        "id no."
    ]

    return value in labels


# ============================================================
# GET VALUE AFTER LABEL
# ============================================================

def find_value_after_label(
    lines,
    index,
    max_distance=5,
    ignored_labels=True
):

    end = min(
        index + max_distance + 1,
        len(lines)
    )

    for j in range(
        index + 1,
        end
    ):

        candidate = clean_value(
            lines[j]
        )

        if not candidate:
            continue

        if ignored_labels and is_label(candidate):
            continue

        return candidate

    return None


# ============================================================
# FIND DATE AFTER LABEL
# ============================================================

def find_date_after_label(
    lines,
    index,
    max_distance=10
):

    end = min(
        index + max_distance + 1,
        len(lines)
    )

    for j in range(
        index + 1,
        end
    ):

        candidate = clean_value(
            lines[j]
        )

        if not candidate:
            continue

        if is_date(candidate):

            return normalize_date(candidate)

    return None


# ============================================================
# FIND GENDER
# ============================================================

def find_gender(lines):

    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value not in [
            "sex",
            "gender"
        ]:
            continue

        # Look at next few OCR lines
        for j in range(
            i + 1,
            min(i + 6, len(lines))
        ):

            candidate = (
                lines[j]
                .strip()
                .upper()
            )

            if candidate in [
                "M",
                "F"
            ]:

                return candidate

            if candidate in [
                "MALE",
                "FEMALE"
            ]:

                if candidate == "MALE":
                    return "M"

                return "F"

    return None


# ============================================================
# FIND NAME
# ============================================================

def find_name(lines):

    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value not in [
            "name",
            "full name",
            "given name"
        ]:
            continue

        # Search next few lines.
        # Ignore other field labels.
        for j in range(
            i + 1,
            min(i + 7, len(lines))
        ):

            candidate = clean_value(
                lines[j]
            )

            if not candidate:
                continue

            candidate_lower = candidate.lower()

            if candidate_lower in [
                "sex",
                "gender",
                "current address",
                "date of birth",
                "dob",
                "nationality",
                "height",
                "eye color",
                "date of issue",
                "date of expiry"
            ]:
                continue

            # Ignore dates
            if is_date(candidate):
                continue

            # Ignore obvious address
            if re.search(
                r'\b(street|st|road|rd|avenue|ave|lane|ln|address|unit)\b',
                candidate,
                re.IGNORECASE
            ):
                continue

            # Ignore numbers
            if re.search(
                r'\d',
                candidate
            ):
                continue

            return candidate

    return None


# ============================================================
# FIND NATIONALITY
# ============================================================

def find_nationality(lines):

    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value not in [
            "nationality",
            "citizenship"
        ]:
            continue

        # Search several lines because OCR order
        # can be different from visual document order.
        for j in range(
            i + 1,
            min(i + 8, len(lines))
        ):

            candidate = clean_value(
                lines[j]
            )

            if not candidate:
                continue

            candidate_lower = candidate.lower()

            # Skip field labels
            if candidate_lower in [
                "height",
                "eye color",
                "sex",
                "gender",
                "date of birth",
                "dob",
                "date of issue",
                "date of expiry"
            ]:
                continue

            # Skip dates
            if is_date(candidate):
                continue

            # Skip measurements
            if re.search(
                r'\b\d+\s*(cm|mm|kg|lb)\b',
                candidate,
                re.IGNORECASE
            ):
                continue

            # Skip obvious address
            if re.search(
                r'\b(street|st|road|rd|avenue|ave|lane|ln|unit)\b',
                candidate,
                re.IGNORECASE
            ):
                continue

            # For the demo document:
            # MOCK CITY, MK -> skip
            # MOCKLAND -> accept
            if re.search(
                r'\b(city|town|district)\b',
                candidate,
                re.IGNORECASE
            ):
                continue

            # Nationality normally contains letters
            if re.search(
                r'[A-Za-z]',
                candidate
            ):
                return candidate

    return None


# ============================================================
# FIND DOCUMENT NUMBER
# ============================================================

def find_document_number(lines):

    # --------------------------------------------------------
    # 1. Try normal document number labels
    # --------------------------------------------------------

    document_labels = [

        "document number",
        "document no",
        "document no.",

        "passport number",
        "passport no",
        "passport no.",

        "id number",
        "id no",
        "id no."
    ]

    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value not in document_labels:
            continue

        candidate = find_value_after_label(
            lines,
            i,
            max_distance=5
        )

        if not candidate:
            continue

        candidate = re.sub(
            r'[^A-Za-z0-9]',
            '',
            candidate
        )

        if 5 <= len(candidate) <= 20:

            return candidate.upper()


    # --------------------------------------------------------
    # 2. Demo MRZ format
    # --------------------------------------------------------

    for line in lines:

        upper_line = line.upper()

        match = re.search(
            r'(\d{7})M',
            upper_line
        )

        if match:

            return match.group(1)


    # --------------------------------------------------------
    # 3. Common alphanumeric format
    # --------------------------------------------------------

    for line in lines:

        upper_line = line.upper()

        match = re.search(
            r'\b[A-Z]{1,3}\d{5,12}\b',
            upper_line
        )

        if match:

            return match.group(0)


    return None


# ============================================================
# FIND DATES USING DOCUMENT ORDER
# ============================================================

def find_all_dates(lines):

    dates = []

    for i, line in enumerate(lines):

        if is_date(line):

            dates.append({
                "index": i,
                "value": normalize_date(line)
            })

    return dates


# ============================================================
# FIND DATE OF BIRTH
# ============================================================

def find_date_of_birth(lines):

    # First try label-based search
    for i, line in enumerate(lines):

        if line.lower().strip() in [
            "date of birth",
            "dob",
            "birth date"
        ]:

            result = find_date_after_label(
                lines,
                i,
                max_distance=10
            )

            if result:
                return result


    return None


# ============================================================
# FIND ISSUE AND EXPIRY DATES
# ============================================================

def find_issue_and_expiry_dates(lines):

    issue_index = None
    expiry_index = None

    # Find labels
    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value in [
            "date of issue",
            "issue date",
            "date issued"
        ]:

            issue_index = i

        elif value in [
            "date of expiry",
            "expiry date",
            "expiration date",
            "expires",
            "valid until"
        ]:

            expiry_index = i


    # --------------------------------------------------------
    # Try normal label based extraction
    # --------------------------------------------------------

    issue_date = None
    expiry_date = None

    if issue_index is not None:

        issue_date = find_date_after_label(
            lines,
            issue_index,
            max_distance=10
        )


    if expiry_index is not None:

        expiry_date = find_date_after_label(
            lines,
            expiry_index,
            max_distance=10
        )


    # --------------------------------------------------------
    # If both labels appear before both dates,
    # assign dates according to their order.
    #
    # Example:
    #
    # Date of Issue
    # Date of Expiry
    # 20-MAR-2023
    # 19-MAR-2033
    # --------------------------------------------------------

    if (
        issue_index is not None
        and expiry_index is not None
        and issue_index < expiry_index
    ):

        dates = find_all_dates(lines)

        dates_after_labels = [
            d for d in dates
            if d["index"] > issue_index
        ]

        if len(dates_after_labels) >= 2:

            issue_date = (
                dates_after_labels[0]["value"]
            )

            expiry_date = (
                dates_after_labels[1]["value"]
            )


    return issue_date, expiry_date


# ============================================================
# MAIN FIELD EXTRACTION
# ============================================================

def extract_fields(text):

    fields = {

        "name": None,

        "gender": None,

        "date_of_birth": None,

        "nationality": None,

        "date_of_issue": None,

        "date_of_expiry": None,

        "document_number": None
    }


    # ========================================================
    # NORMALIZE INPUT
    # ========================================================

    lines = normalize_lines(text)

    if not lines:

        return fields


    print()
    print("==========================================")
    print("EXTRACTING DOCUMENT FIELDS")
    print("==========================================")


    # ========================================================
    # NAME
    # ========================================================

    fields["name"] = find_name(
        lines
    )


    # ========================================================
    # GENDER
    # ========================================================

    fields["gender"] = find_gender(
        lines
    )


    # ========================================================
    # DATE OF BIRTH
    # ========================================================

    fields["date_of_birth"] = find_date_of_birth(
        lines
    )


    # ========================================================
    # NATIONALITY
    # ========================================================

    fields["nationality"] = find_nationality(
        lines
    )


    # ========================================================
    # ISSUE + EXPIRY
    # ========================================================

    (
        fields["date_of_issue"],
        fields["date_of_expiry"]
    ) = find_issue_and_expiry_dates(
        lines
    )


    # ========================================================
    # DOCUMENT NUMBER
    # ========================================================

    fields["document_number"] = find_document_number(
        lines
    )


    # ========================================================
    # PRINT RESULT
    # ========================================================

    print()
    print("EXTRACTED FIELDS")
    print("------------------------------------------")

    for key, value in fields.items():

        print(
            f"{key}: {value}"
        )

    print("------------------------------------------")


    return fields


# ============================================================
# TEST OCR DIRECTLY
# ============================================================

if __name__ == "__main__":

    image_path = "uploads/test.jpg"

    print()
    print("==========================================")
    print("      DOCUMENT OCR TEST")
    print("==========================================")

    try:

        detected_text = extract_text(
            image_path
        )

        fields = extract_fields(
            detected_text
        )

        print()
        print("==========================================")
        print("OCR TEST COMPLETE")
        print("==========================================")

    except Exception as e:

        print()
        print("OCR ERROR:")
        print(e)

        raise