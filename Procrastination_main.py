from collections import defaultdict
import matplotlib.pyplot as plt

# ── Dataset ───────────────────────────────────────────────────
data = [
    ["Yes","No", "No", "Yes","No" ],
    ["Yes","Yes","Yes","Yes","No" ],
    ["Yes","Yes","Yes","Yes","Yes"],
    ["Yes","Yes","Yes","Yes","Yes"],
    ["Yes","Yes","Yes","Yes","Yes"],
    ["Yes","Yes","No", "Yes","No" ],
    ["Yes","No", "No", "Yes","Yes"],
    ["No", "Yes","No", "No", "No" ],
    ["Yes","Yes","Yes","Yes","No" ],
    ["Yes","Yes","No", "Yes","No" ],
]

factors = [
    "Lack of Motivation",
    "Distractions",
    "Task Difficulty",
    "Poor Time Management",
    "Fear of Failure"
]

procrastination = ["Yes"]*7 + ["No"]*3
total = len(data)
total_students = len(data)

# ─────────────────────────────────────────────────────────────
#  PART 1 — FACTOR ANALYSIS
# ─────────────────────────────────────────────────────────────

yes_counts = [0] * len(factors)
for row in data:
    for i, answer in enumerate(row):
        if answer == "Yes":
            yes_counts[i] += 1

no_counts = [total - y for y in yes_counts]

factor_probs = sorted(
    [(factors[i], yes_counts[i], yes_counts[i]/total) for i in range(len(factors))],
    key=lambda x: x[2], reverse=True
)

print("=" * 55)
print("         PROCRASTINATION FACTOR ANALYSIS")
print("=" * 55)
print(f"  Total students    : {total}")
print(f"  Procrastinators   : 7   Non-procrastinators: 3")
print("-" * 55)
print(f"  {'Factor':<25} {'Yes':>4}/{total}   {'Prob':>5}   Bar")
print("-" * 55)
for factor, count, prob in factor_probs:
    bar = "█" * int(prob * 20)
    print(f"  {factor:<25} {count:>4}/{total}   {prob:.0%}     {bar}")
print("=" * 55)


# ─────────────────────────────────────────────────────────────
#  PART 2 — NAÏVE BAYES
# ─────────────────────────────────────────────────────────────

feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
class_counts   = defaultdict(int)

for row, cls in zip(data, procrastination):
    class_counts[cls] += 1
    for i, answer in enumerate(row):
        feature_counts[cls][factors[i]][answer] += 1

priors = {cls: class_counts[cls] / total for cls in class_counts}

cond_probs = defaultdict(lambda: defaultdict(dict))
for cls in feature_counts:
    for factor in feature_counts[cls]:
        for value in ["Yes", "No"]:
            count = feature_counts[cls][factor].get(value, 0)
            cond_probs[cls][factor][value] = (count + 1) / (class_counts[cls] + 2)

new_participant = {
    "Lack of Motivation"   : "Yes",
    "Distractions"         : "No",
    "Task Difficulty"      : "Yes",
    "Poor Time Management" : "Yes",
    "Fear of Failure"      : "No"
}

print()
print("=" * 55)
print("          NAÏVE BAYES — NEW PARTICIPANT")
print("=" * 55)
print("  Their answers:")
for factor, answer in new_participant.items():
    mark = "✔" if answer == "Yes" else "✘"
    print(f"    {mark}  {factor}")
print("=" * 55)

posterior = {}
for cls in ["Yes", "No"]:
    print(f"\n  Procrastination = {cls}")
    print(f"  Prior: {priors[cls]:.2f}  ({class_counts[cls]}/{total} students in this class)")
    print(f"  {'Factor':<25}  {'Answer':>6}  {'Probability':>11}")
    print(f"  {'-'*46}")
    score = priors[cls]
    for factor, answer in new_participant.items():
        p = cond_probs[cls][factor][answer]
        score *= p
        print(f"  {factor:<25}  {answer:>6}  {p:>10.3f}")
    print(f"  {'-'*46}")
    print(f"  Score (unnormalized) = {score:.6f}")
    posterior[cls] = score

total_score = sum(posterior.values())
for cls in posterior:
    posterior[cls] /= total_score

# ─────────────────────────────────────────────────────────────
#  PART 3 — FINAL PREDICTION
# ─────────────────────────────────────────────────────────────
predicted = max(posterior, key=posterior.get)

print()
print("=" * 55)
print("              FINAL PREDICTION")
print("=" * 55)
for cls, prob in posterior.items():
    bar    = "█" * int(prob * 30)
    marker = " <- predicted" if cls == predicted else ""
    print(f"  Procrastination = {cls:<3}  {prob:.1%}  {bar}{marker}")
print("-" * 55)
print(f"  Verdict: This student is likely a PROCRASTINATOR.")
print(f"  Predicted class: {predicted}")
print("=" * 55)


# ─────────────────────────────────────────────────────────────
#  GRAPHS
# ─────────────────────────────────────────────────────────────

short_labels = [
    "Lack of\nMotivation",
    "Distractions",
    "Task\nDifficulty",
    "Poor Time\nManagement",
    "Fear of\nFailure"
]

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
fig.suptitle(
    "Procrastination Factor Analysis — Raw Counts",
    fontsize=14,
    fontweight="bold"
)

# ── Per-factor bar charts ──────────────────────────────────────
for idx in range(len(factors)):
    row_pos = idx // 3
    col_pos = idx % 3
    ax = axes[row_pos][col_pos]

    yes_val = yes_counts[idx]
    no_val  = no_counts[idx]

    bars_yes = ax.bar(["Yes"], [yes_val], color="green", width=0.4, label="Yes")
    bars_no  = ax.bar(["No"],  [no_val],  color="red",   width=0.4, label="No")

    ax.bar_label(bars_yes, fontsize=11, fontweight="bold")
    ax.bar_label(bars_no,  fontsize=11, fontweight="bold")

    ax.set_title(short_labels[idx], fontsize=11, fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_ylim(0, total + 1)
    ax.legend(fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

# ── Pie chart — Overall Prediction Distribution ───────────────
ax_pie = axes[1][2]

pie_labels = ["Procrastinator", "Non-Procrastinator"]
pie_values = [posterior["Yes"], posterior["No"]]
pie_colors = ["green", "red"]
explode    = (0.05, 0)

wedges, texts, autotexts = ax_pie.pie(
    pie_values,
    labels=pie_labels,
    colors=pie_colors,
    autopct="%1.1f%%",
    explode=explode,
    startangle=90,
    textprops={"fontsize": 10}
)

for at in autotexts:
    at.set_fontweight("bold")
    at.set_color("white")

ax_pie.set_title("Overall Prediction Distribution", fontsize=11, fontweight="bold")

plt.tight_layout()
plt.show()