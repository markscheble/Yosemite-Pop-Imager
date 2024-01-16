**Post-Processing**

**well.py**

The Well_Mask class is the basic object that the pop software is built
on. The object class is constructed with the condition that each
Well_Mask object will be initialized with a well number, the contours of
that well defined, the area of the contour, and the mask image for that
well.

Well Mask has the following parameters:

-   self.\_\_well_num

-   self.\_\_contours

-   self.\_\_area

-   self.\_\_mask

and functions to get/set those parameters:

-   \_\_init\_\_(self, well, contours=None, area=None, mask=None)

-   set_contours(self, contours) \# sets contours

-   set_area(self, area) \# sets area

-   set_mask(self, mask) \# sets mask

-   get_contours(self) \# gets contours

-   get_well_num(self) \# gets well number

-   get_area(self) \# gets area

-   get_mask(self) \# gets mask

-   print_all(self) \# prints all parameters

The well mask class builds into a larger mask class which will be
described with Image.py. Well_Mask objects are built for any given mask
and **the number of well masks equals the number of wells that the mask
needs to extract from any image**.

In Well.py, the Well class inherits from Well_Mask and has the addition
of the following parameters that describe the well intensity extracted
from an image:

-   super().\_\_init\_\_(well=well, contours=contours, area=area,
    mask=mask)

-   self.\_\_img

-   self.\_\_mean

-   self.\_\_median

-   self.\_\_stdev

-   self.\_\_mode

-   self.\_\_minimum

-   self.\_\_maximum

-   self.\_\_pixel_int_array

and functions to get/set those parameters:

-   set_pixel_int_array(self, arr) \# extracted pixel array for the well
    mask

-   set_img(self, img) \# sets image to extract pixel array

-   set_mean(self, avg) \# sets mean

-   set_median(self, median) \# sets median

-   set_stdev(self, std) \# sets stdev

-   set_mode(self, mode) \# sets mode

-   set_min(self, minimum) \# sets min

-   set_max(self, maximum) \# sets minimum

-   get_img(self) \# gets img

-   get_pixel_int_array(self) \# gets pixel int array

-   get_mean(self) \# gets mean

-   get_median(self) \# gets median

-   get_stdev(self) \# gets stdev

-   get_mode(self) \# gets mode

-   get_min(self) \# gets min

-   get_max(self) \# gets max

-   print_all(self) \# prints all parameters

-   get_pixels_from_mask(self, img) \# uses the well mask to extract
    that well from the image and sets the pixel int array

-   get_well_statistics(self) \# gets the well statistics for that well
    and sets the statistics parameters: ie. Mean, median, mode, minimum,
    maximum

**image.py**

The Mask Class inherits the Well Mask Class from Well.py with the
addition of the following parameters:

-   self.\_\_file_path

-   self.\_\_original_mask_img

-   self.\_\_number_of_wells

-   self.\_\_mask_blurred

-   self.\_\_wells = \[Well_Mask(w) for w in range(num_wells)\]

-   self.\_\_mask_ostu_thresh

-   self.\_\_combined_mask

-   self.\_\_time

-   self.\_\_min_well_size

-   self.\_\_max_well_size

and the following functions to get/set the parameters:

-   \_\_init\_\_(self, img, num_wells): \# initializes the Class with an
    image to build mask off of and the number of wells to extract

-   set_mask_blurred(self, img): \# sets the gaussian blurred image from
    the original image

-   set_mask_thresh_img(self, img): \# sets the otsu threshold image
    extracted from original image

-   set_combined_mask(self, img): \# sets the combined mask from all
    extracted mask wells

-   get_file_path(self): \# gets the img file path

-   get_time(self): \# gets the time of the creation of the image used
    for mask

-   get_num_wells(self): \# gets the number of wells

-   get_original_mask_img(self): \# gets the original image

-   get_mask_thresh_img(self): \# gets the otsu thresholded image

