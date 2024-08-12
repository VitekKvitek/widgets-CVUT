res_data ={'algo_0' : None,
           'algo_1': None,
           'data_0': None, # Per frame data of algo 0
           'data_1': None, # Per frame data of algo 1
           'sorted_keys': {}, # List of sorted keys by difference
           'selected_img': None, # Selected img to show and compare the 2 algos visually
           'selected_img_dataset' : None, # Selected dataset
           'difference_type' : 'AP' # By which score will be the 2 algos compared
           }