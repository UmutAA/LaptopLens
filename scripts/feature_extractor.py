from google import genai
import json
import pandas as pd
import os
from dotenv import load_dotenv

def extract_features(product_name: str, client: genai.Client, model_name: str = "gemini-3.5-flash-lite"):
    prompt = f"""
       Extract the technical specifications of the provided product name below (use ONLY provided name nothing else),
        and ONLY return it (no buzz words, fillers, markdown code blocks, etc.) ONLY as a PURE JSON FORMAT.
        
        The JSON format SHOULD have these exact keys: 
        "brand", "cpu model", "ram" (number in GBs), "gpu model", "vram" (number in GBs), "storage" (number in GBs), "refresh rate" (number in Hz), "screen size" (number in inches), "OS" (Free, Windows, Linux, Mac)
        
        If a specification is not mentioned, make its value null.
        
        Here is an example:
        
        Input: ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 512GB 140W RTX4050 6GB 16"" 144Hz DOS"
        Output:
        {{
          "brand": "ASUS",
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
          "cpu model": "RYZEN 7-7445HS",
          "ram": 16,
          "gpu model": "RTX4050",
          "vram": 6,
          "storage": 2048,
          "refresh rate": 144,
          "screen size": 16,
          "OS": "Free"
        }}
        
        Product Name: {product_name}
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
        print(f"GenAI Error for '{product_name}': {e}")
        return None

def main():
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    input_file = "../data/products_raw.csv"
    print(f"Reading {input_file} file...")

    try:
        df = pd.read_csv(input_file)

    except FileNotFoundError:
        print(
            f"'{input_file}' not found! Run first 'scrape.py'."
        )
        return

    enriched_data = []

    for index, row in df.iterrows():
        link = row['Link']
        name = row['Name']
        price = row['Price']
        print(
            f"Processing ({index + 1}/{len(df)}): {name[:40]}..."
        )
        features = extract_features(name, client)
        product_record = {'Link': link, 'Name': name, 'Price': price}
        if features:
            product_record.update(features)
        else:
            product_record.update({
                "brand": None,
                "cpu model": None,
                "ram": None,
                "gpu model": None,
                "vram": None,
                "storage": None,
                "refresh rate": None,
                "screen size": None,
                "OS": None
            })

        enriched_data.append(product_record)
    if enriched_data:
        new_df = pd.DataFrame(enriched_data)
        output_file = '../data/enriched_products.csv'
        new_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nProcess Completed! Enriched dataset has been saved as '{output_file}'")

if __name__ == '__main__':
    main()
