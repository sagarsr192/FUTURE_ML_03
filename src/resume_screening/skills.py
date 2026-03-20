from __future__ import annotations

import re
from typing import Iterable, Set

from .preprocess import clean_text


DEFAULT_SKILLS = {
    "python",
    "java",
    "sql",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "machine learning",
    "deep learning",
    "nlp",
    "scikit-learn",
    "pandas",
    "numpy",
    "data analysis",
    "api",
    "communication",
    "tensorflow",
    "pytorch",
    "etl",
    "streamlit",
}


def extract_skills(text: str, skill_catalog: Iterable[str] | None = None) -> Set[str]:
    """Extract skills by exact phrase matching on normalized text."""
    catalog = set(skill_catalog) if skill_catalog is not None else set(DEFAULT_SKILLS)
    normalized_text = clean_text(text)

    found: Set[str] = set()
    for skill in catalog:
        escaped_skill = re.escape(clean_text(skill))
        if re.search(rf"\b{escaped_skill}\b", normalized_text):
            found.add(skill)

    if "apis" in normalized_text and "api" in catalog:
        found.add("api")

    return found
