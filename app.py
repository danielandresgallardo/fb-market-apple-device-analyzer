import json
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# === Setup Directories ===
data_dir = "data"
output_data_dir = "output/data"
output_plots_dir = "output/plots"
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(output_plots_dir, exist_ok=True)

all_data = []

# === Load JSON files ===
for filename in os.listdir(data_dir):
    if filename.endswith(".json") and filename.startswith("marketplace"):
        match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
        file_date = None
        if match:
            try:
                file_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            except ValueError:
                pass

        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
                for item in file_data:
                    item["date"] = file_date
                all_data.extend(file_data)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

print(f"Loaded {len(all_data)} listings from {data_dir}")

# === Extraction Functions ===
def extract_macbook_model(title):
    title = title.lower()
    if "macbook" not in title:
        return "Not MacBook", None, None

    is_air = "air" in title
    is_pro = "pro" in title

    # Match M1/M2/M3/M4 variants including pro/max
    processor_match = re.search(r"m(1|2|3|4)\s*(pro|max)?", title)
    processor = None
    if processor_match:
        base = f"M{processor_match.group(1)}"
        variant = processor_match.group(2)
        if variant:
            processor = f"{base}{variant.capitalize()}"
        else:
            processor = base
    else:
        # Fallback to Intel i7/i9
        intel_match = re.search(r"\bi(7|9)\b", title)
        if intel_match:
            processor = f"Intel i{intel_match.group(1)}"

    # Screen size
    size_match = re.search(r"(13|14|15|16)(\s*\"|\s*inch)?", title)
    screen = f"{size_match.group(1)}" if size_match else "Unknown"

    if is_air:
        return "MacBook Air", processor or "Unknown", screen

    if is_pro:
        return "MacBook Pro", processor or "Unknown", screen

    return "MacBook Unknown", processor or "Unknown", screen

def extract_storage(title):
    title = title.lower()
    match = re.search(r"\b(256|512|1024|2048|4096)\s*(g|gb|t|tb)?\b", title)
    if match:
        size = int(match.group(1))
        return size * 1024 if 't' in (match.group(2) or '') else size
    return "Unknown"

def extract_ram(title):
    title = title.lower()
    match = re.search(r"\b(8|16|24|32|64|96|128)\s*(g|gb)?\b", title)
    if match:
        return int(match.group(1))
    return "Unknown"

def extract_warranty(title):
    title = title.lower()
    has_applecare = "applecare" in title.replace(" ", "")
    if "保固內" in title:
        return "In Warranty"
    elif "過保" in title:
        return "Expired Warranty"
    elif has_applecare:
        return "AppleCare"
    return "Unknown"

def parse_price(price_str):
    try:
        price_str = price_str.strip().lower()
        if price_str in ["free", "0", "nt$0", "nt$0.00"]:
            return 0
        return int(re.sub(r"[^\d]", "", price_str))
    except:
        return None

# === Normalize and Filter ===
for item in all_data:
    model, processor, screen_size = extract_macbook_model(item["title"])
    item["model"] = model
    item["processor"] = processor
    item["screen_size"] = screen_size
    item["storage"] = extract_storage(item["title"])
    item["ram"] = extract_ram(item["title"])
    item["warranty"] = extract_warranty(item["title"])
    item["price_num"] = parse_price(item["price"])

# === DataFrame ===
df = pd.DataFrame(all_data)

def normalize_link(link):
    return re.sub(r"\?.*$", "", link) if isinstance(link, str) else link

df["normalized_link"] = df["link"].apply(normalize_link)
df = df.drop_duplicates(subset="normalized_link", keep="first")
df_clean = df[df["model"].str.startswith("MacBook") & (df["model"] != "MacBook Unknown")]
df_clean = df_clean.dropna(subset=["price_num"])
df_clean = df_clean[df_clean["price_num"] > 0]

# === Summary Stats ===
summary = df_clean.groupby(["model", "processor", "screen_size", "ram", "storage", "warranty"]).agg(
    count=("price_num", "count"),
    min_price=("price_num", "min"),
    max_price=("price_num", "max"),
    avg_price=("price_num", "mean")
).reset_index()

# === Save ===
df_clean = df_clean.drop(columns=["link"])
df_clean.to_csv(os.path.join(output_data_dir, "macbook_data_clean.csv"), index=False)
summary.to_csv(os.path.join(output_data_dir, "macbook_summary_stats.csv"), index=False)

# === Visualization ===
sns.set(style="whitegrid")

# Boxplot
plt.figure(figsize=(16, 10))
sns.boxplot(data=df_clean, x="model", y="price_num", hue="ram")
plt.xticks(rotation=45)
plt.title("Price Distribution by MacBook Model and RAM")
plt.ylabel("Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "macbook_boxplot.png"))
plt.close()

# Histogram
plt.figure(figsize=(16, 10))
sns.histplot(df_clean["price_num"], bins=30, kde=True)
plt.title("Histogram of MacBook Listing Prices")
plt.xlabel("Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "macbook_price_histogram.png"))
plt.close()

print(f"Saved {len(df_clean)} MacBook listings to macbook_data_clean.csv")
print(f"Saved summary to macbook_summary_stats.csv")