from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


def extract_cluster_keywords(texts, labels, top_n=5):
    """Extract top keywords for each cluster based on TF-IDF scores."""
    cluster_keywords = {}
    df = pd.DataFrame({"text": texts, "cluster": labels})
    for cluster_id in sorted(df["cluster"].unique()):
        cluster_texts = df[df["cluster"] == cluster_id]["text"]
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(cluster_texts)
        mean_tfidf = tfidf.mean(axis=0).A1
        top_indices = mean_tfidf.argsort()[::-1][:top_n]
        keywords = [vectorizer.get_feature_names_out()[i] for i in top_indices]
        cluster_keywords[cluster_id] = keywords
    return cluster_keywords
