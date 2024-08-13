import cv2 as cv
import numpy as np
import os
from os import listdir, path
from os.path import isfile, join
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import clear_output, display, FileLink
from settings_handler import add
from data_module import iv

# Color values
obstacle_color = [255,0,0]  # Red obstacles
road_color = [128,64,128]   # Purple road

false_positive_color = [255, 0, 0]   # Red
false_negative_color = [0, 0, 255]  # Blue
true_positive = [0, 255, 0]  # Green

obstacle_cont_color = (0,0,255)  # Blue for obstacle contours
road_cont_color = (0,255,0)   # Green for road contours
thickness = 3

def create_mask(original_gt, dataset, threshold):
    # Create binary masks from normalized values
    road_threshold = 0.4
    
    if(dataset):
        road_mask = (original_gt == 1)
        obstacle_mask = (original_gt == 0)
    else:
        road_mask = (original_gt <= road_threshold)  
        obstacle_mask = (original_gt > threshold) 
    
    return road_mask, obstacle_mask


def draw_overlay(opacity, original_image, original_gt, dataset, threshold):

    assert original_image.shape[:2] == original_gt.shape[:2], "Images must have the same dimensions"
    road_mask, obstacle_mask = create_mask(original_gt, dataset, threshold)

    # Create overlays
    road_overlay = np.zeros_like(original_image)
    road_overlay[:] = road_color

    obstacle_overlay = np.zeros_like(original_image)
    obstacle_overlay[:] = obstacle_color

    # Apply masks
    if(dataset):
        road_clr_mask = road_overlay * road_mask
        obstacle_clr_mask = obstacle_overlay * obstacle_mask
    else:
        road_clr_mask = road_overlay * road_mask [:, :, np.newaxis]  # Add channel dimension
        obstacle_clr_mask = obstacle_overlay * obstacle_mask [:, :, np.newaxis]

    combined_mask = cv.add(road_clr_mask, obstacle_clr_mask)

    if opacity != 1:
        combined_image = cv.addWeighted(combined_mask, opacity, original_image, 1, 0)
    else:        
        # full colors if 100% opacity
        combined_image = np.where(combined_mask.any(axis=-1, keepdims=True), combined_mask, original_image)
    return combined_image

def draw_contours(original_image, original_gt, dataset, threshold):
    road_threshold = 0.4

    if(dataset):
        # Convert image to grayscale
        imgray = cv.cvtColor(original_gt, cv.COLOR_BGR2GRAY)
        # Apply thresholding
        _, road_thresh = cv.threshold(imgray, 1, 255, 0)
        _, obstacle_thresh = cv.threshold(imgray, 0, 255, 0)
    else:
        # Convert normalized ground truth to binary images
        road_thresh = (original_gt >= road_threshold).astype(np.uint8) * 255 
        obstacle_thresh = (original_gt < threshold).astype(np.uint8) * 255 

    # Find contours
    #road_contours, _ = cv.findContours(road_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    obstacle_contours, _ = cv.findContours(obstacle_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw the contours on a copy of the original image
    contours_image = original_image.copy()
    #cv.drawContours(contours_image, road_contours, -1, road_cont_color, thickness)  
    cv.drawContours(contours_image, obstacle_contours, -1, obstacle_cont_color, thickness)  
    
    return contours_image
    
def draw_differance(img, gt, def_gt, thresh):
    # Mozna ziskat obstacle mask z draw conture/ overlay TODO?
    road_mask, obstacle_mask = create_mask(gt, False, thresh)
    
    mask1 = obstacle_mask
    mask2 = np.any(def_gt == 0, axis=-1)

    combined_image = np.zeros((mask1.shape[0], mask1.shape[1], 3), dtype=np.uint8)

    # Set colors where booleans are different
    combined_image[(mask1 & ~mask2)] = false_positive_color
    combined_image[(~mask1 & mask2)] = false_negative_color
    combined_image[(mask1 & mask2)] = true_positive

    # Create black mask
    black_mask = np.all(combined_image == [0, 0, 0], axis=-1)

    grayscale_image = np.dot(img[..., :3], [0.299, 0.587, 0.114])
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

