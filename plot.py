import cv2 as cv
import numpy as np
import os
from os import listdir, path
from os.path import isfile, join

import matplotlib.pyplot as plt


import ipywidgets as widgets
from IPython.display import display
from IPython.display import FileLink

from IPython.display import clear_output, display


def create_mask(original_gt, dataset, threshold):
    # Create binary masks from normalized values
    if(dataset):
        road_mask = (original_gt == 1)
        obstacle_mask = (original_gt == 0)
    else:
        road_mask = (original_gt <= threshold[0])  
        obstacle_mask = (original_gt > threshold[1]) 
    
    return road_mask, obstacle_mask


def drawOverlay(opacity, original_image, original_gt, dataset, threshold):
    #print(threshold)
    obstacle_clr = [255,0,0]  # Red obstacles
    road_clr = [128,64,128]   # Purple road

    assert original_image.shape[:2] == original_gt.shape[:2], "Images must have the same dimensions"
    road_mask, obstacle_mask = create_mask(original_gt, dataset, threshold)

    # Create overlays
    road_overlay = np.zeros_like(original_image)
    road_overlay[:] = road_clr

    obstacle_overlay = np.zeros_like(original_image)
    obstacle_overlay[:] = obstacle_clr

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
        combined_image = np.where(combined_mask.any(axis=-1, keepdims=True), combined_mask, original_image)

    return combined_image

