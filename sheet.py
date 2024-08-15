#
# WARNING - AP and FPRat95 are hardcoded
#
import ipywidgets as widgets
import pandas as pd
from IPython.display import display, HTML
# Custom scripts
from results_loader import read_all_algo_jsons
import results_comparer
from settings_handler import add_widget_to_settings
from data_module import sd


indexes,col_names,data = read_all_algo_jsons()

def calculate_mean_average():
    ap_columns = sd.display_df.xs('AP', level=1, axis=1)
    # Get rid of old average
    ap_columns = ap_columns.drop('Average', axis=1)
    # Extract FPRat95
    fprat95_columns = sd.display_df.xs('FPRat95', level=1, axis=1)
    # Get rid of old average
    fprat95_columns = fprat95_columns.drop('Average', axis=1)
    # Calculate the row-wise mean of the 'AP' subcolumns
    ap_mean = ap_columns.mean(axis=1)
    # Calculate the row-wise mean of the 'FPRat95' subcolumns
    fprat95_mean = fprat95_columns.mean(axis=1)
    # Add the calculated mean as a new column to the original DataFrame
    sd.display_df[('Average', 'AP')] = ap_mean
    sd.display_df[('Average', 'FPRat95')] = fprat95_mean

def sort_by_average(df, called_by_button = False):
    # Determine the column to sort by
    if sd.average_type == 'AP':
        average_column = [('Average', 'AP')]
        ascend = sd.ascend_AP
        if called_by_button:
            sd.ascend_AP = not sd.ascend_AP
    else:
        average_column = [('Average', 'FPRat95')]
        ascend = sd.ascend_FPRat95
        if called_by_button:
            sd.ascend_FPRat95 = not sd.ascend_FPRat95
    # Sort the DataFrame by the selected average column and selected ascending
    sorted_df = df.sort_values(by=average_column, ascending=ascend)
    return sorted_df


# This function is called after clicking a sort button
def sort_button_on_click(button):
    # It gets score type from the description of button
    score_type = button.description.split()[-1]
    # checks if the first word is order type
    if button.description.split()[0] in ['asc', 'desc']:
    # gets the description without the first word (asc or desc)
        description = button.description.split()[1:]
    else:
        description = button.description.split()
    sd.average_type = score_type
    # Sets the new description
    if score_type == 'AP':
        button_FPRat95.description = 'Sort by FPRat95'
        if sd.ascend_AP:
            button.description = 'asc ' + ' '.join(description)
        else:
            button.description = 'desc ' + ' '.join(description)
    if score_type == 'FPRat95':
        button_AP.description = 'Sort by AP'
        if sd.ascend_FPRat95:
            button.description = 'asc ' + ' '.join(description)
        else:
            button.description = 'desc ' + ' '.join(description)
    sd.display_df = sort_by_average(sd.display_df, called_by_button=True)
    update_sheet()
    

# This function copies the original df and removes all blacklisted rows and columns
def drop_blackllisted():
    # Gets original df
    sd.display_df = sd.df.copy()
    # Cycle which drops rows
    for row in sd.bl_row:
        sd.display_df = sd.display_df.drop(row)
    # Cycle which drops columns
    for col in sd.bl_col:
        sd.display_df = sd.display_df.drop((col,'AP'), axis=1)
        sd.display_df = sd.display_df.drop((col,'FPRat95'), axis=1)


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
        sd.bl_row.append(button_description)
    # Whitelist scenario
    else:
        button.button_style = 'success'
        sd.bl_row.remove(button_description)
    export_sheet_row_index_to_comparer()
    update_sheet()

# Function that is called after toggle dataset button clicked
def on_button_toggle_ds_bl(change):
    # Gets the boolean state from the change dict
    toggled = change['new']
    # Gets the button from the change dict
    button = change['owner']
    button_description = button.description
    # Blacklist scenario
    if toggled:
        button.button_style = 'warning'
        # Adds clicked on dataset to blacklist
        sd.bl_col.append(button_description)
    # Whitelist scenario
    else:
        button.button_style = 'info'
        # Removes clicked on dataset from black list
        sd.bl_col.remove(button_description)
    export_sheet_column_index_to_comparer()
    update_sheet()

def toggle_highlight(change):
    toggled = change['new']
    button = change['owner']
    if toggled:
        button.button_style = 'danger'
        sd.apply_highlight = False
    else:
        button.button_style = 'success'
        sd.apply_highlight = True
    update_sheet()


# Functin which updates the showed (displayed) table
def update_sheet():
    drop_blackllisted()
    calculate_mean_average()
    sd.display_df = sort_by_average(sd.display_df)
    styled_df = style_dataframe(sd.display_df, sd.apply_highlight)
    with out:
        out.clear_output()
        display(HTML(styled_df.to_html()))


