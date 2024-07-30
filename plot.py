import cv2 as cv
import numpy as np
import os
from os import listdir, path
from os.path import isfile, join


def drawOverlay(opacity, original_image, original_gt, dataset):
    obstacle_clr = [255,0,0]  # Red for obstacles
    road_clr = [128,64,128]   # Purple for road

    assert original_image.shape[:2] == original_gt.shape[:2], "Images must have the same dimensions"

    # Create binary masks from normalized gt values
    if(dataset):
        road_mask = (original_gt == 1)
        obstacle_mask = (original_gt == 0)
    else:
        road_mask = (original_gt <= 0.5)  # Assuming road values are 0.5 or higher
        obstacle_mask = (original_gt > 0.5)  # Assuming obstacle values are less than 0.5

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
        inverted_mask = np.where(combined_mask == 0, 1, 0).astype(np.uint8)
        combined_image = cv.add(combined_mask, inverted_mask * original_image)
    
    return combined_image

def drawContours(original_image, original_gt, dataset):
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
        road_thresh = (original_gt >= 0.5).astype(np.uint8) * 255  # Threshold for roads
        obstacle_thresh = (original_gt < 0.5).astype(np.uint8) * 255  # Threshold for obstacles

    # Find contours
    road_contours, _ = cv.findContours(road_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    obstacle_contours, _ = cv.findContours(obstacle_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw the contours on a copy of the original image
    contours_image = original_image.copy()
    cv.drawContours(contours_image, road_contours, -1, road_clr_con, thickness)  
    cv.drawContours(contours_image, obstacle_contours, -1, obstacle_clr_con, thickness)  
    
    return contours_image

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

def load_images(selected_file, use_dataset, selected_folder, selected_model):
    # Determine folder paths
    base_folder_path = 'data/export/datasets/' + selected_folder + '/test/'
    if use_dataset:
        gt_folder_path = os.path.join(base_folder_path, 'gt')
        original_gt_path = os.path.join(gt_folder_path, selected_file)
    else:
        results_folder = os.path.join('data/export/results/', selected_model, contract(selected_folder), 'preds')
        print(results_folder)
        base_filename = os.path.splitext(selected_file)[0]
        original_gt_path = os.path.join(results_folder, base_filename+"..png.npy")
    print(original_gt_path)

    # Load ground truth
    original_gt = cv.imread(original_gt_path) if use_dataset else np.load(original_gt_path)
    assert original_gt is not None, f"original_gt could not be read from {original_gt_path}"

    # Load original image
    imgs_folder_path = os.path.join(base_folder_path, 'imgs')
    original_image_path = os.path.join(imgs_folder_path, selected_file)
    #print(original_image_path)
    original_image = cv.imread(original_image_path)
    assert original_image is not None, f"original_image could not be read from {original_image_path}"

    # Convert BGR to RGB format
    original_image_rgb = original_image[:, :, [2, 1, 0]]
    return original_image_rgb, original_gt




