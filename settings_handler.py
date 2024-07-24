import json

# dictionary for all widgets which values are going to be tracked
widget_dic = {}
# current loaded settings from the file
# TODO can be just a memory reference not the whole dict
current_loaded_settings = {}
# Name of file in which the upcoming save of settings will be written
will_save_file_name = 'name_not_given'
# Adds widget to the list of widgets which are going to be stored
def add(new_widget, name):
    widget_dic[name] = new_widget
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
# Called by load_button - Function to load widget values
# _throwaway_ because button sends information about itself as argument
def load_widget_states(_throwaway_):
    for name,loaded_value in current_loaded_settings.items():
        widget_dic[name].value = loaded_value
# loads the data from json file and sets the current_loaded_settings
# Does not change widgets!!!
def load(change):
    # Get the uploaded file
    uploaded_file = change['new'][0]
    # Get the file content in byte format
    byte_data = uploaded_file['content'].tobytes()
    # Converts it to json
    json_data = json.loads(byte_data.decode('utf-8'))
    global current_loaded_settings
    current_loaded_settings = json_data
# This function is called by text button - sets name of file
def set_file_name(change):
    global will_save_file_name
    will_save_file_name = change['new']
    
    