# LaptopLens: Gaming Laptop Market Intelligence Pipeline

An end-to-end data science project that turns messy gaming laptop e-commerce listings into structured, analysis-ready data, and uses it to **understand, predict, and explain laptop prices**.

LaptopLens scrapes gaming laptop listings from idefix.com, uses the Gemini API (LLM) to convert unstructured product titles into structured technical specifications (brand, processor, RAM, GPU, storage), and prepares the resulting dataset for exploratory analysis, price prediction, deal detection, and semantic search.

> Built as a data science course project, designed to follow the full lifecycle of a real-world data product: **data collection → data quality → analysis → modeling → deployment**.

## Why This Project?

Gaming laptop listings are noisy: titles are inconsistent, specs are buried in free text, and prices vary wildly. Buyers cannot easily tell whether a listing is a good deal. LaptopLens answers questions such as:

- Which specs (RAM, CPU generation, GPU, storage) drive the price the most?
- What should a laptop with given specs *fairly* cost?
- Which listings are significantly under- or over-priced?
- Which laptops are most similar to the one I am looking for?

## Features

- **Web Scraping:** Custom headers, session reuse, randomized delays, and request timeouts to collect product links, names, and prices.
- **Local HTML Storage:** Category pages are saved locally and reused on later runs. Product pages are stored compressed so parsing can be fixed offline without re-scraping.
- **Price Provenance:** Each record keeps the raw price text, the selector that matched, and the scrape date.
- **Price Normalization:** Converts Turkish-formatted currency strings into numerical prices (re-verification against the live site is pending, see *Current Status*).
- **LLM-Powered Feature Extraction:** Uses the Google Gemini API with a pydantic schema (structured JSON output) to extract brand, model, CPU, RAM, GPU, VRAM, storage, refresh rate, screen size, and OS from product titles.
- **Prompt Engineering with Iteration:** Evolved from zero-shot to one-shot to few-shot prompting to standardize inconsistent values (see below).
- **Data Cleaning:** Documented in a notebook: invalid prices removed, non-laptop products removed, GPU names standardized, missing VRAM handled, storage errors corrected.
- **EDA and Statistical Testing:** Price drivers analyzed with effect-size-aware non-parametric tests.
- **Feature Engineering:** CPU family/tier/series/suffix parsed from messy CPU strings, GPU generation/tier/Ti flag and GPU variant (e.g. RTX 5070 8GB vs. 12GB) derived, saved as a model-ready table.

## Project Structure

