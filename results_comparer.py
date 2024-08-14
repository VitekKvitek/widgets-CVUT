# script for comparing per frame results
import ipywidgets as widgets
from IPython.display import display
# Custom scripts
from results_loader import read_per_f_results
from plot import update_vals
from settings_handler import add_widget_to_settings
from data_module import rd

# Function for setting row index list which will be showed in algo selector
def import_sheet_row_index(index_list):
    algo_list = index_list
    selector_1_value = algo_selector_1.value
    selector_2_value = algo_selector_2.value
    algo_selector_1.options = algo_list
    algo_selector_2.options = algo_list
    # TODO slow
    # System for displaying old selection
    # Otherwise new option would be picked
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
    rd.algo_0 = change['new']
# Called after alg selection 2
def load_data_2(change):
    rd.algo_1 = change['new']
# Compares results and sorts them by biggest difference in selected score type
def compare_results():
    # Returns if any of the data are None - can not compare only singular data
    if rd.data_0 == None or rd.data_1 == None:
        return
    for dataset_key in rd.data_0.keys():
        dataset_algo_1 = rd.data_0[dataset_key]
        dataset_algo_2 = rd.data_1[dataset_key]
        # Calculate the absolute differences and store them in a new dictionary
        differences = {}
        for key in dataset_algo_1:
            # Extract the value for the given difference type from both datasets
            value_1 = dataset_algo_1[key][rd.difference_type]
            value_2 = dataset_algo_2[key][rd.difference_type]
            # Calculate the absolute difference between the values
            difference = abs(value_1 - value_2)
            # Store the difference in the dictionary with the key
            differences[key] = difference
        # Sort the keys based on the differences in descending order
        dataset_sorted_keys = sorted(differences, key=differences.get, reverse=True)
        rd.sorted_keys[dataset_key] = dataset_sorted_keys
    # Updates the options of img_selector
    update_img_selector()
def set_selected_img(change):
    rd.selected_img = change['new']
# Sets difference type by which it will be sorted
def set_difference_type(button):
    new_difference_type = button.description.split()[-1]
    if new_difference_type != rd.difference_type:
        rd.difference_type = new_difference_type
        compare_results()
    if new_difference_type == 'AP':
        hbox_button.children[0].button_style = 'info'
        hbox_button.children[1].button_style = ''
    else:
        hbox_button.children[0].button_style = ''
        hbox_button.children[1].button_style = 'info'
def make_confirmation(*args,**kwargs):
    
    if rd.algo_0 != None and rd.algo_1 != None:
        rd.data_0 = read_per_f_results (rd.algo_0)
        rd.data_1 = read_per_f_results (rd.algo_1)
        if rd.selected_img != None and rd.selected_img_dataset != None:
            update_vals(rd.algo_0, rd.algo_1, rd.selected_img_dataset, rd.selected_img)
            update_score_labels()
        compare_results()
def update_selected_dataset(change):
    rd.selected_img_dataset = change['new']
    update_img_selector()
def update_img_selector():
    try:
        img_selector.options = rd.sorted_keys[rd.selected_img_dataset]
    except:
        pass
def update_score_labels():
    # Get scores for the current image using the provided function
    algo_1_score, algo_2_score = get_score_for_current_img()

    # Calculate scores for Algorithm 1 and Algorithm 2
    alg_1_AP = algo_1_score['AP'] * 100
    alg_1_FPRat95 = algo_1_score['FPRat95'] * 100

    alg_2_AP = algo_2_score['AP'] * 100
    alg_2_FPRat95 = algo_2_score['FPRat95'] * 100

    # Create a readable string with spaces and labels
    #TODO pak to jeste dat k tomu dalsimu update_vals
    algo_1_label.value = (
        f" AP: {alg_1_AP:.2f} , FPRat95: {alg_1_FPRat95:.2f}"
    )
    # Apply layout styling
    algo_1_label.layout = widgets.Layout(
        width='auto', 
        height='30px', 
        margin='0px 60px 0px 90px', 
        padding='5px',
        border='solid 1px black'
    )   
    algo_2_label.value = (
        f"AP: {alg_2_AP:.2f} , FPRat95: {alg_2_FPRat95:.2f}"
    )
    # Apply layout styling
    algo_2_label.layout = widgets.Layout(
        width='auto', 
        height='30px', 
        margin='0px 40px 0px 80px', 
        padding='5px',
        border='solid 1px black'
    )   
