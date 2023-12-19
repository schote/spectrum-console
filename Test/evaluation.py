# %%
import os
import json
import argparse
import pandas as pd

def compare_results(folder_paths):
    all_results = []

    for folder_path in folder_paths:
        metadata_path = os.path.join(folder_path, 'meta.json')
        with open(metadata_path, 'r') as metadata_file:
            metadata = json.load(metadata_file)

        all_results.append(metadata)
        
    return all_results 
   
def is_valid_path(path):
    if os.path.exists(path):

        folders = sum(os.path.isdir(os.path.join(path, item)) for item in os.listdir(path))
        return folders % 21 == 0
    else:
        return None
    
def split_list(input_list, chunk_size):

    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def extract_and_save_data(measurements, key_to_extract, output_path):
    flat_measurements = [measurement for sublist in measurements for measurement in sublist]
    df = pd.json_normalize(flat_measurements)

    if set(key_to_extract).issubset(df.columns):
        df_selected_keys = df[key_to_extract]

        df_selected_keys.to_excel(output_path, index=True)
        print(f"Data saved to {output_path}")
    else:
        print(f"Error: The specified keys are not present in the DataFrame.")

def main():
    parser = argparse.ArgumentParser(description='A program that accepts a valid path.')
    parser.add_argument('path', type=str, help='The path you want to input.')
    args = parser.parse_args()

    path = args.path

    if is_valid_path(path):
        folders = sorted([os.path.abspath(os.path.join(path, item)) for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))])
        folder_chunks = split_list(folders, 21)
        measurements = []
        
        for chunk in folder_chunks:
            measurements.append(compare_results(chunk))
            
        key_to_extract = ["info.calculated_bandwidth", "info.time_bw_product", "info.pulse_type", "info.true f0", "info.magnitude spectrum max"]

        output_excel_path = "freq_measurement.xlsx"

        extract_and_save_data(measurements, key_to_extract, output_excel_path)

            
if __name__ == "__main__":    

    main()

# %%
