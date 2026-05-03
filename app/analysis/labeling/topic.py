import json

from .prompting import call_task, topics_prompt

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations

def get_topic_labeling_batches(topic_model, batch_size=6):
    def mean_similarity(topic_list):
        pairs = combinations(topic_list, 2)
        sims = [S[topic_to_pos[i], topic_to_pos[j]] for i, j in pairs]
        return float(np.mean(sims)) if sims else 0.0
    X = topic_model.topic_embeddings_

    info = topic_model.get_topic_info()
    topic_ids = info.loc[info.Topic != -1, "Topic"].to_list()

    X_use = X[[t + 1 for t in topic_ids]]

    S = cosine_similarity(X_use)

    pos_to_topic = topic_ids[:]
    topic_to_pos = {t: i for i, t in enumerate(topic_ids)}

    batches = {}
    for i in range(len(pos_to_topic)):
        nn_pos = S[i].argsort()[::-1][:batch_size].tolist()
        nn_topics = [pos_to_topic[p] for p in nn_pos]

        batch_id = " ".join(map(str, nn_topics))
        if batch_id in batches:
            continue
        batches[batch_id] = mean_similarity(nn_topics)

    return [[int(c) for c in k.split()]
            for k, v in sorted(batches.items(), key=lambda b: b[1], reverse=True)]

def label_topics(topic_model):
    def get_topic_json(topic_id, n_terms=10):
        terms = [t for t, s in topic_model.get_topic(topic_id)]
        sents = topic_model.get_representative_docs(topic_id)
        return {
            "topic_id": topic_id,
            "terms": terms[:n_terms],
            "examples": sents,
        }
    batches = get_topic_labeling_batches(topic_model)
    labels = {}
    for batch in batches:
        topic_dicts = []
        for t in batch:
            if t not in labels:
                topic_dicts.append(get_topic_json(t))
                continue
            topic_dicts.append({**labels[t], **get_topic_json(labels[t]['topic_id'])})
        annot = call_task(
                    topics_prompt
                        .replace("{batch_json}", json.dumps({"topics": topic_dicts})),
                    0, 1, model="gpt-4o"
                )
        for a in annot[0]["topics"]:
            labels[a['topic_id']] = a
    
    return labels