def contract(name):
    match name:
        case "Fishyscapes_LaF":
            contraction = 'FS'

        case "RoadAnomaly":
            contraction = 'RA'

        case "RoadObstacles":
            contraction = 'RO'
        
        case "RoadObstacles21":
            contraction = 'RO21A'
        case _:
            print("Could not find correct contraction name")
            contraction = None
    return contraction

def decontract(name):
    match name:
        case "FS":
            long_name = "Fishyscapes_LaF"

        case 'RA':
            long_name = "RoadAnomaly"

        case 'RO':
            long_name = "RoadObstacles"
        
        case 'RO21A':
            long_name = "RoadObstacles21"
        case _:
            print("Could not find correct long name")
            long_name = None
    return long_name

def load_gt(selected_file, selected_folder, selected_algo, use_dataset):
    # Determine gt path
    if use_dataset:        
        gt_folder_path = os.path.join(get_base_folder(selected_folder), 'gt')
        original_gt_path = os.path.join(gt_folder_path, selected_file)
    else:
        results_folder = os.path.join('data/export/results/', selected_algo, contract(selected_folder), 'preds')
        base_filename = os.path.splitext(selected_file)[0]
        original_gt_path = os.path.join(results_folder, f"{base_filename}..png.npy")

    # Load ground truth
    original_gt = cv.imread(original_gt_path) if use_dataset else np.load(original_gt_path)
    assert original_gt is not None, f"original_gt could not be read from {original_gt_path}"    

    return original_gt

def get_base_folder(selected_folder):
    # Determine folder path
    base_folder_path = 'data/export/datasets/' + selected_folder + '/test/'
    return base_folder_path

def load_image(selected_file, selected_folder):
    # Load original image
    imgs_folder_path = os.path.join(get_base_folder(selected_folder), 'imgs')
    original_image_path = os.path.join(imgs_folder_path, selected_file)
    #print(original_image_path)
    original_image = cv.imread(original_image_path)
    assert original_image is not None, f"original_image could not be read from {original_image_path}"

    # Convert BGR to RGB format
    original_image_rgb = original_image[:, :, [2, 1, 0]]
    return original_image_rgb

# Generate all images for one row
def make_row(img, mask, use_dataset, thresh, row_index = None, def_gt = None):
    
    overlay_50 = draw_overlay(0.5, img, mask, use_dataset, thresh)
    contour_w_overlay = draw_contours(overlay_50, mask, use_dataset, thresh)
    #overlay_100 = draw_overlay(1, img, mask, use_dataset, thresh)
    
    # Create a white border of width 10 pixels
    border_width = 10
    white_border = np.full((img.shape[0], border_width, img.shape[2]), 255, dtype=img.dtype)
    
    # Concatenate with borders
    if use_dataset:
        row = np.concatenate((
            img, 
            white_border, 
            contour_w_overlay, 
            white_border, 
            np.full_like(mask, 255)), axis=1)
    else:
        row = np.concatenate((
            normalize_score(row_index),
            white_border,
            contour_w_overlay,
            white_border,
            draw_differance(img, mask, def_gt, thresh)), axis=1)
    return row

def generate_name():
    base_filename = os.path.splitext(iv.selected_file)[0] #strip extension
    # Name: folder-file-algo1-algo2.png
    unique_name = f"{contract(iv.selected_folder)}-{base_filename}-{iv.selected_algo[0][-15:]}-{iv.selected_algo[1][-15:]}"
    return unique_name

def save_image(b):
    # Create 'output' directory if it doesn't exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    unique_name = generate_name()+".png"
    print(unique_name)
    
    # Define the filename with the 'output' directory
    filename = os.path.join(output_dir, unique_name)
    final_rgb = combine_rows()[:, :, [2, 1, 0]]
    cv.imwrite(filename, final_rgb)
    
    with output:
        display(FileLink(filename))

