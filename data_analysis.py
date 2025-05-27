import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
sns.set(style="whitegrid")

# ---------- Load & reshape --------------------------------------- #
file_path = Path("hri-results.csv")
long_df   = pd.read_csv(file_path)
wide_df   = long_df.pivot(index="participant_id", columns="Question", values="Answer")

# ---------- Variables & numeric cast ----------------------------- #
risk_vars      = [f"risk_q{i}" for i in range(1,8)]
influence_vars = [f"influence_{i}" for i in range(1,5)]
anthro_vars    = [f"anthropomorphism_{i}" for i in range(1,6)]
animacy_vars   = [f"animacy_{i}" for i in range(1,7)]
like_vars      = [f"likeability_{i}" for i in range(1,6)]

numeric_cols = [c for c in risk_vars+influence_vars+anthro_vars+animacy_vars+like_vars
                if c in wide_df.columns]
wide_df[numeric_cols] = wide_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# ---------- Derived metrics -------------------------------------- #
wide_df["RPS_score"]             = wide_df[risk_vars].mean(axis=1)
wide_df["Influence_mean"]        = wide_df[influence_vars].mean(axis=1)
wide_df["Anthropomorphism_mean"] = wide_df[anthro_vars].mean(axis=1)
wide_df["Animacy_mean"]          = wide_df[animacy_vars].mean(axis=1)
wide_df["Likeability_mean"]      = wide_df[like_vars].mean(axis=1)

# Label columns
group_col, gender_col = "study_type", "participant_gender"
wide_df[group_col] = wide_df[group_col].astype("category")
wide_df[gender_col] = wide_df[gender_col].astype("category")

# Palettes/titles
palette = {"CONTROL": sns.color_palette("Set2")[0],
           "RISK":    sns.color_palette("Set2")[1]}

# -------------- 1. Overview subplot ------------------------------------- #
fig_overview, axes = plt.subplots(1,2, figsize=(12,4))

# Participants by NAO Behaviour × gender
sns.countplot(data=wide_df, x=group_col, hue=gender_col, palette="Set2", ax=axes[0])
axes[0].set_title("Participants by NAO Behaviour & Gender")
axes[0].set_xlabel("NAO Behaviour"); axes[0].set_ylabel("Count")
axes[0].legend(title="Participant Gender")

# RPS histogram
sns.histplot(wide_df["RPS_score"], bins=range(1,10), color="goldenrod", ax=axes[1])
axes[1].set_title("Distribution of RPS Scores (1–9)")
axes[1].set_xlabel("Mean RPS"); axes[1].set_ylabel("Frequency")
axes[1].set_xlim(1,9)
axes[1].set_ylim(bottom=0)

fig_overview.tight_layout()

# -------------- 2. Composite means 2×2 ---------------------------------- #
composite_vars = ["Influence_mean", "Anthropomorphism_mean",
                  "Animacy_mean", "Likeability_mean"]
titles = ["Influence Composite", "Anthropomorphism",
          "Animacy", "Likeability"]

fig_comp_means, axes = plt.subplots(2,2, figsize=(10,8), sharey=True)
axes = axes.flatten()

for ax, var, title in zip(axes, composite_vars, titles):
    melt = wide_df[[group_col, var]].dropna()
    sns.barplot(data=melt, x=group_col, y=var, palette=palette, ci=None, ax=ax)
    stats = melt.groupby(group_col)[var].agg(["mean","std"])
    for i, (cond,row) in enumerate(stats.iterrows()):
        ax.errorbar(i, row["mean"], yerr=row["std"],
                    fmt='none', ecolor='black', capsize=6, capthick=1, lw=1)
    ax.set_title(title)
    ax.set_ylim(1,5)
    ax.set_xlabel(""); ax.set_ylabel("Likert Mean")
    ax.set_xticklabels(["CONTROL","RISK"])

fig_comp_means.suptitle("Composite Ratings (Mean ± SD) by NAO Behaviour", fontsize=14)
fig_comp_means.tight_layout(rect=[0,0.03,1,0.95])

# -------------- 3. Composite distributions ------------------------------ #
fig_comp_dists, axes = plt.subplots(2,2, figsize=(10,8))
axes = axes.flatten()
bin_edges = [1,2,3,4,5,6]  # width 1 bins

for ax, var, title in zip(axes, composite_vars, titles):
    for cond,color in palette.items():
        sns.histplot(wide_df.query(f"{group_col}==@cond")[var],
                     bins=bin_edges, alpha=0.5, ax=ax, color=color,
                     label=cond if var=="Influence_mean" else "")
    ax.set_title(f"{title} Distribution")
    ax.set_xlabel("Mean Rating"); ax.set_ylabel("Frequency")
    ax.set_xlim(1,5); ax.set_ylim(0,7)
    if var=="Influence_mean":
        ax.legend(title="NAO Behaviour")

fig_comp_dists.suptitle("Composite Score Distributions by NAO Behaviour", fontsize=14)
fig_comp_dists.tight_layout(rect=[0,0.03,1,0.95])

# -------------- 4. Scatter RPS vs Influence ------------------------------ #
fig_scatter = plt.figure(figsize=(6,5))
sns.scatterplot(data=wide_df, x="RPS_score", y="Influence_mean",
                hue=group_col, palette=palette, s=90)
plt.xlabel("RPS Score (1–9)"); plt.ylabel("Influence Composite (1–5)")
plt.title("RPS vs. Perceived Influence by NAO Behaviour")
plt.xlim(1,9); plt.ylim(1,5)
plt.legend(title="NAO Behaviour")
plt.tight_layout()

# -------------- 5. Save to PDF ------------------------------------------- #
out_dir = Path("documents")
fig_overview.savefig(out_dir/"overview.pdf", bbox_inches="tight", pad_inches=0.02)
fig_comp_means.savefig(out_dir/"composite_means.pdf", bbox_inches="tight", pad_inches=0.02)
fig_comp_dists.savefig(out_dir/"composite_distributions.pdf", bbox_inches="tight", pad_inches=0.02)
fig_scatter.savefig(out_dir/"rps_vs_influence.pdf", bbox_inches="tight", pad_inches=0.02)

print("PDFs saved to:", out_dir)
