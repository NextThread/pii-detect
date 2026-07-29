import re
import spacy


nlp_model = spacy.load("en_core_web_sm")


def add_entity(items, kind, text, start_pos, end_pos, confidence=1.0):

    if not text.strip():
        return

    for item in items:

        old_start = item["start"]
        old_end = item["end"]

        if start_pos < old_end and end_pos > old_start:

            if item["confidence"] >= confidence:
                return

            items.remove(item)

    items.append({
        "type": kind,
        "value": text.strip(),
        "start": start_pos,
        "end": end_pos,
        "confidence": confidence
    })


def detect_emails(text, items):

    pattern = (
        r'\b[A-Za-z0-9._%+-]+'
        r'@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    )

    for match in re.finditer(pattern, text):

        add_entity(
            items,
            "EMAIL",
            match.group(),
            match.start(),
            match.end(),
            1.0
        )


def detect_phone_numbers(text, items):

    pattern = (
        r'(?<!\d)'
        r'(?:\+91[\s-]?)?'
        r'[6-9]\d{9}'
        r'(?!\d)'
    )

    for match in re.finditer(pattern, text):

        add_entity(
            items,
            "PHONE",
            match.group(),
            match.start(),
            match.end(),
            1.0
        )


def detect_aadhaar_numbers(text, items):

    pattern = (
        r'(?<!\d)'
        r'\d{4}[\s-]?\d{4}[\s-]?\d{4}'
        r'(?!\d)'
    )

    for match in re.finditer(pattern, text):

        add_entity(
            items,
            "AADHAAR",
            match.group(),
            match.start(),
            match.end(),
            1.0
        )


def detect_pan_numbers(text, items):

    pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'

    for match in re.finditer(pattern, text):

        add_entity(
            items,
            "PAN",
            match.group(),
            match.start(),
            match.end(),
            1.0
        )


def detect_addresses(text, items):

    context_pattern = (
        r'(?im)'
        r'(?:'
        r'(?:current\s+|permanent\s+|home\s+|billing\s+|'
        r'secondary\s+)?address'
        r'(?:\s+is|\s*:)'
        r'|'
        r'live\s+at'
        r'|'
        r'lived\s+at'
        r'|'
        r'residing\s+at'
        r')'
        r'\s*'
        r'([^\n]+)'
    )

    for match in re.finditer(
        context_pattern,
        text
    ):

        address = match.group(1).strip()

        start_pos = match.start(1)
        end_pos = match.end(1)

        while address.endswith((".", ",")):
            address = address[:-1].strip()
            end_pos -= 1

        if len(address) <= 5:
            continue

        if address.lower() in {
            "information",
            "details",
            "section",
            "data",
            "details information"
        }:
            continue

        add_entity(
            items,
            "ADDRESS",
            address,
            start_pos,
            end_pos,
            0.95
        )


    street_pattern = (
        r'\b'
        r'\d{1,5}'
        r'\s+'
        r'[A-Za-z0-9.\-]+'
        r'(?:\s+[A-Za-z0-9.\-]+)*'
        r'\s+'
        r'(?:'
        r'Road|Rd|'
        r'Street|St|'
        r'Lane|Ln|'
        r'Avenue|Ave|'
        r'Colony|'
        r'Nagar|'
        r'Marg'
        r')'
        r'(?:'
        r'\s*,\s*'
        r'[A-Za-z]+'
        r'(?:\s+[A-Za-z]+)*'
        r'){0,5}'
    )

    for match in re.finditer(
        street_pattern,
        text,
        flags=re.IGNORECASE
    ):

        address = match.group().strip()
        address = address.rstrip(".,")

        add_entity(
            items,
            "ADDRESS",
            address,
            match.start(),
            match.start() + len(address),
            0.90
        )


def detect_names(text, items):

    doc = nlp_model(text)

    for entity in doc.ents:

        if entity.label_ != "PERSON":
            continue

        name = entity.text.strip()

        start_pos = entity.start_char
        end_pos = entity.end_char

        before_name = text[
            max(0, start_pos - 60):start_pos
        ].lower()

        valid_context = (
            "my name is" in before_name
            or "name is" in before_name
            or "name:" in before_name
            or "name -" in before_name
            or "contact name:" in before_name
            or "customer name:" in before_name
            or "employee name:" in before_name
            or "emergency contact name:" in before_name
        )

        line_start = text.rfind(
            "\n",
            0,
            start_pos
        ) + 1

        before_line = text[
            line_start:start_pos
        ].strip()

        standalone = (
            before_line == ""
            or before_line.endswith(":")
        )

        if not valid_context and not standalone:
            continue

        add_entity(
            items,
            "NAME",
            name,
            start_pos,
            end_pos,
            0.95
        )


def detect_pii(text):

    results = []

    detect_emails(
        text,
        results
    )

    detect_phone_numbers(
        text,
        results
    )

    detect_aadhaar_numbers(
        text,
        results
    )

    detect_pan_numbers(
        text,
        results
    )

    detect_addresses(
        text,
        results
    )

    detect_names(
        text,
        results
    )

    results.sort(
        key=lambda item: item["start"]
    )

    return results