def combine_rows():
    # Create a white border of height 10 pixels
    border_height = 10
    white_border = np.full((border_height, iv.row[0].shape[1], iv.row[0].shape[2]), 255, dtype=iv.row[0].dtype)
    
    # Concatenate the rows with the white borders
    final_image = np.concatenate((
        iv.row[2],
        white_border,
        iv.row[0],
        white_border,
        iv.row[1]), axis=0)
    
    return final_image
    
# value updating select image and select algo
def update_vals(alg0,alg1,folder,dataset):
    iv.selected_algo[0] = alg0
    iv.selected_algo[1] = alg1
    iv.selected_folder = decontract(folder)
    iv.selected_file = dataset
    show_final(3)

def save_rows(row_index):
    
    

    # New files for everything
    if row_index > 1:
        selected_file = iv.selected_file
        selected_folder = iv.selected_folder

        iv.images[0] = load_gt(selected_file, selected_folder, iv.selected_algo[0], False)
        iv.images[1] = load_gt(selected_file, selected_folder, iv.selected_algo[1], False)
        iv.images[2] = load_gt(selected_file, selected_folder, iv.selected_algo[1], True)
        iv.images[3] = load_image(selected_file, selected_folder)

        iv.row[0] = make_row(iv.images[3], iv.images[0], False, iv.threshold[0], 0, iv.images[2])
        iv.row[1] = make_row(iv.images[3], iv.images[1], False, iv.threshold[1], 1, iv.images[2])
        iv.row[2] = make_row(iv.images[3], iv.images[2], True, iv.threshold[0])
    
    # Edit only changed file based on slider 
    else:
        iv.row[row_index] = make_row(iv.images[3], iv.images[row_index], False, iv.threshold[row_index], row_index, iv.images[2])

output = widgets.Output()

def show_final(row_index, fig_size=(24, 12)):
    save_rows(row_index)
    
    final_image = combine_rows()
    title = generate_name()

    with output:
        clear_output(wait=True)
        plt.figure(figsize=fig_size)
        plt.imshow(final_image)
        plt.axis('off')
        plt.title(title)
        plt.show()

def update_slider( _ , row_index):
    # Update slider values in the global vals dictionary
    if row_index == 0:
        iv.threshold[0] = obstacle_slider0.value
    else:
        iv.threshold[1] = obstacle_slider1.value

    # Show the image with the updated slider values
    show_final(row_index)


def prepare_sliders():
    thresh = iv.threshold

    obstacle_slider0 = widgets.FloatSlider(value=thresh[0], min=0.95, max=1, step=0.0001, description='Obstacle Threshold First row', readout_format='.4f', 
                                           style={'description_width': 'initial'}, layout=widgets.Layout(width='800px'), continuous_update=False)
    obstacle_slider0.observe(lambda change: update_slider(change, 0), names='value')
    add(obstacle_slider0, 'obstacle_slider0')

    obstacle_slider1 = widgets.FloatSlider(value=thresh[1], min=0.95, max=1, step=0.0001, description='Obstacle Threshold Second row', readout_format='.4f', 
                                           style={'description_width': 'initial'}, layout=widgets.Layout(width='800px'), continuous_update=False)
    obstacle_slider1.observe(lambda change: update_slider(change, 1), names='value')
    add(obstacle_slider1,'obstacle_slider1')
    return obstacle_slider0, obstacle_slider1
obstacle_slider0, obstacle_slider1 = prepare_sliders()

def prepare_save_image():
    save_button = widgets.Button(description="Save Image")     
    save_button.on_click(lambda b:save_image(b))
    return save_button
save_button = prepare_save_image()

def display_image_settings():
    display(obstacle_slider0,  
            obstacle_slider1, 
            output,
            save_button)