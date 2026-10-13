from google import genai
import json
import pandas as pd
import os
from dotenv import load_dotenv

def extract_features_batch(product_names: list[str], client: genai.Client, model_name: str):
    formatted_products = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(product_names)])
    prompt = f"""
        Extract the technical specifications for each of the following product names below (use ONLY provided name nothing else),
        and ONLY return it (no buzz words, fillers, markdown code blocks, etc.) just output the raw JSON array..
        
        The JSON format SHOULD have these exact keys: 
        "brand", "model", "cpu model", "ram" (number in GBs), "gpu model", "vram" (number in GBs), "storage" (number in GBs), "refresh rate" (number in Hz), "screen size" (number in inches), "OS" (Free, Windows, Linux, Mac)
        
        If a specification is not mentioned, search for the exact model in internet and find the missing specification if can't then assign it to null.
        
        Here is an example:
        
        Input: ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 512GB 140W RTX4050 6GB 16"" 144Hz DOS"
        Output:
        {{
          "brand": "ASUS",
          "model": "TUF GAMING A16 FA607NUG-RL213",
          "cpu model": "RYZEN 7-7445HS",
          "ram": 16,
          "gpu model": "RTX4050",
          "vram": 6,
          "storage": 512,
          "refresh rate": 144,
          "screen size": 16,
          "OS": "Free"
        }}
        
        Input: ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 1TB 140W RTX4050 6GB 16"" 144Hz DOS"
        Output:
        {{
          "brand": "ASUS",
          "model": "TUF GAMING A16 FA607NUG-RL213",
          "cpu model": "RYZEN 7-7445HS",
          "ram": 16,
          "gpu model": "RTX4050",
          "vram": 6,
          "storage": 1024,
          "refresh rate": 144,
          "screen size": 16,
          "OS": "Free"
        }}
        
        Input: ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 2TB 140W RTX4050 6GB 16"" 144Hz DOS"
        Output:
        {{
          "brand": "ASUS",
          "model": "TUF GAMING A16 FA607NUG-RL213",
          "cpu model": "RYZEN 7-7445HS",
          "ram": 16,
          "gpu model": "RTX4050",
          "vram": 6,
          "storage": 2048,
          "refresh rate": 144,
          "screen size": 16,
          "OS": "Free"
        }}
        
        Product Names: {formatted_products}
        """
    try:

        interaction = client.interactions.create(
            model=model_name,
            system_instruction="You are a precise data extraction assistant. Output only raw JSON.",
            input=prompt
        )
        raw_text = interaction.output_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        return json.loads(raw_text.strip())


    except Exception as e:
        print(f"GenAI Error for '{product_names}': {e}")
        return None


def main():
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    input_file = "../data/products_raw.csv"
    output_file = '../data/enriched_products.csv'

    print(f"Reading {input_file} file...")

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"'{input_file}' not found! Run first 'scrape.py'.")
        return
    START_INDEX = 0
    END_INDEX = df.shape[0]
    BATCH_SIZE = 20

    df_subset = df.iloc[START_INDEX:END_INDEX]
    print(f"\nProcessing rows from index {START_INDEX} to {END_INDEX} in batches of {BATCH_SIZE}...")

    enriched_data = []
    rows_list = df_subset.to_dict('records')

    for i in range(0, len(rows_list), BATCH_SIZE):
        batch_rows = rows_list[i:i + BATCH_SIZE]
        batch_names = [row['Name'] for row in batch_rows]

        print(f"\nProcessing batch {i // BATCH_SIZE + 1} ({len(batch_names)} products)...")

        extracted_features_list = extract_features_batch(batch_names, client, model_name="gemini-3.1-flash-lite")

        for idx, row in enumerate(batch_rows):
            link = row['Link']
            name = row['Name']
            price = row['Price']

            product_record = {'Link': link, 'Name': name, 'Price': price}

            features = None
            if extracted_features_list and idx < len(extracted_features_list):
                features = extracted_features_list[idx]

            if features and isinstance(features, dict):
                product_record.update(features)
            else:
                product_record.update({
                    "brand": None, "cpu model": None, "ram": None,
                    "gpu model": None, "vram": None, "storage": None,
                    "refresh rate": None, "screen size": None, "OS": None
                })

            enriched_data.append(product_record)

    if enriched_data:
        os.makedirs('../data', exist_ok=True)
        new_df = pd.DataFrame(enriched_data)

        if os.path.exists(output_file):
            df_existing = pd.read_csv(output_file)
            df_combined = pd.concat([df_existing, new_df]).drop_duplicates(subset=['Link'], keep='last')
            df_combined.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\nProcess Completed! Total records in '{output_file}': {len(df_combined)}")
        else:
            new_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\nProcess Completed! Saved as '{output_file}'")


if __name__ == '__main__':
    main()