import cv2 as cv
import numpy as np
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
from IPython.display import FileLink


def drawOverlay(opacity, original_image, original_gt):
    obstacle_clr = [255,0,0]
    road_clr = [128,64,128]

    assert original_image.shape[:2] == original_gt.shape[:2], "Images must have the same dimensions"

    # Create masks of gt
    road_mask = (original_gt == 1)
    obstacle_mask = (original_gt == 0)

    # Create a road and anomaly overlays with the same size as the image
    road_overlay = np.zeros_like(original_image)
    road_overlay[:, :] = road_clr

    obstacle_overlay = np.zeros_like(original_image)
    obstacle_overlay[:, :] = obstacle_clr


    #Create colored masks
    road_clr_mask = road_overlay * road_mask
    obstacle_clr_mask = obstacle_overlay * obstacle_mask
    combined_mask = cv.add(road_clr_mask, obstacle_clr_mask)

    if(opacity != 1):
        combined_image = cv.addWeighted(combined_mask, opacity, original_image , 1, 0)
    else:    
        inverted_mask = np.where(combined_mask == 0, 1, 0).astype(np.uint8)
        combined_image = cv.add(combined_mask, inverted_mask * original_image)
    return combined_image

def drawContoure(original_image, original_gt):
    road_clr_con = (0,255,0)
    obstacle_clr_con = (255,0,0)
    thickness = 3
    
    # Convert image to grayscale
    imgray = original_gt[:,:,0]

    # Apply thresholding
    _, road_thresh = cv.threshold(imgray, 1, 255, 0)
    _, obstacle_thresh = cv.threshold(imgray, 0, 255, 0)

    # FindContours 
    road_contours, _ = cv.findContours(road_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    obstacle_contours, _ = cv.findContours(obstacle_thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw the contours on the original image (or a copy of it)
    contours_image = original_image.copy()
    cv.drawContours(contours_image, road_contours, -1, road_clr_con, thickness)  
    cv.drawContours(contours_image, obstacle_contours, -1, obstacle_clr_con , thickness)  
    return contours_image

def get_all_files(folder_path):
    all_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return all_files

