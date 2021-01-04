#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 3 13:34:30 2020

Takes user inputs to determine tail angles of galaxy images based on supplied RA and Dec coordinates.

Returns 3 lists: jellyfish_classification (int), tail_confidence (int), and tail_angle (Float).

Use: run draw_tails_decals_RGB.py (ensure the file is specified in the code)

Requires two input columns of RA and Dec coordinates in decimal form. Must be the same length.
The images are taken from the legacy survey image viewer based on these. If the images cannot be sourced,
then check the internet connection or the Legacy survey server. Legacy survey will show a blank image if 
the image is outside of the legacy survey footprint. This image should be skipped when prompted

The first step will ask users to confirm the image, and alter the field of view, to best see the image.
This sources an image each time, so takes the longest time.

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

author: Jake Crossett
"""

# Required libraries for the function
import math
import numpy as np
from matplotlib import pyplot as plt
import io
import requests
from PIL import Image


# Only needed for the CSV example. 
# Can use other forms of input data if needed. I will always use pandas though
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord


#### Function start ####
def drawtail_decals_RGB(RA_col,Dec_col):
    
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
                    xpoint = (points[1,0] - points[0,0]) # * np.cos(Dec_col[row] * math.pi/180) # To scale RA away from the equator. 
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
##################################################################

'''
Everything below is an example use of the code. The above function can be used in a script like this, 
copy-pasted as a function into another code, or loaded in as a module to import later. 
Use x,y,z = drawtail_decals_RGB(RA,Dec) as the command to run it. 
'''

# Load in example table using pandas
# Can use other means (loadtxt, genfromtxt etc etc) which might be faster
# example_table = pd.read_csv('Coma_JF_not_Roberts.csv')
example_table = pd.read_csv('Tuts_JF_high_BCG.csv')


######## This is an example use of the code ##########
# Run the function and output to variables
jf_flag_val,tail_confid,tail_ang_val = drawtail_decals_RGB(example_table.RA,example_table.Dec) 
######################################################


# Append the columns to the table and mark with my name in case of multiple classifiers
# This step can probably be combined with the function, but I'm making it 2 steps
# Also note that the JC suffx is if people were to concatenate tables, so change this to your own initals
# ... Unless you have initials JC, in which case, JC2, maybe?
example_table['JF_flag_JC'] = jf_flag_val
example_table['tail_confidence_JC'] = tail_confid
example_table['tail_angle_JC'] = tail_ang_val


######## Save file #########
# The variable will be stored in session, but your hard work won't remain if 
# you don't write the file. To write them out to file, I save the table as a csv
#
# example_table.to_csv('example_table_JF_tails.csv',index=False)
############################


# More example plotting stuff. You really don't have to use this if you don't want to
# If one knows a BCG/central position, you can calculate the angular offset from the BCG

# Convert table coordinates into sky coordinates in astropy
Coord_sky = SkyCoord(example_table.RA*u.deg, example_table.Dec*u.deg, frame='icrs')

# If all galaxies are in a single cluster then input the centre position of the cluster
# Mark in a BCG/central position
# BCG_RA =  194.953054 # X-ray centre position of Coma
# BCG_Dec = 27.980694
# BCG_sky = SkyCoord(BCG_RA*u.deg, BCG_Dec*u.deg, frame='icrs') 

# If you wanted to have separate BCG coordinates that are linked with the galaxy coordinates 
# (need to be included as columns in the example table)
BCG_sky = SkyCoord(example_table.BCGRA*u.deg, example_table.BCGDec*u.deg, frame='icrs')


BCG_angle_sky = [] # Create the list to append to the base table later

# Calculate the angle between the Galaxy and the central point. It uses a loop, which I could
# probably improve on, but that is left as an exercise for the reader

for i in range(len(example_table)):
    # Find the spherical offset between the BCG and 
    dra, ddec = BCG_sky.spherical_offsets_to(Coord_sky[i]) 
    
    # If the galaxy is the BCG, with a very small difference, then assume it's zero
    # In these cases, the tail angle = tail offset. BCGs shouldn't have tails though.
    if abs(dra[i].value) < 1e-8 and abs(ddec[i].value) < 1e-8:
        BCG_angle_sky.append(0.0)
    else:
        # Use the atan2 function to calculate the angle based on a y and x coordinate.
        # Also need to convert to degrees, and round it.
        # Make the ra a negative to match the cartesian way the angles are measured (left to right)
        BCG_angle_sky.append(round(180 * math.atan2(ddec[i].value,-(dra[i].value))/math.pi,0))
        ## IF you wanted to have separate BCG coordinates that are linked with the galaxy coordinates
        # BCG_angle_sky.append(round(180 * math.atan2(ddec.value,-(dra.value))/math.pi,0))

example_table['BCG_angle_sky'] = BCG_angle_sky

# Calculate the difference between the JF tail angle, and the BCG angle
# This should give the tail offset. Two angles are calculated, one which 
# a tail pointing to the BCG is 180, and another where pointing to the BCG is 0.
# These are explained below

tail_offset = [] # Create the list to append to the base table later

for i in range(len(example_table)):
    # Only select where a galaxy is a JF and we are confident about a tail
    if example_table.tail_confidence_JC[i] > 0 and example_table.JF_flag_JC[i] == 1:
        
        # Check if the BCG sky angle is zero - these are BCGs and the tail offset is likely meaningless
        if example_table.BCG_angle_sky[i] == 0:
            tail_angle_diff = math.nan # BCGs will have NaN for the tail offsets
            
        else:
            # When the galaxy isn't a BCG thencalculate the difference between tail_angle and BCG_angle
            # Use the absolute value as we don't care about +/-
            tail_angle_diff = abs(example_table.tail_angle_JC[i] - example_table.BCG_angle_sky[i])
        
            # If angles are bigger than 180 degrees then take the remainder of the circle (to keep within 180)
            if tail_angle_diff > 180:
                tail_angle_diff = abs(360 - tail_angle_diff)
            
        # Append the BCG tail offset 
        tail_offset.append(tail_angle_diff)
        
    # If the galaxy isn't a jellyfish galaxy, or the tail can't be found, assign zero offset
    else:
        tail_offset.append(0)

# Make the tail offset. The angle is the angular deviation from the BCG galaxy vector (i.e. a tail pointing to a BCG is 180)
example_table['tail_offset_deviation_JC'] = tail_offset
# If you want the tail angle as an angle away from the BCG (i.e. a tail pointing to the BCG is zero degrees)
# Note, this means that all the non-Jellyfish tail measurements will be set to 180 degrees.
# Do not include them in any results! This should be fine if you select tail_confidence > 0
example_table['tail_offset_BCG_JC'] = 180 - example_table.tail_offset_deviation_JC

# Select only the galaxies with confident tails
example_tails = example_table[(example_table.tail_confidence_JC > 0)]

# Plot the figure
plt.figure() 
plt.hist(example_tails.tail_offset_BCG_JC,bins=6,range=[0,180],edgecolor='k') 
plt.xlim(0,180) 
plt.xticks([0,30,60,90,120,150,180]) 
plt.xlabel('Tail offset (degrees)') 
plt.ylabel('counts') 
plt.tight_layout() 
# Save it if you want
# plt.savefig('Example_JF_tail_offset_nonRoberts.eps') 
plt.show()       