# Initial prepare of dataframe
def prepare_df():
    # create dataframe from dictionary
    df = pd.DataFrame(data)
    # Calculates from data length of 1 row
    length_of_1_row = len(data[0])
    # HARDCODED score types
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
    # | Dataset      |
    # | AP | FPRat95 |
    # | 99 | 2       |
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
    sd.df = df.copy()
    sd.display_df = df.copy()
    sd.display_df = sort_by_average(sd.display_df)


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
                                tooltip='Toggle algo',
                                icon='check' # (FontAwesome names without the `fa-` prefix)
                            )
        add_widget_to_settings(new_toggle_button, algo)
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
                                tooltip='Toggle dataset',
                                icon='check' # (FontAwesome names without the `fa-` prefix)
                            )
        new_toggle_button.observe(on_button_toggle_ds_bl, names='value')
        add_widget_to_settings(new_toggle_button, dataset)
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
    add_widget_to_settings(button_AP, 'button_AP', description= True)
    add_widget_to_settings(button_FPRat95, 'button_FPRat95', description= True)
    return button_AP, button_FPRat95

def prepare_highlight_button():
    highlight_button = widgets.ToggleButton(description="Highlight",
                                            button_style= "success")
    highlight_button.observe(toggle_highlight, names='value')
    add_widget_to_settings(highlight_button, 'highlight_button')
    return highlight_button

# Styling function
def style_dataframe(df, aply_highlight, column_width=60, border_style='solid', border_width='2px', border_color='black'):
    """
    Styles the DataFrame by highlighting min and max values, formatting numbers,
    setting fixed column widths, and drawing lines between columns.
    
    Parameters:
    - df: pd.DataFrame
        The DataFrame with multi-index columns to be styled.
    -aply_highlight: bool
        Bool if the highlight should be aplied
    - column_width: int
        The fixed width of each column in pixels.
    - border_style: str
        The style of the border (e.g., 'solid', 'dashed').
    - border_width: str
        The width of the border (e.g., '2px').
    - border_color: str
        The color of the border (e.g., 'black').
    
    Returns:
    - styled_df: Styler
        A Pandas Styler object with applied styles and formatting.
    """
    
    # Define a function to highlight the max/min values with green and the opposite with red
    def highlight_extremes(column):
        # Check if column is 'AP' to determine order of highlighting
        if column.name[1] == 'AP':
            # Find the maximum and second maximum
            is_max = column == column.max()
            is_second_max = column == column.nlargest(2).iloc[-1]
            
            # Highlight conditions
            return [
                'background-color: green' if max_v else
                'background-color: lightgreen' if second_max_v else ''
                for max_v, second_max_v in zip(is_max, is_second_max)
            ]

        elif column.name[1] == 'FPRat95':
            # Find the minimum and second minimum
            is_min = column == column.min()
            is_second_min = column == column.nsmallest(2).iloc[-1]
            # Highlight conditions
            return [
                'background-color: green' if min_v else
                'background-color: lightgreen' if second_min_v else ''
                for min_v, second_min_v in zip(is_min, is_second_min)
            ]

        else:
            # If not 'AP' or 'FPRat95', return empty styles
            return ['' for _ in column]
    
    if aply_highlight:
        # Apply highlighting
        styled_df = df.style.apply(highlight_extremes, axis=0)
    else:
        styled_df = df.style
    # Format the numbers to be multiplied by 100 and display with one decimal place
    styled_df = styled_df.format(lambda x: "{:.2f}".format(x * 100))
    # Define styles for headers and data cells
    styles = {
        (col[0], col[1]): [
            {'selector': 'th', 'props': [
                ('width', f'{column_width}px'),
                ('border-right', f'{border_width} {border_style} {border_color}'),
                ('border-left', f'{border_width} {border_style} {border_color}'),
                ('text-align', 'center')
            ]},
            {'selector': 'td', 'props': [
                ('border-right', f'{border_width} {border_style} {border_color}'),
                ('border-left', f'{border_width} {border_style} {border_color}'),
                ('text-align', 'center')
            ]}
        ]
        for col in df.columns
    }
    # Apply styles to the DataFrame
    styled_df = styled_df.set_table_styles(styles)
    
    return styled_df


def export_sheet_row_index_to_comparer():
    algo_list = sd.df.index
    algo_list = [item for item in algo_list if item not in sd.bl_row]
    results_comparer.import_sheet_row_index(algo_list)

def export_sheet_column_index_to_comparer():
    df_column_list = sd.df.columns.get_level_values(0)
    df_column_list = list(set(df_column_list))
    df_column_list.remove('Average')
    df_column_list = [item for item in df_column_list if item not in sd.bl_col]
    results_comparer.import_sheet_col_index(df_column_list)


# Function to display everything
def initial_display():
    prepare_df()
    hbox_button = widgets.HBox([button_AP, button_FPRat95, highlight_button])
    styled_df = style_dataframe(sd.display_df, sd.apply_highlight)
    with out:
        display(HTML(styled_df.to_html()))
    display(out)
    display(hbox_button)
    display(prepare_algo_black_list())
    display(prepare_dataset_black_list())
    export_sheet_row_index_to_comparer()
    export_sheet_column_index_to_comparer()


button_AP, button_FPRat95 = prepare_sort_buttons()
highlight_button = prepare_highlight_button()
# Out widget that displays sheet (table)
out = widgets.Output()