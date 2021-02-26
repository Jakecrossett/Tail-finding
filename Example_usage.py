#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 14:12:10 2021

This is a basic example use of the functions prvided in  draw_tails_func  This probably isn't needed, 
but might help show how I use the functions.

Takes user inputs to determine tail angles of galaxy images based on supplied RA and Dec coordinates.

Returns 3 lists: jellyfish_classification (int), tail_confidence (int), and tail_angle (Float).

author: Jacob P. Crossett
"""

import pandas as pd # Can use other forms of input data if needed. I will always use pandas though
from draw_tails_func import drawtail_decals_RGB

# Load in example table using pandas
# Can use other means (loadtxt, genfromtxt etc etc) which might be faster
example_table = pd.read_csv('Example_table_Poggianti16.csv') # Load in table

# Run the function and output to variables
jf_flag_val,tail_confid,tail_ang_val = drawtail_decals_RGB(example_table.RA,example_table.Dec)

# Append the columns to the table and mark with my name in case of multiple classifiers
# This step can probably be combined with the function, but I'm making it 2 steps
# Also note that the JC suffx is if people were to concatenate tables, so change this to your own initals
# ... Unless you have initials JC, in which case, JC2, maybe?
example_table['JF_flag_JC'] = jf_flag_val
example_table['tail_confidence_JC'] = tail_confid
example_table['tail_angle_JC'] = tail_ang_val

# Use these to check outputs
print(example_table.JF_flag_JC)
print(example_table.tail_confidence_JC)
print(example_table.tail_angle_JC)
#####################################################