#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:34:30 2020

Main function list for drawing tails. Does not run on its own, but is called by other codes.

Takes user inputs to determine tail angles of galaxy images based on supplied RA and Dec coordinates.

Returns 3 lists: jellyfish_classification (int), tail_confidence (int), and tail_angle (Float).

#########
drawtail_decals_RGB:
Requires two input columns of RA and Dec coordinates in decimal form. Must be the same length.
The images are taken from the legacy survey image viewer based on these. If the images cannot be sourced,
then check the internet connection or the Legacy survey server. Legacy survey will show a blank image if 
the image is outside of the legacy survey footprint. This image should be skipped when prompted

The first step will ask users to confirm the image, and alter the field of view, to best see the image.
This sources an image each time, so takes the longest time.
#########

The user input is based on questions which all need to be answered. 
The user needs to confirm each galaxy before it will move on. Currently, the  entire input lists are looped over, 
so the user is advised to sit down, and get comfy if a large number of galaxies needs to be classified. 
Alternatively, break up the input files into separate chunks and run the function on each one.
A potential save progress feature may be added later (although that doesn't help you now does it).

Also, the use of interactive plot mode for marking the points (command ion), does not play well with some
IDEs and python GUI interfaces. There may be problems with programs like spyder and jupiter notebooks when using
this. This is likely due to settings these IDEs have settings which don't play nicely with interactive plotting.
If in doubt, just use a python/ipython terminal window, which seems to work fine.

Two suggestions to add to the start of the code to run in jupyter notebooks and/or spyder:
    
%matplotlib qt

and/or 

import matplotlib
matplotlib.use('TkAgg')

Try these at your own risk :)
    
    
Update 30/12/2020:
Included astropy sky coordinates to better calculate BCG offsets. This currently uses a single offset point, but
can be easily changed to a BCG_coord column if necessary.

Update 11/1/2021:
Fixed deltaRA and deltaDec to use astropy coordinates. This means the lines will not appear to match the 
final angles at high/low Declinations. The angles are converted based on the image having the declination dependance
on the field of view.

Update 26/2/2021:
This script is now contains the working functions for all the codes. It is a required module to download to use for any
different script. 
The function drawtail_decals_RGB is the main code for downloading Legacy Survey RGB images from the internet to classify them
(needs a connection to legacysurvey.org)


