import json

widget_list = []
# Adds widget to the list of widgets which are going to be stored
def add(new_widget):
    widget_list.append(new_widget)
# Function to collect widget states
def get_widget_values():
    values_list = []
    for widget in widget_list:
        values_list.append(widget.value)
    return values_list
# _throwaway_ because button sends information about itself as argument
def save(_throwaway_):
    # Dump the list of values to file
    values_list = get_widget_values()
    with open('data/settings.json', 'w') as file:
        json.dump(values_list, file)

# Function to load widget values
def load_widget_states(loaded_value_list):
    for index,widget in enumerate(widget_list):
        widget.value = loaded_value_list[index]
# _throwaway_ because button sends information about itself as argument
def load(_throwaway_):
    # Load the list of values back from the file
    with open('data/settings.json', 'r') as file:
        loaded_vlaue_list = json.load(file)
    load_widget_states(loaded_vlaue_list)
    