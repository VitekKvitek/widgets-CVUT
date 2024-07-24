import json

widget_dic = {}
current_loaded_settings = {}
# Adds widget to the list of widgets which are going to be stored
def add(new_widget, name):
    widget_dic[name] = new_widget
    # widget_list.append(new_widget)
    
# Function to collect widget states
def get_widget_values():
    values_dic = {}
    # TODO
    for name, widget in widget_dic.items():
        values_dic[name] = widget.value
    return values_dic

# _throwaway_ because button sends information about itself as argument
def save(_throwaway_):
    # Dump the list of values to file
    values_dic = get_widget_values()
    with open('data/settings.json', 'w') as file:
        json.dump(values_dic, file)

# Function to load widget values
def load_widget_states(_throwaway_):
    for name,loaded_value in current_loaded_settings.items():
        widget_dic[name].value = loaded_value

def load(change):
    # Get the uploaded file
    uploaded_file = change['new'][0]
    # Get the file content in byte format
    byte_data = uploaded_file['content'].tobytes()
    # Converts it to json
    json_data = json.loads(byte_data.decode('utf-8'))
    global current_loaded_settings
    current_loaded_settings = json_data