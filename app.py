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

def extract_apple_model(title):
    title = title.lower()

    # === Filter out accessories and unrelated products ===
    excluded_keywords = [
        "keyboard", "鍵盤", "watch", "apple watch", "pencil",
        "巧控", "滑鼠", "mouse", "trackpad", "妙控", "耳機", "airpods", "鍵", "保護殼"
    ]
    if any(kw in title for kw in excluded_keywords):
        return "Not Apple Computer", None, None

    # === iPad Detection ===
    if "ipad" in title:
        if "mini" in title:
            model = "iPad Mini"
            screen = "8.3"
        elif "pro" in title:
            model = "iPad Pro"
        elif "air" in title:
            model = "iPad Air"
        else:
            model = "iPad"

        screen_match = re.search(r"(8\.3|10\.9|11|12\.9|13)(吋|inch|\"|”)?", title)
        if screen_match:
            screen = screen_match.group(1)
        elif model != "iPad Mini":
            screen = "Unknown"

        processor_match = re.search(r"m\s*([1234])", title)
        processor = f"M{processor_match.group(1)}" if processor_match else "Unknown"
        return model, processor, screen

    # === Other Macs (Mac mini, iMac, Mac Studio) ===
    if "mac mini" in title:
        model = "Mac mini"
    elif "mac studio" in title:
        model = "Mac Studio"
    elif "imac" in title:
        model = "iMac"
    elif "macbook" in title:
        model = None  # handled below
    else:
        return "Not Apple Computer", None, None

    # === Extract processor (M1–M4, Pro/Max/Ultra, Intel) ===
    processor_match = re.search(r"m\s*([1234])\s*(pro|max|ultra)?", title)
    processor = None
    if processor_match:
        base = f"M{processor_match.group(1)}"
        variant = processor_match.group(2)
        processor = f"{base}{variant.capitalize()}" if variant else base
    else:
        intel_match = re.search(r"\bi[3579]\b", title)
        if intel_match:
            processor = f"Intel {intel_match.group(0)}"
        else:
            processor = "Unknown"

    # === Screen size ===
    screen_match = re.search(r"(11|12|13|14|15|16|21\.5|24|27|30)(\.\d)?\s*(吋|inch|\"|”)?", title)
    screen = screen_match.group(1) if screen_match else "Unknown"

    # === MacBook model fallback ===
    if "macbook" in title:
        is_air = "air" in title
        is_pro = "pro" in title

        model_map = {
            "a1466": ("MacBook Air", "13"),
            "a1932": ("MacBook Air", "13"),
            "a2179": ("MacBook Air", "13"),
            "a2337": ("MacBook Air", "13"),  # M1 Air
            "a2681": ("MacBook Air", "13"),  # M2 Air
            "a3113": ("MacBook Air", "13"),  # M3 Air
            "a1534": ("MacBook Retina", "12"),
            "a1989": ("MacBook Pro", "13"),
            "a1990": ("MacBook Pro", "15"),
            "a2251": ("MacBook Pro", "13"),
            "a2141": ("MacBook Pro", "16"),
            "a2442": ("MacBook Pro", "14"),
            "a2485": ("MacBook Pro", "16"),
            "a2780": ("MacBook Pro", "14"),
            "a2786": ("MacBook Pro", "16"),
        }

        model_number_match = re.search(r"a\d{4}", title)
        if model_number_match:
            code = model_number_match.group(0)
            if code in model_map:
                model, model_screen = model_map[code]
                screen = model_screen
                return model, processor, screen

        if is_air:
            if processor and screen == "12":
                screen = "13"
            if screen not in ["13", "15"]:
                screen = "13"
            return "MacBook Air", processor, screen
        if is_pro:
            if screen not in ["13", "14", "15", "16"]:
                screen = "13"
            return "MacBook Pro", processor, screen
        if "retina" in title and screen == "12":
            return "MacBook Retina", processor, screen
        return "MacBook Unknown", processor, screen

    # === iMac or Mac mini/Studio ===
    return model, processor, screen

