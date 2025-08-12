from __future__ import annotations

"""Simple text classifier and question answering utility.

This module trains a Naive Bayes classifier on labelled text data and
uses it to classify new questions or cases.

Usage::

    python classification.py path/to/data.csv "새로운 질문"

The CSV file must contain ``text`` and ``label`` columns.
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
import argparse

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


@dataclass
class TextClassifier:
    """Wraps a TF-IDF vectorizer and Naive Bayes model."""

    vectorizer: TfidfVectorizer
    model: MultinomialNB

    def predict(self, text: str) -> str:
        """Return the predicted label for *text*."""
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]


def train_from_csv(csv_path: Path) -> TextClassifier:
    """Train a classifier from a CSV with ``text`` and ``label`` columns."""
    df = pd.read_csv(csv_path)
    texts: List[str] = df["text"].astype(str).tolist()
    labels: List[str] = df["label"].astype(str).tolist()

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)
    return TextClassifier(vectorizer, model)


def answer_question(classifier: TextClassifier, question: str) -> str:
    """Classify *question* and return a human readable response."""
    label = classifier.predict(question)
    return f"Predicted label: {label}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train classifier and answer a question")
    parser.add_argument("data", type=Path, help="CSV file with text and label columns")
    parser.add_argument("question", help="New question or case text")
    args = parser.parse_args()

    clf = train_from_csv(args.data)
    print(answer_question(clf, args.question))


if __name__ == "__main__":
    main()