def drawContours(original_image, original_gt, dataset, threshold):
    
    #if BUG debuging
    #plt.imshow(original_gt)
    #plt.title(dataset)
    #plt.axis('off')
    #plt.show()
    
    road_clr_con = (0,255,0)   # Green for road contours
    obstacle_clr_con = (255,0,0)  # Red for obstacle contours
    thickness = 3
    
    if(dataset):
        # Convert image to grayscale
        imgray = cv.cvtColor(original_gt, cv.COLOR_BGR2GRAY)
        # Apply thresholding
        _, road_thresh = cv.threshold(imgray, 1, 255, 0)
        _, obstacle_thresh = cv.threshold(imgray, 0, 255, 0)
    else:
        # Convert normalized ground truth to binary images
        road_thresh = (original_gt >= threshold[0]).astype(np.uint8) * 255  # Threshold for roads
        obstacle_thresh = (original_gt < threshold[1]).astype(np.uint8) * 255  # Threshold for obstacles

    # Find contours
    road_contours, _ = cv.findContours(road_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    obstacle_contours, _ = cv.findContours(obstacle_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw the contours on a copy of the original image
    contours_image = original_image.copy()
    cv.drawContours(contours_image, road_contours, -1, road_clr_con, thickness)  
    cv.drawContours(contours_image, obstacle_contours, -1, obstacle_clr_con, thickness)  
    
    return contours_image

def draw_differance(img, gt, def_gt, thresh):
    
    # Mozna ziskat obstacle mask z draw conture/ overlay
    road_mask, obstacle_mask = create_mask(gt, False, thresh)
    
    wrong_color = [255, 0, 0]
    missed_color = [0, 255, 0]

    mask1 = obstacle_mask
    mask2 = np.any(def_gt == 0, axis=-1)

    combined_image = np.zeros((mask1.shape[0], mask1.shape[1], 3), dtype=np.uint8)

    # Set colors where booleans are different
    combined_image[(mask1 & ~mask2)] = wrong_color
    combined_image[(~mask1 & mask2)] = missed_color

    # Create black mask
    black_mask = np.all(combined_image == [0, 0, 0], axis=-1)

    grayscale_image = np.dot(img[..., :3], [0.299, 0.587, 0.114])
    grayscale_image_expanded = np.stack([grayscale_image]*3, axis=-1)

    # Create a copy of the combined image to add the grayscale image
    result_image = np.copy(combined_image)
    result_image[black_mask] = grayscale_image_expanded[black_mask]

    return result_image

def get_all_files(folder_path):
    all_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return all_files

def get_all_folders(directory):
    # Return only directories, not files
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

def load_gt(selected_file, selected_folder, selected_algo, use_dataset):
    # Determine gt path
        
    if use_dataset:        
        gt_folder_path = os.path.join(get_base_folder(selected_folder), 'gt')
        original_gt_path = os.path.join(gt_folder_path, selected_file)
    else:
        results_folder = os.path.join('data/export/results/', selected_algo, contract(selected_folder), 'preds')
        base_filename = os.path.splitext(selected_file)[0]
        original_gt_path = os.path.join(results_folder, f"{base_filename}..png.npy")
    #print(original_gt_path)

    # Load ground truth
    original_gt = cv.imread(original_gt_path) if use_dataset else np.load(original_gt_path)
    assert original_gt is not None, f"original_gt could not be read from {original_gt_path}"
    return original_gt

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

def get_base_folder(selected_folder):
    # Determine folder path
    base_folder_path = 'data/export/datasets/' + selected_folder + '/test/'
    return base_folder_path

def process_image(img, gt, use_dataset, thresh, def_gt = None):
    # Three images
    contoured_image = drawContours(img, gt, use_dataset, thresh)
    overlay_50 = drawOverlay(0.5, img, gt, use_dataset, thresh)
    overlay_100 = drawOverlay(1, img, gt, use_dataset, thresh)
    
    if(use_dataset):
        four_imgs = np.concatenate((contoured_image, overlay_50, overlay_100, img), axis=1)
    else:
        four_imgs = np.concatenate((contoured_image, overlay_50, overlay_100, draw_differance(img, gt, def_gt, thresh)), axis=1)
    
    
    return four_imgs

def save_image(r1, r2, r3, b):
    # Create 'output' directory if it doesn't exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the filename with the 'output' directory
    filename = os.path.join(output_dir, 'combined_image.png')
    
    final_rgb = combine_rows(r1, r2, r3)[:, :, [2, 1, 0]]
    
    cv.imwrite(filename, final_rgb)
    
    #TODO display properly
    #display(FileLink(filename))

def combine_rows(r1, r2, r3):
    final_image = np.concatenate((r1, r2, r3), axis=0)  
    return final_image



vals = {
    'images': [None, None, None, None],  # [pred_gt, pred_gt2, default_gt, default_image]
    'processed_images': [None, None, None],  # [alg1, alg2, default]
    'selected_file': '01_Hanns_Klemm_Str_45_000002_000190.png',
    'selected_folder': 'Fishyscapes_LaF',
    'selected_algo': ['grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1',
                      'grood_knn_e2e_cityscapes_500k_fl003_condensv5_randomcrop1344_hflip_nptest_lr0025wd54_ipdf0_ioodpdf0uni1_staticood1'],
    'threshold': [0.8, 0.997] 
}


def make_combined(new_gt, id):
    # změna slideru = ulozeny #2 (ctyrty obrazek) a default zustanou stejne, nacteni #1 jen metod na kresleni       show_final(False, 0)
    # změna metody = ulozeny #1 a default zustane stejny, nacteni gt noveho + metody kresleni                       show_final(True, 1)
    # změna filu = nacteni novych obrazku + gt + metod kresleni u všech obrázků (id 3)                              show_final(True/False, 2)
    
    global vals

    # New files for everything
    if id > 1:
        selected_file = vals['selected_file']
        selected_folder = vals['selected_folder']

        vals['images'][0] = load_gt(selected_file, selected_folder, vals['selected_algo'][0], False)
        vals['images'][1] = load_gt(selected_file, selected_folder, vals['selected_algo'][1], False)
        vals['images'][2] = load_gt(selected_file, selected_folder, vals['selected_algo'][1], True)
        vals['images'][3] = load_image(selected_file, selected_folder)

        vals['processed_images'][0] = process_image(vals['images'][3], vals['images'][0], False, vals['threshold'], vals['images'][2])
        vals['processed_images'][1] = process_image(vals['images'][3], vals['images'][1], False, vals['threshold'], vals['images'][2])
        vals['processed_images'][2] = process_image(vals['images'][3], vals['images'][2], True, vals['threshold'])
    
    # New process / gt + process for selected image 
    else:
        # Process image with new gt with ID
        if new_gt:
            vals['images'][id] = load_gt(vals['selected_file'], vals['selected_folder'], vals['selected_algo'][id], False)
            vals['processed_images'][id] = process_image(vals['images'][3], vals['images'][id], False, vals['threshold'], vals['images'][2])
        # Process with old gt with ID 
        else:
            vals['processed_images'][id] = process_image(vals['images'][3], vals['images'][id], False, vals['threshold'], vals['images'][2])


def show_final(new_gt, id, fig_size=(16, 12)):
    make_combined(new_gt, id)
    final_image = combine_rows(vals['processed_images'][2], vals['processed_images'][0], vals['processed_images'][1])
    

    with output:
        clear_output(wait=True)
        plt.figure(figsize=fig_size)
        plt.imshow(final_image)
        plt.axis('off')
        plt.title('Contours and Overlays')
        plt.show()

def update_slider(change, id):    
    if(id == 0):
        vals['threshold'] = [road_slider0.value, obstacle_slider0.value]
    
    else:
        vals['threshold'] = [road_slider1.value, obstacle_slider1.value]
    
    # Show the image with the updated slider values
    show_final(False, id)

def prepare_save_image():
    save_button = widgets.Button(description="Save Image")     
    save_button.on_click(lambda b:save_image(vals['processed_images'][2], vals['processed_images'][0], vals['processed_images'][1], b))
    return save_button
save_button = prepare_save_image()

def prepare_sliders():
    road_slider0 = widgets.FloatSlider(value=0.8, min=0.4, max=0.9995, step=0.0001, description='Road Threshold', readout_format='.4f',
                                  style={'description_width': 'initial'}, layout=widgets.Layout(width='500px'))
    road_slider0.observe(lambda change:update_slider(change, 0), names='value')

    obstacle_slider0 = widgets.FloatSlider(value=0.997, min=0.95, max=1, step=0.0001, description='Obstacle Threshold', readout_format='.4f', 
                                        style={'description_width': 'initial'}, layout=widgets.Layout(width='500px'))
    obstacle_slider0.observe(lambda change:update_slider(change, 0), names='value')


    road_slider1 = widgets.FloatSlider(value=0.8, min=0.4, max=0.9995, step=0.0001, description='Road Threshold', readout_format='.4f',
                                    style={'description_width': 'initial'}, layout=widgets.Layout(width='500px'))
    road_slider1.observe(lambda change:update_slider(change, 1), names='value')

    obstacle_slider1 = widgets.FloatSlider(value=0.997, min=0.95, max=1, step=0.0001, description='Obstacle Threshold', readout_format='.4f', 
                                        style={'description_width': 'initial'}, layout=widgets.Layout(width='500px'))
    obstacle_slider1.observe(lambda change:update_slider(change, 1), names='value')
    return road_slider0, obstacle_slider0, road_slider1, obstacle_slider1
road_slider0, obstacle_slider0, road_slider1, obstacle_slider1 = prepare_sliders()

def display_image_settings():
    display(road_slider0, 
            obstacle_slider0, 
            road_slider1, 
            obstacle_slider1, 
            output, 
            save_button)
output = widgets.Output()




def funkce():
    vals['selected_algo'][0] = 'nix'
    vals['selected_algo'][1] = 'nix'
    vals['selected_folder'] = 'nix'
    vals['selected_file'] = 'nix'
    show_final(False, 3)

