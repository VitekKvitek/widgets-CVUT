import ipywidgets as widgets
from IPython.display import display
import pandas as pd
from IPython.display import display, HTML
# Custom scripts
from results_loader import read_all_jsons
# create a dictionary
# TODO - load part

indexes,col_names,data = read_all_jsons()


# Dataframe with all of the data
df = None
# Dataframe version which will be displayed - after black list and sorting
display_df = None
# Out widget that displays sheet (table)
out = widgets.Output()

# Stores the state of ascending AP and FPRat95
ascend_AP = False
ascend_FPRat95 = False
# Stores the column by which it should be ordered
average_type = 'Average AP'
# Sorts the table based on selected criteria
def sort_by_average(df, called_by_button = False):
    global ascend_AP
    global ascend_FPRat95
    global average_type
    # Determine the column to sort by
    
    if average_type == 'AP':
        if called_by_button:
            ascend_AP = not ascend_AP
        average_column = [('Average', 'AP')]
        ascend = ascend_AP
    else:
        if called_by_button:
            ascend_FPRat95 = not ascend_FPRat95
        average_column = [('Average', 'FPRat95')]
        ascend = ascend_FPRat95
    
    # Sort the DataFrame by the selected average column and selected ascending
    sorted_df = df.sort_values(by=average_column, ascending=ascend)
    return sorted_df
# This function is called after clicking a sort button
def sort_button_on_click(button):
    global display_df
    global average_type
    # It gets score type from the description of button
    score_type = button.description.split()[-1]
    average_type = score_type
    display_df = sort_by_average(display_df, called_by_button=True)
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
        display_df = sort_by_average(display_df)
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
    # Calculates from data length of 1 row
    length_of_1_row = len(data[0])
    # TODO? - hardcoded
    score_types = ['AP', 'FPRat95']
    # Calculates how many score types is there
    score_types_count = len(score_types)
    # Creates sub column based on the length of the row
    sub_col= score_types * (length_of_1_row//score_types_count)
    # ['A','B'] -> ['A','A','B','B'] "multiplies" each element by score_count_type
    # --> To support multiple index
    col = [element for element in col_names for _ in range(score_types_count)]
    # Sets multipleindex columns to the df
    # Example:
    # | full name    |
    # |name |surname |
    # |Borek|Stavitel|
    df.columns = pd.MultiIndex.from_arrays([col,sub_col])
    # Sets the indexes
    df.index = indexes
    # Extract AP
    ap_columns = df.xs('AP', level=1, axis=1)
    # Extract FPRat95
    fprat95_columns = df.xs('FPRat95', level=1, axis=1)
    # Calculate the row-wise mean of the 'AP' subcolumns
    ap_mean = ap_columns.mean(axis=1)
    # Calculate the row-wise mean of the 'FPRat95' subcolumns
    fprat95_mean = fprat95_columns.mean(axis=1)
    # Add the calculated mean as a new column to the original DataFrame
    df[('Average', 'AP')] = ap_mean
    df[('Average', 'FPRat95')] = fprat95_mean
    display_df = df.copy()
    #BUG
    #style_display_sheet()
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
def style_display_sheet():
    global display_df
    # Define the styles to center the main column names
    styles = {
    ('RA', ''): [{'selector': 'th', 'props': [('text-align', 'center')]}],
    ('FS', ''): [{'selector': 'th', 'props': [('text-align', 'center')]}],
    ('RO21A', ''): [{'selector': 'th', 'props': [('text-align', 'center')]}],
    ('RO', ''): [{'selector': 'th', 'props': [('text-align', 'center')]}],
    ('Average', ''): [{'selector': 'th', 'props': [('text-align', 'center')]}],
    }

    # Apply the styles and display the DataFrame
    display_df = df.style.set_table_styles(styles, axis=1)