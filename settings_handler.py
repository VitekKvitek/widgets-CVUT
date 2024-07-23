import json

widget_dic = {}
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
def load_widget_states(loaded_value_dic):
    for name,loaded_value in loaded_value_dic.items():
        widget_dic[name].value = loaded_value
        
# _throwaway_ because button sends information about itself as argument
def load(_throwaway_):
    # Load the list of values back from the file
    with open('data/settings.json', 'r') as file:
        loaded_vlaue_dic = json.load(file)
    load_widget_states(loaded_vlaue_dic)
    