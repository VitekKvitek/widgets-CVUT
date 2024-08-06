import json
from os import listdir
from os.path import isfile, join
import ipywidgets as widgets
from IPython.display import display
# dictionary for all widgets which values are going to be tracked
widget_dic = {}
settings_folder = 'settings/'
# Name of file in which the upcoming save of settings will be written
will_save_file_name = 'name_not_given'
will_load_file_name = None
uploader_widget = None
# Adds widget to the list of widgets which are going to be stored
def add(new_widget, name):
    widget_dic[name] = new_widget
def add_uploader_widget(uploader_widget_par):
    global uploader_widget
    uploader_widget = uploader_widget_par
# Function to collect widget states
def get_widget_values():
    values_dic = {}
    # TODO
    for name, widget in widget_dic.items():
        values_dic[name] = widget.value
    return values_dic
# Called by save button
def save(*args,**kwargs):
    # Dump the list of values to file
    values_dic = get_widget_values()
    with open(settings_folder + will_save_file_name+'.json', 'w') as file:
        json.dump(values_dic, file)
    # Updates options of uploader widget
    uploader_widget.options = get_all_files()
# Called by load_button - Function to load widget values
def load_widget_states(loaded_vlaue_dict):
    for name,loaded_value in loaded_vlaue_dict.items():
        widget_dic[name].value = loaded_value
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
    add_uploader_widget(uploader_widget)
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