author: Jacob P. Crossett
"""

#### Function start ####
def drawtail_decals_RGB(RA_col,Dec_col):
    '''
    Plots images of galaxies based on Legacy Survey cutout images to classify potential jellyfish 
    features and tails. Will always attempt to acquire the image from Legacy Survey, but will show
    a blank image if the coordiinates are outside the Legacy Survey footprint. 

    Parameters
    ----------
    RA_col : float (RA decimal coordinates)
        Input RA coodinates to look up for legacy survey images. Must be in decimal RA format,
        and the same length as Dec_col
    Dec_col : float (RA decimal coordinates)
        Input Dec coodinates to look up for legacy survey images. Also used to determine the final 
        angle of the tail, to adjust the RA to account for the spherical RA-Dec system.
        Must be in decimal Dec format, and the same length as RA_col

    Returns
    -------
    jellyfish_flag_list (list - int)
        int describing if the galaxy is a jellyfish. Is 1 for a jellyfish, -1 for a merger
        and 0 if neither. If the image is broken/can't be classified it is -2
    tail_confidence (list - int)
        int describing the strength of a jellyfish tail. 0 is used if no tail can be seen,
        1 is for a potential/weak tail, and 2 for a prominent/obvious tail. If a galaxy 
        is classified as a merger/null/not-jellyifsh, this is set to 0.
    tail_angle_list (list - float)
        The angle of the tail, taken from a line pointing east/to the right hand side 
        (float between -179 and 180 degrees). Currently rounds this to 1 degree precision,
        but is ouptut as float to allow higher precision if needed. If a galaxy 
        is classified as a merger/null/not-jellyifsh, or no tail is seen, this is set to 0.
    '''

    # Required libraries
    import math
    import numpy as np
    from matplotlib import pyplot as plt

    import io
    import requests
    from PIL import Image
    
    # Check if the RA and Dec lists are the same size. End if they are not
    if len(RA_col) != len(Dec_col):
        raise Exception("RA and Dec columns are not the same length!")
        return None # Ending the function
    
    # Create lists for the output values
    jellyfish_flag_list = []
    tail_confidence = []
    tail_angle_list =[] 
    
    # Loop over all JFs in the table to get the image
    for row in range (len(RA_col)):
        
        # Need to confirm the galaxy has a good FOV. Calls a while loop to confirm the FOV
        FOVcheck = False
        Zoom=0.25
        while FOVcheck == False:
            # Pull the image from legacysurvey with the zoom specified - this is a slow step
            JF_decals_image = requests.get("http://legacysurvey.org/viewer/cutout.jpg?ra=%f&dec=%f&layer=dr8&pixscale=%f" % (RA_col[row], Dec_col[row],Zoom))
            image = Image.open(io.BytesIO(JF_decals_image.content))
            
            fig, ax = plt.subplots() # Plot the figure each time
            plt.imshow(image,extent=[-128,128,-128,128]) # Have the centre be labelled [0,0]
            plt.pause(0.1)
            #plt.show(block=False) #Broke on Yara's machine. Currently testing with pause instead
            
            #User inputs whether zoom in out out
            print('Is the galaxy a good size to classify?')
            print("If the image is broken, type 'continue', and flag the image in the next question")
            ZoomQ = input("Type 'i' to Zoom in, 'o' to Zoom out, or 'c' to classify: ").lower()
            
            if ZoomQ == 'in' or ZoomQ == 'i':
                Zoom = Zoom/2 # FOV smaller
                plt.close(fig=None) # Close figure to refresh
            
            # If needing a bigger field of view/zoom out
            elif ZoomQ == 'out' or ZoomQ == 'o':
                Zoom = Zoom*2 # FOV bigger
                plt.close(fig=None) # Close figure to refresh
            
            # If needing a smaller field of view/zoom in
            elif ZoomQ == 'continue' or ZoomQ == 'classify' or ZoomQ == 'c' or ZoomQ == 'cont':
                FOVcheck = True # Break loop when continue is called
            

        certain = False # Give users a chance to reset classifications
        while certain == False: # Long While loop. There's no break other than confirmation of the classification
            
            print("Does this galaxy have signs of ram pressure stripping, or tidal interactions?")  # User input if the galaxy is a JF
            JellyQ = input("Type 'j' for jellyfish, 'm' for merger/tidal, 'n' for nothing, and 'b' if blank/broken image: ").lower()
            
            # Only draw the tail if they answer yes. 
            # It's probably better to compare to a list of strings, but what are you, my teacher?
            if JellyQ == 'j' or JellyQ == 'jf' or JellyQ == 'jellyfish':
               
                # Ask whether the user is confident about the tail angle. Might need to be reworded
                Tail_conQ = int(input('Are you confident about the tail (0=no tail; 1=marginal, 2=clear tail): '))
                # Check that the user is following the rules
                if Tail_conQ > 2: # If above the max
                    tail_confid = 2
                elif Tail_conQ < 0: # If below the minimum
                    tail_confid = 0
                else:
                    tail_confid = Tail_conQ # put tail confidence into the variable from the question
                
                if Tail_conQ > 0: # Only ask to draw the tail if the tail can be seen
                    print("Draw the tail: Click the centre of the galaxy, and then away from the galaxy in the direction of the tail")
                    points = np.array(plt.ginput(2))  # User inputs 2 positions 
                    # Might be able to do a version with only 1 and a centre
        
                    # Create the line to visually confirm
                    xline = [points[0,0],points[1,0]]
                    yline = [points[0,1],points[1,1]]
                    plt.plot(xline,yline,'-',color='red',linewidth=2.5)
                    plt.pause(0.1) #Pause to highlight the line
                    
                    # Calculate the distance from the centre of the galaxy to the tail edge
                    # It comes from the centre click in case the galaxy isn't centred
                    # It should be able to work with either click being the centre, because lines do that 
                    ypoint = (points[1,1] - points[0,1]) 
                    xpoint = (points[1,0] - points[0,0]) * np.cos(Dec_col[row] * math.pi/180) # To scale RA away from the equator. 
                                                         # I don't think we need to do this here
                
                    theta = math.atan2(ypoint,xpoint)  # Calculate angle (theta) in radian. atan2 defines polar angle from right 
                    theta = round(180 * theta/math.pi,0) # Converting theta from radian to degree and round it. No one likes radians
                    
                    # Add in a line to show the zero point, and highlight the angle to help the user see what they've done
                    plt.plot([128,0],[0,0],'-',color='red',linewidth=2.5)
                    plt.pause(0.1) #Pause to see the result
                    
                    print('This is a Jellyfish with a tail at ', theta)  # Confirm the classification   

                    # Ask to finish the classification
                    FinishQ = input('Save and go next?: ' ).lower()
                    if FinishQ == 'yes' or FinishQ =='y'or FinishQ == 's' or FinishQ == 'si':
                        isjelly = 1  # Flag the galaxy as a JF
                        certain = True # To leave the while loop
               
                else: # If tail can't be seen
                    print("This is a Jellyfish, but we can't determine the tail angle")  # Confirm the classification   
                    # Ask to finish the classification
                    FinishQ = input('Save and go next?: ' ).lower()
                    if FinishQ == 'yes' or FinishQ =='y'or FinishQ == 's' or FinishQ == 'si':
                        isjelly = 1  # Flag the galaxy as a JF
                        theta = 0 # Angle set at 0
                        certain = True # To leave the while loop
            
            # If the galaxy is not a JF
            elif JellyQ == 'no' or JellyQ == 'n':
                
                print('This is not a Jellyfish') # Confirm the classification  
                
                # Ask to finish the classification
                FinishQ = input('Save and go next?: ' ).lower()
                if FinishQ == 'yes' or FinishQ =='y' or FinishQ == 's' or FinishQ == 'si':
                    # Ensure that all parameters are reset in case of multiple attempts
                    isjelly = 0 #0 for non-JF
                    theta = 0 # Angle set at 0
                    tail_confid = 0 # No tail
                    certain = True # To leave the while loop
            
            # Specific case if the galaxy is a merger/tidal
            elif JellyQ == 'merger' or JellyQ == 'merge' or JellyQ == 'm' or JellyQ == 'tidal' or JellyQ == 't':
                print('This is a tidal interaction or merger') # Confirm the classification
                
                # Ask to finish the classification
                FinishQ = input('Save and go next?: ' ).lower()
                if FinishQ == 'yes' or FinishQ =='y' or FinishQ == 's' or FinishQ == 'si':
                    # Ensure that all parameters are reset in case of multiple attempts
                    isjelly = -1 # -1 is for merger
                    theta = 0 # Angle set at 0
                    tail_confid = 0 # No tail
                    certain = True # To leave the while loop
            
            # If the image is broken or unable to be classified
            elif JellyQ == 'skip' or JellyQ == 'null' or JellyQ == 'broken' or JellyQ == 'b':
                print('This image cannot be displayed, or the galaxy cannot be classified') # Confirm the classification
                
                # Ask to finish the classification
                FinishQ = input('Save and go next?: ' ).lower()
                if FinishQ == 'yes' or FinishQ =='y' or FinishQ == 's' or FinishQ == 'si':
                    isjelly = -2 # -2 for null image
                    theta = 0 # Angle set at 0
                    tail_confid = 0 # No tail
                    certain = True # To leave the while loop
            
            plt.close(fig=None) # Close the figure to keep things clean
            if certain == False:        
                # Prompt that they are about to do another classifcation for the same galaxy 
                plt.close(fig=None) # Close the figure to keep things clean
                print('Restarting classification: Lets try again') 
                
                # Remake the figure. 
                # I think it's quicker to replot here instead of replotting at the start of the loop
                # This is because you would be plotting the figure twice initially with the Zoom counter
                fig, ax = plt.subplots()
                plt.imshow(image,extent=[-128,128,-128,128]) # Show image, origin should be in the centre
                plt.ion() # Ensure in interactive mode
                plt.pause(0.1) #Pause to see the result
        
        # Append the values into the lists        
        jellyfish_flag_list.append(isjelly) # Jellyfish flag. 1 if yes, 0 if no, -1 if merger, -2 if broken image/unclassified
        tail_confidence.append(tail_confid) # Jellyfish tail confidence flag. 1 if confident, 0 otherwise
        tail_angle_list.append(theta) # Jellyfish tail angle between [-180,180]. 
                                      # Given 0 not a Jellyfish, so need to check the JF flag if there's a tail at 0.0
        
    return(jellyfish_flag_list,tail_confidence,tail_angle_list) #Returns all values

def drawtail_decals_testmessage():
    # Testing feature to ensure only some functions are imported when using the example scripts.
    print("I hope you don't see this")







