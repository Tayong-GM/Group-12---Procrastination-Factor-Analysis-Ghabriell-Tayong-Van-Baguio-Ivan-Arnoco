
from collections import defaultdict

# ── Dataset (corrected from real survey) ──────────────────────
data = [
    ["Yes","Yes","No", "Yes","No" ],
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

# --------------------------------------------
# Count Yes responses for each factor
# --------------------------------------------
yes_counts = [0] * len(factors)

for row in data:
    for i,answer in enumerate(row):
        if answer == "Yes":
            yes_counts[i] += 1


# --------------------------------------------
# Calculate probabilities
# --------------------------------------------
probabilities = []

for i,count in enumerate(yes_counts):
    prob = count / total_students
    probabilities.append((factors[i], count, prob))


# --------------------------------------------
# Sort factors by probability
# --------------------------------------------
probabilities.sort(key=lambda x: x[2], reverse=True)


# --------------------------------------------
# Display results
# --------------------------------------------
print("Total Students:", total_students)
print("\nProcrastination Factor Analysis\n")

for factor,count,prob in probabilities:
    print(factor)
    print("Students affected:", count)
    print("Probability:", round(prob,2))
    print()


# ─────────────────────────────────────────────────────────────
#  PART 1 — FACTOR ANALYSIS
# ─────────────────────────────────────────────────────────────

yes_counts = [0] * len(factors)
for row in data:
    for i, answer in enumerate(row):
        if answer == "Yes":
            yes_counts[i] += 1

factor_probs = sorted(
    [(factors[i], yes_counts[i], yes_counts[i]/total) for i in range(len(factors))],
    key=lambda x: x[2], reverse=True
)

print("=" * 55)
print("         PROCRASTINATION FACTOR ANALYSIS")
print("=" * 55)
print(f"  Total students : {total}")
print(f"  Procrastinators: 7   Non-procrastinators: 3")
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

# Count answers per class
feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
class_counts   = defaultdict(int)

for row, cls in zip(data, procrastination):
    class_counts[cls] += 1
    for i, answer in enumerate(row):
        feature_counts[cls][factors[i]][answer] += 1

# Prior probabilities
priors = {cls: class_counts[cls] / total for cls in class_counts}

# Conditional probabilities with Laplace smoothing
cond_probs = defaultdict(lambda: defaultdict(dict))
for cls in feature_counts:
    for factor in feature_counts[cls]:
        for value in ["Yes", "No"]:
            count = feature_counts[cls][factor].get(value, 0)
            cond_probs[cls][factor][value] = (count + 1) / (class_counts[cls] + 2)

# New participant
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

# Compute posterior for each class
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

# Normalize
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
