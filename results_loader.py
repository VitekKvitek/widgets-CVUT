# Script fpr loading results data
import os
import json

initial_folder = 'data/export/results'
algo_json_general_path = 'res/res.json'
per_f_json_general_path = 'res/per_frame_res.json'
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        value_AP = data['AP']
        value_FPRat95 = data['FPRat95']
        return value_AP, value_FPRat95
def read_per_f_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Gets AP and FPRat95 values from the loaded data
    extracted_data = {}
    for picture_name, metrics in data.items():
        extracted_data[picture_name] = {
            "AP": metrics["AP"],
            "FPRat95": metrics["FPRat95"]
        }
    return extracted_data
# This function serves for loading results from data folder
def read_all_algo_jsons():
    algo_list = []
    dataset_list = []
    # 2D list of AP and FPRat95 values
    all_score_list = []
    for algo_folder in os.listdir(initial_folder):
        # 1D list of AP and FPRat95 one just for speciffic method
        solo_score_list = []
        algo_list.append(algo_folder)
        a_folder_path = os.path.join(initial_folder, algo_folder)
        dataset_folders = os.listdir(a_folder_path)
        for dataset_f in dataset_folders:
            if dataset_f not in dataset_list:
                dataset_list.append(dataset_f)
            json_r_path = os.path.join(a_folder_path, dataset_f, algo_json_general_path)
            value_AP, value_FPRat95 = read_json(json_r_path)
            solo_score_list.append(value_AP)
            solo_score_list.append(value_FPRat95)
        all_score_list.append(solo_score_list)
    return algo_list, dataset_list, all_score_list
def read_per_f_results(algo):
    all_datasets_per_f_res = {}
    a_folder_path = os.path.join(initial_folder, algo)
    dataset_folders = os.listdir(a_folder_path)
    for dataset_f in dataset_folders:
        per_f_json_path = os.path.join(a_folder_path, dataset_f, per_f_json_general_path)
        results = read_per_f_json(per_f_json_path)
        all_datasets_per_f_res[dataset_f] = results
    return all_datasets_per_f_res

#read_per_f_results('grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1')