# Script fpr loading results data
import os
import json


def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        value_AP = data['AP']
        value_FPRat95 = data['FPRat95']
        return value_AP, value_FPRat95


def read_json_files(folder_path):
    # List all files in the given folder
    files = os.listdir(folder_path)
    
    # Filter out JSON files
    json_files = [file for file in files if file.endswith('.json')]
    
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
def read_all_jsons():
    method_list = []
    dataset_list = []
    score_list = []
    for method_folder in os.listdir(initial_folder):
        method_list.append(method_folder)
        m_folder_path = os.path.join(initial_folder, method_folder)
        dataset_folders = os.listdir(m_folder_path)
        # TODO list vsech tech value, pujde to na jeden radek
        for dataset_f in dataset_folders:
            dataset_list.append(dataset_f)
            json_r_path = os.path.join(m_folder_path, dataset_f, json_general_path)
            value_AP, value_FPRat95 = read_json(json_r_path)
# Example usage
file_path = 'data/export/results/grood_logml_1000K_01adamw_tau10_resetthr1/RO21A/res/res.json'
initial_folder = 'data/export/results'
json_general_path = 'res/res.json'


read_all_jsons()
# TODO
dataset = file_path.split('/')[-3]
