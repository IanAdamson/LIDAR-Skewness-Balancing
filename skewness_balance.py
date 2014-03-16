# Ian Adamson, Celeste Melosh
# Written for Python 2.7.3
# Last modified Feb 06, 2013
import string
import math
from bisect import bisect_left
from sys import stdout

# User settings
input_file  = "DC.csv"     # The CSV file containing the data to work with.

output_file = "output.csv" # The file to output the unskewed data to. This file
                           # will be created at run time.
                           # WARNING!!! This file will be OVERWRITTEN
                           # if it already exists!

tolerance = 0              # Acceptable distance from 0 for end skewness value.
                           # Should be left at 0 unless you have a good reason
                           # to change it. By default, the script should end once
                           # it has found the lowest possible skewness value.


#####################################
## Functions
#####################################

# Returns true if the value x exists in container a, false if it does not.
def valueExistsIn(x, a):
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return True # Value exists
    return False # Value does not exist

# Measures and returns the skewness of all points from
# index 0 to the point at the index specified by the
# "end" parameter.
def getSkewnessToPoint(data_points, end):
    # Get Sigma, the mean average for all points in range.
    S, N = 0, 0
    for i in range(0,end+1): # range() is not inclusive on the upper bound, hence end+1
        S += float (data_points[i][1])
        N = N + 1
        sigma = S/N

    # Get the standard deviation for all points in specified range.
    sqr_dif_from_mean = 0
    for i in range(0,end+1):
        sqr_dif_from_mean = sqr_dif_from_mean + (data_points[i][1] - sigma)**2
    standard_deviation = math.sqrt(sqr_dif_from_mean/(N-1)) 

    # And, finally, get the skewness value.
    sum_diff_cubed = 0
    max_value = 0;
    for i in range(0,end+1):
        sum_diff_cubed = sum_diff_cubed + (data_points[i][1] - sigma)**3
    sk = sum_diff_cubed/(N*(standard_deviation**3))
    
    return sk

#####################################
## Main program
#####################################

# Load the data into a List of Tuples and hope the computer doesn't explode
# or run out of memory. Break out of the loop once we hit the end of the file.

stdout.write("Loading data... ")

LIDAR_input = open(input_file, "r")     # Open LIDAR data file
column_headers = LIDAR_input.readline() # Get the column headers out of the way.
data_points = list()                    # The list that holds the original set of points
 
while True:
    data_point = LIDAR_input.readline()                           # Grab a line from the file.
    if not data_point:                                            # If we don't get a line, we're done and we leave the loop.
        break
    data_array = string.split(data_point, ',')                    # Split the comma-separated values into array.
    new_point = (int(data_array[0]), float(data_array[3]))        # Add the ID and elevation of the point to a tuple.
    data_points.append(new_point)                                 # Add the new point tuple to the list of all points.

stdout.write("Loaded " + (str)(len(data_points)) + " data points.\r\n")

# Sort the data in ascending order.
stdout.write("Sorting data... ")
data_points = sorted(data_points, key=lambda tup: tup[1])
stdout.write("Success!\r\n")

# Set the right bound and get the inital skewness.
right_bound = len(data_points)-1
skewness = getSkewnessToPoint(data_points, right_bound)
stdout.write("Initial skewness: " + (str)(skewness) + "\r\n")

# This subroutine performs a binary search to find the
# index value that returns the lowest skewness when
# passed to getSkewnessToPoint. We can then assume that
# all points past that index value are object points.
loopcount = 1
while abs(skewness) > 0 + tolerance and right_bound//(2**loopcount) > 0:
    if skewness > 0: # Move right_bound to the left by half.
        right_bound = right_bound - right_bound//(2**loopcount)
    if skewness < 0: # Move right_bound to the right by half.
        right_bound = right_bound + right_bound//(2**loopcount) 
    stdout.write("(" + (str)(loopcount).zfill(2) + ") Getting skewness up to index " + (str)(right_bound) + "... ")
    skewness = getSkewnessToPoint(data_points, right_bound)
    print (str)(skewness)
    loopcount = loopcount + 1

print "Lowest skewness value found at index " + (str)(right_bound)

# Clip off bottom half of data set, from 0 to right_bound. All remaining
# points have been identified as object points.
del data_points[:right_bound]
stdout.write("Points to remove from data: " + (str)(len(data_points)) + "\r\n")

# For each remaining point in data set, let the value equal the value of the index in the tuple.
# That is, drop the elevation value. We don't need it any more, and this makes comparisons
# easier in the next step.
stdout.write("Trimming points...\r\n")
for i in range(0, len(data_points)):
    data_points[i] = data_points[i][0]
    
# Sort the list by index value, so that we can easily search for specific indices.
stdout.write("Resorting points...\r\n")
data_points.sort()

# Open the output file and begin copying all non-object points to it.
stdout.write("Writing non-object points to output file...\r\n")
LIDAR_output = open(output_file, "w")      # Create output file
LIDAR_input.seek(0)                        # Rewind input file
LIDAR_output.write(LIDAR_input.readline()) # Write the column headers to the new file.

# Loop through all points in the input file and, if they're not
# among the points we've identified as object points, write them
# to the output file.
while True:
    data_point = LIDAR_input.readline()                           # Input the next point.
    if not data_point:                                            # If we don't get a line, we're done and we leave the loop.
        break
    data_array = string.split(data_point, ',')                    # Split the comma-separated values into array.
    if not valueExistsIn(int(data_array[0]), data_points):        # If the point isn't in our list of object points, output it.
        LIDAR_output.write(data_point)

# Close the output and input files.
LIDAR_output.close()
LIDAR_input.close()

stdout.write("Done.\r\n")
