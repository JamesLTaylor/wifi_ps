import copy
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math

""" Takes a path on a single level with estimated x and y positions and spreads 
it out evenly according to the time.

The walk needs to be have been done at a fairly constant pace

"""
def fix_path(points_in, level=None):
    if level is None:
        path1 = np.array([ [point["x"], point["y"], point["offset"], i] for (i, point) in enumerate(points_in)])
    else:
        path1 = np.array([[point["x"], point["y"], point["offset"], i] for (i,point) in enumerate(points_in) if point["level"]==level])
        
    # no point should be returned to after a step away from it
    for i in range(1, len(path1)):
        d = abs(path1[i,0]-path1[i-1,0]) + abs(path1[i,1]-path1[i-1,1])
        if d>2: # Have moved, check it is not back to somewhere we recently were
            for j in range(max(0, i-10), i):
                d = abs(path1[i,0]-path1[j,0]) + abs(path1[i,1]-path1[j,1])
                if d < 2:
                    path1[i,0] = path1[i-1,0]
                    path1[i,1] = path1[i-1,1]
            
    
    
    shift_for_display = 10 # only set this if you want to display the orignal and fixed paths
    points_out = copy.deepcopy(points_in)
    cum_len = np.zeros((len(path1),1))
    
    for i in range(1, len(path1)):
        cum_len[i] = cum_len[i-1] + np.sqrt((path1[i,0]-path1[i-1,0])**2 + (path1[i,1]-path1[i-1,1])**2)
        
    cum_len = cum_len/cum_len[-1]
        
    start_lag = 5000 # to allow that the walk did not start exactly at the first 
                  # mapped point or that there was a period o
    end_lag = 8000
    new_path = np.zeros((len(path1),2))
    new_path[0,:] = path1[0,0:2] + [0,shift_for_display]
    for i in range(1, len(path1)):
        tw = (path1[i,2] - (path1[0,2] + start_lag)) / (path1[-1,2]-end_lag - (path1[0,2] + start_lag)) # time weigyht
        # find the x,y pair that is closest to this weight in cum_len
        if tw<=0:
            left_ind = np.where(cum_len>0)[0][0]-1
            sw = (tw-cum_len[left_ind]) / (cum_len[left_ind+1] - cum_len[left_ind]) # segment weight
        elif tw>1:
            left_ind = np.where(cum_len<1)[0][-1]
            sw = (tw-cum_len[left_ind]) / (cum_len[left_ind+1] - cum_len[left_ind]) # segment weight
        else:
            left_ind = np.where(cum_len<tw)[0][-1]
            sw = (tw-cum_len[left_ind]) / (cum_len[left_ind+1] - cum_len[left_ind]) # segment weight
            
        new_path[i,0] = path1[left_ind,0] + sw * (path1[left_ind+1,0] - path1[left_ind,0])
        new_path[i,1] = path1[left_ind,1] + sw * (path1[left_ind+1,1] - path1[left_ind,1])+shift_for_display
        
        points_out[int(np.round(path1[i,3]))]["x"] = new_path[i,0]
        points_out[int(np.round(path1[i,3]))]["y"] = new_path[i,1]
        
#    plt.figure()
#    path1 = path1
#    plt.plot(path1[:,0], path1[:,1])
#    plt.gca().set_ylim(800, 400)
#
#    plt.figure()        
#    plt.gca().set_ylim(800, 400)
#    for i in range(len(path1)):
#        plt.plot([new_path[i,0], path1[i,0]],[new_path[i,1], path1[i,1]], color="Black")
    
        
    return points_out        
 
 
if __name__ == "__main__":
    fix_path(original_points_processed)
    
    
    

    
