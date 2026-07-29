from pii_detector import detect_pii


def redact_document(document):

    detected_items = detect_pii(document)

    entities_to_replace = sorted(
        detected_items,
        key=lambda item: item["start"],
        reverse=True
    )

    cleaned_document = document

    for item in entities_to_replace:

        entity_start = item["start"]
        entity_end = item["end"]
        entity_category = item["type"]

        mask = f"[REDACTED_{entity_category}]"

        cleaned_document = (
            cleaned_document[:entity_start]
            + mask
            + cleaned_document[entity_end:]
        )

    return cleaned_document, detected_items