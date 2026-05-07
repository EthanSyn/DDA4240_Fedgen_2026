"""
Data utilities for federated learning: text vectorization and dataset preparation.
Converts raw JSON data from the FedGen data backend into feature matrices.
"""
import re
import math
import numpy as np
from collections import Counter
from typing import List, Tuple, Dict, Any


class SimpleTfidfVectorizer:
    """Lightweight TF-IDF vectorizer using pure Python + NumPy (no sklearn needed)."""

    def __init__(self, max_features: int = 500, min_df: int = 1):
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_ = {}
        self.idf_ = None

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'[a-z]{2,}', text)
        # Remove very common English stop words
        stop = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
                'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
                'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
                'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
                'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
                'which', 'go', 'me', 'when', 'make', 'can', 'like', 'no', 'just',
                'him', 'know', 'take', 'into', 'your', 'some', 'could', 'them',
                'than', 'other', 'been', 'its', 'over', 'also', 'are', 'was', 'is',
                'has', 'had', 'were', 'did', 'more', 'how', 'may', 'most'}
        return [t for t in tokens if t not in stop]

    def fit(self, texts: List[str]) -> 'SimpleTfidfVectorizer':
        n_docs = len(texts)
        doc_freq = Counter()
        all_tf = []

        for text in texts:
            tokens = self._tokenize(text)
            tf = Counter(tokens)
            all_tf.append(tf)
            for token in set(tokens):
                doc_freq[token] += 1

        # Select top features by document frequency (filtered by min_df)
        candidates = [(word, df) for word, df in doc_freq.items() if df >= self.min_df]
        candidates.sort(key=lambda x: -x[1])
        top_words = [w for w, _ in candidates[:self.max_features]]
        self.vocabulary_ = {w: i for i, w in enumerate(top_words)}

        # Compute IDF
        self.idf_ = np.zeros(len(self.vocabulary_))
        for word, idx in self.vocabulary_.items():
            df = doc_freq[word]
            self.idf_[idx] = math.log((1 + n_docs) / (1 + df)) + 1

        return self

    def transform(self, texts: List[str]) -> np.ndarray:
        n = len(texts)
        m = len(self.vocabulary_)
        X = np.zeros((n, m))
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            tf = Counter(tokens)
            total = sum(tf.values()) or 1
            for word, count in tf.items():
                if word in self.vocabulary_:
                    j = self.vocabulary_[word]
                    X[i, j] = (count / total) * self.idf_[j]
        # L2 normalize rows
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        X = X / norms
        return X

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        self.fit(texts)
        return self.transform(texts)


def extract_texts_and_labels(legal_data: Dict[str, Any],
                              news_data: Dict[str, Any]) -> Tuple[List[str], np.ndarray]:
    """
    Extract text content and binary labels from FedGen data backend responses.

    Returns:
        texts: list of text strings
        labels: numpy array, 0 = legal, 1 = news
    """
    texts = []
    labels = []

    # Legal documents (label=0)
    docs = legal_data.get("documents", legal_data.get("cases", []))
    for doc in docs:
        content = doc.get("content", "") or doc.get("text", "") or doc.get("title", "")
        if content.strip():
            texts.append(content)
            labels.append(0)

    # News articles (label=1)
    articles = news_data.get("articles", [])
    for art in articles:
        content = art.get("content", "") or art.get("headline", "")
        if content.strip():
            texts.append(content)
            labels.append(1)

    return texts, np.array(labels)


def split_by_node(texts: List[str], labels: np.ndarray
                   ) -> Tuple[Dict[str, Tuple[List[str], np.ndarray]],
                              Tuple[List[str], np.ndarray]]:
    """
    Split data into node-local partitions (Non-IID) and a test set.

    Node A gets legal data, Node B gets news data.
    20% of each is held out for a shared test set.

    Returns:
        partitions: {"node_a": (texts, labels), "node_b": (texts, labels)}
        test_set: (texts, labels)
    """
    legal_idx = np.where(labels == 0)[0]
    news_idx = np.where(labels == 1)[0]

    np.random.seed(42)
    np.random.shuffle(legal_idx)
    np.random.shuffle(news_idx)

    # 80/20 split
    legal_split = max(1, int(0.8 * len(legal_idx)))
    news_split = max(1, int(0.8 * len(news_idx)))

    train_legal = legal_idx[:legal_split]
    test_legal = legal_idx[legal_split:]
    train_news = news_idx[:news_split]
    test_news = news_idx[news_split:]

    partitions = {
        "node_a": ([texts[i] for i in train_legal], labels[train_legal]),
        "node_b": ([texts[i] for i in train_news], labels[train_news]),
    }

    test_idx = np.concatenate([test_legal, test_news])
    test_set = ([texts[i] for i in test_idx], labels[test_idx])

    return partitions, test_set
