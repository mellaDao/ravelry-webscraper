from pathlib import Path

import pandas as pd


def save_dataframe(df, output_path):
    output_file = Path(output_path)
    df.to_excel(output_file, index=False)
    return output_file


def load_dataframe(input_path):
    input_file = Path(input_path)
    if not input_file.is_file():
        raise FileNotFoundError(f"Excel file not found: {input_file}")

    df = pd.read_excel(input_file)
    if "project_notes" in df.columns:
        df["project_notes"] = df["project_notes"].fillna("")
    return df