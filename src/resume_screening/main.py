from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from resume_screening.ranking import rank_candidates
else:
    from .ranking import rank_candidates


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_resumes(resumes_dir: Path) -> Dict[str, str]:
    resumes: Dict[str, str] = {}
    for file_path in sorted(resumes_dir.glob("*.txt")):
        resumes[file_path.stem] = _read_text_file(file_path)
    return resumes


def parse_skills(skills: str) -> List[str]:
    return [item.strip().lower() for item in skills.split(",") if item.strip()]


def to_csv(path: Path, rows: List[dict]) -> None:
    headers = [
        "candidate_id",
        "final_score",
        "text_similarity",
        "skill_match",
        "matched_skills",
        "missing_skills",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume screening and candidate ranking")
    parser.add_argument("--job-file", required=True, type=Path, help="Path to job description text file")
    parser.add_argument("--resumes-dir", required=True, type=Path, help="Directory containing .txt resumes")
    parser.add_argument(
        "--skills",
        required=True,
        type=str,
        help="Comma-separated required skills, e.g. 'python,sql,aws,docker'",
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional output CSV file")
    args = parser.parse_args()

    job_description = _read_text_file(args.job_file)
    resumes = load_resumes(args.resumes_dir)
    required_skills = parse_skills(args.skills)

    results = rank_candidates(
        job_description=job_description,
        resumes=resumes,
        required_skills=required_skills,
    )

    rows: List[dict] = []
    for index, result in enumerate(results, start=1):
        row = {
            "candidate_id": result.candidate_id,
            "final_score": result.final_score,
            "text_similarity": result.text_similarity,
            "skill_match": result.skill_match,
            "matched_skills": ", ".join(result.matched_skills),
            "missing_skills": ", ".join(result.missing_skills),
        }
        rows.append(row)

        print(
            f"{index}. {result.candidate_id} | "
            f"Final={result.final_score:.4f} | "
            f"Similarity={result.text_similarity:.4f} | "
            f"SkillMatch={result.skill_match:.4f}"
        )
        print(f"   Matched: {row['matched_skills'] or 'None'}")
        print(f"   Missing: {row['missing_skills'] or 'None'}")

    if args.output is not None:
        to_csv(args.output, rows)
        print(f"\nSaved results to: {args.output}")


if __name__ == "__main__":
    main()
