# ranker.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def rank_resumes(resume_texts, job_description, top_k=None):
    """
    Compares resumes with job description using TF-IDF + cosine similarity.
    Returns list of dicts with index and score.
    """
    processed = [txt if txt.strip() else " " for txt in resume_texts]
    jd = job_description if job_description.strip() else " "
    docs = processed + [jd]

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs)
    jd_vec = tfidf[-1]
    resume_vecs = tfidf[:-1]
    sims = cosine_similarity(jd_vec, resume_vecs)[0]
    order = np.argsort(sims)[::-1]
    results = [{'index': int(i), 'score': float(sims[i])} for i in order]
    if top_k:
        return results[:top_k]
    return results
