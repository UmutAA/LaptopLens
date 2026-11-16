# LaptopLens: Second-Hand Laptop Market Intelligence Pipeline

An end-to-end data science project that turns messy second-hand e-commerce listings into structured, analysis-ready data, and uses it to **understand, predict, and explain laptop prices**.

LaptopLens scrapes second-hand laptop listings from idefix.com, uses the Gemini API (LLM) to convert unstructured product titles into structured technical specifications (brand, processor, RAM, GPU, storage), and prepares the resulting dataset for exploratory analysis, price prediction, deal detection, and semantic search.

> Built as a data science course project, designed to follow the full lifecycle of a real-world data product: **data collection → data quality → analysis → modeling → deployment**.

## Why This Project?

Second-hand listings are noisy: titles are inconsistent, specs are buried in free text, and prices vary wildly. Buyers cannot easily tell whether a listing is a good deal. LaptopLens answers questions such as:

- Which specs (RAM, CPU generation, GPU, storage) drive the price the most?
- What should a laptop with given specs *fairly* cost?
- Which listings are significantly under- or over-priced?
- Which laptops are most similar to the one I am looking for?

## Features

- **Robust Web Scraping:** Custom headers and parameters to collect product links, names, and prices efficiently.
- **Local HTML Caching:** Category pages are stored locally for offline debugging and to avoid redundant requests to the server.
- **Multi-Page Pagination:** Dynamically iterates through multiple category pages using custom page indicators.
- **Data Normalization:** Converts currency strings and raw text into clean numerical prices.
- **LLM-Powered Feature Extraction:** Uses the Google Gemini API to extract structured specifications (brand, processor, RAM, GPU, storage) from unstructured product titles.
- **Prompt Engineering with Iteration:** Moved from one-shot to few-shot prompting to standardize inconsistent values (see below).
- **CSV Export:** Produces clean, encoded CSV datasets ready for data science and machine learning workflows.

## Project Structure

```
└── data
    ├── enriched_products.csv   
    └── products_raw.csv
└── scripts
    ├── scraper.py             # Multi-page HTML downloading, link parsing, price/name extraction
    └── feature_extractor.py   # Sends raw product names to Gemini API to extract structured features
├── .gitignore
├── README.md
├── requirements.txt
└── .env.example
```

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

1. **Scrape products:** collect product links, names, and prices into a CSV file.

   ```
   python scraper.py
   ```

2. **Enrich the dataset:** process product names with Gemini and generate structured attributes.

   ```
   python feature_extractor.py
   ```

## Prompt Strategy Evolution

The first implementation used **one-shot prompting**. This caused inconsistencies because storage capacities appeared in many formats (`1TB`, `1000GB`, `1024GB`). To standardize them into precise integers (in GB), the system moved to a **few-shot prompting** strategy with multiple examples mapping different storage notations to a single canonical value.

---

## Roadmap

A single, ordered path: finishing every phase below completes the whole project. Each phase is one work session and builds on the previous one. The whole path is planned as roughly one month of work, one phase per sitting.

### Phase 1: Data Quality & Reliability
- [ ] **Goal:** make data collection and extraction robust and reproducible.
  - Structured Gemini output enforced and validated with `pydantic` (types, allowed ranges, required fields).
  - Retries with exponential backoff, rate-limit handling, and caching of API responses.
  - Responsible scraping: respect `robots.txt`, polite request delays, document data-use limits.

### Phase 2: Extraction Evaluation & Data Cleaning
- [ ] **Goal:** measure how good the LLM extraction really is and clean the dataset.
  - Manually label a gold-standard sample (100-200 listings); report per-field accuracy / precision / recall.
  - Quantitative comparison of one-shot vs. few-shot prompting.
  - Data cleaning report: duplicates, missing values, outliers, inconsistent categories (notebook).

