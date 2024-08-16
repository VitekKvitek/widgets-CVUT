import cv2 as cv
import numpy as np
import os
from os import listdir, path
from os.path import isfile, join
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import clear_output, display, FileLink
from settings_handler import add_widget_to_settings
from data_module import iv, name_mapping
import tkinter as tk
from tkinter import filedialog
from ipywidgets import HBox, VBox

# Color values
obstacle_color = [255,0,0]  # Red obstacles
road_color = [128,64,128]   # Purple road
void_color = [255,255,255]  # White ignore region
opacity = 0.6

false_positive_color = [255, 0, 0]   # Red
false_negative_color = [0, 0, 255]  # Blue
true_positive_color = [0, 255, 0]  # Green

obstacle_cont_color = (0,0,255)  # Blue for obstacle contours
road_cont_color = (0,255,0)   # Green for road contours
thickness = 3

def create_mask(gt, use_dataset, threshold):
    #road_threshold = 0.4
    void_mask = (iv.ground_truth == 255)

    if(use_dataset):
        #road_mask = (original_gt == 1)
        obstacle_mask = (gt == 0)
    else:
        #road_mask = (original_gt <= road_threshold)  
        obstacle_mask = (gt > threshold) 
        
    return void_mask, obstacle_mask

def draw_overlay(opacity, original_image, gt, use_dataset, threshold):

    assert original_image.shape[:2] == gt.shape[:2], "Images must have the same dimensions"
    void_mask, obstacle_mask = create_mask(gt, use_dataset, threshold)

    # Create overlays
    #road_overlay = np.zeros_like(original_image)
    #road_overlay[:] = road_color

    obstacle_overlay = np.zeros_like(original_image)
    obstacle_overlay[:] = obstacle_color
    
    void_overlay = np.zeros_like(original_image)
    void_overlay[:] = void_color

    

    # Apply masks
    if(use_dataset):
        void_clr_mask = void_overlay * void_mask
        obstacle_clr_mask = obstacle_overlay * obstacle_mask
        combined_mask = cv.add(void_clr_mask, obstacle_clr_mask)
    else:
        if iv.ignore:
            obstacle_mask[np.any(void_mask == True, axis=-1)] = False
        #road_clr_mask = road_overlay * road_mask [:, :, np.newaxis]  # Add channel dimension
        obstacle_clr_mask = obstacle_overlay * obstacle_mask [:, :, np.newaxis]
        combined_mask = obstacle_clr_mask

    if opacity != 1:
        combined_image = cv.addWeighted(combined_mask, opacity, original_image, 1, 0)
    else:        
        # full colors if 100% opacity
        combined_image = np.where(combined_mask.any(axis=-1, keepdims=True), obstacle_clr_mask, original_image)
    return combined_image

def draw_contours(original_image, original_gt, dataset, threshold):
    #road_threshold = 0.4

    if(dataset):
        # Convert image to grayscale
        imgray = cv.cvtColor(original_gt, cv.COLOR_BGR2GRAY)
        # Apply thresholding
        #_, road_thresh = cv.threshold(imgray, 1, 255, 0)
        _, obstacle_thresh = cv.threshold(imgray, 0, 255, 0)
    else:
        # Convert normalized ground truth to binary images
        #road_thresh = (original_gt >= road_threshold).astype(np.uint8) * 255 
        obstacle_thresh = (original_gt < threshold).astype(np.uint8) * 255 

    # Find contours
    #road_contours, _ = cv.findContours(road_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    obstacle_contours, _ = cv.findContours(obstacle_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw the contours on a copy of the original image
    contours_image = original_image.copy()
    #cv.drawContours(contours_image, road_contours, -1, road_cont_color, thickness)  
    cv.drawContours(contours_image, obstacle_contours, -1, obstacle_cont_color, thickness)  
    
    return contours_image
    
def draw_differance(original_image, gt, def_gt, thresh):
    
    
    _, obstacle_mask = create_mask(gt, False, thresh)
    
    mask1 = obstacle_mask
    mask2 = np.any(def_gt == 0, axis=-1)

    if iv.ignore:
        # Set mask1 to False where def_gt has value 255
        mask1[np.any(def_gt == 255, axis=-1)] = False

    combined_image = np.zeros((mask1.shape[0], mask1.shape[1], 3), dtype=np.uint8)

    # Set colors where booleans are different
    combined_image[(mask1 & ~mask2)] = false_positive_color
    combined_image[(~mask1 & mask2)] = false_negative_color
    combined_image[(mask1 & mask2)] = true_positive_color
    
    # Create black mask
    black_mask = np.all(combined_image == [0, 0, 0], axis=-1)

    grayscale_image = np.dot(original_image[..., :3], [0.299, 0.587, 0.114])
    grayscale_image_expanded = np.stack([grayscale_image]*3, axis=-1)

    # Create a copy of the combined image to add the grayscale image
    result_image = np.copy(combined_image)
    result_image[black_mask] = grayscale_image_expanded[black_mask]

    return result_image

