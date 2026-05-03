from bertopic import BERTopic

from .labeling import label_topics
from app.analysis.tokenizer import tokenize_data

from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import CountVectorizer

import pandas as pd

from .utils import postprocess_heatmap_matrix

def get_topic_model(sentence_records, n_clusters=None):
    sentences = [r["sentence"] for r in sentence_records]
    vectorizer_model = CountVectorizer(stop_words="english")
    if n_clusters:
        cluster_model = AgglomerativeClustering(n_clusters=n_clusters)
        topic_model = BERTopic(language="english", hdbscan_model=cluster_model, 
                               top_n_words=30, vectorizer_model=vectorizer_model,
                               calculate_probabilities=True)
    else:
        topic_model = BERTopic(language="english", top_n_words=30, 
                               vectorizer_model=vectorizer_model, calculate_probabilities=True)
    topics, probs = topic_model.fit_transform(sentences)
    return topic_model, topics, probs

def topic_modeling_pipeline(data, with_labels=False, n_clusters=None):
    sentence_records = tokenize_data(data)
    topic_model, topics, probs = get_topic_model(sentence_records, n_clusters)
    df = pd.DataFrame(sentence_records)
    df["topic"] = topics
    df["prob"] = [1 if topic == -1 else probs[sen_i][topic] for sen_i, topic in enumerate(topics)]
    labels = None
    if with_labels:
        labels = label_topics(topic_model)
    return df, topic_model.get_topics(), topic_model.get_representative_docs(), labels

def compute_topic_matrix(data, per_prompt=False, labels=None):
    prob = (
        data.groupby(["topic", "prompt_key", "response_idx"], sort=False)["prob"]
            .max()
            .unstack(["prompt_key", "response_idx"], sort=False)
            .fillna(0.0)
    )

    if -1 in prob.index:
        prob = prob.drop(index=-1)

    prob.index = [int(t) for t in prob.index]

    matrix, col_meta = postprocess_heatmap_matrix(
        prob,
        per_prompt=per_prompt
    )

    row_meta = None

    if labels:
        labels = {int(k): v for k, v in labels.items()}
        row_meta = pd.DataFrame({
            "id": matrix.index,
            "label": [labels[id]["label"] for id in matrix.index],
            "description": [labels[id]["definition"] for id in matrix.index],
        }).set_index("id")

    return matrix, col_meta, row_meta
