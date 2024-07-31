# script for comparing per frame rusults
import ipywidgets as widgets
# Custom scripts
import sheet

algo_selector_1 = widgets.Dropdown(
    options=['1', '2', '3'],
    value='2',
    description='Number:',
    disabled=False,
)
algo_selector_2 = widgets.Dropdown(
    options=['1', '2', '3'],
    value='2',
    description='Number:',
    disabled=False,
)