def normalize_score(row_index, norm_scale=0.2, norm_thr=0.9):
    score = load_gt(iv.selected_file, iv.selected_folder , iv.selected_algo[row_index], False)
    
    # Create masks for ID and OOD
    mask_id = score <= norm_thr
    mask_ood = score > norm_thr
    
    # Apply normalization for ID scores
    score[mask_id] = norm_scale * (score[mask_id] / norm_thr)
    
    # Apply normalization for OOD scores
    score[mask_ood] = norm_scale + (1.0 - norm_scale) * ((score[mask_ood] - norm_thr) / (1.0 - norm_thr))
    
    # Convert the 2D array to a 3D array by applying a colormap
    score_rgb = plt.cm.magma(score)[:, :, :3]  # Discard the alpha channel
    score_rgb = (score_rgb * 255).astype(np.uint8)
    return score_rgb

def get_all_files(folder_path):
    all_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return all_files

def get_all_folders(directory):
    return [name for name in listdir(directory) if path.isdir(path.join(directory, name))]

def convert_name(name):
    if name in name_mapping:
        return name_mapping[name]
    else:
        print("Name not found in name_mapping ")

def get_base_folder(selected_folder):
    # Determine folder path
    base_folder_path = 'data/export/datasets/' + selected_folder + '/test/'
    return base_folder_path

def load_gt(selected_file, selected_folder, selected_algo, use_dataset):
    # Determine gt path
    if use_dataset:        
        gt_folder_path = os.path.join(get_base_folder(selected_folder), 'gt')
        original_gt_path = os.path.join(gt_folder_path, selected_file)
    else:
        results_folder = os.path.join('data/export/results/', selected_algo, convert_name(selected_folder), 'preds')
        base_filename = os.path.splitext(selected_file)[0]
        original_gt_path = os.path.join(results_folder, f"{base_filename}..png.npy")

    # Load ground truth
    original_gt = cv.imread(original_gt_path) if use_dataset else np.load(original_gt_path)
    assert original_gt is not None, f"original_gt could not be read from {original_gt_path}"    
    return original_gt

def load_image(selected_file, selected_folder):
    # Load original image
    images_folder_path = os.path.join(get_base_folder(selected_folder), 'imgs')
    original_image_path = os.path.join(images_folder_path, selected_file)
    #print(original_image_path)
    original_image = cv.imread(original_image_path)
    assert original_image is not None, f"original_image could not be read from {original_image_path}"

    # Convert BGR to RGB format
    original_image_rgb = original_image[:, :, [2, 1, 0]]
    return original_image_rgb

def make_legend(target_h, target_w):
    
    legend_path = 'legend.png'
    legend_image = np.full((target_h, target_w, 3), 255, dtype=np.uint8)
    legend = cv.imread(legend_path, cv.IMREAD_UNCHANGED)
    
    # Get dimensions of the white image (target) and legend
    legend_h, legend_w = legend.shape[:2]

    # Determine the scaling factor to maintain aspect ratio
    scale_factor = min(target_w / legend_w, target_h / legend_h)

    # Resize the legend image while maintaining aspect ratio
    new_size = (int(legend_w * scale_factor), int(legend_h * scale_factor))
    legend_resized = cv.resize(legend, new_size, interpolation=cv.INTER_AREA)

    # Calculate top-left corner to place the legend in the center of the white image
    x_offset = (target_w - new_size[0]) // 2
    y_offset = (target_h - new_size[1]) // 2

    # Overlay the resized legend onto the white image
    legend_image[y_offset:y_offset+new_size[1], x_offset:x_offset+new_size[0]] = legend_resized
    return legend_image[:, :, [2, 1, 0]]

