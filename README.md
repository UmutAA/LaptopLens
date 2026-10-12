# E-Commerce Web Scraper & AI Feature Extractor

A modular, robust, and anti-ban Python pipeline designed to scrape product data from e-commerce sites (specifically built for **idefix.com**) and enrich raw text titles into structured, machine-learning-ready datasets using the Gemini API.

---

## Features

- **Robust Web Scraping**: Utilizes custom `HEADERS` (User-Agent, Accept-Language) to bypass basic bot detection and rate-limiting.
- **Local HTML Caching**: Downloads category pages locally (`../categories_X.html`) to enable offline debugging and avoid redundant server requests.
- **Multi-Page Pagination**: Dynamically iterates through multiple category pages using custom `page_indicator` query parameters.
- **Data Normalization**: Cleans currency strings, dots, and commas into clean, float-type numerical prices.
- **AI-Powered Feature Extraction**: Integrates Google's Gemini API to extract structured technical specifications (Brand, Processor, RAM, GPU, Storage) directly from unstructured product titles.
- **CSV Export**: Compiles clean, UTF-8-sig encoded CSV datasets ready for Data Science and Machine Learning workflows.

---

## Project Structure

```text
├── scraper.py             # Handles multi-page HTML downloading, link parsing, and price/name extraction
└── feature_extractor.py   # Sends raw product names to Gemini API to extract structured features
```

---

## Prerequisites & Installation

Make sure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

Set up your Gemini API key in your environment variables:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

---

## How to Run

1. **Scrape Products**: Run the primary scraper to collect product links, names, and prices into a CSV file:
   ```bash
   python scraper.py
   ```
2. **Enrich Dataset**: Run the feature extractor script to process product names with Gemini and generate structured attributes.

---

## Next Steps

- LLM Prompt Strategy Optimization: Experiment with One-Shot and Few-Shot 
prompting techniques to maximize extraction accuracy for complex or messy product titles.


- Model & Prompt Comparison: Benchmark different prompting strategies and model 
configurations (e.g., standard vs. structured JSON output) to minimize extraction errors.


- Iterative User Feedback Loop: Incorporate custom user comments and domain-specific 
rules to iteratively refine LLM instructions and engineer entirely new synthetic features.


- Vector Embeddings & Semantic Search: Generate vector embeddings for the enriched product
descriptions using Gemini's embedding models to build a semantic recommendation engine and similarity search pipeline.