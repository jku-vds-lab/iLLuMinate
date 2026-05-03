import re
from openai import OpenAI
import json

system_style = '''You are a linguist interpreting factors derived from a multidimensional analysis (MDA) following Douglas Biber’s framework.

Multidimensional Analysis Principles
- Multidimensional analysis is a corpus-based method for studying patterns of linguistic variation across many texts.
- It analyzes the distribution of linguistic features across a corpus in order to identify systematic patterns of co-occurrence.
- These patterns reflect underlying communicative functions used by speakers and writers in different discourse styles.

Factor Structure
- Factor analysis groups together linguistic features that frequently occur together across the corpus.
- Each factor represents a communicative dimension.
- Unipolar factors are defined by a set of co-occurring linguistic features.
- Bipolar factors are defined by the contrast between two sets of co-occurring linguistic features (positive and negative poles).
- The poles of a bipolar factor correspond to contradicting communicative function that appear across texts in the corpus.

Communicative Function
- Communicative function refers to how information is communicated.
- It describes the mode of communication, not the topic or subject matter of the text.
- Communicative function is inferred from patterns of linguistic features observed across the corpus, not from the semantic content of individual texts in the corpus.

Factor Interpretation Procedure
- Interpret each factor primarily from its associated linguistic features.
- Features that hold higher loading scores contribute more to the factor interpretation.
- Identify the communicative tendencies implied by individual features.
- Determine the shared communicative function underlying the co-occurrence of those features.
- Interpret the bipolar factors as a communicative contrast between the positive and negative poles.

Use of Example Snippets
- Example snippets come from texts in the corpus where the factor is strongly represented.
- They illustrate how the inferred communicative function appears in real language.
- They are used only to confirm the interpretation derived from the linguistic features.
- Do NOT use the topic or subject matter of the snippets to interpret the factor.'''


user_style = '''Interpret the following factors from a multidimensional analysis.

INPUT
The factors are provided in JSON format. Each factor contains:
- linguistic features that load positively and negatively.
- example snippets from texts where each pole is strongly represented.

{factors_json}

TASK
1) Compare all factors to detect overlapping signals and avoid generic or duplicate labels.
2) For each factor:
   a) Identify the communicative function implied by the features in the positive pole.
   b) Identify the communicative function implied by the features in the negative pole.
   c) Determine the communicative contrast linking the two poles.
   d) Assign a ≤ 5 words label with NO conjunctions and a one-sentence description of the communicative function for each pole:
      - Use plain language understandable to a non-linguist.
      - Listing the factor features in the label or description is prohibited.
3) Verify that the example snippets reflect the inferred communicative function.
4) Self-check:
   - Ask: “If the example snippets were removed, do this label and description still fit the linguistic features alone?”
   - If the answer is NO, the interpretation is topic-driven and MUST be replaced with a discourse style interpretation that is supported by the linguistic features.

OUTPUT
- Labels are Title Case.
- If the factor is unipolar interpret its existing pole and return an empty JSON object for the non-existing one.
- Return ONLY valid JSON in the following structure:
{
  "results": [
    {
      "factor_id": "<factor_id>",
      "pos": {
        "label": "<label>",
        "description": "<description>"
      },
      "neg": {
        "label": "<label>",
        "description": "<description>"
      }
    }
  ]
}
'''

topics_prompt = '''You are given a set of related topics drawn from the same semantic neighborhood.

Each topic includes:
- topic_id
- top terms strongly associated with the topic
- example sentences referencing the topic
- optionally, a previously assigned label and definition

Your tasks:

1) Produce or refine a topic label and definition for EACH semantic topic.
   - If a topic already has a label/definition, keep them unchanged unless the batch context reveals overlap, ambiguity, or a clearer more specific phrasing.
   - When refining, prefer minimal edits that improve specificity and mutual distinctness.

Definition rules:
- EXACTLY one sentence.
- Start with a neutral noun-phrase subject (e.g., “Discussion of…”, “Descriptions of…”).
- Do NOT use annotation-instruction phrasing (forbidden starts include: “A text should be annotated…”, “Annotate when…”, “This topic applies if…”).
- Only return printable UTF-8 characters.
- Do not include control characters.

Labeling rules:
- Output a Title Case, singular noun phrase.
- The label must be specific to the definition.
- Labels MUST be mutually distinct within this batch.
- Avoid generic labels that simply restate a broad category unless the topic truly has no narrower scope.

---

Output ONLY a JSON object in the following format:

{
  "topics": [
    {
      "topic_id": <id>,
      "label": "<Title Case, singular noun phrase>",
      "definition": "<single-sentence definition>"
    }
  ]
}

Output rules:
- Every input topic_id must appear exactly once across the output arrays.
- Do not output explanations or any text outside the JSON.

Input topics (JSON):
{batch_json}
'''
client = OpenAI(api_key="sk-XXXXXXXXXXXXXXXX")

MODEL = "gpt-4o"

def call_task(user_prompt, temprature=0, n=1, system_prompt=None, model=MODEL):
  messages = [ {"role": "user", "content": user_prompt} ]
  if system_prompt:
      messages.append({"role": "system", "content": system_prompt})
  completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temprature,
                    n=n,
                    response_format={"type": "json_object"}
                )
  responses = []
  for _, choice in enumerate(completion.choices):
        raw = choice.message.content or ""

        try:
            responses.append(json.loads(raw))
            continue
        except json.JSONDecodeError:
            pass

        repaired = re.sub(
            r'"definition"\s*:\s*".*?(?=",\s*"(?:topic_id|label|definition)"|",\s*}|"\s*})',
            '"definition": ""',
            raw,
            flags=re.DOTALL,
        )

        repaired = re.sub(
            r'"definition"\s*:\s*".*$',
            '"definition": ""}]}',
            repaired,
            flags=re.DOTALL,
        )

        try:
            responses.append(json.loads(repaired))
        except json.JSONDecodeError as e:
            print("Tail:", repr(raw[-120:]))
            continue
  return responses
