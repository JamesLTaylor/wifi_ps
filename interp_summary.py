import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
import matplotlib.cbook as cbook
import time
import copy
import datetime
import os

def show_points(location_summaries):
    datafile = cbook.get_sample_data('C:/Dev/android/WifiRecord/app/src/main/res/drawable/greenstone_lower.png')
    lower_img = imread(datafile)
    lower_img_flip = lower_img[::-1, :, :]
    lower_img_faded = (255*0.7 + lower_img_flip*0.3).astype('uint8')
    datafile = cbook.get_sample_data('C:/Dev/android/WifiRecord/app/src/main/res/drawable/greenstone_upper.png')
    upper_img = imread(datafile)
    upper_img_flip = upper_img[::-1, :, :]
    upper_img_faded = (255*0.7 + upper_img_flip*0.3).astype('uint8')
    
    fig, (ax_upper, ax_lower) = plt.subplots(2, 1)
    #mng = plt.get_current_fig_manager()
    #mng.full_screen_toggle()
    ax_upper.cla()
    ax_upper.imshow(upper_img_faded, zorder=0, extent=[0, 2200, 0, 1054])    
    ax_upper.set_xlim(400, 1100) 
    ax_upper.set_ylim(800, 400) 
    
    ax_lower.cla()
    ax_lower.imshow(lower_img_faded, zorder=0, extent=[0, 2200, 0, 760])
    ax_lower.axis([300, 1000, 100, 500])
    ax_lower.set_ylim(500, 100) 
    
    
    
    for (i, s) in enumerate(location_summaries):
        x = s["x"]
        y = s["y"]
        display = str(i)
        if s.has_key("interp"):
            color = "Yellow"
        else:
            color = "Black"
        if s["level"]==0:             
            ax_lower.plot([x], [y], 'o', color = color)            
            ax_lower.text(x+2, y, display, fontsize=10)
        else:
            ax_upper.plot([x], [y], 'o', color = color)            
            ax_upper.text(x+2, y, display, fontsize=10)
            
        
    plt.show()
    
def add_interp_points(avg_pairs, location_summaries):    
    
    extended_location_summaries = copy.deepcopy(location_summaries)
    for (i1, i2) in avg_pairs:
        new_stats = {}
        stats1 = location_summaries[i1]["stats"]
        stats2 = location_summaries[i2]["stats"]
        new_summary = {}
        new_summary["x"] = 0.5*(location_summaries[i1]["x"] + location_summaries[i2]["x"])
        new_summary["y"] = 0.5*(location_summaries[i1]["y"] + location_summaries[i2]["y"])
        new_summary["level"] = location_summaries[i1]["level"]
        new_summary["interp"] = True
        new_summary["stats"] = new_stats
        extended_location_summaries.append(new_summary)
    
        for (key, value) in stats1.iteritems():
            if stats2.has_key(key):
                new_stats[key] = [0.5*(value[0] + stats2[key][0]),
                                  0.5*(value[1] + stats2[key][1]),
                                  0.5*(value[2] + stats2[key][2])]
            else:
                new_stats[key] = [0.5*value[0],
                                  value[1],
                                  value[2]]
                                  
        for (key, value) in stats2.iteritems():
            if not new_stats.has_key(key):
                 new_stats[key] = [0.5*value[0],
                                  value[1],
                                  value[2]]
                                  
    return extended_location_summaries
    
def write_summary(folder, name, location_summaries):
    now_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")
    f = open(os.path.join(folder, name + "_summary_" + now_str + ".txt"), "w")
    for location in location_summaries:    
        f.write("LOCATION,"+str(location["level"])+","+"{:.1f}".format(location["x"])+","+"{:.1f}".format(location["y"]) + "\n")
        for (key, data) in location["stats"].iteritems():
            f.write(str(key) + "," + "{:.1f}".format(data[0]) + "," + "{:.1f}".format(data[1]) + "," + "{:.1f}".format(data[2]) + "\n")
        
    f.close()
                             
            
    

avg_pairs =[[0,1],
            [1,2],
            [2,3],
            [3,4],
            [4,5],
            [3,6],
            [0,3],
            [6,7],
            [7,8],
            [8,9],
            [12,13],
            [13,14],
            [14,15],
            [15,16],
            [16,17],
            [17,18]]
#extended_location_summaries = add_interp_points(avg_pairs, location_summaries)
show_points(location_summaries)
#write_summary(folder_tablet,"greenstone", extended_location_summaries)            


        
        


