# script for comparing per frame rusults
import ipywidgets as widgets
from IPython.display import display
# Custom scripts
from results_loader import read_per_f_results
from plot import update_vals

algo_1 = None

algo_2 = None
# Per frame data of algo 1 
data_1 = None
# Per frame data of algo 2
data_2 = None
# List of sorted keys by difference
sorted_keys = {}
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
    # System for displaying old selection 
    if selector_1_value in algo_list:
        algo_selector_1.value = selector_1_value
    if selector_2_value in algo_list:
        algo_selector_2.value = selector_2_value
def import_sheet_col_index(index_list):
    dataset_list = index_list
    folder_selector_value = dataset_selector.value
    dataset_selector.options = dataset_list
    # System for displaying old selection 
    if folder_selector_value in dataset_list:
        dataset_selector.value = folder_selector_value
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
    for dataset_key in data_1.keys():
        dataset_algo_1 = data_1[dataset_key]
        dataset_algo_2 = data_2[dataset_key]
        # Calculate the absolute differences and store them in a new dictionary
        differences = {}
        for key in dataset_algo_1:
            # Extract the value for the given difference type from both datasets
            value_1 = dataset_algo_1[key][difference_type]
            value_2 = dataset_algo_2[key][difference_type]
            # Calculate the absolute difference between the values
            difference = abs(value_1 - value_2)
            # Store the difference in the dictionary with the key
            differences[key] = difference
        # Sort the keys based on the differences in descending order
        dataset_sorted_keys = sorted(differences, key=differences.get, reverse=True)
        sorted_keys[dataset_key] = dataset_sorted_keys
    # Updates the options of img_selector
    update_img_selector()
def set_selected_img(change):
    global selected_img
    selected_img = change['new']
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
    
    if algo_1 != None and algo_2 != None:
        data_1 = read_per_f_results (algo_1)
        data_2 = read_per_f_results (algo_2)
        if selected_img != None and selected_img_dataset != None:
            update_vals(algo_1, algo_2, selected_img_dataset, selected_img)
    compare_results()
def update_selected_dataset(change):
    global selected_img_dataset
    dataset = change['new']
    selected_img_dataset = dataset
    update_img_selector()
def update_img_selector():
    try:
        img_selector.options = sorted_keys[selected_img_dataset]
    except:
        pass
# TODO call Jirka
def select_image(*args,**kwargs):
    update_vals(algo_1, algo_2, selected_img_dataset, selected_img)
    #TODO
    # Get scores for the current image using the provided function
    algo_1_score, algo_2_score = get_score_for_current_img()

    # Calculate scores for Algorithm 1 and Algorithm 2
    alg_1_AP = algo_1_score['AP'] * 100
    alg_1_FPRat95 = algo_1_score['FPRat95'] * 100

    alg_2_AP = algo_2_score['AP'] * 100
    alg_2_FPRat95 = algo_2_score['FPRat95'] * 100

    # Create a readable string with spaces and labels
    #TODO pak to jeste dat k tomu dalsimu update_vals
    score_label.value = (
        f"Algorithm 1 AP: {alg_1_AP:.2f}\n"
        f"Algorithm 1 FPR at 95: {alg_1_FPRat95:.2f}\n"
        f"Algorithm 2 AP: {alg_2_AP:.2f}\n"
        f"Algorithm 2 FPR at 95: {alg_2_FPRat95:.2f}"
    )

def get_score_for_current_img():
    return data_1[selected_img_dataset][selected_img], data_2[selected_img_dataset][selected_img]

# Displays all widgets needed for comparer to function
# Prepare dropdowns to select algo
def prepare_algo_selectors():
    algo_selector_1 = widgets.Dropdown(
        options=[],
        description='Algo 1:',
        disabled=False,
    )
    algo_selector_1.observe(load_data_1, names='value')
    algo_selector_2 = widgets.Dropdown(
        options=[],
        description='Algo 2:',
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
# Prepares dropdown widgets which lists all available images for each dataset
def prepare_img_selector():
    img_selector = widgets.Dropdown(
        options=[],
        description='Image',
        disabled=False,
    )
    img_selector.observe(set_selected_img, names='value')
    return img_selector
def prepare_dataset_selector():
    dataset_selector = widgets.Dropdown(
        options = [],
        description= 'Dataset',
        disabled = False
    )
    dataset_selector.observe(update_selected_dataset, names='value')
    return dataset_selector
def prepare_confirm_button():
    confirm_button = widgets.Button(description="Confirm algs")
    confirm_button.on_click(make_confirmation)
    return confirm_button
def prepare_select_img_button():
    button_select = widgets.Button(description="Select image")
    button_select.on_click(select_image)
    return button_select
def prepare_label():
    # Create a Label widget
    label = widgets.Label(value="Hello, this is a static text using ipywidgets!")
    return label
def display_controls():
    hbox_alg_selector = widgets.HBox([algo_selector_1,
                                  algo_selector_2,
                                  confirm_button])
    hbox_img_selector = widgets.HBox([dataset_selector,
                                      img_selector,
                                      select_button])
    display(hbox_alg_selector,
            hbox_button,
            hbox_img_selector,
            score_label)
algo_selector_1, algo_selector_2 = prepare_algo_selectors()
hbox_button = prepare_difference_type_buttons()
confirm_button = prepare_confirm_button()
dataset_selector = prepare_dataset_selector()
img_selector = prepare_img_selector()
select_button = prepare_select_img_button()
score_label = prepare_label()