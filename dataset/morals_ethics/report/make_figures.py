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

# Figure: dataset composition by source (single series, one hue)
comp = [("Synthetic applied ethics*", 1498), ("PhilPapers 2020", 16), ("BIG-bench ethical qs", 115), ("MoralExceptQA", 132),
        ("DailyDilemmas", 1354), ("MoralChoice", 1367), ("Scruples Dilemmas", 2468), ("Scruples Anecdotes", 4390),
        ("Social Chemistry 101", 6397), ("ETHICS", 7263)]
fig, ax = plt.subplots(figsize=(4.2, 2.6), dpi=200)
names, vals2 = zip(*comp)
ax.barh(names, vals2, color=C[0], height=0.62)
for i, v in enumerate(vals2):
    ax.text(v + 90, i, f"{v:,}", va="center", fontsize=7, color=INK)
ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlim(0, 8400); ax.tick_params(axis="y", labelsize=7); ax.tick_params(axis="x", labelsize=7)
ax.set_xlabel("Items in the dataset")
fig.tight_layout(); fig.savefig("fig_composition.png"); plt.close(fig)

# Figure: accuracy by label agreement
bands = ["Unanimous\n(n=223)", "0.8-0.99\n(n=359)", "Below 0.8\n(n=327)", "Single annotator\n(n=507)"]
agr = {"Llama 3.1 8B": [67.3, 64.1, 37.9, 37.1], "Qwen 2.5 7B": [67.3, 51.5, 35.2, 44.6], "Gemma 2 9B": [81.2, 66.6, 34.9, 45.0]}
fig, ax = plt.subplots(figsize=(4.2, 2.6), dpi=200)
for i, m in enumerate(models):
    xs = [k + (i - 1) * 0.27 for k in range(len(bands))]
    ax.bar(xs, agr[m], width=0.25, color=C[i], label=m)
ax.set_xticks(range(len(bands))); ax.set_xticklabels(bands, fontsize=6.8)
style(ax)
ax.legend(fontsize=6.4, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.1)
fig.tight_layout(); fig.savefig("fig_agreement.png"); plt.close(fig)

# Figure: Scruples Anecdotes verdicts, people vs models (share of 352 posts)
cats = ["AUTHOR", "OTHER", "EVERYBODY", "NOBODY", "INFO"]
dist = {"People (label)": [95, 122, 48, 78, 9], "Llama 3.1 8B": [246, 35, 0, 70, 0],
        "Qwen 2.5 7B": [223, 79, 2, 10, 8], "Gemma 2 9B": [93, 65, 40, 7, 147]}
cols = ["#6b6b6b"] + C
fig, ax = plt.subplots(figsize=(4.4, 2.6), dpi=200)
for i, (k, v) in enumerate(dist.items()):
    xs = [j + (i - 1.5) * 0.2 for j in range(len(cats))]
    ax.bar(xs, [100 * a / 352 for a in v], width=0.18, color=cols[i], label=k)
ax.set_xticks(range(len(cats))); ax.set_xticklabels(cats, fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_ylim(0, 80); ax.set_ylabel("Share of the 352 posts (%)")
ax.legend(fontsize=6.4, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.1, columnspacing=0.8)
fig.tight_layout(); fig.savefig("fig_scruples_verdicts.png"); plt.close(fig)
print("all figures ok")
