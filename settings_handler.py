import json
from os import listdir
from os.path import isfile, join
# dictionary for all widgets which values are going to be tracked
widget_dic = {}
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
# _throwaway_ because button sends information about itself as argument
def save(_throwaway_):
    # Dump the list of values to file
    values_dic = get_widget_values()
    with open('data/'+will_save_file_name+'.json', 'w') as file:
        json.dump(values_dic, file)
    # Updates options of uploader widget
    uploader_widget.options = get_all_files()
# Called by load_button - Function to load widget values
# _throwaway_ because button sends information about itself as argument
def load_widget_states(loaded_vlaue_dict):
    for name,loaded_value in loaded_vlaue_dict.items():
        widget_dic[name].value = loaded_value
# loads the data from json file and sets the current_loaded_settings
# Does not change widgets!!!
def load(_throwaway_):
    # Load the list of values back from the file
    with open('data/' + will_load_file_name, 'r') as file:
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
    folder = 'data/'
    all_files = [f for f in listdir(folder) if isfile(join(folder, f))]
    return all_files