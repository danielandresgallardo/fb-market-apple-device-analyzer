import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === Config ===
output_data_dir = "output/data"
output_plots_dir = "output/plots"
os.makedirs(output_plots_dir, exist_ok=True)

# === Load summary data ===
summary_path = os.path.join(output_data_dir, "macbook_summary_stats.csv")
summary = pd.read_csv(summary_path)

# Ensure correct type
summary["screen_size"] = summary["screen_size"].astype(str)

# === Plot config ===
models_to_plot = ["MacBook Air", "MacBook Pro"]
screen_sizes_to_plot = ["13", "14", "15", "16"]
sns.set(style="whitegrid")

# === Plotting ===
for model in models_to_plot:
    for size in screen_sizes_to_plot:
        df_sub = summary[(summary["model"] == model) & (summary["screen_size"] == size)]

        if df_sub.empty:
            continue

        plt.figure(figsize=(10, 6))
        df_sub_sorted = df_sub.sort_values(by="avg_price", ascending=False)

        sns.barplot(
            x="processor",
            y="avg_price",
            hue="processor",
            data=df_sub_sorted,
            palette="viridis",
            legend=False
        )

        plt.title(f"Average Price by Processor for {model} {size}\"")
        plt.xlabel("Processor")
        plt.ylabel("Average Price (NTD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        filename_safe_model = model.replace(" ", "_")
        filename = f"{filename_safe_model}_{size}inch_avg_price.png"
        filepath = os.path.join(output_plots_dir, filename)
        plt.savefig(filepath)
        plt.close()

print("All plots saved to", output_plots_dir)