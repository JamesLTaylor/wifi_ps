import matplotlib.pyplot as plt

def add_points(ax, this_id, location_summaries):
    ax.axis([0, 837, -935, 0])
    ax.set_title(str(this_id))

    lower = -100.0
    upper = -50.0
    cmap=plt.get_cmap("jet")
    
    
    for s in location_summaries:
        x = s["x"]
        y = s["y"]
        level = s["level"]
        if level==1:        
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
            circle = plt.Circle((x,-y),r,color=color)
            ax.add_artist(circle)
            ax.plot([x-length, x+length], [-y, -y], color = "Black")
            
            ax.text(x+1, -y, s_mu, fontsize=10)        

# row and column sharing
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
#ax1.cla()
#ax2.cla()
#ax3.cla()
#ax4.cla()
add_points(ax1, 12, location_summaries)
add_points(ax2, 13, location_summaries)
add_points(ax3, 14, location_summaries)
add_points(ax4, 15, location_summaries)
    
#fig = plt.figure()
#ax = fig.add_subplot(111)


        
plt.show()        
        