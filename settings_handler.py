import json
from os import listdir,makedirs
from os.path import isfile, join, exists
import ipywidgets as widgets
from IPython.display import display
# Dictionary for all widgets which values are going to be tracked
widget_dic = {}
description_widget_dic = {}
# Dictionary for all variables that are going to be tracked
# Most of the times values that are associated with buttons but can not be accessed through the button
variable_dic = {}
# Default settings folder
settings_folder = 'settings/'
# Name of file in which the upcoming save of settings will be written
will_save_file_name = 'unnamed_preset'
will_load_file_name = None
# Adds widget to the list of widgets which are going to be stored
def add(new_object_to_remember, name, widget = True, description = False):
    if widget:
        if description:
            description_widget_dic[name] = new_object_to_remember
        else:
            widget_dic[name] = new_object_to_remember
    else:
        variable_dic[name] = new_object_to_remember
        pass
# Function to collect widget states
def get_widget_values():
    widget_values_dic = {}
    for name, widget in widget_dic.items():
        widget_values_dic[name] = widget.value
    return widget_values_dic
def get_var_values():
    var_value_dict = {}
    for name, var in variable_dic.items():
        var_value_dict[name] = var[0]
    return var_value_dict
def get_description_values():
    descriptions_dic = {}
    for name, widget in description_widget_dic.items():
        descriptions_dic[name] = widget.description
    return descriptions_dic
# Called by save button
def save(*args,**kwargs):
    print('start save')
    # Dump the list of values to file
    all_values = {}
    widget_values_dic = get_widget_values()
    var_value_dic = get_var_values()
    description_dict = get_description_values()
    all_values['widgets'] = widget_values_dic
    all_values['variables'] = var_value_dic
    all_values['description'] = description_dict
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
            widget_dic[name].value = loaded_value
    # Confirms newly loaded algos
    from results_comparer import make_confirmation
    make_confirmation()
    # After selecting algos, set the value to newly loaded img selector value
    # Otherwise would cause crash
    widget_dic['img_selector'].value = img_selector_value
    for name, loaded_value in loaded_vlaue_dict['variables'].items():
        variable_dic[name][0] = loaded_value
    for name, loaded_value in loaded_vlaue_dict['description'].items():
        description_widget_dic[name].description = loaded_value
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