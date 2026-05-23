# AI Resume Ranker

An AI-inspired resume ranking system that compares uploaded resumes against a job description using keyword matching and text preprocessing techniques.

## Features
- Upload multiple resumes
- Add custom job descriptions
- Automatic resume ranking
- Resume relevance scoring
- Text preprocessing using NLP
- Simple HR workflow simulation

## Tech Stack
- Python
- Streamlit
- NLTK
- PDF/Text Extraction

## Project Structure

```bash
AI-Resume-Ranker/
│
├── app.py
├── requirements.txt
├── resume_ranker/
│   ├── extractor.py
│   ├── preprocess.py
│   └── ranker.py
│
├── sample_data/
└── .streamlit/
```

## How It Works
1. Upload resumes
2. Enter job description
3. System preprocesses text
4. Keywords are matched
5. Resumes are ranked based on relevance

## Future Improvements
- Semantic similarity matching
- Embedding-based ranking
- Better scoring system
- Recruiter dashboard
- Resume feedback generation

## Live Demo
https://ai-resume-ranker-acoolproject.streamlit.app/