def select_image(*args,**kwargs):
    # print(rd.selected_img,rd.selected_img_dataset)
    if rd.selected_img == None or rd.selected_img_dataset == None:
        return
    update_vals(rd.algo_0, rd.algo_1, rd.selected_img_dataset, rd.selected_img)
    update_score_labels()

def get_score_for_current_img():
    return rd.data_0[rd.selected_img_dataset][rd.selected_img], rd.data_1[rd.selected_img_dataset][rd.selected_img]

# Displays all widgets needed for comparer to function
# Prepare dropdowns to select algo
def prepare_algo_selectors():
    algo_selector_1 = widgets.Dropdown(
        options=[],
        description='Algo 1:',
        disabled=False,
    )
    algo_selector_1.observe(load_data_1, names='value')
    add_widget_to_settings(algo_selector_1, ' algo_selector_1')
    algo_selector_2 = widgets.Dropdown(
        options=[],
        description='Algo 2:',
        disabled=False,
    )
    algo_selector_2.observe(load_data_2, names='value')
    add_widget_to_settings(algo_selector_2, 'algo_selector_2')
    return algo_selector_1, algo_selector_2
# Prepares buttons to choose diffrence type by which will be the images sorted
def prepare_difference_type_buttons():    
    button_AP = widgets.Button(description="Difference by AP")
    button_AP.on_click(set_difference_type)
    button_AP.button_style = 'info'
    button_FPRat95 = widgets.Button(description="Difference by FPRat95")
    button_FPRat95.on_click(set_difference_type)
    button_list = [button_AP, button_FPRat95]
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
    add_widget_to_settings(img_selector, 'img_selector')
    return img_selector
def prepare_dataset_selector():
    dataset_selector = widgets.Dropdown(
        options = [],
        description= 'Dataset',
        disabled = False
    )
    dataset_selector.observe(update_selected_dataset, names='value')
    add_widget_to_settings(dataset_selector, 'data_selector')
    return dataset_selector
def prepare_confirm_button():
    confirm_button = widgets.Button(description="Confirm algs")
    confirm_button.on_click(make_confirmation)
    return confirm_button
def prepare_select_img_button():
    button_select = widgets.Button(description="Select image")
    button_select.on_click(select_image)
    return button_select
def prepare_labels():
    # Create a Label widget
    algo_1_label = widgets.Label(value = " ")
    algo_2_label = widgets.Label(value = " ")
    # add(algo_1_label, 'algo_1_label')
    # add(algo_2_label, 'algo_2_label')
    return algo_1_label, algo_2_label
def display_controls():
    hbox_alg_selector = widgets.HBox([algo_selector_1,
                                  algo_selector_2,
                                  confirm_button])
    hbox_img_selector = widgets.HBox([dataset_selector,
                                      img_selector,
                                      select_button])
    hbox_labels = widgets.HBox([algo_1_label, algo_2_label])
    display(hbox_button,
            hbox_img_selector,
            hbox_alg_selector,
            hbox_labels)
algo_selector_1, algo_selector_2 = prepare_algo_selectors()
hbox_button = prepare_difference_type_buttons()
confirm_button = prepare_confirm_button()
dataset_selector = prepare_dataset_selector()
img_selector = prepare_img_selector()
select_button = prepare_select_img_button()
algo_1_label, algo_2_label = prepare_labels()