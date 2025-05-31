import pandas as pd, seaborn as sns, matplotlib.pyplot as plt
from pathlib import Path
sns.set(style="whitegrid")

# Load data
file_path = Path("hri-results.csv")
long_df = pd.read_csv(file_path)
wide_df = long_df.pivot(index="participant_id", columns="Question", values="Answer")

# Numeric conversions
influence_vars = [f"influence_{i}" for i in range(1,5)]
risk_vars      = [f"risk_q{i}" for i in range(1,8)]
wide_df[influence_vars] = wide_df[influence_vars].apply(pd.to_numeric, errors="coerce")
wide_df[risk_vars]      = wide_df[risk_vars].apply(pd.to_numeric, errors="coerce")
wide_df["Influence_mean"] = wide_df[influence_vars].mean(axis=1)
wide_df["RPS_score"]      = wide_df[risk_vars].mean(axis=1)

# Map turn answers to risk
turn_answer_map = {
    "turn_1": {"lockdown":"less", "monitor":"more"},
    "turn_2": {"health":"less", "order":"more"},
    "turn_3": {"vaccine":"less", "lie":"more"},
    "turn_4": {"emergency":"less", "disinformation":"more"},
    "turn_5": {"equity":"less", "unequal":"more"}
}
def risk_prop(row):
    scores=[]
    for turn, amap in turn_answer_map.items():
        ans=str(row.get(turn,"")).lower()
        if ans in amap:
            scores.append(1 if amap[ans]=="more" else 0)
    return sum(scores)/len(scores) if scores else None
wide_df["Risk_prop"] = wide_df.apply(risk_prop, axis=1)

# Categorise
wide_df["User Strategy"] = pd.cut(wide_df["Risk_prop"],
                                      bins=[-0.01,0.5,1.01],
                                      labels=["Risk Adverse","Risky"])

# Palette blue & yellow
palette = {"Risk Adverse": "#1F77B4",  # yellow
           "Risky":        "#FDBE35"}  # blue

# Plot
fig, axes = plt.subplots(1,2, figsize=(12,4), sharey=True)

# Influence composite distribution
for grp,color in palette.items():
    sns.histplot(data=wide_df[wide_df["User Strategy"]==grp],
                 x="Influence_mean", bins=[1,2,3,4,5,6], color=color,
                 alpha=0.7, ax=axes[0], label=grp)
axes[0].set_xlim(1,5)
axes[0].set_xlabel("Influence Composite (1–5)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Influence Composite")
axes[0].legend(title="User Strategy")

# RPS distribution
for grp,color in palette.items():
    sns.histplot(data=wide_df[wide_df["User Strategy"]==grp],
                 x="RPS_score", bins=range(1,10), color=color,
                 alpha=0.7, ax=axes[1])
axes[1].set_xlim(1,9)
axes[1].set_xlabel("RPS Score (1–9)")
axes[1].set_title("Risk Propensity Scale")

# Uniform y-axis
max_freq=max(ax.get_ylim()[1] for ax in axes)
for ax in axes:
    ax.set_ylim(0, max_freq)

plt.suptitle("Influence & RPS Distributions by User Strategy", y=1.05)
plt.tight_layout()

# Save
out_path=Path("documents/influence_rps_objective_measure.pdf")
plt.savefig(out_path, bbox_inches="tight", pad_inches=0.02)
print("Saved updated figure to:", out_path)
