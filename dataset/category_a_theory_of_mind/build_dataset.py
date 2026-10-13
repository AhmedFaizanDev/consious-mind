"""
Build Category A (Interactive Theory of Mind) dataset items from the real
FANToM data (raw_fantom/fantom_v1.json, downloaded from
https://storage.googleapis.com/ai2-mosaic-public/projects/fantom/fantom.tar.gz,
sha256 verified against the hash hardcoded in reference/fantom/task/dataset_loader.py).

Follows dataset/category_a_theory_of_mind/SCHEMA.md exactly:
- short_context only (the human-baselined condition)
- three question types only: belief_choice, answerability_list, info_access_list
  (binary Y/N variants excluded - no human baseline exists for them)
- filtered to missed_info_accessibility == "inaccessible" (the scenario the
  published human baseline numbers were measured on - see eval_fantom.py
  score_and_analyze(), target_scenario='inaccessible')
- deduped on (set_id, question_type, question_text)
- stratified sample of 50 items per type, seed=42, per the pilot spec
  referenced in SCHEMA.md (belief stratified by tom_order: first/second-order,
  proportional to their availability)
- exact prompt templates and MC-choice construction reused verbatim from
  reference/fantom/eval_fantom.py (set_beliefQA_multiple_choices, prompt header)
"""
import json
import random

SEED = 42
N_PER_TYPE = 50

HUMAN_BASELINE = {
    "belief_choice": 0.938,
    "answerability_list": 0.906,
    "info_access_list": 0.906,
}
LICENSE_NOTE = "MIT (code); dataset for evaluation purposes only per author note"
FIRST_PUBLIC_DATE = "2023-10"

PROMPT_HEADER = (
    "This is a theory-of-mind test. Please answer the question regarding "
    "facts or beliefs, based on the following in-person conversation between "
    "individuals who have just met.\n\n"
)


def make_mc_choices(correct_answer, wrong_answer, rng):
    """Verbatim logic from eval_fantom.py's set_beliefQA_multiple_choices."""
    answer_goes_last = rng.choice([True, False])
    if answer_goes_last:
        choices = [wrong_answer, correct_answer]
        answer_idx = 1
    else:
        choices = [correct_answer, wrong_answer]
        answer_idx = 0
    option_letters = [chr(x) for x in range(ord("a"), ord("a") + len(choices))]
    choices_text = "".join(
        "({}) {}\n".format(letter, option) for letter, option in zip(option_letters, choices)
    )
    return choices_text.strip(), option_letters[answer_idx]


def load_sets():
    with open("raw_fantom/fantom_v1.json") as f:
        return json.load(f)


def build_belief_items(sets, rng):
    candidates = []
    for s in sets:
        context = s["short_context"].strip()
        for b in s["beliefQAs"]:
            if b["missed_info_accessibility"] != "inaccessible":
                continue
            candidates.append((s["set_id"], s["conv_id"], context, b))

    # Stratify by tom_order, proportional to availability (first vs second order)
    first_order = [c for c in candidates if c[3]["tom_type"].split(":")[0] == "first-order"]
    second_order = [c for c in candidates if c[3]["tom_type"].split(":")[0] == "second-order"]
    total = len(first_order) + len(second_order)
    n_first = round(N_PER_TYPE * len(first_order) / total)
    n_second = N_PER_TYPE - n_first

    rng.shuffle(first_order)
    rng.shuffle(second_order)
    sample = first_order[:n_first] + second_order[:n_second]

    items = []
    seen = set()
    for set_id, conv_id, context, qa in sample:
        key = (set_id, "belief_choice", qa["question"])
        if key in seen:
            continue
        seen.add(key)
        choices_text, answer_letter = make_mc_choices(qa["correct_answer"], qa["wrong_answer"], rng)
        question_with_choices = "{}\n{}".format(qa["question"], choices_text)
        items.append({
            "item_id": "fantom_belief_{:04d}".format(len(items) + 1),
            "conversation_id": set_id,
            "question_type": "belief_choice",
            "context": context,
            "question": question_with_choices,
            "correct_answer": answer_letter,
            "wrong_answer": [l for l in "abcd"[:2] if l != answer_letter][0],
            "tom_order": qa["tom_type"].split(":")[0],
            "human_baseline_accuracy": HUMAN_BASELINE["belief_choice"],
            "license_note": LICENSE_NOTE,
            "first_public_date": FIRST_PUBLIC_DATE,
        })
    return items


def build_list_items(sets, field, qtype, rng):
    candidates = []
    for s in sets:
        context = s["short_context"].strip()
        qa = s[field]
        if qa["missed_info_accessibility"] != "inaccessible":
            continue
        candidates.append((s["set_id"], context, qa, s["factQA"]))

    rng.shuffle(candidates)

    items = []
    seen = set()
    for set_id, context, qa, fact_qa in candidates:
        key = (set_id, qtype, qa["question"])
        if key in seen:
            continue
        seen.add(key)
        if qtype == "answerability_list":
            question_text = "Target: {}\nQuestion: {}".format(fact_qa["question"], qa["question"])
        else:
            question_text = "Information: {} {}\nQuestion: {}".format(
                fact_qa["question"], fact_qa["correct_answer"], qa["question"]
            )
        items.append({
            "item_id": "fantom_{}_{:04d}".format(qtype.split("_")[0], len(items) + 1),
            "conversation_id": set_id,
            "question_type": qtype,
            "context": context,
            "question": question_text,
            "correct_answer": qa["correct_answer"],
            "wrong_answer": qa["wrong_answer"],
            "human_baseline_accuracy": HUMAN_BASELINE[qtype],
            "license_note": LICENSE_NOTE,
            "first_public_date": FIRST_PUBLIC_DATE,
        })
        if len(items) == N_PER_TYPE:
            break
    return items


def main():
    sets = load_sets()
    rng = random.Random(SEED)

    belief_items = build_belief_items(sets, rng)
    answerability_items = build_list_items(sets, "answerabilityQA_list", "answerability_list", rng)
    info_access_items = build_list_items(sets, "infoAccessibilityQA_list", "info_access_list", rng)

    all_items = belief_items + answerability_items + info_access_items

    with open("items.json", "w") as f:
        json.dump(all_items, f, indent=2)

    print("belief_choice:", len(belief_items))
    print("answerability_list:", len(answerability_items))
    print("info_access_list:", len(info_access_items))
    print("total:", len(all_items))


if __name__ == "__main__":
    main()
