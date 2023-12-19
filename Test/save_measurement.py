
# %%
import os
import json
import numpy as np
# %%
main_directory = r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\2023-11-23-session'
spectrum_name = 'spectrum_block'
rf_duration = 5e-05
time_bw_product = 0
output_directory_name = f'output_{spectrum_name}_{rf_duration}_{time_bw_product}'
output_directory = os.path.join(r'C:\Users\Jana0\OneDrive\Desktop\Bachelorarbeit\Frequenzkalibrierung Messdaten\Freq_Measurement', output_directory_name)


def read_and_save_data(main_directory, spectrum_name, rf_duration, time_bw_product, output_directory):
    matching_folders = []

    for folder_name in os.listdir(main_directory):
        folder_path = os.path.join(main_directory, folder_name)

        if os.path.isdir(folder_path) and spectrum_name in folder_name:

            meta_json_path = os.path.join(folder_path, 'meta.json')
            raw_data_path = os.path.join(folder_path, 'raw_data.npy')

            if os.path.isfile(meta_json_path) and os.path.isfile(raw_data_path):

                try:
                    with open(meta_json_path, 'r') as json_file:
                        meta_data = json.load(json_file)

                    if 'rf_duration' in meta_data.get('info', {}) and meta_data['info']['rf_duration'] == rf_duration \
                            and 'time_bw_product' in meta_data.get('info', {}) and meta_data['info']['time_bw_product'] == time_bw_product:
                        
                        output_folder = os.path.join(output_directory, folder_name)
                        os.makedirs(output_folder, exist_ok=True)

                        # Save "meta.json" and raw_data.npy in folder
                        meta_json_output_path = os.path.join(output_folder, 'meta.json')
                        raw_data_output_path = os.path.join(output_folder, 'raw_data.npy')

                        with open(meta_json_output_path, 'w') as json_file:
                            json.dump(meta_data, json_file)

                        np.save(raw_data_output_path, np.load(raw_data_path))

                        matching_folders.append({'folder_name': folder_name, 'info_data': meta_data})
                except Exception as e:
                    print(f"Error loading data from folder {folder_name}: {e}")

    np.save(os.path.join(output_directory, 'matching_folders.npy'), matching_folders)

read_and_save_data(main_directory, spectrum_name, rf_duration, time_bw_product, output_directory)

loaded_data = np.load(os.path.join(output_directory, 'matching_folders.npy'), allow_pickle=True)

# for folder_info in loaded_data:
#     print(f'Daten aus Ordner "{folder_info["folder_name"]}":')
#     print("Info Data:", folder_info["info_data"])
#     print('\n')
#     print(len(loaded_data))

# %%