def generate_image_text(border_height, border_width, num_channels, row_index):
    from results_comparer import get_score_for_current_img
    try:
        score0, score1 = get_score_for_current_img()
        if row_index == 0:
            text = f"{iv.selected_algo[0]} | AP: {score0['AP']*100:0.2f} | FPRat95: {score0['FPRat95']*100:0.2f} | Threshold: {iv.threshold[0]:0.5}"
        else:
            text = f"{iv.selected_algo[1]} | AP: {score1['AP']*100:0.2f} | FPRat95: {score1['FPRat95']*100:0.2f} | Threshold: {iv.threshold[1]:0.5}"
    except:
        text = "Score was not load properly"

    # Create a white image inside the function
    white_image = np.full((border_height, border_width, num_channels), 255, dtype=np.uint8)
    
    font = cv.FONT_HERSHEY_SIMPLEX  # Choose font type
    font_scale = 1.0  # Font scale factor that multiplies the base font size
    font_color = (0, 0, 0)  # Font color (black in BGR format)
    thickness = 2  # Thickness of the text

    # Calculate the position to center the text
    text_size = cv.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (white_image.shape[1] - text_size[0]) // 2
    text_y = (white_image.shape[0] + text_size[1]) // 2
    
    # Put the text on the white image
    cv.putText(white_image, text, (text_x, text_y), font, font_scale, font_color, thickness)
    
    return white_image

# Generate all images for one row
def make_row(original_image, mask, use_dataset, thresh, row_index = None, def_gt = None):
    
    opacity_overlay = draw_overlay(opacity, original_image, mask, use_dataset, thresh)
    contour_w_overlay = draw_contours(opacity_overlay, mask, use_dataset, thresh)
    #overlay_100 = draw_overlay(1, img, mask, use_dataset, thresh)
    
    # Create a white border of width 10 pixels
    border_width = 10
    white_border = np.full((original_image.shape[0], border_width, original_image.shape[2]), 255, dtype=original_image.dtype)
    
    # Concatenate with borders
    if use_dataset:
        target_h, target_w = original_image.shape[:2]
        row = np.concatenate((
            original_image, 
            white_border, 
            contour_w_overlay, 
            white_border,
            make_legend(target_h, target_w)), axis=1)
    else:
        row = np.concatenate((
            normalize_score(row_index),
            white_border,
            opacity_overlay,
            white_border,
            draw_differance(original_image, mask, def_gt, thresh)), axis=1)
    return row

def save_image(b):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Define the default 'output' directory
    default_directory = 'output'

    # Ensure 'output' directory exists, create it if it doesn't
    if not os.path.exists(default_directory):
        os.makedirs(default_directory)

    # Open the file dialog to choose the directory, with 'output' as the initial directory
    initial_dir = os.path.abspath(default_directory)
    directory = filedialog.askdirectory(initialdir=initial_dir, title='Select Folder')

    # If no directory is selected, use the 'output' directory
    if not directory:
        directory = initial_dir

    # Generate a unique filename based on folder and file name
    unique_name = f"{convert_name(iv.selected_folder)}-{iv.selected_file}"

    # Open the save as dialog allowing the user to choose the folder and filename
    file_path = filedialog.asksaveasfilename(initialdir=directory,  # start in the selected directory
                                             initialfile=unique_name,
                                             title="Save Image As",
                                             filetypes=[("PNG files", "*.png")])

    # If the user cancels the save, return early
    if not file_path:
        return

    # Ensure the file has a .png extension
    if not file_path.endswith(".png"):
        file_path += ".png"

    # Combine rows and save the image in RGB format
    final_rgb = combine_rows()[:, :, [2, 1, 0]]
    cv.imwrite(file_path, final_rgb)

    # Display a link to the saved file
    relative_path = os.path.relpath(file_path, start=os.getcwd())
    with output:
        display(FileLink(relative_path))

def combine_rows():
    border_height = 100
    border_width = iv.row[0].shape[1]
    num_channels = iv.row[0].shape[2]
    
    # Concatenate the rows with the white borders
    final_image = np.concatenate((
        iv.row[2],
        generate_image_text(border_height, border_width, num_channels, 0),
        iv.row[0],
        generate_image_text(border_height, border_width, num_channels, 1),
        iv.row[1]), axis=0)
    
    return final_image
    
# value updating select image and select algo
def update_vals(alg0,alg1,folder,dataset):
    iv.selected_algo[0] = alg0
    iv.selected_algo[1] = alg1
    iv.selected_folder = convert_name(folder) #FA > fish
    iv.selected_file = dataset
    show_final(3)

