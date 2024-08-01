# script for comparing per frame rusults
import ipywidgets as widgets
from IPython.display import display
# Custom scripts
import sheet
from results_loader import read_per_f_results

data_1 = None
data_2 = None
sorted_keys = None
selected_img = None
selected_img_folder = None
# By which score will be the 2 algos compared
difference_type = 'AP' # default AP
def load_data_1(change):
    global data_1
    algo_1 = change['new']
    data_1 = read_per_f_results (algo_1)
    compare_results()
def load_data_2(change):
    global data_2
    algo_2 = change['new']
    data_2 = read_per_f_results (algo_2)
    compare_results()
# TODO hradcoded AP
def compare_results():
    global sorted_keys
    if data_1 == None or data_2 == None:
        return
    # Calculate the absolute differences and store them in a new dictionary
    differences = {key: abs(data_1[key][difference_type] - data_2[key][difference_type]) for key in data_1}

    # Sort the keys based on the differences in descending order
    sorted_keys = sorted(differences, key=differences.get, reverse=True)

    img_selector.options = sorted_keys
    # Print the sorted keys

    # If you want to see the sorted differences as well
    # sorted_differences = {key: differences[key] for key in sorted_keys}
    # print(sorted_differences)
def set_selected_img(change):
    global selected_img
    global selected_img_folder
    selected_img = change['new']
    selected_img_folder = data_1[selected_img]['dataset']
    print(selected_img)
    print(selected_img_folder)
def set_difference_type(button):
    global difference_type
    new_difference_type = button.description.split()[-1]
    if new_difference_type != difference_type:
        difference_type = new_difference_type
        compare_results()
def display_controls():
    display(algo_selector_1,
            algo_selector_2,
            hbox_button,
            img_selector)
# TODO load algo z sheet.py
def prepare_algo_selectors():
    algo_selector_1 = widgets.Dropdown(
        options=['grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1',
                'grood_logml_1000K_01adamw_tau10_resetthr1',
                'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf1_ioodpdf0uni1m0s1c1_staticood1'],
        value= 'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1',
        description='Algo:',
        disabled=False,
    )
    algo_selector_1.observe(load_data_1, names='value')
    algo_selector_2 = widgets.Dropdown(
        options=['grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1',
                'grood_logml_1000K_01adamw_tau10_resetthr1',
                'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf1_ioodpdf0uni1m0s1c1_staticood1'],
        value= 'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1',
        description='Algo:',
        disabled=False,
    )
    algo_selector_2.observe(load_data_2, names='value')
    return algo_selector_1, algo_selector_2
def prepare_difference_type_buttons():    
    button_AP = widgets.Button(description="Difference by AP")
    button_AP.on_click(set_difference_type)
    button_FPRat95 = widgets.Button(description="Difference by FPRat95")
    button_FPRat95.on_click(set_difference_type)
    button_list = [button_AP,button_FPRat95]
    hbox_button = widgets.HBox(button_list)
    return hbox_button
def prepare_img_selector():
    img_selector = widgets.Dropdown(
        options=[],
            description='File:',
        disabled=False,
    )
    img_selector.observe(set_selected_img, names='value')
    return img_selector
algo_selector_1, algo_selector_2 = prepare_algo_selectors()
hbox_button = prepare_difference_type_buttons()
img_selector = prepare_img_selector()