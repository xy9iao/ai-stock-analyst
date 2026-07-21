"""Untrusted-content sanitization + demarcation (Phase 15, OWASP LLM01).

Sanitization defends the demarcation, not the model: it strips only the
structure that could break content out of its box (marker forgeries, role-tag
lookalikes). Persuasive text stays inside the box, where the system prompt's
external-content policy handles it. Pure functions; applied at prompt-assembly
time, never at ingest — stored chunks stay verbatim, and the rules can evolve
without re-ingesting the corpus.
"""

import re

UNTRUSTED_OPEN = "<<<EXTERNAL-CONTENT"
UNTRUSTED_CLOSE = "END-EXTERNAL-CONTENT>>>"

_ANGLE_RUNS = re.compile(r"<<<|>>>")
_MARKER_WORDS = re.compile(r"END-EXTERNAL-CONTENT|EXTERNAL-CONTENT")
_ROLE_TAG = re.compile(r"(?im)^([ \t>]*)(system|assistant|user|tool|human)[ \t]*:")
_BRACKET_TAGS = re.compile(r"(?i)\[/?(?:INST|SYS)\]")


def sanitize(text: str) -> str:
    """Remove escape vectors; preserve meaning. Never rejects, only defangs."""
    text = _ANGLE_RUNS.sub("", text)
    text = _MARKER_WORDS.sub("", text)
    text = _BRACKET_TAGS.sub("", text)
    return _ROLE_TAG.sub(r"\1\2 -", text)


def demarcate(text: str) -> str:
    """Sanitize and wrap: the ONLY close marker is the real one at the end."""
    return f"{UNTRUSTED_OPEN}\n{sanitize(text)}\n{UNTRUSTED_CLOSE}"
