# In this script data are stored
from types import SimpleNamespace
from settings_handler import add_var_to_settings
import json

sheet_data = {'df': None, # Dataframe with all of the data
              'display_df': None, # Dataframe version which will be displayed - after black list and sorting
              'bl_col': [], # Black list for columns
              'bl_row': [], # Black list for rows
              'ascend_AP': True, # Stores the state of ascending AP and FPRat95
              'ascend_FPRat95' : False,
              'average_type': 'AP', # Stores the column by which it should be ordered
              'apply_highlight': True # If highlighting should be applied
              }
sd = SimpleNamespace(**sheet_data)
add_var_to_settings(sd.ascend_AP, 'ascend_AP')
add_var_to_settings(sd.ascend_FPRat95, 'ascend_FPRat95')
add_var_to_settings(sd.average_type, 'average_type')

res_data ={'algo_0' : None,
           'algo_1': None,
           'data_0': None, # Per frame data of algo 0
           'data_1': None, # Per frame data of algo 1
           'sorted_keys': {}, # List of sorted keys by difference
           'selected_img': None, # Selected img to show and compare the 2 algos visually
           'selected_img_dataset' : None, # Selected dataset
           'difference_type' : 'AP' # By which score will be the 2 algos compared
           }
rd = SimpleNamespace(**res_data)
add_var_to_settings(rd.difference_type, 'difference_type')
image_values = {
    'original_image': None,
    'ground_truth': None, 
    'predict': [None, None],
    'row': [None, None, None],  # [alg1, alg2, default]
    'selected_file': None, 
    'selected_folder': None,
    'selected_algo': [None,
                      None],
    'threshold': [0.97, 0.97],
    'ignore': True
}
iv = SimpleNamespace(**image_values)

# Load the config.json file
with open('data/export/config.json', 'r') as f:
    config = json.load(f)

# Initialize the name_mapping dictionary
name_mapping = {}

# Iterate over the datasets in the config
for key, value in config['Datasets'].items():
    # Extract the dataset name from the path
    full_name = value['path'].split('/')[-1]  # Get the last part of the path
    # Add to the name_mapping dictionary
    name_mapping[full_name] = key
    name_mapping[key] = full_name
