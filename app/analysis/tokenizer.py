from nltk.tokenize import sent_tokenize

def tokenize_response(response: str):
    sentences = []
    paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        sentences.extend(sent_tokenize(paragraph))
    return sentences

def tokenize_data(data, drop_short=True, min_len=5, drop_duplicates=False):
    records = []
    seen = set()

    for response_idx, record in enumerate(data):
        sents = tokenize_response(record["response"])
        for sentence_idx, sentence in enumerate(sents):
            if drop_short and len(sentence.split()) <= min_len:
                continue

            if drop_duplicates:
                key = (record['comp_key'], response_idx, sentence.strip())
                if key in seen:
                    continue
                seen.add(key)

            records.append({
                "comp_key": record['comp_key'],
                "response_idx": response_idx,
                "sentence_idx": sentence_idx,
                "sentence": sentence.strip(),
            })

    return records
