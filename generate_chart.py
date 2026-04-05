import os, requests, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

TOKEN    = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

# --- fetch all repos ---
repos, page = [], 1
while True:
    r = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        headers=HEADERS,
        params={"per_page": 100, "page": page, "type": "owner"}
    ).json()
    if not r:
        break
    repos += r
    page += 1

# --- aggregate language bytes ---
lang_totals = {}
for repo in repos:
    if repo.get("fork"):
        continue
    langs = requests.get(repo["languages_url"], headers=HEADERS).json()
    for lang, count in langs.items():
        lang_totals[lang] = lang_totals.get(lang, 0) + count

# --- top 8 only ---
sorted_langs = sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)[:8]
labels  = [l[0] for l in sorted_langs]
sizes   = [l[1] for l in sorted_langs]
total   = sum(sizes)
percents = [s / total * 100 for s in sizes]

# --- neon cyberpunk colors ---
COLORS = ["#00F5FF","#FF0090","#00FF41","#FF6B00",
          "#FFD21E","#5C3EE8","#FF4444","#20BEFF"]

# --- plot ---
fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0D0D0D")
ax.set_facecolor("#0D0D0D")

wedges, _ = ax.pie(
    sizes,
    colors=COLORS[:len(labels)],
    startangle=140,
    wedgeprops=dict(width=0.6, edgecolor="#0D0D0D", linewidth=2)
)

# --- legend with percentages ---
legend_labels = [f"{l}  {p:.1f}%" for l, p in zip(labels, percents)]
patches = [mpatches.Patch(color=COLORS[i], label=legend_labels[i])
           for i in range(len(labels))]
ax.legend(
    handles=patches,
    loc="center left",
    bbox_to_anchor=(0.85, 0.5),
    frameon=False,
    fontsize=9,
    labelcolor="white"
)

ax.set_title("Languages", color="#00F5FF", fontsize=14, fontweight="bold", pad=10)
plt.tight_layout()
plt.savefig("lang-stats.svg", format="svg",
            facecolor="#0D0D0D", bbox_inches="tight", dpi=150)
print("✅ lang-stats.svg saved")
