
import os
import pandas as pd

def assemble_project_csvs(csv_folder_path, project_name):
    combined = []
    for fname in os.listdir(csv_folder_path):
        if fname.startswith(project_name) and fname.endswith('.csv'):
            df = pd.read_csv(os.path.join(csv_folder_path, fname))
            combined.append(df)
    if not combined:
        print(f"No chunks found for {project_name}")
        return
    all_data = pd.concat(combined, ignore_index=True)
    all_data = all_data.drop_duplicates(subset=['date', 'summary'], keep='last').sort_values(by='date')
    out_csv = os.path.join(csv_folder_path, f"{project_name}_merged.csv")
    all_data.to_csv(out_csv, index=False)
    print(f"Merged CSV written to {out_csv}")
    return out_csv
