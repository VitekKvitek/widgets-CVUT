import ipywidgets as widgets
from IPython.display import display
import pandas as pd
from IPython.display import display, HTML

# create a dictionary
# TODO - load part
data = {
    "Method 1": ["18", "25", "31", "10"],
    "Method 2": ["95", "36", "28", "33"],
    "Method 3": ["9", "42", "72", "22"],
    "Method 4": ["12", "69", "85", "15"],
    "Method 5": ["50", "23", "65", "14"],
    "Method 6": ["78", "45", "39", "20"],
    "Method 7": ["21", "56", "47", "33"],
    "Method 8": ["64", "32", "10", "57"],
    "Method 9": ["80", "54", "29", "17"],
    "Method 10": ["43", "67", "22", "11"],
}
# Dataframe with all of the data
df = None
# Dataframe version which will be displayed - after black list and sorting
display_df = None
# Out widget that displays sheet (table)
out = widgets.Output()

# Remembers the state of ascending AP and FPRat95
ascend_AP = True
ascend_FPRat95 = True

# Sorts the table based on selected criteria
def sort_by_average(df, average_type):
    global ascend_AP
    global ascend_FPRat95
    # Determine the column to sort by
    if average_type == 'AP':
        average_column = 'Average AP'
        ascend = ascend_AP
        ascend_AP = not ascend_AP
    else:
        average_column = 'Average FPRat95'
        ascend = ascend_FPRat95
        ascend_FPRat95 = not ascend_FPRat95
    
    # Sort the DataFrame by the selected average column and selected ascending
    sorted_df = df.sort_values(by=average_column, ascending=ascend)
    return sorted_df
# This function is called after clicking a sort button
def sort_button_on_click(button):
    global display_df
    # It gets score type from the description of button
    score_type = button.description.split()[-1]
    display_df = sort_by_average(display_df, score_type)
    update_sheet()
# Function that is called after toggle button clicked
def on_button_toggle(change):
    global display_df
    global df
    # Gets the boolean state from the change dict
    toggled = change['new']
    # Gets the button from the change dict
    button = change['owner']
    button_description = button.description
    if toggled:
        button.button_style = 'danger'
        display_df = display_df.drop(button_description)
    else:
        button.button_style = 'success'
        display_df.loc[button_description] = df.loc[button_description]
    update_sheet()
# Functin which updates the showed (displayed) table
def update_sheet():
    with out:
        out.clear_output()
        display(HTML(display_df.to_html()))
# Initial prepare of dataframe
def prepare_df():
    global df
    global display_df
    # create dataframe from dictionary
    df = pd.DataFrame(data)
    df = df.transpose()
    df.columns = ['Dataset 1 (AP)', 'Dataset 1 (FPRat95)', 'Dataset 2 (AP)', 'Dataset 2 (FPRat95)']
    # Extract AP and FPRat95 columns
    ap_columns = [col for col in df.columns if 'AP' in col]
    fprat95_columns = [col for col in df.columns if 'FPRat95' in col]

    df = df.apply(pd.to_numeric)
    # Calculate the average for AP and FPRat95
    df['Average AP'] = df[ap_columns].mean(axis=1)
    df['Average FPRat95'] = df[fprat95_columns].mean(axis=1)
    # stores the data in both dataframes
    df = sort_by_average(df, 'AP')
    # Copys the values of dataframe 
    display_df = df.copy()
# Function for preparing toggle buttons (blacklist) based on the amount of methods in it
def prepare_toggle_buttons():
    all_mehtods = df.index.tolist()
    black_list_buttons = []
    for method in all_mehtods:
        new_toggle_button = widgets.ToggleButton(
                                value=False,
                                description= method,
                                disabled=False,
                                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                                tooltip='Description',
                                icon='check' # (FontAwesome names without the `fa-` prefix)
                            )
        new_toggle_button.observe(on_button_toggle, names='value')
        black_list_buttons.append(new_toggle_button)
    # adds the buttons to the HBox so they shopup horizontally
    hbox = widgets.HBox(black_list_buttons)
    return hbox
# Prepares sort button
def prepare_sort_buttons():
    button_AP = widgets.Button(description="Sort by AP")
    button_AP.on_click(sort_button_on_click)
    button_FPRat95 = widgets.Button(description="Sort by FPRat95")
    button_FPRat95.on_click(sort_button_on_click)
    return button_AP, button_FPRat95
# Function to display everything
def initial_display():
    prepare_df()
    button_AP, button_FPRat95 = prepare_sort_buttons()
    display(button_AP,button_FPRat95)
    with out:
        display(HTML(display_df.to_html()))
    display(out)
    display(prepare_toggle_buttons())