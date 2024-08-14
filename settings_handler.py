import json
from os import listdir,makedirs
from os.path import isfile, join, exists
import ipywidgets as widgets
from IPython.display import display
from types import SimpleNamespace
# Dictionary for all widgets which values are going to be tracked
widgets_tracked = {}
descriptions_tracked = {}
# Dictionary for all variables that are going to be tracked
# Most of the times values that are associated with buttons but can not be accessed through the button
vars_tracked = {}
# Default settings folder
settings_folder = 'settings/'
# Name of file in which the upcoming save of settings will be written
will_save_file_name = 'unnamed_preset'
will_load_file_name = None
# Adds widget to the list of widgets which are going to be stored
def add_var_to_settings(new_var, name):
    vars_tracked[name] = new_var
def add_widget_to_settings(new_object_to_remember, name, description = False):
    if description:
        descriptions_tracked[name] = new_object_to_remember
    else:
        widgets_tracked[name] = new_object_to_remember
# Function to collect widget states
def get_widget_values():
    widget_values = {}
    for name, widget in widgets_tracked.items():
        widget_values[name] = widget.value
    return widget_values
def get_description_values():
    descriptions_dic = {}
    for name, widget in descriptions_tracked.items():
        descriptions_dic[name] = widget.description
    return descriptions_dic
# Called by save button
def save(*args,**kwargs):
    # Dump the list of values to file
    all_values = {}
    widget_values = get_widget_values()
    descriptions = get_description_values()
    all_values['widgets'] = widget_values
    all_values['vars'] = vars_tracked
    all_values['descriptions'] = descriptions
    with open(settings_folder + will_save_file_name+'.json', 'w') as file:
        json.dump(all_values, file)
    # Updates options of uploader widget
    uploader_widget.options = get_all_files()
# Called by load_button - Function to load widget values
def load_widget_states(loaded_vlaue_dict):
    # Variable which is used in mechanism for setting img selector value
    img_selector_value = None
    for name,loaded_value in loaded_vlaue_dict['widgets'].items():
        if name == 'img_selector':
            img_selector_value = loaded_value
        else:
            widgets_tracked[name].value = loaded_value
            
    for name, loaded_value in loaded_vlaue_dict['vars'].items():
        vars_tracked[name] = loaded_value
    for name, loaded_value in loaded_vlaue_dict['descriptions'].items():
        descriptions_tracked[name].description = loaded_value
    
    from results_comparer import make_confirmation
    # Confirms newly loaded algos
    # After selecting algos, set the value to newly loaded img selector value
    # Otherwise would cause crash
    make_confirmation()
    widgets_tracked['img_selector'].value = img_selector_value
    
    from sheet import update_sheet
    update_sheet()
    from results_comparer import select_image
    select_image()
# loads the data from json file and sets the current_loaded_settings
# Does not change widgets!!!
def load(*args,**kwargs):
    # Load the list of values back from the file
    with open(settings_folder + will_load_file_name, 'r') as file:
        loaded_vlaue_dict = json.load(file)
    load_widget_states(loaded_vlaue_dict)
# This function is called by text button - sets name of file to save into
def set_save_file_name(change):
    global will_save_file_name
    will_save_file_name = change['new']
# This function is called by dropdown - sets name of file to load from
def set_load_file_name(change):
    global will_load_file_name
    will_load_file_name = change['new']
def get_all_files():
    # Check if the folder exists, and create it if it doesn't
    if not exists(settings_folder):
        makedirs(settings_folder)
    # List all files in the folder
    all_files = [f for f in listdir(settings_folder) if isfile(join(settings_folder, f))]
    return all_files
def prepare_uploader():
        # File upload widget
    uploader_widget = widgets.Dropdown(
        options= get_all_files(),
        description='Choose preset',
        disabled=False,
    )
    # Adds uploader widget to settigns handler - on save it updates the options it can chose from
    uploader_widget.observe(set_load_file_name, names = 'value') # observes change in value of the widget
    return uploader_widget
def prepare_save_button():
    # Create a save button widget
    save_button = widgets.Button(
    description ='Save',
    tooltip ='Click to save data',
    button_style ='success'  # 'success' (green), 'info' (blue), 'warning' (yellow), 'danger' (red)
)
    save_button.on_click(save)
    return save_button
def prepare_load_butotn():
    # Create a load button widget
    load_button = widgets.Button(
    description ='Load',
    tooltip ='Click to load data',
    button_style ='success'  # 'success' (green), 'info' (blue), 'warning' (yellow), 'danger' (red)
)
    load_button.on_click(load)
    return load_button
def prepare_file_text():
    # Cretes a text widget in which is written name of file you want to save current settings
    file_text_widget = widgets.Text(
    value='',
    placeholder='Do not include .json',
    description='Name preset',
    disabled=False   
)
    file_text_widget.observe(set_save_file_name, names='value')
    return file_text_widget
def display_settings():
    display(uploader_widget,
            load_button,
            file_text_widget,
            save_button
        )

uploader_widget = prepare_uploader()
save_button = prepare_save_button()
file_text_widget = prepare_file_text()
load_button = prepare_load_butotn()