def save_rows(row_index):
    
    # New files for everything
    if row_index > 1:
        selected_file = iv.selected_file
        selected_folder = iv.selected_folder

        iv.predict[0] = load_gt(selected_file, selected_folder, iv.selected_algo[0], False)
        iv.predict[1] = load_gt(selected_file, selected_folder, iv.selected_algo[1], False)
        iv.ground_truth = load_gt(selected_file, selected_folder, iv.selected_algo[1], True)
        iv.original_image = load_image(selected_file, selected_folder)

        iv.row[0] = make_row(iv.original_image, iv.predict[0], False, iv.threshold[0], 0, iv.ground_truth)
        iv.row[1] = make_row(iv.original_image, iv.predict[1], False, iv.threshold[1], 1, iv.ground_truth)
        iv.row[2] = make_row(iv.original_image, iv.ground_truth, True, iv.threshold[0])
    
    # Edit only changed file based on slider 
    else:
        iv.row[row_index] = make_row(iv.original_image, iv.predict[row_index], False, iv.threshold[row_index], row_index, iv.ground_truth)

output = widgets.Output()

def show_final(row_index, fig_size=(24, 12)):
    save_rows(row_index)
    
    filename = os.path.splitext(iv.selected_file)[0]
    final_image = combine_rows()
    title = f"Folder: {iv.selected_folder} | File: {filename}" 
    with output:
        clear_output(wait=True)
        plt.figure(figsize=fig_size)
        plt.imshow(final_image)
        plt.axis('off')
        plt.title(title)
        plt.show()

def update_slider( _ , row_index, slider):
    try:
        if not slider.disabled:
            
            if obstacle_slider1.disabled and not obstacle_slider0.disabled:
                obstacle_slider1.value = obstacle_slider0.value
                iv.threshold[0] = obstacle_slider0.value
                iv.threshold[1] = obstacle_slider1.value
                show_final(3)

            else:
                iv.threshold[row_index] = slider.value
                show_final(row_index)
    # When using before sliders were initialized
    except:
        pass
    
def sync_sliders(checked):
    obstacle_slider1.disabled = checked 

    
def toggle_ignore(checked):
    iv.ignore = checked
    show_final(3)


def prepare_sliders():
    thresh = iv.threshold

    obstacle_slider0 = widgets.FloatSlider(value=thresh[0], min=0.90, max=0.99999, step=0.00001, description='Obstacle Threshold First row', readout_format='.5f', 
                                           style={'description_width': '300px'}, layout=widgets.Layout(width='800px'), continuous_update=False)
    obstacle_slider0.observe(lambda change: update_slider(change, 0, obstacle_slider0), names='value')
    add_widget_to_settings(obstacle_slider0, 'obstacle_slider0')

    obstacle_slider1 = widgets.FloatSlider(value=thresh[1], min=0.90, max=0.99999, step=0.00001, description='Obstacle Threshold Second row', readout_format='.5f', 
                                           style={'description_width': '300px'}, layout=widgets.Layout(width='800px'), continuous_update=False)
    obstacle_slider1.observe(lambda change: update_slider(change, 1, obstacle_slider1), names='value')
    add_widget_to_settings(obstacle_slider1,'obstacle_slider1')
    return obstacle_slider0, obstacle_slider1
obstacle_slider0, obstacle_slider1 = prepare_sliders()

def prepare_save_image():
    save_button = widgets.Button(description="Save Image")     
    save_button.on_click(lambda b:save_image(b))
    return save_button
save_button = prepare_save_image()

def prepare_sync_button():
    sync_button = widgets.Checkbox(    
        value=False,
        description='Sync sliders',
        disabled=False,
        indent=False
        )
    sync_button.observe(lambda change: sync_sliders(change['new']), names='value')
    add_widget_to_settings(sync_button, 'sync_button')
    return sync_button
sync_button = prepare_sync_button()

def prepare_ignore_button():
    ignore_button = widgets.Checkbox(    
        value=iv.ignore,
        description='Hide ignore region',
        disabled=False,
        indent=False
        )
    ignore_button.observe(lambda change: toggle_ignore(change['new']), names='value')
    add_widget_to_settings(ignore_button, 'ignore_button')
    return ignore_button
ignore_button = prepare_ignore_button()

def display_image_settings():
    sliders = VBox([obstacle_slider0, obstacle_slider1])
    buttons = HBox([sync_button, ignore_button, save_button])
    display(output, HBox([sliders, buttons]))