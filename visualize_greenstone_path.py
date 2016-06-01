import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
import matplotlib.cbook as cbook
import time

def show(all_points_list):
    datafile = cbook.get_sample_data('C:/Dev/android/WifiRecord/app/src/main/res/drawable/greenstone_lower.png')
    lower_img = imread(datafile)
    lower_img_flip = lower_img[::-1, :, :]
    lower_img_faded = (255*0.7 + lower_img_flip*0.3).astype('uint8')
    datafile = cbook.get_sample_data('C:/Dev/android/WifiRecord/app/src/main/res/drawable/greenstone_upper.png')
    upper_img = imread(datafile)
    upper_img_flip = upper_img[::-1, :, :]
    upper_img_faded = (255*0.7 + upper_img_flip*0.3).astype('uint8')
    
    fig, (ax_upper, ax_lower) = plt.subplots(2, 1)
    #fig = fig = plt.gcf()
    #(ax_upper, ax_lower) = fig.axes
    #mng = plt.get_current_fig_manager()
    #mng.full_screen_toggle()
    
    
    
    for (i, points) in enumerate(zip(*all_points_list)):
        ax_upper.cla()
        ax_upper.imshow(upper_img_faded, zorder=0, extent=[0, 2200, 0, 1054])    
        ax_upper.set_xlim(400, 1800) 
        ax_upper.set_ylim(800, 300) 
        #ax_upper.set_xlim(1000, 1850) 
        #ax_upper.set_ylim(750, 450) 
        
        ax_lower.cla()
        ax_lower.imshow(lower_img_faded, zorder=0, extent=[0, 2200, 0, 760])
        ax_lower.axis([300, 1000, 100, 500])
        ax_lower.set_ylim(500, 100)
        colors = ("Black", "Red", "Blue", "Yellow")
        for (j, point) in enumerate(points):
            x = point["x"]
            y = point["y"]
            display = str(i) + "," + "{:.1f}".format(point["score"])
            if point["level"]==0:             
                ax_lower.plot([x], [y], 'o', color = colors[j])            
                ax_lower.text(x+1, y, display, fontsize=8)
            else:
                ax_upper.plot([x], [y], 'o', color = colors[j])            
                ax_upper.text(x+1, y, display, fontsize=8)
            
        
        plt.draw()
        time.sleep(0.1)
        
    plt.show()
