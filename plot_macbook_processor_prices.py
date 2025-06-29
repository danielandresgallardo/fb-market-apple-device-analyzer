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

# Filter only MacBook Air and MacBook Pro models
models_to_plot = ["MacBook Air", "MacBook Pro"]
screen_sizes_to_plot = ["13", "14", "15", "16"]

sns.set(style="whitegrid")

for model in models_to_plot:
    for size in screen_sizes_to_plot:
        df_sub = summary[(summary["model"] == model) & (summary["screen_size"] == size)]

        if df_sub.empty:
            continue  # Skip if no data for this combo

        plt.figure(figsize=(10, 6))
        df_sub_sorted = df_sub.sort_values(by="avg_price", ascending=False)

        sns.barplot(
            x="processor",
            y="avg_price",
            data=df_sub_sorted,
            palette="viridis"
        )

        plt.title(f"Average Price by Processor for {model} {size}\"")
        plt.xlabel("Processor")
        plt.ylabel("Average Price (NTD)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        filename_safe_model = model.replace(" ", "_")
        plt.savefig(os.path.join(output_plots_dir, f"{filename_safe_model}_{size}inch_avg_price.png"))
        plt.close()

print("Plots saved to", output_plots_dir)