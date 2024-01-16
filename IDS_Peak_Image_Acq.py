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

from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
import numpy as np
import cv2
import os
from datetime import datetime
import time
import sys

VERSION = "1.0.0"
MODEL = "U3-356xXLE-M"

def set_roi(nodemap_remote_device):
    """This function changes the roi for the image pixel size. It is currently set to the max pixel size."""
    try:
        # Set ROI to max that our nodemap can be
        x_min = nodemap_remote_device.FindNode("OffsetX").Minimum()
        y_min = nodemap_remote_device.FindNode("OffsetY").Minimum()
        
        w_max = nodemap_remote_device.FindNode("Width").Maximum()
        h_max = nodemap_remote_device.FindNode("Height").Maximum()
      
        nodemap_remote_device.FindNode("OffsetX").SetValue(x_min)
        nodemap_remote_device.FindNode("OffsetY").SetValue(y_min)
        nodemap_remote_device.FindNode("Width").SetValue(w_max)
        nodemap_remote_device.FindNode("Height").SetValue(h_max)
 
        print("Roi Set")
        # Get the current ROI
        x = nodemap_remote_device.FindNode("OffsetX").Value()
        y = nodemap_remote_device.FindNode("OffsetY").Value()
        w = nodemap_remote_device.FindNode("Width").Value()
        h = nodemap_remote_device.FindNode("Height").Value()

        print(f"Offset X: {x} | Offset Y: {y} | Width: {w} | Height: {h}")
        
    except Exception as e:
        print(e)

def initialize_directory(directory = "./Images/"):
    """This function checks to make sure there is an existing directory. 
    If not, it will create one to store the images."""
    #check if directory path exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory

