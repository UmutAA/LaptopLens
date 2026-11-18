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
 
- **Web Scraping:** Custom headers, session reuse, and randomized delays to collect product links, names, and prices.
- **Local HTML Storage:** Category pages are saved locally so parsing can be debugged offline.
- **Multi-Page Pagination:** Iterates through multiple category pages using a custom page indicator.
- **Price Normalization:** Converts Turkish-formatted currency strings into numerical prices (under validation, see *Current Status*).
- **LLM-Powered Feature Extraction:** Uses the Google Gemini API to extract structured specifications (brand, model, CPU, RAM, GPU, VRAM, storage, refresh rate, screen size, OS) from unstructured product titles.
- **Prompt Engineering with Iteration:** Evolved from zero-shot to one-shot to few-shot prompting to standardize inconsistent values (see below).
- **CSV Export:** Produces UTF-8 encoded CSV datasets ready for data science and machine learning workflows.
## Project Structure
 
```
LaptopLens/
├── data/
│   ├── products_raw.csv         # Scraped links, names, prices
│   └── enriched_products.csv    # Raw data plus Gemini-extracted specs
├── scripts/
│   ├── scraper.py               # Page downloading, link parsing, price/name extraction
│   └── feature_extractor.py     # Sends product names to Gemini to extract structured features
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```
 
> Note: a `categories/` folder (cached category HTML pages) is created at runtime and is excluded from version control via `.gitignore`.
 
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
 
The scripts use relative paths (`../data`, `../categories`), so run them from inside the `scripts/` folder:
 
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
 
## Prompt Strategy Evolution
 
The first implementation used **zero-shot prompting**, which produced unstructured output. Moving to **one-shot prompting** improved the structure, but caused inconsistencies because storage capacities appeared in many formats (`1TB`, `1000GB`, `1024GB`). To standardize them into precise integers (in GB), the system moved to a **few-shot prompting** strategy with multiple examples mapping different storage notations to a single canonical value.
 
## Current Status
 
- Scraping and LLM-based feature extraction are working end to end.
- Price parsing is being verified against the live site; some stored prices do not yet match the website.
- Phase 1 below is in progress.
## Roadmap / Next Steps
 
The roadmap is ordered so that each stage builds on the previous one and produces a tangible, demonstrable result.
 
### Phase 1: Data Quality & Reliability
 
- [x] **Price parsing verification:** validate scraped prices against the website and fix Turkish number-format handling.
- [ ] **Structured output with schema validation:** enforce Gemini JSON output and validate it with `pydantic` (types, allowed ranges, required fields).
- [ ] **Extraction accuracy evaluation:** manually label a gold-standard sample (e.g., 100-200 listings) and report per-field accuracy/precision/recall of the LLM extraction. Compare zero-shot vs. one-shot vs. few-shot quantitatively.
- [x] **Error handling at scale:** retries with exponential backoff, rate-limit handling, and caching of API responses to cut cost and make runs reproducible.
- [ ] **Data cleaning report:** duplicates, missing values, outliers, and inconsistent categories documented in a notebook.
- [x] **Responsible scraping:** respect `robots.txt`, use polite request delays, and document data-use limitations.
### Phase 2: Exploratory Data Analysis & Feature Engineering
 
- [ ] **In-depth EDA notebook:** price distributions, brand/CPU/RAM effects, correlations, and clearly written business insights with visualizations.
- [ ] **Feature engineering:** CPU generation/tier parsing (e.g., i5-10th gen vs. Ryzen 5), GPU class and tier (e.g., RTX 4050 vs. RTX 4070), storage size, and screen size/refresh rate.
- [ ] **Statistical testing:** verify observed price differences (e.g., between brands or RAM sizes) with appropriate tests rather than eyeballing charts.
### Phase 3: Price Prediction Model
 
- [ ] **Baselines first:** Linear/Ridge Regression as a reference point.
- [ ] **Tree-based models:** Random Forest, XGBoost / LightGBM with cross-validation and hyperparameter tuning (Optuna or GridSearchCV).
- [ ] **Proper evaluation:** MAE, RMSE, MAPE, R² with a held-out test set; avoid data leakage via scikit-learn `Pipeline`s.
- [ ] **Explainability:** SHAP values to show *why* the model predicts a given price and which specs matter most.
- [ ] **Error analysis:** investigate where the model fails (rare brands, extreme prices) and discuss limitations honestly.
### Phase 4: Deal Detection
 
- [ ] **"Fair price" estimator:** compare predicted vs. listed price to flag undervalued and overpriced listings.
- [ ] **Anomaly detection:** Isolation Forest / residual-based methods to surface suspicious or exceptional listings.
### Phase 5: Embeddings & Semantic Search
 
- [ ] **Vector embeddings:** generate embeddings for enriched product descriptions with Gemini embedding models.
- [ ] **Semantic recommendation engine:** natural-language queries such as *"gaming laptop with RTX 4060 under 50,000 TL"* returning the most relevant listings (cosine similarity, optionally a vector store like FAISS or ChromaDB).
- [ ] **Retrieval evaluation:** measure relevance with a small set of test queries (e.g., Precision@k).
### Phase 6: Productionization & Engineering Practices
 
- [ ] **Interactive demo app:** Streamlit (or FastAPI + simple frontend) where users enter specs, get a predicted fair price, and search similar listings.
- [ ] **Persistent storage:** move from CSV-only to SQLite/PostgreSQL, and collect data periodically to build a **price-over-time dataset** (trend and seasonality analysis).
- [ ] **Experiment tracking:** log models, parameters, and metrics with MLflow.
- [ ] **Code quality:** unit tests (`pytest`) for parsers and normalizers, linting (`ruff`/`black`), type hints.
- [ ] **CI & containerization:** GitHub Actions for tests, and a `Dockerfile` for reproducible runs.
- [ ] **Documentation:** architecture diagram, results section with real metrics and screenshots, and a short write-up of key findings and limitations.
## Planned Tech Stack
 
`Python` · `requests` / `BeautifulSoup` · `pandas` · `Gemini API` · `pydantic` · `scikit-learn` · `XGBoost / LightGBM` · `SHAP` · `FAISS / ChromaDB` · `Streamlit` · `SQLite / PostgreSQL` · `MLflow` · `pytest` · `Docker` · `GitHub Actions`
 
## Results
 
*Results will be added here as phases are completed: extraction accuracy, model metrics, feature importance plots, and demo screenshots.*
 
## Disclaimer
 
This project is for educational purposes. Scraped data belongs to its respective owners and should be used in accordance with the website's terms of service.
 