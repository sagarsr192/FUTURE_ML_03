from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocess import clean_text
from .skills import extract_skills


@dataclass
class CandidateScore:
    candidate_id: str
    final_score: float
    text_similarity: float
    skill_match: float
    matched_skills: List[str]
    missing_skills: List[str]


def _similarity(job_description: str, resume_text: str) -> float:
    docs = [clean_text(job_description), clean_text(resume_text)]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(docs)
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


def rank_candidates(
    job_description: str,
    resumes: Dict[str, str],
    required_skills: Iterable[str],
    similarity_weight: float = 0.7,
    skill_weight: float = 0.3,
) -> List[CandidateScore]:
    """Rank candidates using text similarity and required-skill match."""
    required = set(required_skills)
    ranked: List[CandidateScore] = []

    for candidate_id, resume_text in resumes.items():
        similarity = _similarity(job_description, resume_text)
        candidate_skills = extract_skills(resume_text, required)

        matched = sorted(candidate_skills.intersection(required))
        missing = sorted(required.difference(candidate_skills))
        skill_match = len(matched) / len(required) if required else 0.0

        final_score = (similarity_weight * similarity) + (skill_weight * skill_match)
        ranked.append(
            CandidateScore(
                candidate_id=candidate_id,
                final_score=round(final_score, 4),
                text_similarity=round(similarity, 4),
                skill_match=round(skill_match, 4),
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    ranked.sort(key=lambda item: item.final_score, reverse=True)
    return ranked
