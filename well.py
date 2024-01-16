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

class Well_Mask:
    def __init__(self, well, contours=None, area=None, mask=None):
        self.__well_num = well
        self.__contours = contours  
        self.__area = area
        self.__mask = mask

    def set_contours(self, contours):
        self.__contours = contours

    def set_area(self, area):
        self.__area = area

    def set_mask(self, mask):
        self.__mask = mask
    
    def get_contours(self):
        return self.__contours
    
    def get_well_num(self):
        return self.__well_num
    
    def get_area(self):
        return self.__area
    
    def get_mask(self):
        return self.__mask
    
    def print_all(self):
        well_num = self.get_well_num()
        contours = self.get_contours()
        area = self.get_area()
        mask = self.get_mask()

        print(f'Well Num: {well_num} | Area: {area}  | Contours: {contours.shape} | Mask: {mask.shape[1], mask.shape[0]}')

class Well(Well_Mask):
    def __init__(self, well, contours, area, mask):
        super().__init__(well=well, contours=contours, area=area, mask=mask)
        self.__img = None
        self.__mean = None
        self.__median = None
        self.__stdev = None
        self.__mode = None
        self.__minimum = None
        self.__maximum = None
        self.__pixel_int_array = None

    def set_pixel_int_array(self, arr):
        self.__pixel_int_array = arr

    def set_img(self, img):
        self.__img = img

    def set_mean(self, avg):
        self.__mean = avg

    def set_median(self, median):
        self.__median = median

    def set_stdev(self, std):
        self.__stdev = std

    def set_mode(self, mode):
        self.__mode = mode

    def set_min(self, minimum):
        self.__minimum = minimum

    def set_max(self, maximum):
        self.__maximum = maximum

    def get_img(self):
        return self.__img

    def get_pixel_int_array(self):
        return self.__pixel_int_array

    def get_mean(self):
        return self.__mean
    
    def get_median(self):
        return self.__median

    def get_stdev(self):
        return self.__stdev

    def get_mode(self):
        return self.__mode

    def get_min(self):
        return self.__minimum

    def get_max(self):
        return self.__maximum
    
    
    def print_all(self):
        well_num = self.get_well_num()
        img = self.get_img()
        mean = self.get_mean()
        stdev = self.get_stdev()
        mode = self.get_mode()
        minimum = self.get_min()
        maximum = self.get_max()
        contours = self.get_contours()
        area = self.get_area()
        pixel_int_array = self.get_pixel_int_array()
        mask = self.get_mask()
        median = self.get_median()

        print(f'Well Num: {well_num} | Img: {img.shape[1], img.shape[0]} | Contours: {contours.shape} | Pixel Int Array: {len(pixel_int_array)} | Mask: {mask.shape[1], mask.shape[0]}')
        print(f'Area: {area} | Mean: {mean} | Stdev: {stdev} | Mode: {mode} | Median: {median} | Minimum: {minimum} | Maximum: {maximum}')

        
    def get_pixels_from_mask(self, img):
        """ This function uses the well mask to extract the pixels for that well. It sets the pixel_int_array with the corresponding pixel points and there intensities.
        
        """
        WHITE = 255
        self.set_img(img)
        # Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(self.get_mask() == WHITE)
        assert len(pts[0]) == len(pts[1]), "Mask does not give x, y pts of even length"

        well_pix = []
        for pt in zip(pts[0], pts[1]):
            well_pix.append([pt[0], pt[1], img[pt[0], pt[1]]])

        self.set_pixel_int_array(well_pix)

    
    def get_well_statistics(self):
        """ This function uses the pixel_int_array to extract statistics about the img.
        """

        pixelArray = self.get_pixel_int_array()
        int_array = []
        for pix in pixelArray:
            int_array.append(pix[2])

        mean = np.mean(int_array)
        stdev = np.std(int_array)
        mode = st.mode(int_array)
        minimum = np.min(int_array)
        maximum = np.max(int_array)
        median = np.median(int_array)

        print(f'Well Num: {self.get_well_num()} | Area: {self.get_area()} | Mean: {mean} | Stdev: {stdev} | Mode: {mode} | Median: {median} | Minimum: {minimum} | Maximum: {maximum}')

        self.set_mean(mean)
        self.set_max(maximum)
        self.set_min(minimum)
        self.set_mode(mode)
        self.set_stdev(stdev)
        self.set_median(median)

