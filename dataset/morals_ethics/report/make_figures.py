"""Figures for the Morals & Ethics progress report (values from eval/summary.csv, recomputed from eval/responses)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = ["#257de0", "#f47230", "#00b894"]           # categorical slots 1-3 (validated)
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK2})
models = ["Llama 3.1 8B", "Qwen 2.5 7B", "Gemma 2 9B"]

def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_ylim(0, 100); ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("Accuracy vs human label (%)")

# Figure 1: overall
fig, ax = plt.subplots(figsize=(3.6, 2.5), dpi=200)
acc = [54.2, 53.4, 59.5]
bars = ax.bar(models, acc, color=C, width=0.55)
for b, v in zip(bars, acc):
    ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}%", ha="center", color=INK, fontsize=9, fontweight="bold")
style(ax); fig.tight_layout(); fig.savefig("fig1_overall.png"); plt.close(fig)

# Figure 2: by source, with always-most-common baseline
src = ["Moral\nChoice", "BIG-\nbench", "ETHICS", "Moral\nExceptQA", "Scruples\nDilemmas", "Social\nChem. 101", "Scruples\nAnecdotes"]
vals = {"Llama 3.1 8B": [96.2, 88.0, 77.0, 60.0, 53.6, 37.7, 34.4],
        "Qwen 2.5 7B": [100, 92.0, 71.1, 60.0, 51.7, 45.5, 28.1],
        "Gemma 2 9B": [100, 96.0, 83.2, 72.0, 69.4, 45.8, 27.0]}
base = [65.4, 32.0, 35.7, 52.0, 50.7, 23.7, 34.7]
fig, ax = plt.subplots(figsize=(4.4, 2.7), dpi=200)
w = 0.26
for i, m in enumerate(models):
    xs = [k + (i - 1) * (w + 0.02) for k in range(len(src))]
    ax.bar(xs, vals[m], width=w, color=C[i], label=m)
for k, b in enumerate(base):
    ax.plot([k - 0.45, k + 0.45], [b, b], color=INK, lw=1.4)
ax.plot([], [], color=INK, lw=1.4, label="Always most common answer")
ax.set_xticks(range(len(src))); ax.set_xticklabels(src, fontsize=6.2)
style(ax)
h, l = ax.get_legend_handles_labels()
ax.legend(h[1:] + h[:1], l[1:] + l[:1], fontsize=6.2, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.45, 1.0), handlelength=1.1, columnspacing=0.7)
fig.tight_layout(); fig.savefig("fig2_by_source.png"); plt.close(fig)
print("ok")
