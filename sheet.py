#
# WARNING - AP and FPRat95 are hardcoded
#
import ipywidgets as widgets
import pandas as pd
from IPython.display import display, HTML
# Custom scripts
from results_loader import read_all_algo_jsons
import results_comparer
# create a dictionary
# TODO - load part

indexes,col_names,data = read_all_algo_jsons()


# Dataframe with all of the data
df = None# Dataframe version which will be displayed - after black list and sorting
display_df = None
# Black list for columns
bl_col = []
# Black list for rows
bl_row = []
# Out widget that displays sheet (table)
out = widgets.Output()

# Stores the state of ascending AP and FPRat95
ascend_AP = False
ascend_FPRat95 = False
# Stores the column by which it should be ordered
average_type = 'AP'
# Sorts the table based on selected criteria
def calculate_mean_average():
    global display_df
    ap_columns = display_df.xs('AP', level=1, axis=1)
    # Get rid of old average
    ap_columns = ap_columns.drop('Average', axis=1)
    # Extract FPRat95
    fprat95_columns = display_df.xs('FPRat95', level=1, axis=1)
    # Get rid of old average
    fprat95_columns = fprat95_columns.drop('Average', axis=1)
    # Calculate the row-wise mean of the 'AP' subcolumns
    ap_mean = ap_columns.mean(axis=1)
    # Calculate the row-wise mean of the 'FPRat95' subcolumns
    fprat95_mean = fprat95_columns.mean(axis=1)
    # Add the calculated mean as a new column to the original DataFrame
    display_df[('Average', 'AP')] = ap_mean
    display_df[('Average', 'FPRat95')] = fprat95_mean
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
# This function copies the original df and removes all blacklisted rows and columns
def drop_blackllisted():
    global display_df
    # Gets original df
    display_df = df.copy()
    # Cycle which drops rows
    for row in bl_row:
        display_df = display_df.drop(row)
    # Cycle which drops columns
    for col in bl_col:
        display_df = display_df.drop((col,'AP'), axis=1)
        display_df = display_df.drop((col,'FPRat95'), axis=1)
# This function is called after clicking a sort button
def sort_button_on_click(button):
    global display_df
    global average_type
    # It gets score type from the description of button
    score_type = button.description.split()[-1]
    average_type = score_type
    display_df = sort_by_average(display_df, called_by_button=True)
    update_sheet()
# Function that is called after toggle algo button clicked
def on_button_toggle_alg_bl(change):
    # Gets the boolean state from the change dict
    toggled = change['new']
    # Gets the button from the change dict
    button = change['owner']
    button_description = button.description
    # Blacklist scenario
    if toggled:
        button.button_style = 'danger'
        bl_row.append(button_description)
    # Whitelist scenario
    else:
        button.button_style = 'success'
        bl_row.remove(button_description)
    export_sheet_row_index_to_comparer()
    update_sheet()
# Function that is called after toggle dataset button clicked
def on_button_toggle_ds_bl(change):
    global display_df
    global df
    # Gets the boolean state from the change dict
    toggled = change['new']
    # Gets the button from the change dict
    button = change['owner']
    button_description = button.description
    # Blacklist scenario
    if toggled:
        button.button_style = 'warning'
        # Adds clicked on dataset to blacklist
        bl_col.append(button_description)
    # Whitelist scenario
    else:
        button.button_style = 'info'
        # Removes clicked on dataset from black list
        bl_col.remove(button_description)
    export_sheet_column_index_to_comparer()
    update_sheet()
# Functin which updates the showed (displayed) table
def update_sheet():
    global display_df
    drop_blackllisted()
    calculate_mean_average()
    display_df = sort_by_average(display_df)
    styled_df = display_df.style.apply(highlight_min_max, axis= 0)
    styled_df = styled_df.format(lambda x: "{:.1f}".format(x * 100))
    column_width = 60  # Fixed width in pixels
    styled_df = styled_df.set_table_styles(
    {
        (col[0], col[1]): [{'selector': 'th, td', 'props': [('width', f'{column_width}px')]}]
        for col in df.columns
    }
)
    with out:
        out.clear_output()
        display(HTML(styled_df.to_html()))
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
    display_df = sort_by_average(display_df)
# Function for preparing toggle buttons (blacklist) for algos
def prepare_algo_black_list():
    all_algos = indexes
    black_list_buttons = []
    for algo in all_algos:
        new_toggle_button = widgets.ToggleButton(
                                value=False,
                                description= algo,
                                disabled=False,
                                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                                tooltip='Description',
                                icon='check' # (FontAwesome names without the `fa-` prefix)
                            )
        new_toggle_button.observe(on_button_toggle_alg_bl, names='value')
        black_list_buttons.append(new_toggle_button)
    # adds the buttons to the HBox so they shopup horizontally
    hbox = widgets.HBox(black_list_buttons)
    return hbox
# Function for preparing toggle buttons (blacklist) for datasets
def prepare_dataset_black_list():
    all_datasets = col_names
    black_list_buttons = []
    for dataset in all_datasets:
        new_toggle_button = widgets.ToggleButton(
                                value=False,
                                description= dataset,
                                disabled=False,
                                button_style='info', # 'success', 'info', 'warning', 'danger' or ''
                                tooltip='Description',
                                icon='check' # (FontAwesome names without the `fa-` prefix)
                            )
        new_toggle_button.observe(on_button_toggle_ds_bl, names='value')
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
    styled_df = display_df.style.apply(highlight_min_max, axis= 0)
    styled_df = styled_df.format(lambda x: "{:.1f}".format(x * 100))
    column_width = 60  # Fixed width in pixels
    styled_df = styled_df.set_table_styles(
    {
        (col[0], col[1]): [{'selector': 'th, td', 'props': [('width', f'{column_width}px')]}]
        for col in df.columns
    }
)
    with out:
        display(HTML(styled_df.to_html()))
    display(out)
    display(prepare_algo_black_list())
    display(prepare_dataset_black_list())
    export_sheet_row_index_to_comparer()
    export_sheet_column_index_to_comparer()
def highlight_min_max(column):
    if column.name[1] == 'AP':
        is_max = column == column.max()
        is_min = column == column.min()
        return ['background-color: lightgreen' if max_v else 'background-color: lightcoral' if min_v else '' for max_v, min_v in zip(is_max, is_min)]
    elif column.name[1] == 'FPRat95':
        is_min = column == column.min()
        is_max = column == column.max()
        return ['background-color: lightgreen' if min_v else 'background-color: lightcoral' if max_v else '' for min_v, max_v in zip(is_min, is_max)]
    else:
        return ['' for _ in column]
def export_sheet_row_index_to_comparer():
    algo_list = df.index
    algo_list = [item for item in algo_list if item not in bl_row]
    results_comparer.import_sheet_row_index(algo_list)
def export_sheet_column_index_to_comparer():
    df_column_list = df.columns.get_level_values(0)
    df_column_list = list(set(df_column_list))
    df_column_list.remove('Average')
    df_column_list = [item for item in df_column_list if item not in bl_col]
    results_comparer.import_sheet_col_index(df_column_list)