# Tail-finding

A set of codes which help people measure tail angles of ram pressure stripping galaxies. The most important part of the script is the plt.ginput() command, which allows the interactive clicking of coordinates on top of displayed images, and returns the coordinates. This allows a line to be drawn to get an estimate of the tail direction from visual inspection.

The main functions are given in the file draw_tails_func.py. This contains the needed function for any tail drawing. It currently has 1 useful function, but will include more as time goes on.

The function drawtail_decals_RGB which takes input RA and Dec coordinates, and displays a Legacy Survey cutout image to classify. It outputs 3 values per galaxy: 
- whether the galaxy is a Jellyfish, merger, or neither (1, -1, 0)
- How obvious/strong the tail is (0, 1, 2)
- The angle of the tail, taken from a line pointing east/to the right hand side (float between -179 and 180 degrees). An example of how this angle is shown is displayed in Angle_examples.pdf

I've created several files to help demonstrate how I run the functions. 
BCGoffset_plot.py: This code loads in a csv formatted table, and runs any drawtails function (the example uses drawtail_decals_RGB) to get tail angles. From this, it then takes the RA and Dec coordinates, and compares them to the BCGRA and BCGDec coordinates, to calculate the angle between the BCG and each tagrt galaxy. The code then plots a histogram, showing the difference between the ram pressure stripped tail angle, and the angle between galaxy and BCG. The

BCGoffset_plot_single_cluster.py: This code is a modified version of the code above, which has a single input for the cluster centre coordinates. It should have the same functionality as the code above, but doesn't require the additional BCG coordinate table columns as input (The default is set to the Coma cluster).

Example_usage.py is a very basic script that demonstrates how I use the function. It doesn't have any of the plotting features, but prints the outputs of drawtail_decals_RGB.

I've also included 2 example files, which demonstrate the format that needs to be input into the codes
- Example_table_Coma.csv contains four ram pressure stripped galaxies in the Coma cluster. They are sourced from the papers Yagi et al., (2010); Smith et al., (2010); and Roberts et al., (2020). This is a good example file to test any single_cluster files.
- Example_table_Poggianti16.csv contains four ram pressure stripped galaxies from various WINGS clusters in the study of Poggianti et al., (2016). This file should be good to test any code that prefers multiple clusters.

Other files:
- Angle_examples.pdf displays a graphic which highlights the angles I define in the various functions. Use it to help visualise what is being measured.