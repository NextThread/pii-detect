import streamlit as st
from pypdf import PdfReader
from document_processor import redact_document

st.set_page_config(
    page_title="PII Redactor",
    layout="wide"
)


st.title("🔒 PII Detection and Redaction System")

st.write(
    "Upload a TXT or PDF document to automatically detect "
    "and redact Personally Identifiable Information."
)


uploaded_document = st.file_uploader(
    "Upload your document",
    type=["txt", "pdf"]
)


if uploaded_document:

    document_name = uploaded_document.name

    if document_name.lower().endswith(".txt"):

        document_text = uploaded_document.read().decode(
            "utf-8",
            errors="ignore"
        )

    elif document_name.lower().endswith(".pdf"):

        pdf_document = PdfReader(uploaded_document)

        document_text = ""

        for page in pdf_document.pages:

            page_text = page.extract_text()

            if page_text:
                document_text += page_text + "\n"


    if st.button("Detect and Redact PII"):

        cleaned_document, detected_items = redact_document(
    document_text
)

        st.success(
            f"Successfully detected "
            f"{len(detected_items)} PII items."
        )


        st.subheader("Detected PII")

        if detected_items:

            for item in detected_items:

                st.write(
                    f"**{item['type']}** → "
                    f"`{item['value']}`"
                )

        else:

            st.info("No PII detected.")



        st.subheader("Redacted Document")

        st.text_area(
            "Output",
            cleaned_document,
            height=300
        )


        st.download_button(
            label="Download Redacted TXT",
            data=cleaned_document,
            file_name="redacted_document.txt",
            mime="text/plain"
        )