def extract_storage(title):
    title = title.lower()
    match = re.search(r"\b(256|512|1024|2048|4096)\s*(g|gb|t|tb)?\b", title)
    if match:
        size = int(match.group(1))
        return size * 1024 if 't' in (match.group(2) or '') else size
    return "Unknown"

def extract_ram(title):
    title = title.lower()

    # Try direct match: 8gb, 16g, etc.
    match = re.search(r"(?<![a-z0-9])(?<!m)(4|8|16|24|32|64|96|128)\s*(g|gb|記憶體|記)?(?!\w)", title)
    if match:
        return int(match.group(1))

    # Try combined format like 8+256 or 16/512
    combo_match = re.search(r"(?<!m)(4|8|16|24|32|64|96|128)\s*[\+/]\s*(256|512|1024|2048)", title)
    if combo_match:
        return int(combo_match.group(1))

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
    model, processor, screen_size = extract_apple_model(item["title"])
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

# === Save Clean Data ===
df_clean = df_clean.drop(columns=["link"])
df_clean.to_csv(os.path.join(output_data_dir, "apple_devices_data_clean.csv"), index=False)
summary.to_csv(os.path.join(output_data_dir, "apple_devices_summary_stats.csv"), index=False)

# === Save Unknown Processor Listings ===
unknown_processors = df[
    (df["processor"] == "Unknown") & df["model"].str.startswith("MacBook")
][["model", "screen_size", "processor", "title"]]
unknown_processors.to_csv(os.path.join(output_data_dir, "unknown_processors.csv"), index=False)

# === Save Unknown Storage Listings ===
unknown_storage = df[
    (df["storage"] == "Unknown") & df["model"].str.startswith("MacBook")
][["model", "screen_size", "storage", "title"]]
unknown_storage.to_csv(os.path.join(output_data_dir, "unknown_storage.csv"), index=False)

# === Save Unknown RAM Listings ===
unknown_ram = df[
    (df["ram"] == "Unknown") & df["model"].str.startswith("MacBook")
][["model", "screen_size", "ram", "title"]]
unknown_ram.to_csv(os.path.join(output_data_dir, "unknown_ram.csv"), index=False)

# === Export Unknown Model Listings ===
unknown_model_df = df[df["model"] == "MacBook Unknown"]
unknown_model_df[["model", "screen_size", "ram", "storage", "title"]].to_csv(
    os.path.join(output_data_dir, "unknown_apple_model.csv"),
    index=False
)
print(f"Saved {len(unknown_model_df)} unknown model listings to unknown_apple_model.csv")

# === Save Unknown Screen Size Listings ===
unknown_screen_size = df[
    (df["screen_size"] == "Unknown") & df["model"].str.startswith("MacBook")
][["model", "processor", "screen_size", "storage", "ram", "title"]]
unknown_screen_size.to_csv(os.path.join(output_data_dir, "unknown_screen_size.csv"), index=False)
print(f"Saved {len(unknown_screen_size)} unknown screen size listings to unknown_screen_size.csv")

# === Save Full Verification File ===
verification_cols = ["model", "processor", "screen_size", "storage", "ram", "title"]
df[verification_cols].to_csv(os.path.join(output_data_dir, "apple_devices_verification.csv"), index=False)
print(f"Saved verification file with {len(df)} listings to apple_devices_verification.csv")

# === Visualization ===
sns.set(style="whitegrid")

# Boxplot
plt.figure(figsize=(16, 10))
sns.boxplot(data=df_clean, x="model", y="price_num", hue="ram")
plt.xticks(rotation=45)
plt.title("Price Distribution by Apple Device Model and RAM")
plt.ylabel("Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "apple_devices_boxplot.png"))
plt.close()

# Histogram
plt.figure(figsize=(16, 10))
sns.histplot(df_clean["price_num"], bins=30, kde=True)
plt.title("Histogram of Apple Device Listing Prices")
plt.xlabel("Price (NTD)")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "apple_devices_price_histogram.png"))
plt.close()

print(f"Saved {len(df_clean)} Apple device listings to apple_devices_data_clean.csv")
print(f"Saved summary to apple_devices_summary_stats.csv")