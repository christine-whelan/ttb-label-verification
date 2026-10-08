import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
from rapidfuzz import fuzz


# -----------------------------
# Helper Functions
# -----------------------------

def compare_text(expected, label_text):
    score = fuzz.partial_ratio(
        expected.upper(),
        label_text.upper()
    )

    if score >= 80:
        return "PASS"
    else:
        return "REVIEW"


def find_abv(text):
    match = re.search(
        r"(\d{1,2}(?:\.\d+)?)\s*%",
        text
    )

    if match:
        return float(match.group(1))

    return None


def find_net_contents(text):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(ML|L|CL)",
        text.upper()
    )

    if match:
        return f"{match.group(1)} {match.group(2)}"

    return None


def check_government_warning(text):
    if "GOVERNMENT WARNING" in text.upper():
        return "PASS"
    else:
        return "REVIEW"


# -----------------------------
# App Layout
# -----------------------------

st.title("AI-Powered Alcohol Label Verification")

st.write(
    "Upload an alcohol label and enter the expected application "
    "information to compare the label against the application."
)

st.subheader("Application Information")

brand = st.text_input("Brand Name")

class_type = st.text_input("Class / Type")

abv = st.number_input(
    "Alcohol Content (ABV %)",
    min_value=0.0,
    max_value=100.0,
    step=0.1
)

net_contents = st.text_input(
    "Net Contents",
    placeholder="Example: 750 ML"
)

st.subheader("Upload Label Image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg"]
)


# -----------------------------
# Verification
# -----------------------------

if uploaded_file is not None:

    img = Image.open(uploaded_file)

    st.image(
        img,
        caption="Uploaded Label"
    )

    if st.button("Verify Label"):

        ocr_text = pytesseract.image_to_string(img)

        # Brand
        brand_result = compare_text(
            brand,
            ocr_text
        )

        # Class / Type
        class_result = compare_text(
            class_type,
            ocr_text
        )

        # Alcohol Content
        detected_abv = find_abv(ocr_text)

        if detected_abv is None:
            abv_result = "REVIEW"

        elif detected_abv == abv:
            abv_result = "PASS"

        else:
            abv_result = "MISMATCH"

        # Net Contents
        detected_contents = find_net_contents(
            ocr_text
        )

        expected_contents = net_contents.upper().strip()

        if detected_contents is None:
            contents_result = "REVIEW"

        elif detected_contents == expected_contents:
            contents_result = "PASS"

        else:
            contents_result = "MISMATCH"

        # Government Warning
        warning_result = check_government_warning(
            ocr_text
        )

        # Results
        results = pd.DataFrame([
            {
                "Field": "Brand Name",
                "Expected": brand,
                "Detected": "See OCR text",
                "Result": brand_result
            },
            {
                "Field": "Class / Type",
                "Expected": class_type,
                "Detected": "See OCR text",
                "Result": class_result
            },
            {
                "Field": "Alcohol Content",
                "Expected": f"{abv}%",
                "Detected": (
                    f"{detected_abv}%"
                    if detected_abv is not None
                    else "Not detected"
                ),
                "Result": abv_result
            },
            {
                "Field": "Net Contents",
                "Expected": expected_contents,
                "Detected": (
                    detected_contents
                    if detected_contents is not None
                    else "Not detected"
                ),
                "Result": contents_result
            },
            {
                "Field": "Government Warning",
                "Expected": "Present",
                "Detected": (
                    "Detected"
                    if warning_result == "PASS"
                    else "Not detected"
                ),
                "Result": warning_result
            }
        ])

        # Overall Result
        if "MISMATCH" in results["Result"].values:
            overall_result = "MISMATCH FOUND"

        elif "REVIEW" in results["Result"].values:
            overall_result = "MANUAL REVIEW REQUIRED"

        else:
            overall_result = "PASS"

        st.subheader("Overall Result")
        st.write(overall_result)

        st.subheader("Verification Results")
        st.dataframe(
            results,
            use_container_width=True
        )

        with st.expander("View Extracted OCR Text"):
            st.text(ocr_text)