```
LaptopLens/
├── data/
│   ├── products_raw.csv         # Scraped links, names, prices
│   ├── enriched_products.csv    # Raw data plus Gemini-extracted specs
│   ├── cleaned_products.csv     # Analysis-ready dataset
│   └── features.csv             # Model-ready features and target (log price)
├── notebooks/
│   ├── 01_data_cleaning.ipynb   # Data cleaning report
│   ├── 02_eda.ipynb             # EDA and statistical tests
│   └── 03_feature_engineering.ipynb  # CPU/GPU feature extraction
├── scripts/
│   ├── scraper.py               # Category/product page scraping and price parsing
│   └── feature_extractor.py     # Sends product names to Gemini to extract structured features
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

> Note: `categories/`, `product_html/`, and `data/snapshots/` are created at runtime and are excluded from version control via `.gitignore`.

## Prerequisites & Installation

Make sure you have Python installed, then install the required dependencies:

```
pip install -r requirements.txt
```

Create a `.env` file based on the provided `.env.example` and add your Gemini API key:

```
GEMINI_API_KEY="your_api_key_here"
```

## How to Run

Run the scripts from inside the `scripts/` folder:

```
cd scripts
```

1. **Scrape products:** collect product links, names, and prices into `data/products_raw.csv`.

   ```
   python scraper.py
   ```

2. **Enrich the dataset:** process product names with Gemini and write structured attributes to `data/enriched_products.csv`.

   ```
   python feature_extractor.py
   ```

3. **Clean, explore, and build features:** run `notebooks/01_data_cleaning.ipynb` (produces `data/cleaned_products.csv`), then `notebooks/02_eda.ipynb`, then `notebooks/03_feature_engineering.ipynb` (produces `data/features.csv`).

## Prompt Strategy Evolution

The first implementation used **zero-shot prompting**, which produced unstructured output. Moving to **one-shot prompting** improved the structure, but caused inconsistencies because storage capacities appeared in many formats (`1TB`, `1000GB`, `1024GB`). To standardize them into precise integers (in GB), the system moved to a **few-shot prompting** strategy with multiple examples mapping different storage notations to a single canonical value.

## Current Status

- Phases 1 and 2 (data collection, cleaning, EDA, statistical testing, feature engineering) are done except for the open items below.
- **Open:** price parsing has been rewritten but not yet re-verified against the live site; extraction accuracy against a hand-labeled sample has not been measured.
- Next: Phase 3 (price prediction model) on `data/features.csv`.
- The cleaned dataset contains **1,681 listings** of gaming laptops with a dedicated NVIDIA RTX GPU. Listings without a dedicated GPU were removed, so results do not apply to office or ultrabook models.

## Roadmap / Next Steps

The roadmap is ordered so that each stage builds on the previous one and produces a tangible, demonstrable result.

### Phase 1: Data Quality & Reliability

- [x] **Structured output with schema validation:** enforce Gemini JSON output and validate it with `pydantic` (types, allowed ranges, required fields).
- [x] **Error handling at scale:** retries with exponential backoff, rate-limit handling, and caching of API responses to cut cost and make runs reproducible.
- [x] **Data cleaning report:** duplicates, missing values, outliers, and inconsistent categories documented in a notebook.
- [x] **Responsible scraping:** respect `robots.txt`, use polite request delays, and document data-use limitations.

### Phase 2: Exploratory Data Analysis & Feature Engineering

- [x] **In-depth EDA notebook:** price distributions, brand/GPU/RAM effects, correlations, and clearly written insights with visualizations.
- [x] **Feature engineering:** CPU family/tier/series/suffix parsing, GPU generation/tier/Ti flag and GPU variant (e.g., RTX 5070 8GB vs. 12GB); output saved to `data/features.csv`.
- [x] **Statistical testing:** verify observed price differences (e.g., between brands, OS, VRAM variants) with appropriate tests rather than eyeballing charts.

### Phase 3: Price Prediction Model

- [ ] **Baselines first:** Linear/Ridge Regression as a reference point.
- [ ] **Tree-based models:** Random Forest, XGBoost / LightGBM with cross-validation and hyperparameter tuning (Optuna or GridSearchCV).
- [ ] **Proper evaluation:** MAE, RMSE, MAPE, R² with a held-out test set (grouped split by `group_id`); avoid data leakage via scikit-learn `Pipeline`s.
- [ ] **Ablation study:** drop (or add back) one feature group at a time (GPU, CPU, RAM/storage, brand, OS, screen/refresh rate) and measure the change in grouped-CV MAE and R², to show which features actually carry the signal. Complements SHAP, which explains a single trained model.
- [ ] **Explainability:** SHAP values to show *why* the model predicts a given price and which specs matter most.
- [ ] **Error analysis:** investigate where the model fails (rare brands, extreme prices) and discuss limitations honestly.

### Phase 4: Deal Detection

- [ ] **"Fair price" estimator:** compare predicted vs. listed price to flag undervalued and overpriced listings.
- [ ] **Anomaly detection:** Isolation Forest / residual-based methods to surface suspicious or exceptional listings.

### Phase 5: Embeddings & Semantic Search

- [ ] **Vector embeddings:** generate embeddings for enriched product descriptions with Gemini embedding models.
- [ ] **Semantic recommendation engine:** natural-language queries such as *"gaming laptop with RTX 5060 under 130,000 TL"* returning the most relevant listings (cosine similarity, optionally a vector store like FAISS or ChromaDB).
- [ ] **Retrieval evaluation:** measure relevance with a small set of test queries (e.g., Precision@k).

### Phase 6: Productionization & Engineering Practices

- [ ] **Interactive demo app:** Streamlit (or FastAPI + simple frontend) where users enter specs, get a predicted fair price, and search similar listings.
- [ ] **Persistent storage:** move from CSV-only to SQLite/PostgreSQL, and collect data periodically to build a **price-over-time dataset** (trend and seasonality analysis).
- [ ] **Experiment tracking:** log models, parameters, and metrics with MLflow.
- [ ] **Code quality:** unit tests (`pytest`) for parsers and normalizers, linting (`ruff`/`black`), type hints.
- [ ] **CI & containerization:** GitHub Actions for tests, and a `Dockerfile` for reproducible runs.
- [ ] **Documentation:** architecture diagram, results section with real metrics and screenshots, and a short write-up of key findings and limitations.

## Planned Tech Stack

`Python` · `requests` / `BeautifulSoup` · `pandas` · `Gemini API` · `pydantic` · `scipy` · `seaborn` · `scikit-learn` · `XGBoost / LightGBM` · `SHAP` · `FAISS / ChromaDB` · `Streamlit` · `SQLite / PostgreSQL` · `MLflow` · `pytest` · `Docker` · `GitHub Actions`

## Results

Key findings from the EDA (1,681 listings, single collection date, prices in TL, prices not yet re-verified against the live site):

| Finding | Evidence |
|---|---|
| Price is right-skewed; `log(price)` is the modeling target | Skewness 1.52 raw, 0.29 after log |
| GPU tier is the main price driver | Median price from 68,397 TL (RTX 3050) to 414,744 TL (RTX 5090); RTX 5050 and 5060 are nearly equal (118,200 vs 122,606 TL) |
| RAM and storage matter beyond the GPU | Within one GPU tier, Spearman with price is 0.60 to 0.70 for RAM and 0.38 to 0.48 for storage |
| Refresh rate and screen size mostly mirror GPU tier | Inconsistent correlation sign inside a tier |
| RTX 5070 12 GB variants cost far more than 8 GB | +47% median, Cliff's delta 0.56 (large), p < 0.001 |
| Windows listings cost more than Free/DOS (same GPU) | +18% to +32% median, Cliff's delta 0.24 to 0.30 (small) |
| Brand matters within a GPU tier | Kruskal-Wallis p < 0.001; e.g. RTX 5070 median 243,244 TL (MSI) vs 156,212 TL (ASUS) |

These are associations in observational data. Brand, OS, and VRAM comparisons do not control for RAM, storage, or CPU, so they are not causal effects. Full limitations are in `notebooks/02_eda.ipynb`.

*Model metrics, feature importance plots, and demo screenshots will be added as later phases are completed.*

## Disclaimer

This project is for educational purposes. Scraped data belongs to its respective owners and should be used in accordance with the website's terms of service.