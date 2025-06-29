# MacBook Marketplace Analyzer

A data analysis tool for extracting, normalizing, and visualizing used MacBook listings from Facebook Marketplace in Taiwan.

🔍 Overview
-----------
This project scrapes and analyzes JSON exports of Facebook Marketplace listings for MacBooks. It aims to provide insights into used MacBook prices, models, configurations, and value retention by comparing against official launch prices (planned).

✅ Features
-----------
- 📦 Data Extraction & Cleaning
  - Extracts MacBook model, processor (M1–M4, Pro/Max), screen size, RAM, storage, warranty status, and price.
  - Normalizes messy listing formats using robust regex-based extraction.
  - Deduplicates listings by normalized Facebook Marketplace URLs.

- 📊 Data Analysis
  - Generates summary statistics (count, min/max/average price) by model + config.
  - Outputs clean dataset and grouped stats as CSVs.
  - Includes Seaborn-based plots: boxplots and histograms of price distribution.

- 📁 Organized Output
  - Clean listings saved to: output/data/macbook_data_clean.csv
  - Summary statistics saved to: output/data/macbook_summary_stats.csv
  - Plots saved to: output/plots/

📂 Folder Structure
-------------------
data/                  # Raw JSON files from Facebook Marketplace
output/
├── data/              # Processed CSVs
└── plots/             # Visualizations (PNG)

🧠 Future Work
--------------
- 🎨 Front-End UI
  - Build a simple web UI for easier dataset uploads and result visualization.
  - Filter listings by model, RAM, screen size, etc.

- 🔍 Serial Number Dictionary
  - Add support for model number recognition (e.g., A2681 → MacBook Air M2 13-inch).
  - Maintain a JSON/CSV lookup table of model identifiers.

- 💰 Launch Price Comparison
  - Create and integrate a macbook_launch_prices.csv file.
  - Show used price vs. launch price with percent depreciation.

- 🌍 Multi-Language & Region Support
  - Handle different languages and formats (e.g., English, Chinese).
  - Extend to other regions (e.g., Hong Kong, Singapore).

- 📅 Temporal Trend Analysis
  - Track how used prices change over time per model.
  - Monthly average price visualizations.

- 🧪 ML-Based Matching (Optional)
  - Use NLP to better handle noisy or inconsistent titles.
  - Classify listings with missing attributes using learned patterns.

🛠 Requirements
---------------
- Python 3.8+
- pandas
- matplotlib
- seaborn

Install via pip:
pip install -r requirements.txt

📝 Usage
--------
1. Place your scraped Facebook Marketplace .json files inside the data/ folder.
2. Run the main script:
   python app.py
3. View outputs in the output/ directory.

Author: Daniel Andres Gallardo
License: MIT