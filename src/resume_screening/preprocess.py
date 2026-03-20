from __future__ import annotations

import re
from typing import List


def clean_text(text: str) -> str:
    """Normalize text while preserving characters useful for tech skills."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Simple tokenizer that works without external model downloads."""
    normalized = clean_text(text)
    return [tok for tok in normalized.split(" ") if tok]
