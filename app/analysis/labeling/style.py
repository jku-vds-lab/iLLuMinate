import json

from .prompting import call_task, user_style, system_style


def label_factors(factors):
    factors_json = json.dumps(factors)
    prompt = user_style.replace("{factors_json}", factors_json)
    response = call_task(prompt, temprature=1, n=1, system_prompt=system_style, model="gpt-5.4")[0]
    labels = {
        (
            f"{item['factor_id']}_{polarity}"
            if item.get("neg")
            else item["factor_id"]
        ): (
            item[polarity]
            if item.get("neg")
            else item["pos"]
        )
        for item in response["results"]
        for polarity in (("pos", "neg") if item.get("neg") else ("pos",))
    }
    return labels
