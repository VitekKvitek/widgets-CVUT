# In this script data are stored
from types import SimpleNamespace

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