# Script fpr loading results data
import os
import json


def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        value_AP = data['AP']
        value_FPRat95 = data['FPRat95']
        return value_AP, value_FPRat95
# This function serves for loading results from data folder
def read_all_jsons():
    method_list = []
    dataset_list = []
    # 2D list of AP and FPRat95 values
    all_score_list = []
    for method_folder in os.listdir(initial_folder):
        # 1D list of AP and FPRat95 one just for speciffic method
        solo_score_list = []
        method_list.append(method_folder)
        m_folder_path = os.path.join(initial_folder, method_folder)
        dataset_folders = os.listdir(m_folder_path)
        # TODO list vsech tech value, pujde to na jeden radek
        for dataset_f in dataset_folders:
            if dataset_f not in dataset_list:
                dataset_list.append(dataset_f)
            json_r_path = os.path.join(m_folder_path, dataset_f, json_general_path)
            value_AP, value_FPRat95 = read_json(json_r_path)
            solo_score_list.append(value_AP)
            solo_score_list.append(value_FPRat95)
        all_score_list.append(solo_score_list)
    return method_list, dataset_list, all_score_list
initial_folder = 'data/export/results'
json_general_path = 'res/res.json'
