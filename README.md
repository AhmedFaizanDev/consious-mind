# ConsciousMind: Morals and Ethics

**ConsciousMind: Modeling Consciousness and Metacognitive Awareness for Mental Health AI.** Category: **Morals and Ethics**.
Faizan Ahmed, roll number SE23UCSE003.

## Goal
Find out how closely AI models' moral judgments match the judgments people made, and **where they diverge**, so that the contested
questions can be taken forward to a matched human-versus-AI study (the ConsciousMind question of where people still judge better).
Two parts:

1. **A documented dataset** of 25,000 moral and ethical questions with the human judgments attached: who wrote each item, how its label was
   produced, how much the labelers agreed, and under what licence.
2. **A first evaluation** of three local open models (Llama 3.1 8B, Qwen 2.5 7B, Gemma 2 9B, run with Ollama) on a 2,029-item sample.

A "human label" is what a group of people said in the source study (crowd workers, Reddit voters, study participants). It is not moral
truth, and this work compares models with those labels; it does not yet compare models with people answering under the same conditions.

## Results at a glance
| | Llama 3.1 8B | Qwen 2.5 7B | Gemma 2 9B |
|---|---|---|---|
| Matched the human label (1,753 labeled items) | 54.2% | 53.4% | **59.5%** |
| Clear-cut sources (MoralChoice / BIG-bench / ETHICS) | 96 / 88 / 77% | 100 / 92 / 71% | 100 / 96 / 83% |
| Contested sources (Scruples Dilemmas / Scruples Anecdotes) | 54 / 34% | 52 / 28% | 69 / 27% |

Near ceiling where people agree easily; at chance, or below always choosing the most common answer, on contested real-life questions.
Full analysis: the report below.

## Where to look
| Path | What it is |
|---|---|
| [`dataset/morals_ethics/report/ConsciousMind_Morals_Ethics_Research_Progress_Report.pdf`](dataset/morals_ethics/report/ConsciousMind_Morals_Ethics_Research_Progress_Report.pdf) | **The report** (detailed, with appendices) |
| [`dataset/morals_ethics/DATA_CARD.md`](dataset/morals_ethics/DATA_CARD.md) | Data card: motivation, composition, collection, cleaning, uses, licences |
| `dataset/morals_ethics/output/morals_ethics_25k.csv` | The dataset (25,000 rows, 36 columns) |
| `dataset/morals_ethics/output/morals_ethics_published.csv` | Published-source rows only (23,502) |
| `dataset/morals_ethics/output/morals_ethics_synthetic.csv` | Synthetic applied-ethics rows only (1,498, unlabeled) |
| `dataset/morals_ethics/output/source_manifest.csv` | Per-source counts, licences, URLs, citations |
| `dataset/morals_ethics/DATA_QUALITY_REPORT.md` | Validation results (duplicates, labels, split leakage) |
| `dataset/morals_ethics/eval/ConsciousMind_LLM_Evaluation_Results_Explained.xlsx` | Evaluation workbook: every item, every model reply, all result tables |
| `dataset/morals_ethics/eval/` | Evaluation sample, raw replies (`responses/*.jsonl`), `summary.csv`, run log |
| `dataset/morals_ethics/README.md` | Dataset schema, method and how to rebuild |
| `dataset/morals_ethics/papers/PAPERS.md` | Source papers (links verified) |
| `dataset/morals_ethics/HANDOFF_MORALS_ETHICS.md` | Work log of this category |
| `data/CM_Ethics_Dataset_1.xlsx` | Earlier ethics workbook (416 items, 1,248 Claude responses); its items are inside the dataset |
| `dataset/category_*`, `reference/`, `archive/` | Earlier ConsciousMind work (Theory of Mind, counseling) and copied reference code, kept unchanged |

## Reproduce
```bash
pip install -r dataset/morals_ethics/requirements.txt
bash dataset/morals_ethics/scripts/run_all.sh            # download sources, build, validate (deterministic)
python3 dataset/morals_ethics/scripts/export_release.py  # published-only and synthetic-only files
# evaluation (needs Ollama and a GPU machine)
bash dataset/morals_ethics/scripts/run_ollama_eval.sh
python3 dataset/morals_ethics/scripts/eval_ollama.py score
```
Raw downloads (`data/raw_sources/`, ~4 GB) and staging checkpoints are not committed; the scripts recreate them.

## Licences
ETHICS (MIT), DailyDilemmas (CC BY 4.0), MoralChoice (MIT), BIG-bench (Apache-2.0). Scruples, Social Chemistry 101 and MoralExceptQA state no data
licence in the files retrieved; the dataset is for research and review, and those terms should be checked before any public release.
