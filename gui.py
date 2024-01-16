# https://medium.com/@fareedkhandev/modern-gui-using-tkinter-12da0b983e22
# Modified by Mark Scheble for Yosemite Area Imager

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

import tkinter.messagebox
import customtkinter
from post_processing import *
from IDS_Peak_Image_Acq import *
from datetime import datetime

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Default Variables
WELLS = 5               # Number of Wells to Image
IMAGEPERIOD = 30        # Image Period
IMAGEACQUISITIONS = 20  # Number of Acquisitions
EXPOSURE_TIME = 763.108 # Exposure Time
ANALOG_GAIN = 5.0       # Analog Gain

# Camera Values
MIN_GAIN = 1
MAX_GAIN = 9.5
MIN_EXPOSURE = 0
MAX_EXPOSURE = 763.108

# Version
VERSION = "1.0.0"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # variables
        self.__number_of_wells = WELLS
        self.__image_period = IMAGEPERIOD
        self.__image_acquisitions = IMAGEACQUISITIONS
        self.__wells_toggle = False
        self.__period_toggle = False
        self.__image_acq_toggle = False

        # configure window
        self.title("yosemite_area_imager.py - v" + VERSION)
        self.geometry(f"{1100}x{400}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Yosemite - Area Imager", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # create appearance label on lower left
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # create scaling label on lower left
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # set scaling to 100%
        self.scaling_optionemenu.set("100%")

        # create exit button on lower right
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.quit, text="Exit")
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=400)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(10, 0), sticky="nsew")
        self.tabview.add("Image Settings")
        self.tabview.add("Number of Wells")  
        self.tabview.tab("Image Settings").grid_columnconfigure(0, weight=1) # configure grid of individual tabs
        self.tabview.tab("Number of Wells").grid_columnconfigure(0, weight=1)

        self.optionmenu_1 = customtkinter.CTkComboBox(self.tabview.tab("Number of Wells"),
                                                    values=["1", "5", "20"])
        self.optionmenu_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.optionmenu_1.set(str(WELLS))

        self.string_input_button1 = customtkinter.CTkButton(self.tabview.tab("Number of Wells"), text="Open Well Number Dialog",
                                                           command=self.open_well_numbers_dialog_event)
        self.string_input_button1.grid(row=2, column=0, padx=20, pady=(10, 10))

        self.optionmenu_2 = customtkinter.CTkComboBox(self.tabview.tab("Image Settings"),
                                                    values=["1","5", "15", "30", "60", "90", "120", "300"])
        self.optionmenu_2.grid(row=1, column=1, padx=20, pady=(10, 10))
        self.string_input_button2 = customtkinter.CTkButton(self.tabview.tab("Image Settings"), text="Open Image Period Dialog",
                                                           command=self.open_camera_period_dialog_event)
        self.string_input_button2.grid(row=1, column=0, padx=(0,28), pady=(10, 10))
        self.optionmenu_2.set("Period (sec)")

        self.optionmenu_3 = customtkinter.CTkComboBox(self.tabview.tab("Image Settings"),
                                                    values=["1", "3", "5", "10", "15", "20", "25", "30", "40", "60"])
        self.optionmenu_3.grid(row=2, column=1, padx=20, pady=(10, 10))

        self.optionmenu_3.set("# of Acquisitions")
        self.string_input_button3 = customtkinter.CTkButton(self.tabview.tab("Image Settings"), text="Open Image Acquistions Dialog",
                                                           command=self.open_camera_acqs_dialog_event)
        self.string_input_button3.grid(row=2, column=0, padx=20, pady=(10, 10))

        # Set slider between max values and min values of analog gain
        self.slider_1 = customtkinter.CTkSlider(self.tabview.tab("Image Settings"), width = 150, from_= MIN_GAIN, to = MAX_GAIN, number_of_steps=2*(MAX_GAIN - MIN_GAIN), command=self.sliding_gain)
        self.slider_1.grid(row=3, column=1, padx=(20, 20), pady=(20, 10), sticky="ew")
        self.slider_1.set(ANALOG_GAIN)

        # label analog gain slider
        self.gain_text = customtkinter.CTkLabel(self.tabview.tab("Image Settings"), text = "Gain:", font= ("Helvetica", 18))
        self.gain_text.grid(row=3, column=0, padx=(0, 130), pady=(20, 10), sticky="ew")
        self.gain_label = customtkinter.CTkLabel(self.tabview.tab("Image Settings"), text = str(ANALOG_GAIN) + " ADU", font= ("Helvetica", 18))
        self.gain_label.grid(row=3, column=0, padx=(150, 10), pady=(20, 10), sticky="ew")

        # set exposure label and entry
        self.exposure_text = customtkinter.CTkLabel(self.tabview.tab("Image Settings"), text = "Exposure:", font= ("Helvetica", 18))
        self.exposure_text.grid(row=4, column=0, padx=(0, 95), pady=(10, 10), sticky="ew")
        self.exposure_label = customtkinter.CTkLabel(self.tabview.tab("Image Settings"), text = str(EXPOSURE_TIME) + " ms", font= ("Helvetica", 18))
        self.exposure_label.grid(row=4, column=0, padx=(130, 10), pady=(10, 10), sticky="ew")
        self.entry = customtkinter.CTkEntry(self.tabview.tab("Image Settings"), placeholder_text="max: " + str(EXPOSURE_TIME))
        self.entry.grid(row=4, column=1, padx=(25, 20), pady=(20, 20), sticky="nsew")

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(6, weight=1)
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1.set(0)
        self.seg_button_1 = customtkinter.CTkButton(master=self.slider_progressbar_frame, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.start_imaging, text="Start Imaging")
        self.seg_button_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")


        # create checkbox and switch frame
        self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        self.checkbox_slider_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, text="Post-Process")
        self.checkbox_1.select()
        self.checkbox_1.grid(row=1, column=0, pady=(20,0), padx=20, sticky="nsew")

        self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, text="Log Data")
        self.checkbox_2.select()
        self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="nsew")

        
    # get value for exposure time
    def get_exposure(self, value):
        try:
            value = float(value)
            value = round(value, 3)
            if value < MIN_EXPOSURE or value > MAX_EXPOSURE:
                print("Invalid Exposure Time\n")
                print(f"Default value used: {EXPOSURE_TIME} ms\n")
                value = EXPOSURE_TIME
        except:
            print("Could not get exposure time value\n")
            print(f"Default value used: {EXPOSURE_TIME} ms\n")
            value = EXPOSURE_TIME
        self.exposure_label.configure(text = str(value) + " ms")
        return value

    # sliding value for gain
    def sliding_gain(self, _):
        gain = round(self.slider_1.get(), 1) # round to one decimal
        self.gain_label.configure(text = str(gain) + " ADU")
 
        
    # dialog function for Period (Seconds)
    def open_camera_period_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Image Period (seconds)")
        try:
            self.__image_period = int(dialog.get_input())
            self.__period_toggle = True
            print("Image Period Dialog:", self.__image_period)
        except:
            self.__image_period = IMAGEPERIOD
            self.__period_toggle = False

    # dialog function for Image Acquisitions
    def open_camera_acqs_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Image Acquisitions")
        try:
            self.__image_acquisitions = int(dialog.get_input())
            self.__image_acq_toggle = True
            print("Image Acq Dialog:", self.__image_acquisitions)
        except:
            self.__image_acquisitions = IMAGEACQUISITIONS
            self.__image_acq_toggle = False

    # dialog function for well numbers
    def open_well_numbers_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Number of Wells")
        try:
            self.__number_of_wells = int(dialog.get_input())
            self.__wells_toggle = True
            print("Number of Wells:", self.__number_of_wells)
        except:
            self.__number_of_wells = WELLS
            self.__wells_toggle = False

    # function for change appearance of gui
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # function for changing scaling of gui
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # start imaging function
    def start_imaging(self):
        # grab what current configuration (Wells, Period, Image Acq) currently is unless the open dialog has been set
        if not self.__wells_toggle:
            number_of_wells = int(self.optionmenu_1.get())
        else:
            number_of_wells = self.__number_of_wells
            self.__wells_toggle = False
        if not self.__period_toggle:
            try:
                image_period = int(self.optionmenu_2.get())
            except:
                print("No Image Period Value\n")
                print(f"Setting to default: {IMAGEPERIOD} sec\n")
                image_period = IMAGEPERIOD
        else:
            image_period = self.__image_period
            self.__period_toggle = False
        if not self.__image_acq_toggle:
            try:
                image_acquisitions = int(self.optionmenu_3.get())
            except:
                print("No Image Acquisitions Value\n")
                print(f"Setting to default: {IMAGEACQUISITIONS}\n")
                image_acquisitions = IMAGEACQUISITIONS
        else:
            image_acquisitions = self.__image_acquisitions
            self.__image_acq_toggle = False

        # poll the toggle buttons
        post_processing_toggle = int(self.checkbox_1.get())
        logging_toggle = int(self.checkbox_2.get())

        # poll the gain and exposure
        gain = round(self.slider_1.get(), 1)
        exposure = self.get_exposure(self.entry.get()) * 1000 # convert to us

        print(f"Logging: {bool(logging_toggle)} | Post-Processing: {bool(post_processing_toggle)} | Number of Wells: {number_of_wells} | Imaging Acquisitions: {image_acquisitions} | Imaging Period: {image_period} sec | Gain: {gain} ADU | Exposure {exposure} us")
        
        # timestamp of acquisition
        ts = datetime.now().strftime('./Yosemite_Area_Imager/%Y_%m_%d_%H-%M-%S/')

        # call image acquisition function
        self.progressbar_1.set(0)
        self.progressbar_1.start()
        self.progressbar_1.update_idletasks()
        image_arr = image_acquisition(period=image_period, image_acquisitions=image_acquisitions, directory = ts + "Original_Images/", progressbar = self.progressbar_1, gain = gain, exposure_time=exposure)
        self.progressbar_1.stop()

        # check that post processing has been toggled. If so, call post-processing function
        if post_processing_toggle:
            post_processing(image_array=image_arr, wells=number_of_wells, logging = logging_toggle, directory = ts)

            # Uncomment to test on already taken image
            # post_processing_test(logging_toggle)
        
        # check that logging has been toggled and that post-processing has also been toggled
        if logging_toggle and not post_processing_toggle:
            print("Post Processing Toggle must be checked to log")



if __name__ == "__main__":
    app = App()
    app.mainloop()