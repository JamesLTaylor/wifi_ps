import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
import matplotlib.cbook as cbook
import time

def add_points(ax_upper, ax_lower, this_id, name, location_summaries):
    ax_upper.set_title(str(this_id) + ":" + name)

    lower = -100.0
    upper = -50.0
    cmap=plt.get_cmap("jet")
    
    
    for s in location_summaries:
        x = s["x"]
        y = s["y"]        
        level = s["level"]
        if s["stats"].has_key(this_id):
            p = s["stats"][this_id][0]
            mu = s["stats"][this_id][1]
            s_mu = "{:.1f}".format(mu)
            std = s["stats"][this_id][2]
            length = std*7
            color = cmap(int(255*(mu-lower)/(upper-lower)))
            r = 10 + 20 * p
        else:
            p = "N/A"
            mu = "N/A"
            s_mu = "N/A"
            color = 'gray'
            length = 0
            r = 10
            
        #ax.plot([x], [935-y], 'o', color=color)
        circle = plt.Circle((x,y),r,color=color)
        if level==0: 
            ax_lower.add_artist(circle)
            ax_lower.plot([x-length, x+length], [y, y], color = "Black")            
            ax_lower.text(x+1, y, s_mu, fontsize=10)
        else:
            ax_upper.add_artist(circle)
            ax_upper.plot([x-length, x+length], [y, y], color = "Black")            
            ax_upper.text(x+1, y, s_mu, fontsize=10)
            
            
            

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

for (num, name) in int_to_name.iteritems():
    ax_upper.cla()
    ax_upper.imshow(upper_img_faded, zorder=0, extent=[0, 2200, 0, 1054])    
    ax_upper.set_xlim(400, 1100) 
    ax_upper.set_ylim(800, 400) 
    
    ax_lower.cla()
    ax_lower.imshow(lower_img_faded, zorder=0, extent=[0, 2200, 0, 760])
    ax_lower.axis([300, 1000, 100, 500])
    ax_lower.set_ylim(500, 100) 
    
    add_points(ax_upper, ax_lower, num, name, location_summaries)
    
    plt.draw()
    time.sleep(0.25)