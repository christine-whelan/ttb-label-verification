# AI-Powered Alcohol Label Verification Prototype

## Overview

This project is a simple AI-assisted prototype designed to help review alcohol beverage labels.

The system uses OCR to extract text from an alcohol label image and compares key label information against expected application data.

The goal is to help a reviewer quickly identify:

- Matching information
- Potential mismatches
- Fields that may require manual review

This prototype is intended to assist compliance reviewers and does not replace human regulatory judgment.

---

## Project Purpose

Alcohol label review can involve repetitive comparisons between an application and the actual submitted label.

This prototype demonstrates how OCR and simple Python-based validation can help automate part of that process.

The system checks several common label fields and assigns one of three results:

- `PASS` — the field was successfully verified
- `REVIEW` — the system could not confidently verify the field
- `MISMATCH` — the detected value conflicts with the expected application value

A manual review is still required whenever the system cannot confidently verify a field.

---

## Fields Checked

The prototype currently checks:

- Brand name
- Class / type
- Alcohol content (ABV)
- Net contents
- Government warning presence

---

## How It Works

1. An alcohol label image is loaded into the notebook.
2. Tesseract OCR extracts readable text from the image.
3. Expected application information is stored in Python.
4. Text-based fields, such as brand name and class/type, are compared using fuzzy text matching.
5. Structured values such as alcohol percentage and net contents are extracted using regular expressions.
6. The government warning is checked for presence.
7. Each field receives a result of `PASS`, `REVIEW`, or `MISMATCH`.
8. The results are displayed in a pandas DataFrame.
9. An overall verification result is generated.

---

## Technologies Used

- Python
- Jupyter Notebook
- Tesseract OCR
- pytesseract
- Pillow
- pandas
- RapidFuzz
- Regular expressions

---

## Project Files

- `ttb_label_verification.ipynb` — main prototype notebook
- `app.py` — deployable web application for testing the label verification prototype
- `sample_label.png` — sample alcohol label used for testing
- `requirements.txt` — Python package requirements
- `README.md` — project documentation

---

## Setup Instructions

### 1. Install Python

Python 3.x is required.

### 2. Install Tesseract OCR

Tesseract OCR must be installed separately from the Python packages.

For Windows, this prototype uses the default installation path:

~~~text
C:\Program Files\Tesseract-OCR\tesseract.exe
~~~

If Tesseract is installed in another location, update the path in the notebook.

### 3. Install Python Requirements

Install the required Python packages using:

~~~bash
pip install -r requirements.txt
~~~

### 4. Open the Notebook

Open:

~~~text
ttb_label_verification.ipynb
~~~

in Jupyter Notebook.

Run the cells in order from top to bottom.


## Application Data

For this prototype, application information is entered directly into a Python dictionary.

Example:

```python
application = {
    "brand": "Tito's",
    "class_type": "Vodka",
    "abv": 40,
    "net_contents": "750 ML"
}
```

This represents information that a reviewer would already have from the application and wants to verify against the submitted label.

## Verification Logic

### Brand Name and Class / Type

Text fields are compared using fuzzy text matching. This is helpful because OCR may not reproduce decorative label text perfectly.

If the system finds a strong match, the result is `PASS`.

If the text cannot be confidently verified, the result is `REVIEW`.

### Alcohol Content

The system uses a regular expression to find a percentage value in the extracted OCR text.

For example: `40%`

If the detected percentage matches the expected application value, the result is `PASS`.

If the system detects a different percentage, the result is `MISMATCH`.

If no percentage can be detected, the result is `REVIEW`.

### Net Contents

The system searches the extracted text for common volume formats such as:

- `750 ML`
- `1 L`
- `50 CL`

If the detected value matches the expected application value, the field passes.

If the system cannot detect the value, the field is sent for manual review.

### Government Warning

The prototype checks whether the extracted label text contains `GOVERNMENT WARNING`.

If detected, the field passes.

If the warning cannot be detected, the field is marked for manual review.

The prototype does not currently evaluate all government warning typography or formatting requirements.

## Overall Result

The system produces an overall result based on the field-level results.

Possible outputs include:

- `PASS`
- `MANUAL REVIEW REQUIRED`
- `MISMATCH FOUND`

A mismatch takes priority because it means the system detected information that conflicts with the expected application data.

A review result means the system could not confidently verify one or more fields.

## Design Decisions

The prototype was intentionally designed to remain simple and easy to understand.

Tesseract OCR is used as an existing tool for extracting text from label images rather than building a custom OCR model.

Python is then used for the verification logic.

Fuzzy matching is used for text fields because decorative fonts and OCR errors may cause small differences in extracted text.

Regular expressions are used for structured values such as ABV and net contents because these values follow predictable numeric patterns.

The system uses a `REVIEW` status when it cannot confidently verify a field rather than automatically treating an unreadable field as a compliance failure.

This keeps the human reviewer involved in uncertain cases.

## Assumptions

- Application information is already available to the reviewer.
- The prototype does not directly integrate with the existing COLA system.
- Label images should be reasonably clear and readable.
- OCR output may not perfectly reproduce decorative or stylized text.
- A `REVIEW` result means a human reviewer should inspect the field.
- The prototype is intended as a proof of concept rather than a production compliance system.

## Limitations

- OCR accuracy may decrease with decorative fonts, glare, curved bottles, poor lighting, or low-resolution images.
- The prototype checks only a limited number of common label fields.
- Government warning verification currently checks for the presence of the warning heading rather than all formatting requirements.
- Brand recognition may be less accurate when the brand uses highly stylized lettering.
- The prototype currently processes one label image at a time.
- The system does not make final regulatory decisions.
- The system does not currently integrate with external government systems or databases.

## Future Improvements

Potential future enhancements include:

- Batch processing for multiple label applications
- Support for multiple images per label
- Improved image preprocessing
- More detailed government warning validation
- Additional beverage-specific compliance rules
- Improved handling of angled or low-quality label images
- Integration with application systems such as COLA

## Prototype Status

The current version demonstrates the core verification workflow:

```text
Label Image
    ↓
OCR Text Extraction
    ↓
Application Comparison
    ↓
PASS / REVIEW / MISMATCH
    ↓
Overall Review Result
```

The prototype is designed to demonstrate how AI-assisted text extraction and simple validation rules could reduce repetitive manual label checks while still keeping a human reviewer involved in uncertain cases.
