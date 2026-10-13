# Second Hand Pricer

A modular and robust Python pipeline designed to scrape second-hand e-commerce data, specifically built for idefix.com, and enrich raw text titles into structured datasets using the Gemini API as part of a comprehensive data science course project.

## Features

* **Robust Web Scraping:** Utilizes custom headers and parameters to collect product links, names, and prices efficiently.
* **Local HTML Caching:** Downloads category pages locally to enable offline debugging and avoid redundant server requests.
* **Multi-Page Pagination:** Dynamically iterates through multiple category pages using custom page indicators.
* **Data Normalization:** Cleans currency strings and text into clean numerical prices.
* **AI Powered Feature Extraction:** Integrates Google Gemini API to extract structured technical specifications, including brand, processor, RAM, GPU, and storage, directly from unstructured product titles.
* **CSV Export:** Compiles clean encoded CSV datasets ready for Data Science and Machine Learning workflows.

## Project Structure

```text
├── scraper.py             # Handles multi-page HTML downloading, link parsing, and price/name extraction
└── feature_extractor.py   # Sends raw product names to Gemini API to extract structured features
```

## Prerequisites & Installation

Make sure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on the provided `.env.example` format and add your Gemini API key:

```env
GEMINI_API_KEY="your_api_key_here"
```

## How to Run

1. Scrape Products: Run the primary scraper to collect product links, names, and prices into a CSV file:
   ```bash
   python scraper.py
   ```
2. Enrich Dataset: Run the feature extractor script to process product names with Gemini and generate structured attributes:
   ```bash
   python feature_extractor.py
   ```

## Prompt Strategy Evolution

Initial implementation used a one-shot prompting approach. However, inconsistencies arose because storage capacities were written in various formats such as 1TB, 1000GB, or 1024GB. To standardize these values into precise integers, the system transitioned to a few-shot prompting strategy with multiple examples mapping different storage inputs correctly.

## Next Steps

* Vector Embeddings and Semantic Search: Generate vector embeddings for the enriched product descriptions using Gemini embedding models to build a semantic recommendation engine.