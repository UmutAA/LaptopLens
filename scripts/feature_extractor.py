from google import genai
import pandas as pd
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal


class LaptopSpecs(BaseModel):
    """Specs of ONE laptop. 'id' is the number of the title inside the batch."""
    id: int
    brand: str | None
    model: str | None
    cpu_model: str | None
    ram_gb: int | None = Field(default=None, ge=4, le=128)
    gpu_model: str | None
    vram_gb: int | None = Field(default=None, ge=1, le=32)
    storage_gb: int | None = Field(default=None, ge=64, le=8192)
    refresh_rate_hz: int | None = Field(default=None, ge=30, le=500)
    screen_size: float | None = Field(default=None, ge=10, le=20)
    os: Literal["Free", "Windows", "Linux", "Mac"] | None


class BatchResult(BaseModel):
    """What the API returns for one call: one LaptopSpecs per title."""
    results: list[LaptopSpecs]


SPEC_FIELDS = [name for name in LaptopSpecs.model_fields if name != "id"]


class FeatureExtractor:
    def __init__(self, end_index=None, start_index=0, batch_size=20,
                 input_file="../data/products_raw.csv",
                 output_file="../data/enriched_products.csv"):
        load_dotenv()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.input_file = input_file
        self.output_file = output_file
        self.BATCH_SIZE = batch_size
        self.START_INDEX = start_index
        self.END_INDEX = end_index

    def extract_features_batch(self, product_names: list[str], model_name: str):
        """Returns {id: LaptopSpecs} for the batch, or None if the call failed."""
        formatted_products = "\n".join(
            [f"{i + 1}. {name}" for i, name in enumerate(product_names)]
        )
        prompt = f"""
                    Extract the technical specifications of each laptop listed below.
                    Use ONLY the information in its title. If a spec is not stated in the title, use null. Never guess.
                    
                    Return one result per laptop and copy the laptop's number into "id".
                    
                    Rules:
                    - ram_gb, vram_gb, storage_gb: integers in GB (1TB = 1024, 2TB = 2048)
                    - refresh_rate_hz: integer in Hz
                    - screen_size: number in inches
                    - os: one of Free, Windows, Linux, Mac (DOS and FreeDOS mean Free)
                    
                    Example input:
                    1. ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 512GB 140W RTX4050 6GB 16" 144Hz DOS
                    2. ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 1TB 140W RTX4050 6GB 16" 144Hz DOS
                    3. ASUSTUF GAMING A16 FA607NUG-RL213 RYZEN 7-7445HS 16GB DDR5 2TB 140W RTX4050 6GB 16" 144Hz DOS
                    
                    Example output:
                    {{"results": [
                      {{"id": 1, "brand": "ASUS", "model": "TUF GAMING A16 FA607NUG-RL213", "cpu_model": "RYZEN 7-7445HS", "ram_gb": 16, "gpu_model": "RTX4050", "vram_gb": 6, "storage_gb": 512, "refresh_rate_hz": 144, "screen_size": 16, "os": "Free"}},
                      {{"id": 2, "brand": "ASUS", "model": "TUF GAMING A16 FA607NUG-RL213", "cpu_model": "RYZEN 7-7445HS", "ram_gb": 16, "gpu_model": "RTX4050", "vram_gb": 6, "storage_gb": 1024, "refresh_rate_hz": 144, "screen_size": 16, "os": "Free"}},
                      {{"id": 3, "brand": "ASUS", "model": "TUF GAMING A16 FA607NUG-RL213", "cpu_model": "RYZEN 7-7445HS", "ram_gb": 16, "gpu_model": "RTX4050", "vram_gb": 6, "storage_gb": 2048, "refresh_rate_hz": 144, "screen_size": 16, "os": "Free"}}
                    ]}}
                    
                    Laptops:
                    {formatted_products}
                    """
        try:
            interaction = self.client.interactions.create(
                model=model_name,
                system_instruction="You are a precise data extraction assistant.",
                input=prompt,
                generation_config={"temperature": 0},
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": BatchResult.model_json_schema(),
                },
            )
            parsed = BatchResult.model_validate_json(interaction.output_text)
            return {spec.id: spec for spec in parsed.results}

        except Exception as e:
            print(f"GenAI Error for batch: {e}")
            return None

    def extract_features(self):
        print(f"Reading {self.input_file} file...")

        try:
            df = pd.read_csv(self.input_file)
        except FileNotFoundError:
            print(f"'{self.input_file}' not found! Run first 'scraper.py'.")
            return

        if self.END_INDEX is None:
            self.END_INDEX = len(df)

        df_subset = df.iloc[self.START_INDEX:self.END_INDEX]
        print(f"\nProcessing rows from index {self.START_INDEX} to {self.END_INDEX} in batches of {self.BATCH_SIZE}...")

        enriched_data = []
        rows_list = df_subset.to_dict('records')

        for i in range(0, len(rows_list), self.BATCH_SIZE):
            batch_rows = rows_list[i:i + self.BATCH_SIZE]
            batch_names = [row['Name'] for row in batch_rows]

            print(f"\nProcessing batch {i // self.BATCH_SIZE + 1} ({len(batch_names)} products)...")

            specs_by_id = self.extract_features_batch(batch_names, model_name="gemini-3.1-flash-lite")

            for idx, row in enumerate(batch_rows):
                product_record = {
                    'Link': row['Link'],
                    'Name': row['Name'],
                    'Price': row['Price'],
                }

                spec = specs_by_id.get(idx + 1) if specs_by_id else None

                if spec is not None:
                    product_record.update(spec.model_dump(exclude={"id"}))
                else:
                    product_record.update({field: None for field in SPEC_FIELDS})

                enriched_data.append(product_record)

        if enriched_data:
            os.makedirs('../data', exist_ok=True)
            new_df = pd.DataFrame(enriched_data)

            if os.path.exists(self.output_file):
                df_existing = pd.read_csv(self.output_file)
                df_combined = pd.concat([df_existing, new_df]).drop_duplicates(subset=['Link'], keep='last')
                df_combined.to_csv(self.output_file, index=False, encoding='utf-8-sig')
                print(f"\nProcess Completed! Total records in '{self.output_file}': {len(df_combined)}")
            else:
                new_df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
                print(f"\nProcess Completed! Saved as '{self.output_file}'")


if __name__ == "__main__":
    extractor = FeatureExtractor()
    extractor.extract_features()