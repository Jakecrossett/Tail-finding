#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 3 13:34:30 2020

This is an example use of the code draw_tails_decals.py. The imported function can be used in a script like this, 
Or copy-pasted as a function into another code.
Use x,y,z = drawtail_decals_RGB(RA,Dec) as the command to run it. 

Takes user inputs to determine tail angles of galaxy images based on supplied RA and Dec coordinates for multilpe clusters.

Returns 3 lists: jellyfish_classification (int), tail_confidence (int), and tail_angle (Float).

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
Import math
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
The function has been removed from the script. Instead, it calls the function  drawtail_decals_RGB 
from draw_tails_decals. You will need to download both this code as well as  draw_tails_func to use this script
This is done so that different versions are all kept together. Apologies if this ruins everything for you.

author: Jacob P. Crossett
"""

# Needed modules
import math # For the functions atan2, the value pi, and to format NaN values. 
from matplotlib import pyplot as plt # Make the plot
from astropy import units as u # Helps astropy.Skycoord work
from astropy.coordinates import SkyCoord # Get accurate BCG galaxy distances
import pandas as pd # Can use other forms of input data if needed. I will always use pandas though

from draw_tails_func import drawtail_decals_RGB # I mean, that's why you're here surely?

# Load in example table using pandas
# Can use other means (loadtxt, genfromtxt etc etc) which might be faster
example_table = pd.read_csv('Example_table_Poggianti16.csv')

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

#######################################
######## Important: Save file #########
#######################################
# The variable will be stored in session, but your hard work won't remain if 
# you don't write the file. To write them out to file, I save the table as a csv

# example_table.to_csv('example_table_JF_tails.csv',index=False)
#######################################
#######################################

# Convert table coordinates into sky coordinates in astropy
Coord_sky = SkyCoord(example_table.RA*u.deg, example_table.Dec*u.deg, frame='icrs')

# Convert BCG coordinates that are linked with the galaxy coordinates 
# (need to be included as columns in the input table)
# There exists a single cluster example version. Please use that if you have a single cluster
BCG_sky = SkyCoord(example_table.BCGRA*u.deg, example_table.BCGDec*u.deg, frame='icrs')


# Calculate the angle between the Galaxy and the central point. It uses a loop, which I could
# probably improve on, but that is left as an exercise for the reader
BCG_angle_sky = [] # Create the list to append to the base table later

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

example_table['BCG_angle_sky'] = BCG_angle_sky

# Calculate the difference between the JF tail angle, and the BCG angle
# This should give the tail offset. Two angles are calculated, one which 
# a tail pointing to the BCG is 180, and another where pointing to the BCG is 0.
# These are explained below. Please also check Angle_examples.pdf for a viusal example

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
#plt.savefig('Example_JF_tail_offset_JC.eps') 
plt.show()       


