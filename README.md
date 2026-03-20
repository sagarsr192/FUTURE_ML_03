# Resume / Candidate Screening System

https://futureml03-gjpdsazwejhxcz3seujyt9.streamlit.app/



This project builds an NLP-based resume screening system that:

- cleans and parses resume text
- extracts skills from resumes and job descriptions
- calculates resume-to-role fit scores
- ranks candidates from best to weakest fit
- highlights missing required skills

It is designed to satisfy the Future Interns Machine Learning Task 3 (2026) requirements.

## Live Application

- Streamlit Cloud URL: `Add your deployed URL here`
- Example format: `https://your-app-name.streamlit.app`

After deployment, replace the placeholder with your real live link.

## Project Structure

```
.
|-- app.py
|-- requirements.txt
|-- data/
|   |-- job_descriptions/
|   |   `-- software_engineer.txt
|   `-- resumes/
|       |-- candidate_1.txt
|       |-- candidate_2.txt
|       |-- candidate_3.txt
|       |-- candidate_4.txt
|       `-- candidate_5.txt
`-- src/
    `-- resume_screening/
        |-- __init__.py
        |-- main.py
        |-- preprocess.py
        |-- ranking.py
        `-- skills.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Optional NLP model for richer extraction:

```bash
python -m spacy download en_core_web_sm
```

## Run CLI Ranking

```bash
python src/resume_screening/main.py \
  --job-file data/job_descriptions/software_engineer.txt \
  --resumes-dir data/resumes \
  --skills "python,sql,aws,docker,kubernetes,ml,communication"
```

Optional output CSV:

```bash
python src/resume_screening/main.py \
  --job-file data/job_descriptions/software_engineer.txt \
  --resumes-dir data/resumes \
  --skills "python,sql,aws,docker,kubernetes,ml,communication" \
  --output ranked_candidates.csv
```

## Run Streamlit App

```bash
python -m streamlit run app.py
```

The app supports:

- default sample data from this repository
- custom pasted job description
- uploaded resume `.txt` and `.pdf` files

## Deploy To Streamlit Community Cloud

1. Open `https://share.streamlit.io/` and sign in with your GitHub account.
2. Click `Create app`.
3. Select repository: `sagarsr192/FUTURE_ML_03`.
4. Select branch: `main`.
5. Set main file path: `app.py`.
6. Click `Deploy`.
7. Copy the generated app URL and update the `Live Application` section above.

## Scoring Logic

Each candidate score is a weighted blend:

- Text Similarity Score: cosine similarity between job description and resume TF-IDF vectors
- Skill Match Score: matched required skills divided by total required skills

Final score:

`final_score = 0.7 * text_similarity + 0.3 * skill_match`

You can adjust weights in `src/resume_screening/ranking.py`.

## Deliverable Fit

This implementation includes all required features:

- resume text cleaning and parsing
- skill extraction and matching
- job description parsing
- resume scoring and ranking
- skill-gap identification
- explainable output for recruiters and non-technical users