-   get_mask_blurred(self): \# gets the gaussian blurred image

-   get_well(self, well_num): \# gets the well with well_num n

-   get_combined_mask(self): \# gets the combined mask for all wells

-   get_min_well_size(self): \# returns thresholded min well size

-   get_max_well_size(self): \# returns thresholded max well size

-   print_all(self): \# prints all parameters

-   getMasks(self):

> """This function takes in an image and sets the masks of each well for
> that image. First it uses a gaussian blur and otsu threshold as a
> first pass to isolate the wells. Next, the algo uses **openCVs find
> contours** function to isolate the wells in the image from the otsu
> mask and eliminate contours that are too small/too large to be wells
> based on min_well_size and max_well size. This threshold for too small
> and too large of wells is something that will have to fine tuned with
> more data. Finally, the function returns the masks of the wells. Each
> of the well mask classes will be set with a mask for that well as well
> as the blurred, thresholded parameters. \"\"\"

-   combineMasks(self, show):

> \"\"\" This function combines all of the well masks in the Mask class
> and sets the combined mask. \"\"\"

-   saveImages(self, directory): \# saves all the images and well masks
    in directory

The Image Class inherits the Well Class from Well.py with the addition
of the following parameters:

-   self.\_\_file_path = img

-   self.\_\_image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)

-   self.\_\_number_of_wells = num_wells

-   self.\_\_wells = None

-   self.\_\_time = time.ctime(os.path.getmtime(img))

and the following functions to get/set the parameters:

-   \_\_init\_\_(self, img, num_wells): \# initializes the image with
    img and number of wells

-   get_file_path(self): \# gets the file path initialized on creation

-   get_time(self): \# gets the time of creation for img

-   get_image(self): \# gets the original image

-   get_num_wells(self): \# gets the number of wells in image

-   get_well(self, well_num): \# gets the well with well number (Well
    class described above)

-   initialize_wells_from_mask(self, mask): \# initializes the wells
    parameter with Well Objects for number of wells.

-   analyze_img(self): \# uses the masks of each individual well to
    extract those intensities and set the well statistics

-   print_all(self): \# prints all Well parameters

-   saveImages(self, directory = \"./Images/\"): \# saves well images in
    directory

**To use Well.py and Image.py:**

1.  **Create a mask img with the following command:**

-   mask_img = "Mask(\"Mask Image\", num_wells=wells)

2.  **Call the Mask class function getMasks()**

    -   mask_img.getMasks()

3.  **Call print_all(), combineMasks(), and saveImages(), to print
    statistics about the Mask Wells, combine Masks and save all
    images.**

    -   mask_img.print_all()

    -   mask_img.combineMasks(show=False)

    -   mask_img.saveImages()

4.  **Create Image Objects for each image you wish to analyze.**

    -   analysis_img = Image("Analysis_Image\", num_wells=wells)

5.  **Initialize the Wells from the Mask and analyze the image.**

    -   analysis_img.initialize_wells_from_mask(mask_img)

    -   analysis_img.analyze_img()

6.  **Print statistics about the image and save all Images.**

    -   analysis_img.print_all()

    -   analysis_img.saveImages()

**post_processing.py**

The post_processing.py imports the Mask and Image classes from image.py
and puts everything together for post processing.

The python file contains the following functions:

-   write_data(imgs, analysis_filename, numberofwells): \# writes the
    img data to csv

-   post_processing_test(logging = True, wells = 1, directory =
    \"./Images/\"):

""" post processing test function, will be deleted"""

-   post_processing(image_array, wells, logging, directory =
    \"./Images/\"): """post processing function that is called from gui
    image acquisition """

-   post_processing_user (wells, logging, image_dir, directory): """
    user post processing function """

The main function of this file that is called from the gui is
post-processing -- third function above. This function creates a Mask
object from the last image acquired from image acquisition. This is when
all wells are fluorescing, so it is the optimal image to produce masks
from. After creating the mask and printing the mask data to console,
Image objects are created for all images acquired. The images are
analyzed using the binary mask created and isolates each well in the
image. The data is then written to a csv if the log toggle is set to
True.

**Image Acquisition**

**IDS_Peak_Image_Acq.py**

The IDS_Peak_Image_Acq.py is the image capture portion of the pop
software.

The python file contains the following functions:

-   set_roi(nodemap_remote_device): \# sets the region of interest for
    the image pixel size, currently set to max

-   initialize_directory(directory): \# initializes the file structure
    to save images acquired

-   image_acquisition(period, image_acquisitions): \# takes n
    image_acquisitions at x period. Saves the images to the initialized
    directory

The image acquisition function starts by initializing the ids_peak
library and finding the ids camera device. The function then proceeds to
set the region of interest to the maximum pixel size and allocate
buffers for the number of images in image acquisitions. Each buffer is
used to store a set image until it is saved. The exposure time and gain
are then set. (Still needs to be characterized and will vary pending on
the imaging hardware setup. Images are acquired at a period set by the
function parameters. Images are acquired at a period set by function
parameters and saved in the directory set by function parameters.
Finally, the ids_peak library is closed, and imaging is complete.

**Wrapper**

**gui.py**

The gui.py is the gui wrapper for the above files. It is a modified
version of the open-source repo from
<https://medium.com/@fareedkhandev/modern-gui-using-tkinter-12da0b983e22>.

![A screenshot of a computer Description automatically
generated](./images/media/image1.png){width="6.5in"
height="2.522222222222222in"}

As of 01/16/2024, this is the appearance of the gui. The gui has the
following capabilities:

-   Ability to change appearance of the gui, ![A screenshot of a
    computer Description automatically
    generated](./images/media/image2.png){width="1.906515748031496in"
    height="1.7085717410323709in"}

-   Ability to scale the UI, ![A screenshot of a computer Description
    automatically
    generated](./images/media/image3.png){width="2.0940419947506563in"
    height="2.000278871391076in"}

-   Set the number of wells for post-processing detection: ![A
    screenshot of a computer Description automatically
    generated](./images/media/image4.png){width="4.13545384951881in"
    height="2.8642136920384953in"}

-   Set the Image Period (Seconds), time between images

-   Set the number of images to acquire

-   Set the gain (ADU) for image acquisition

-   Set the exposure time (ms) for image acquisition

> ![A screenshot of a computer Description automatically
> generated](./images/media/image5.png){width="4.445845363079615in"
> height="2.9122615923009625in"}

\*Note: the Number of Wells, Image Period (Seconds), Image Acquisitions
functions has open dialogs which allow the user to input any valid
number of it is not listed in the dropdown![A screenshot of a computer
Description automatically
generated](./images/media/image6.png){width="3.510906605424322in"
height="1.6877351268591425in"}

Valid Numbers:

Number of Wells \> 0

Image Period (Seconds) \>= 0

Image Acquisitions \> 0

-   Toggle Post-Processing of Images acquired ![A black and white text
    Description automatically
    generated](./images/media/image7.png){width="1.3439370078740158in"
    height="0.5729965004374453in"}

-   Toggle Log Data to excel sheet (post-process box must be toggled)
    ![A black text on a white background Description automatically
    generated](./images/media/image8.png){width="1.4272823709536309in"
    height="0.6042508748906387in"}

-   Start Imaging with the set parameters (Number of Wells, Image Period
    (Seconds), Image Acquisitions). Will set default values if user does
    not set. ![](./images/media/image9.png){width="2.281568241469816in"
    height="0.5104877515310586in"}

-   Exit the gui

![A black and white text Description automatically generated with medium
confidence](./images/media/image10.png){width="1.8440069991251093in"
height="0.5625787401574803in"}

A requirements.txt file has been included in the directory for all
relevant packages and libraries.
