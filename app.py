import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
import shutil
from rapidfuzz import fuzz


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Alcohol Label Verification",
    page_icon="🔎",
    layout="centered"
)


# --------------------------------------------------
# TESSERACT SETUP
# --------------------------------------------------

# Automatically locate Tesseract in the deployment environment
tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def compare_text(expected, label_text):
    """
    Compare an expected text value against OCR output
    using fuzzy matching.
    """

    score = fuzz.partial_ratio(
        expected.upper(),
        label_text.upper()
    )

    if score >= 80:
        return "PASS", score

    return "REVIEW", score


def find_abv(text):
    """
    Search OCR output for an alcohol percentage.
    """

    match = re.search(
        r"(\d{1,2}(?:\.\d+)?)\s*%",
        text
    )

    if match:
        return float(match.group(1))

    return None


def find_net_contents(text):
    """
    Search OCR output for common volume formats.
    """

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(ML|L|CL)",
        text.upper()
    )

    if match:
        return f"{match.group(1)} {match.group(2)}"

    return None


def check_government_warning(text):
    """
    Check whether the government warning heading
    appears in the OCR output.
    """

    if "GOVERNMENT WARNING" in text.upper():
        return "PASS"

    return "REVIEW"


def display_status(status):
    """
    Display the overall result using Streamlit status messages.
    """

    if status == "PASS":
        st.success("PASS — All checked fields were verified.")

    elif status == "MISMATCH FOUND":
        st.error(
            "MISMATCH FOUND — At least one detected value "
            "conflicts with the application information."
        )

    else:
        st.warning(
            "MANUAL REVIEW REQUIRED — One or more fields "
            "could not be confidently verified."
        )


# --------------------------------------------------
# APP HEADER
# --------------------------------------------------

st.title("AI-Powered Alcohol Label Verification")

st.write(
    "This prototype compares information from an alcohol "
    "label image against expected application data."
)

st.info(
    "Enter the application information first, upload a clear "
    "label image, and then select **Verify Label**."
)


# --------------------------------------------------
# APPLICATION INFORMATION
# --------------------------------------------------

st.header("1. Application Information")

brand = st.text_input(
    "Brand Name",
    placeholder="Example: Tito's"
)

class_type = st.text_input(
    "Class / Type",
    placeholder="Example: Vodka"
)

abv = st.number_input(
    "Alcohol Content (ABV %)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=0.1
)

net_contents = st.text_input(
    "Net Contents",
    placeholder="Example: 750 ML"
)


# --------------------------------------------------
# IMAGE UPLOAD
# --------------------------------------------------

st.header("2. Upload Label Image")

uploaded_file = st.file_uploader(
    "Upload a clear PNG or JPG image of the alcohol label.",
    type=["png", "jpg", "jpeg"]
)


if uploaded_file is not None:

    img = Image.open(uploaded_file).convert("RGB")

    st.image(
        img,
        caption="Uploaded Label",
        width=400
    )


# --------------------------------------------------
# VERIFY BUTTON
# --------------------------------------------------

st.header("3. Verification")

verify_button = st.button(
    "Verify Label",
    type="primary",
    use_container_width=True
)


if verify_button:

    # ----------------------------------------------
    # INPUT VALIDATION
    # ----------------------------------------------

    missing_fields = []

    if not brand.strip():
        missing_fields.append("Brand Name")

    if not class_type.strip():
        missing_fields.append("Class / Type")

    if abv == 0:
        missing_fields.append("Alcohol Content")

    if not net_contents.strip():
        missing_fields.append("Net Contents")

    if uploaded_file is None:
        missing_fields.append("Label Image")


    if missing_fields:

        st.error(
            "Please complete the following before verification: "
            + ", ".join(missing_fields)
        )

    else:

        # ------------------------------------------
        # OCR
        # ------------------------------------------

        try:

            with st.spinner("Reading label and checking information..."):

                ocr_text = pytesseract.image_to_string(img)

        except Exception as error:

            st.error(
                "The label could not be processed. "
                "Please try another image."
            )

            with st.expander("Technical details"):
                st.write(error)

            st.stop()


        # ------------------------------------------
        # BRAND NAME
        # ------------------------------------------

        brand_result, brand_score = compare_text(
            brand,
            ocr_text
        )


        # ------------------------------------------
        # CLASS / TYPE
        # ------------------------------------------

        class_result, class_score = compare_text(
            class_type,
            ocr_text
        )


        # ------------------------------------------
        # ALCOHOL CONTENT
        # ------------------------------------------

        detected_abv = find_abv(
            ocr_text
        )

        if detected_abv is None:

            abv_result = "REVIEW"

        elif detected_abv == abv:

            abv_result = "PASS"

        else:

            abv_result = "MISMATCH"


        # ------------------------------------------
        # NET CONTENTS
        # ------------------------------------------

        detected_contents = find_net_contents(
            ocr_text
        )

        expected_contents = (
            net_contents
            .upper()
            .strip()
        )

        if detected_contents is None:

            contents_result = "REVIEW"

        elif detected_contents == expected_contents:

            contents_result = "PASS"

        else:

            contents_result = "MISMATCH"


        # ------------------------------------------
        # GOVERNMENT WARNING
        # ------------------------------------------

        warning_result = check_government_warning(
            ocr_text
        )


        # ------------------------------------------
        # RESULTS TABLE
        # ------------------------------------------

        results = pd.DataFrame([
            {
                "Field": "Brand Name",
                "Expected": brand,
                "Detected": (
                    f"Text similarity: {brand_score:.0f}%"
                ),
                "Result": brand_result
            },
            {
                "Field": "Class / Type",
                "Expected": class_type,
                "Detected": (
                    f"Text similarity: {class_score:.0f}%"
                ),
                "Result": class_result
            },
            {
                "Field": "Alcohol Content",
                "Expected": f"{abv:g}%",
                "Detected": (
                    f"{detected_abv:g}%"
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


        # ------------------------------------------
        # OVERALL RESULT
        # ------------------------------------------

        if "MISMATCH" in results["Result"].values:

            overall_result = "MISMATCH FOUND"

        elif "REVIEW" in results["Result"].values:

            overall_result = "MANUAL REVIEW REQUIRED"

        else:

            overall_result = "PASS"


        # ------------------------------------------
        # DISPLAY RESULTS
        # ------------------------------------------

        st.divider()

        st.header("Verification Results")

        display_status(
            overall_result
        )

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )


        # ------------------------------------------
        # RESULT EXPLANATION
        # ------------------------------------------

        st.subheader("Result Guide")

        st.write(
            "**PASS** — The field was successfully verified."
        )

        st.write(
            "**REVIEW** — The system could not confidently "
            "verify the field and a human should inspect it."
        )

        st.write(
            "**MISMATCH** — The system detected information "
            "that conflicts with the expected application value."
        )


        # ------------------------------------------
        # OCR OUTPUT
        # ------------------------------------------

        with st.expander("View Extracted OCR Text"):

            if ocr_text.strip():

                st.text(ocr_text)

            else:

                st.write(
                    "No readable text was detected in the image."
                )


        # ------------------------------------------
        # PROTOTYPE NOTE
        # ------------------------------------------

        st.caption(
            "This prototype assists with label review and does "
            "not replace final regulatory judgment."
        )