### Phase 3: Exploratory Data Analysis & Statistical Testing
- [ ] **Goal:** understand the market before modeling.
  - EDA notebook: price distributions, brand / CPU / RAM effects, correlations, business insights with visualizations.
  - Statistical tests (t-test / ANOVA / Mann-Whitney, Kruskal-Wallis) to verify price differences between brands and RAM sizes.

### Phase 4: Feature Engineering
- [ ] **Goal:** turn raw LLM-extracted specs into a model-ready feature set.
  - CPU: brand, family, generation, tier, suffix (U/H/HQ/HX). GPU: dedicated vs. integrated, brand, class, VRAM.
  - Memory/storage: `ram_gb`, `storage_gb`, storage type (SSD/HDD), log transforms.
  - Brand: frequency / target encoding, segment (premium / mainstream / budget), rare-brand grouping.
  - Title text: gaming, ultrabook, touchscreen, screen size. Target: `log1p(price)`.
  - Everything wrapped in a scikit-learn `Pipeline` + `ColumnTransformer` to avoid data leakage; code in `src/features.py`.

### Phase 5: Grid Search
- [ ] **Goal:** systematically search preprocessing + feature-set choices.
  - `GridSearchCV` with repeated 5-fold CV (primary metric MAE; also RMSE and R²).
  - Dimensions: categorical encoding (One-Hot / Ordinal / Target), scaling (None / Standard / Robust), target transform (raw / log), feature set (base / + CPU-GPU / + text / all), outlier handling (none / IQR / winsorize).
  - Save every combination to `results/grid_search_results.csv`; summarize which transformations helped most.

### Phase 6: Baselines, Model Comparison & Score Table
- [ ] **Goal:** train every candidate model under identical conditions and fill the score table.
  - Regression: Dummy, Linear, Ridge, Lasso, ElasticNet, KNN, SVR, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM.
  - Metrics: MAE, RMSE, MAPE, R², CV mean ± std, training time.
  - Price-segment classification (budget / mid / premium by price quantiles): Accuracy, Precision, Recall, F1 (macro and weighted), ROC-AUC, plus per-class report and confusion matrix for the best model.
  - Same split and same CV folds for all models; tables auto-generated into `results/model_scores.csv` and copied to the Results section.

### Phase 7: Hyperparameter Tuning
- [ ] **Goal:** tune the strongest models and quantify the gain.
  - Coarse `RandomizedSearchCV`, then fine search with Optuna (TPE + pruner, 100+ trials); early stopping for XGBoost / LightGBM.
  - Nested cross-validation for an unbiased estimate.
  - Set up MLflow tracking and log all runs from here on.
  - Before vs. after tuning table, `results/best_params.json`, Optuna history / importance plots.

### Phase 8: Ablation Study I: Feature Groups
- [ ] **Goal:** find out which feature groups really matter (tuned model, 5 seeds, mean ± std).
  - Leave-one-group-out: A0 full model, A1 −CPU, A2 −GPU, A3 −RAM, A4 −Storage, A5 −Brand, A6 −Text features, A7 only CPU + RAM + Storage.
  - Forward addition curve: Brand → +CPU → +RAM → +Storage → +GPU → +Text (cumulative R² / MAE, marginal gain per group).

### Phase 9: Ablation Study II: Engineering, Data Quality & Data Size
- [ ] **Goal:** test the pipeline decisions and the LLM data quality.
  - Feature engineering: B1 raw vs. engineered features, B2 CPU parsing on/off, B3 log vs. raw target, B4 rare-brand grouping, B5 interaction features.
  - Data quality: C1 one-shot vs. few-shot extracted data (downstream effect), C2 outlier removal, C3 duplicate removal, C4 complete rows vs. imputed rows, C5 simulated extraction noise (5 / 10 / 20% corrupted RAM/CPU values).
  - Learning curve (10% → 100% of data) and model-complexity sweep (bias-variance).
  - Summary table (experiment → MAE / RMSE / R² → Δ vs. A0), ΔR² bar chart, paired t-test / Wilcoxon on per-fold scores, short "Key findings" paragraph.

