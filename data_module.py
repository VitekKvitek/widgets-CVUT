# In this script data are stored
from types import SimpleNamespace
from settings_handler import add_var_to_settings

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
    'selected_file': '01_Hanns_Klemm_Str_45_000002_000190.png', #TODO Initial values for debuging
    'selected_folder': 'Fishyscapes_LaF',
    'selected_algo': ['grood_logml_1000K_01adamw_tau10_resetthr1',
                      'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1'],
    'threshold': [0.997, 0.997],
    'ignore': False
}
iv = SimpleNamespace(**image_values)

name_mapping = {
    "Fishyscapes_LaF": 'FS',
    "RoadAnomaly": 'RA',
    "RoadObstacles": 'RO',
    "RoadObstacles21": 'RO21A'
}