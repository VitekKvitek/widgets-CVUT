# script for comparing per frame rusults
import ipywidgets as widgets
from IPython.display import display
# Custom scripts
from results_loader import read_per_f_results


algo_1 = None

algo_2 = None
# Per frame data of algo 1 
data_1 = None
# Per frame data of algo 2
data_2 = None
# List of sorted keys by difference
sorted_keys = None
# Selected img to show and compare the 2 algos visually
selected_img = None
# Selected img dataset - functions only for giving to the other part of code
selected_img_dataset = None
# By which score will be the 2 algos compared
difference_type = 'AP'

# Function for setting row index list which will be showed in algo selector
def import_sheet_row_index(index_list):
    algo_list = index_list
    selector_1_value = algo_selector_1.value
    selector_2_value = algo_selector_2.value
    algo_selector_1.options = algo_list
    algo_selector_2.options = algo_list
    # TODO slow
    # Mechanism for displaying old selection 
    if selector_1_value in index_list:
        algo_selector_1.value = selector_1_value
    if selector_2_value in index_list:
        algo_selector_2.value = selector_2_value
def import_sheet_col_index(index_list):
    dataset_list = index_list        
# Called after alg selection 1
def load_data_1(change):
    global algo_1
    algo_1 = change['new']
# Called after alg selection 2
def load_data_2(change):
    global algo_2
    algo_2 = change['new']
# Compares results and sorts them by biggest difference in selected score type
def compare_results():
    global sorted_keys
    # Returns if any of the data are None - can not compare only singular data
    if data_1 == None or data_2 == None:
        return
    # Calculate the absolute differences and store them in a new dictionary
    differences = {key: abs(data_1[key][difference_type] - data_2[key][difference_type]) for key in data_1}
    # Sort the keys based on the differences in descending order
    sorted_keys = sorted(differences, key=differences.get, reverse=True)
    # Updates the options of img_selector
    #TODO
    img_selector.options = sorted_keys
# Sets new img
def set_selected_img(change):
    global selected_img
    global selected_img_dataset
    selected_img = change['new']
    selected_img_dataset = data_1[selected_img]['dataset']
    print(selected_img)
    print(selected_img_dataset)
# Sets difference type by which it will be sorted
def set_difference_type(button):
    global difference_type
    new_difference_type = button.description.split()[-1]
    if new_difference_type != difference_type:
        difference_type = new_difference_type
        compare_results()
    if new_difference_type == 'AP':
        hbox_button.children[0].button_style = 'info'
        hbox_button.children[1].button_style = ''
    else:
        hbox_button.children[0].button_style = ''
        hbox_button.children[1].button_style = 'info'
def make_confirmation(*args,**kwargs):
    global data_1
    global data_2
    
    if algo_1 != None:
        data_1 = read_per_f_results (algo_1)
    if algo_2 != None:
        data_2 = read_per_f_results (algo_2)
    compare_results()
# Displays all widgets needed for comparer to function
def display_controls():
    hbox_selector = widgets.HBox([algo_selector_1,
                                  algo_selector_2,
                                  confirm_button])
    display(hbox_selector,
            hbox_button,
            img_selector)
# TODO load algo z sheet.py
# Prepare dropdowns to select algo
def prepare_algo_selectors():
    algo_selector_1 = widgets.Dropdown(
        options=[],
        description='Algo:',
        disabled=False,
    )
    algo_selector_1.observe(load_data_1, names='value')
    algo_selector_2 = widgets.Dropdown(
        options=[],
        description='Algo:',
        disabled=False,
    )
    algo_selector_2.observe(load_data_2, names='value')
    return algo_selector_1, algo_selector_2
# Prepares buttons to choose diffrence type by which will be the images sorted
def prepare_difference_type_buttons():    
    button_AP = widgets.Button(description="Difference by AP")
    button_AP.on_click(set_difference_type)
    button_AP.button_style = 'info'
    button_FPRat95 = widgets.Button(description="Difference by FPRat95")
    button_FPRat95.on_click(set_difference_type)
    button_list = [button_AP,button_FPRat95]
    hbox_button = widgets.HBox(button_list)
    return hbox_button
# Prepares dropdown widget which lists all available images
def prepare_img_selector():
    img_selector = widgets.Dropdown(
        options=[],
            description='File:',
        disabled=False,
    )
    img_selector.observe(set_selected_img, names='value')
    return img_selector
def prepare_confirm_button():
    confirm_button = widgets.Button(description="Confirm algs")
    confirm_button.on_click(make_confirmation)
    return confirm_button
algo_selector_1, algo_selector_2 = prepare_algo_selectors()
hbox_button = prepare_difference_type_buttons()
img_selector = prepare_img_selector()
confirm_button = prepare_confirm_button()