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
}
df = None
after_black_list_df = None
out = widgets.Output()

def sort_by_best_average(df, average_type):
    # Ensure the average_type is valid
    if average_type not in ['AP', 'FPRat95']:
        raise ValueError("average_type must be either 'AP' or 'FPRat95'")
    
    # Determine the column to sort by
    if average_type == 'AP':
        average_column = 'Average AP'
    else:
        average_column = 'Average FPRat95'
    
    # Sort the DataFrame by the selected average column in descending order
    sorted_df = df.sort_values(by=average_column, ascending=False)
    
    return sorted_df


def sort_button_on_click(button):
    global after_black_list_df
    score_type = button.description.split()[-1]
    after_black_list_df = sort_by_best_average(after_black_list_df, score_type)
    update_sheet()    

def on_button_toggle(change):
    global after_black_list_df
    global df
    toggled = change['new']
    button_description = change['owner'].description
    if toggled:
        after_black_list_df = after_black_list_df.drop(button_description)
    else:
        after_black_list_df.loc[button_description] = df.loc[button_description]
    update_sheet()
def update_sheet():
    with out:
        out.clear_output()
        display(HTML(after_black_list_df.to_html()))
        
def prepare_df():
    global df
    global after_black_list_df
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
    df = sort_by_best_average(df, 'AP')
    after_black_list_df = df.copy()
def prepare_toggle_buttons():
    all_mehtods = df.index.tolist()
    black_list = []
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
        black_list.append(new_toggle_button)
    return black_list
def prepare_sort_buttons():
    button_AP = widgets.Button(description="Sort by AP")
    button_AP.on_click(sort_button_on_click)
    button_FPRat95 = widgets.Button(description="Sort by FPRat95")
    button_FPRat95.on_click(sort_button_on_click)
    return button_AP, button_FPRat95
def initial_display():
    prepare_df()
    button_AP, button_FPRat95 = prepare_sort_buttons()
    display(button_AP,button_FPRat95)
    for button in prepare_toggle_buttons():
       display(button)
    with out:
        display(HTML(after_black_list_df.to_html()))
    display(out)