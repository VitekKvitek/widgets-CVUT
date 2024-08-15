import json
from os import listdir,makedirs
from os.path import isfile, join, exists
import ipywidgets as widgets
from IPython.display import display
from collections import OrderedDict
# Dictionary for all widgets which values are going to be tracked
widgets_tracked = {}
# Dict in which are store widgets which descroption is going to be tracked
descriptions_tracked = {}
# Dict in which are store widgets which style is going to be tracked
styles_tracked = {}
# Widgets which are stored in order - to achive corret loading order
orderred_widgets_tracked = OrderedDict()
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
def add_widget_to_settings(new_tracked_widget, name, description = False, style = False):
    if description:
        descriptions_tracked[name] = new_tracked_widget
    elif style:
        styles_tracked[name] = new_tracked_widget
    else:
        widgets_tracked[name] = new_tracked_widget
def add_widget_to_ord_settings(new_tracked_widget, name, order):
    orderred_widgets_tracked[name] = (new_tracked_widget, order)
# Function to collect widget states
def get_widget_values():
    widget_values = {}
    for name, widget in widgets_tracked.items():
        widget_values[name] = widget.value
    return widget_values
def get_ordered_widget_values():
    sorted_ord_widg = OrderedDict(sorted(orderred_widgets_tracked.items(), key=lambda item: item[1][1]))
    widget_values = {}
    for name, widget_tuple in sorted_ord_widg.items():
        widget_values[name] = widget_tuple[0].value
    return widget_values 
def get_description_values():
    descriptions_dic = {}
    for name, widget in descriptions_tracked.items():
        descriptions_dic[name] = widget.description
    return descriptions_dic
def get_styles_values():
    styles_dic = {}
    for name, widget in styles_tracked.items():
        styles_dic[name] = widget.button_style
    return styles_dic
# Called by save button
def save(*args,**kwargs):
    # Dump the list of values to file
    all_values = {}
    widget_values = get_widget_values()
    ordered_widgets_values = get_ordered_widget_values()
    descriptions = get_description_values()
    styles = get_styles_values()
    all_values['widgets'] = widget_values
    all_values['ordered_widgets'] = ordered_widgets_values
    all_values['vars'] = vars_tracked
    all_values['descriptions'] = descriptions
    all_values['styles'] = styles
    with open(settings_folder + will_save_file_name+'.json', 'w') as file:
        json.dump(all_values, file)
    # Updates options of uploader widget
    uploader_widget.options = get_all_files()
# Called by load_button - Function to load widget values
def load_widget_states(loaded_vlaue_dict):
    for name,loaded_value in loaded_vlaue_dict['widgets'].items():
        if 'slider' in name:
            # disable
            pass
        widgets_tracked[name].value = loaded_value
    for name,loaded_value in loaded_vlaue_dict['ordered_widgets'].items():
        orderred_widgets_tracked[name][0].value = loaded_value 
    for name, loaded_value in loaded_vlaue_dict['vars'].items():
        vars_tracked[name] = loaded_value
    for name, loaded_value in loaded_vlaue_dict['descriptions'].items():
        descriptions_tracked[name].description = loaded_value
    for name, loaded_value in loaded_vlaue_dict['styles'].items():
        styles_tracked[name].button_style = loaded_value
    
    from sheet import update_sheet
    update_sheet()
    from results_comparer import regenerate
    regenerate()
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
# File upload widget
def prepare_uploader():
    all_presets = get_all_files()
    uploader_widget = widgets.Dropdown(
        options= all_presets,
        description='Choose preset',
        disabled=False,
    )
    # Adds uploader widget to settigns handler - on save it updates the options it can chose from
    uploader_widget.observe(set_load_file_name, names = 'value') # observes change in value of the widget
    global will_load_file_name
    will_load_file_name = all_presets[0]
    return uploader_widget
# Save button widget
def prepare_save_button():
    save_button = widgets.Button(
    description ='Save',
    tooltip ='Click to save data',
    button_style ='success'  # 'success' (green), 'info' (blue), 'warning' (yellow), 'danger' (red)
)
    save_button.on_click(save)
    return save_button
# Load button
def prepare_load_butotn():
    # Create a load button widget
    load_button = widgets.Button(
    description ='Load',
    tooltip ='Click to load data',
    button_style ='success'  # 'success' (green), 'info' (blue), 'warning' (yellow), 'danger' (red)
)
    load_button.on_click(load)
    return load_button
# Text input for naming a preset
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
# Display all widgets needed for settign to work
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