def image_acquisition(period = 5, image_acquisitions = 5, directory = "./Images/", progressbar = None, gain = 5, exposure_time = 763108.0):
    """This is the main image acquistion function. The function initializes the ids_peak libray and finds the camera device. 
    It sets the exposure, resolution, and analog_gain. For image acquisition, it images for n number of image acquistions at a period of n period."""
    
    # Make sure period and image acquisition parameters are valid
    assert (period >= 1), "Period parameter invalid, must be >= 1 second"
    assert (image_acquisitions > 0), "Image acquisitions parameter invalid"

    print("Ids_Peak_Image_Acq-Python_" + VERSION)

    # initialize library
    ids_peak.Library.Initialize()

    # create a device manager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # update the device manager
        device_manager.Update()

        # exit program if no device was found
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return

        # list all available devices
        selected_device = None
        for i, device in enumerate(device_manager.Devices()):
            print(str(i) + ": " + device.ModelName() + " ("
                  + device.ParentInterface().DisplayName() + "; "
                  + device.ParentInterface().ParentSystem().DisplayName() + "v."
                  + device.ParentInterface().ParentSystem().Version() + ")")
            if device.ModelName() == MODEL:
                selected_device = int(i)

        # open selected device
        device = device_manager.Devices()[selected_device].OpenDevice(ids_peak.DeviceAccessType_Control)

        # get the remote device node map
        nodemap_remote_device = device.RemoteDevice().NodeMaps()[0]

        # print model name and user ID
        print("Model Name: " + nodemap_remote_device.FindNode("DeviceModelName").Value())
        print("User ID: " + nodemap_remote_device.FindNode("DeviceUserID").Value())

        # print sensor information, not knowing if device has the node "SensorName"
        try:
            print("Sensor Name: " + nodemap_remote_device.FindNode("SensorName").Value())
        except ids_peak.Exception:
            print("Sensor Name: " + "(unknown)")

        # print resolution
        print("Max. resolution (w x h): "
              + str(nodemap_remote_device.FindNode("WidthMax").Value()) + " x "
              + str(nodemap_remote_device.FindNode("HeightMax").Value()))

        # Set roi to max pixel sensor size
        set_roi(nodemap_remote_device)

        # open the data stream
        dataStream = device.DataStreams()[0].OpenDataStream()

        #allocate and announce image buffers
        payloadSize = nodemap_remote_device.FindNode("PayloadSize").Value()
        bufferCountMin = dataStream.NumBuffersAnnouncedMinRequired()
        
        for _ in range(max(bufferCountMin, image_acquisitions)):
            buffer = dataStream.AllocAndAnnounceBuffer(payloadSize)
            dataStream.QueueBuffer(buffer)

        # Get image information for opencv image format
        height = nodemap_remote_device.FindNode("Height").Value()
        width = nodemap_remote_device.FindNode("Width").Value()
        print("Resolution (w x h): " + str(width) + " x "+ str(height))
        
        # prepare for untriggered continuous image acquisition
        nodemap_remote_device.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        nodemap_remote_device.FindNode("TriggerMode").SetCurrentEntry("On")
        nodemap_remote_device.FindNode("TriggerSource").SetCurrentEntry("Software")


        # set gain 
        nodemap_remote_device.FindNode("Gain").SetValue(gain)
        gain = nodemap_remote_device.FindNode("Gain").Value()
        print(f"Gain: {gain}")

        # check min/max gain
        # maxgain = nodemap_remote_device.FindNode("Gain").Maximum()
        # mingain = nodemap_remote_device.FindNode("Gain").Minimum()
        # print(f"MaxGain: {maxgain}")
        # print(f"Mingain: {mingain}")

        # set frame rate
        # min_frame_rate = nodemap_remote_device.FindNode("AcquisitionFrameRate").Minimum()
        # nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(min_frame_rate)
        frame_rate = nodemap_remote_device.FindNode("AcquisitionFrameRate").Value()
        print(f"Frame Rate: {frame_rate} fps")

        # modify exposure time
        # maxExp = nodemap_remote_device.FindNode("ExposureTime").Maximum()
        # minExp = nodemap_remote_device.FindNode("ExposureTime").Minimum()

        # set exposure time
        nodemap_remote_device.FindNode("ExposureTime").SetValue(exposure_time) # us
        exposure = nodemap_remote_device.FindNode("ExposureTime").Value()
        print(f"Exposure Time: {exposure} us")

        #initialize image directory
        directory = initialize_directory(directory = directory)
        image_arr = []
        try:
            # process the acquired images
            image_count = 1

            # start acquisition
            print("Image acquistion starting...")

            dataStream.StartAcquisition()
            nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            
            # update gui progress bar
            if progressbar:
                progress = 1/image_acquisitions
                progressbar.set(progress)
                progressbar.update_idletasks()

            while image_count <= image_acquisitions:

                ti0 = time.time()
                nodemap_remote_device.FindNode("TriggerSoftware").Execute()

                # get buffer from datastream 
                buffer = dataStream.WaitForFinishedBuffer(5000)
                raw_image = ids_peak_ipl.Image.CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(), buffer.Size(), buffer.Width(), buffer.Height())

                print(f"Image Acquired: {image_count}")

                # get the time acquired
                time_acquired = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')

                # convert raw image to numpy 3D array
                np_image = raw_image.get_numpy_3D()

                # save image in directory
                destination = directory + time_acquired + f"_Acq_{image_count}.png"
                cv2.imwrite(destination, np_image)
                image_arr.append(destination)
                print(f"Image Saved: {image_count}")

                # uncomment to show images
                # cv2.imshow('image', np_image) 
                # cv2.waitKey(0)          
                
                # queue buffer  
                dataStream.QueueBuffer(buffer)

                # increase the image counter
                image_count += 1


                # Image Wait Time for Desired Period
                ti1 = time.time()
                try:
                    if (image_count <= image_acquisitions):
                        print(f"Image wait time: {period - (ti1-ti0)} seconds")
                        time.sleep(period - (ti1-ti0))
                except:
                    print("Image Acquisition Took Too Long")

                # update gui progress bar
                if progressbar:
                    progress += 1/image_acquisitions
                    progressbar.set(progress)
                    progressbar.update_idletasks()

        except Exception as e:
            print(e)
                        
            
    except Exception as e:
        print("Exception: " + str(e) + "")
        print("Stopping Imaging")

    finally:
        ids_peak.Library.Close()
        print("Image Acquisition Complete")
        return image_arr

# Unit test
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            period = float(sys.argv[1])
            image_acquisitions = int(sys.argv[2])
            print(f"Period: {period} | Image Acquisition: {image_acquisitions}")
            image_acquisition(period=period, image_acquisitions=image_acquisitions)
        except Exception as e:
            print(e)
    else: 
        try:
            period = 1
            image_acquisitions = 20
            print(f"Period: {period} | Image Acquisition: {image_acquisitions}")
            image_acquisition(period=period, image_acquisitions=image_acquisitions)
        except Exception as e:
            print(e)