### Phase 10: Explainability & Error Analysis
- [ ] **Goal:** explain *why* the model predicts a given price and where it fails.
  - Global: SHAP summary and bar plots, permutation importance (cross-check vs. impurity importance), PDP / ICE for RAM, CPU tier, storage, GPU class, SHAP dependence plots for interactions.
  - Local: SHAP waterfall / force plots (typical laptop, underpriced, overpriced, worst-predicted), LIME comparison, counterfactual "what-if" (e.g., 8 GB → 16 GB RAM in TL).
  - Consistency check against Ridge coefficients.
  - Error analysis by brand, price band, and CPU tier (residual plots, MAPE per segment); bias check and honest limitations.

### Phase 11: Deal Detection
- [ ] **Goal:** turn the model into a buyer-facing tool.
  - "Fair price" estimator: predicted vs. listed price flags undervalued and overpriced listings.
  - Anomaly detection with Isolation Forest and residual-based methods for suspicious or exceptional listings.

### Phase 12: Embeddings & Semantic Search
- [ ] **Goal:** natural-language search over listings.
  - Gemini embeddings for enriched product descriptions.
  - Semantic recommendation (cosine similarity, optionally FAISS / ChromaDB) for queries like *"light laptop for programming under 20,000 TL"*.
  - Retrieval evaluation with a small set of test queries (Precision@k).

### Phase 13: Interactive Demo & Storage
- [ ] **Goal:** ship the demo.
  - Streamlit app: enter specs → predicted fair price with a SHAP-based "Why this price?" panel, plus similar-listing search and deal flags.
  - Move from CSV-only to SQLite / PostgreSQL and add periodic collection for a price-over-time dataset (trend and seasonality).

### Phase 14: Engineering Quality & Final Documentation
- [ ] **Goal:** make the project reproducible and presentable.
  - Unit tests (`pytest`) for parsers and normalizers, linting (`ruff` / `black`), type hints.
  - GitHub Actions CI and a `Dockerfile`.
  - Fill the Results section with real metrics, figures, and screenshots; add an architecture diagram and a short write-up of key findings and limitations.

---

## Planned Tech Stack

`Python` · `requests` / `BeautifulSoup` · `pandas` · `Gemini API` · `pydantic` · `scikit-learn` · `XGBoost / LightGBM` · `Optuna` · `SHAP` · `LIME` · `FAISS / ChromaDB` · `Streamlit` · `SQLite / PostgreSQL` · `MLflow` · `pytest` · `Docker` · `GitHub Actions`

## Results

*Filled in as phases are completed.*

### Model Scores: Price Regression (Phase 6)

| Model | MAE (TL) ↓ | RMSE (TL) ↓ | MAPE (%) ↓ | R² ↑ | CV R² (mean ± std) | Train time (s) |
|---|---|---|---|---|---|---|
| Dummy (mean) | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Linear Regression | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Ridge | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Lasso | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| ElasticNet | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| KNN Regressor | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| SVR | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Decision Tree | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Random Forest | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Gradient Boosting | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| XGBoost | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| LightGBM | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

### Model Scores: Price-Segment Classification (Phase 6)

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) | F1 (weighted) | ROC-AUC (OvR) |
|---|---|---|---|---|---|---|
| Dummy (most frequent) | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Logistic Regression | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| KNN | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| SVM | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Decision Tree | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Random Forest | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| XGBoost | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| LightGBM | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

### Hyperparameter Tuning: Before vs. After (Phase 7)

*TBD*

### Ablation Study Summary (Phases 8-9)

*TBD*

### Explainability (Phase 10)

*TBD: SHAP summary plot, example local explanations.*

## Disclaimer

This project is for educational purposes. Scraped data belongs to its respective owners and should be used in accordance with the website's terms of service.