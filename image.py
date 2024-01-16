# Note: This software is Reserved Product developed by Planet Innovation
#
# Copyright (c) 2024, Planet Innovation
# 436 Elgar Rd, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.
#

import cv2
import numpy as np
from scipy import stats as st
from well import Well_Mask, Well
import os
import time

class Mask:
    def __init__(self, img, num_wells):
        self.__file_path = img
        self.__original_mask_img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        self.__number_of_wells = num_wells
        self.__mask_blurred = None
        self.__wells = [Well_Mask(w) for w in range(num_wells)]
        self.__mask_ostu_thresh = None
        self.__combined_mask = None
        self.__time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(os.path.getmtime(img)))
        self.__min_well_size = 1000   # NEEDS TO BE CHARACTERIZED
        self.__max_well_size = 7000   # NEEDS TO BE CHARACTERIZED
    
    def set_mask_blurred(self, img):
        self.__mask_blurred = img

    def set_mask_thresh_img(self, img):
        self.__mask_ostu_thresh = img

    def set_combined_mask(self, img):
        self.__combined_mask = img

    def get_file_path(self):
        return self.__file_path

    def get_time(self):
        return self.__time
    
    def get_num_wells(self):
        return self.__number_of_wells

    def get_original_mask_img(self):
        return self.__original_mask_img
    
    def get_mask_thresh_img(self):
        return self.__mask_ostu_thresh

    def get_mask_blurred(self):
        return self.__mask_blurred
    
    def get_well(self, well_num):
        assert 0 <= well_num < self.__number_of_wells, "Well Index not valid"
        well = self.__wells[well_num]
        assert well.get_well_num() == well_num, "Return Well is not what we are looking for"
        return well
    
    def get_combined_mask(self):
        return self.__combined_mask
    
    def get_min_well_size(self):
        return self.__min_well_size
    
    def get_max_well_size(self):
        return self.__max_well_size
    
    def print_all(self):

        original_mask_img = self.get_original_mask_img()
        number_of_wells = self.get_num_wells()
        mask_blurred = self.get_mask_blurred()
        mask_ostu_thresh = self.get_mask_thresh_img()
        combined_mask = self.get_combined_mask()

        print(f'Original Mask Img: {original_mask_img.shape[1], original_mask_img.shape[0]} | Number of Wells: {number_of_wells} | Mask Blurred: {mask_blurred.shape[1], mask_blurred.shape[0]} | Otsu Threshold: {mask_ostu_thresh.shape[1], mask_ostu_thresh.shape[0]}')
        for w in range(number_of_wells):
            well = self.get_well(w)
            well.print_all()


    def getMasks(self):
        """ This function takes in an image and returns the masks of each well for that image. 
        First it uses a gaussian blur and otsu threshold as a first pass to isolate the well. 
        Next, the algo uses openCVs find contours function to isolate the wells in the image from the OTSU mask and eliminate contours that are too small to be wells.
        Finally it returns the masks of the wells 
        
        """
        img = self.get_original_mask_img()
        # Gaussian blur
        blurred = cv2.GaussianBlur(img, (7, 7), 0)
        self.set_mask_blurred(blurred)

        # Otsu thresholding used for bimodal images (two peaks of intensities)
        ret, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
        self.set_mask_thresh_img(thresh_otsu)

        # Find the contours in the image
        contours, hierarchy = cv2.findContours(thresh_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
        # contours, hierarchy = cv2.findContours(thresh_otsu, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) 

        # show otsu threshold
        # cv2.imshow('thresh_otsu', thresh_otsu)
        # cv2.waitKey()

        # Initialize Well Counter and Mask Arrays
        wellCounter = 0
        WHITE = 255
        DRAWINGTHICKNESS = 1

        # get minimum and maximum area thresholds for well size (characterized)
        minimumwellsize = self.get_min_well_size()
        maximumwellsize = self.get_max_well_size()

        # Iterate through contours found with cv2.findCountours and throw away those too small for well size (noise)
        for index, cont in enumerate(contours):
            areaContour = cv2.contourArea(cont)
            print(f'Area of Found Contour: {areaContour}')
            if areaContour < minimumwellsize or areaContour > maximumwellsize:
                print(f'Area of Contour Not Within Threshold: Contour Index {index}')
                continue
            else:
                assert (wellCounter < self.get_num_wells()), "Too Many Wells Found"
                well = self.get_well(wellCounter)
                well.set_area(areaContour)
                well.set_contours(cont)
                print(f'Well found | Contour Index: {index}')
                mask = np.zeros(img.shape, dtype='uint8')
                cv2.drawContours(mask, contours, index, color = WHITE, thickness = -DRAWINGTHICKNESS)
                well.set_mask(mask)
                # cv2.imshow('Mask', mask)
                # cv2.waitKey()
                wellCounter += 1

        assert (wellCounter == self.get_num_wells()), "Not enough wells found in mask: Stop Post Processing"

        
    def combineMasks(self, show):
        """ This function combines all of the well masks in the class and displays the combined mask.
        """
        original_img = self.get_original_mask_img()
        size_og = original_img.shape
        combined = np.zeros(size_og, dtype='uint8')

        for w in range(self.get_num_wells()):
            well = self.get_well(w)
            mask = well.get_mask()
            combined = cv2.bitwise_or(combined, mask)
        
        self.set_combined_mask(combined)
        if show:
            cv2.imshow('Combined', combined)
            cv2.waitKey()

    def saveImages(self, directory):
        """This function saves all the masked images"""
        folder_time = self.get_time()
        if not os.path.exists(directory + folder_time + "/"):
            os.makedirs(directory + folder_time + "/")
        cv2.imwrite(directory + folder_time + "/" + "gaussian_blurred.png", self.get_mask_blurred())
        cv2.imwrite(directory + folder_time + "/" + "combined_mask.png", self.get_combined_mask())
        cv2.imwrite(directory + folder_time + "/" + "otsu_threshold_mask.png", self.get_mask_thresh_img())
        cv2.imwrite(directory + folder_time + "/" + "original_img.png", self.get_original_mask_img())
        for w in range(self.get_num_wells()):
            well = self.get_well(w)
            cv2.imwrite(directory + folder_time + "/" + f"well_{w}_mask.png", well.get_mask())
        return directory + folder_time + "/"




class Image:
    def __init__(self, img, num_wells):
        self.__file_path = img
        self.__image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        self.__number_of_wells = num_wells
        self.__wells = None
        self.__time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(os.path.getmtime(img)))
    
    def get_file_path(self):
        return self.__file_path

    def get_time(self):
        return self.__time
    
    def get_image(self):
        return self.__image
    
    def get_num_wells(self):
        return self.__number_of_wells
    
    def get_well(self, well_num):
        assert 0 <= well_num < self.__number_of_wells, "Well Index not valid"
        return self.__wells[well_num]
    
    def initialize_wells_from_mask(self, mask):
        """ This function initializes this images wells from mask: mask img, contour, and contour area
        """
        assert self.get_num_wells() == mask.get_num_wells(), "Image Well Number and Mask Well Number do not match"
        wells = []
        for w in range(self.get_num_wells()):
            mask_well = mask.get_well(w)
            wells.append(Well(well=mask_well.get_well_num(), contours=mask_well.get_contours(), area=mask_well.get_area(), mask=mask_well.get_mask()))
        self.__wells = wells

    def analyze_img(self):
        """ This function takes in a image and iterates through each of the wells.
        It extracts the intensity statistics for each of the wells using the corresponding wells mask.
        """
        for w in range(self.get_num_wells()):
            well = self.get_well(w)
            well.get_pixels_from_mask(self.get_image())
            well.get_well_statistics()

    def print_all(self):

        image = self.get_image()
        number_of_wells = self.get_num_wells()

        print(f'Original Mask Img: {image.shape[1], image.shape[0]} | Number of Wells: {number_of_wells}')
        for w in range(number_of_wells):
            well = self.get_well(w)
            well.print_all()

    def saveImages(self, directory):
        """This function saves all the masked images"""
        folder_time = self.get_time()
        if not os.path.exists(directory + folder_time + "/"):
            os.makedirs(directory + folder_time + "/")
        for w in range(self.get_num_wells()):
            well = self.get_well(w)
            cv2.imwrite(directory + folder_time + "/" + f"well_{w}_Image_mask.png", well.get_mask())
        return directory + folder_time + "/"