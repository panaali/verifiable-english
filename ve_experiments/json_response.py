"""Formatting tolerance shared by experiment response parsers."""


def strip_json_fence(text):
    """Strip one enclosing Markdown fence; callers still enforce their schema."""
    if isinstance(text, str):
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = stripped.split("\n", 1)[1] if "\n" in stripped else ""
            if stripped.rstrip().endswith("```"):
                stripped = stripped.rstrip()[:-3]
        text = stripped.strip()
    return text
