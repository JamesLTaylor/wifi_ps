import process_android
import datetime
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize
import visualize_greenstone_path

""" Functional form of WIFI strengths
"""
def func5(x, K, x0, al, bl, ar, br):
    x = np.array(x)
    y = np.zeros(x.shape)
    y[x<=x0] = K + al*(( x0 - x[x<=x0] )**2) - bl*( x0 - x[x<=x0] )
    y[x>x0]  = K + ar*(( x[x>x0]- x0  )**2) -  br*( x[x>x0]- x0  )    
    
    tpr = (br/(2*(ar+1e-9))) # from x0
    y[(x-x0)>tpr] = K + ar*(tpr**2) -  br*tpr
    
    tpl = (bl/(2*(al+1e-9))) # from x0 to the left
    y[(x0-x)>tpl] = K + al*(tpl**2) -  bl*tpl    
    
    return y
    
def func6(x, K, x0, wl, bl, wr, br):
    if x0<1:
        ar = wr*br/(2*(1-x0))
    else:
        ar = 0
    if x0>0:
        al = wl*bl/(2*x0)
    else:
        al = 0
    y = np.zeros(x.shape)
    y[x<=x0] = K + al*(( x0 - x[x<=x0] )**2) - bl*( x0 - x[x<=x0] )
    y[x>x0]  = K + ar*(( x[x>x0]- x0  )**2) -  br*( x[x>x0]- x0  )    
    return y    

""" sum of squares of residuals
""" 
def func5_res(p, x, y):
    K, x0, al, bl, ar, br = p
    y_model = func5(x, K, x0, al, bl, ar, br)
    res = np.sum((y-y_model)**2)
    return res
    
def func6_res(p, x, y):
    K, x0, wl, bl, wr, br = p
    y_model = func5(x, K, x0, wl, bl, wr, br)
    res = np.sum((y-y_model)**2)
    return res   
    
def fit(x, y):    
    x0 = [-50, x[np.argmax(y)], 1, 25, 1, 25]
    bounds = ((-80, 0),
            (min(x), max(x)),
            (0, 100),
            (20, None),
            (0, 100),
            (20, None))
            
    res = minimize(func5_res, x0, args=(x,y), method = "L-BFGS-B", bounds = bounds, options={'gtol': 1e-6, 'disp': True})
    return res
""" Fitted y
"""
def fitted(x2, x, y):
    res = fit(x,y)
    y2 = func5(x2,*res.x)
    return y2

class drawer(object):
    def __init__(self, ax, all_ids, original_points, macs_tablet, names_tablet):        
        self.counter = 0
        self.ax = ax
        self.all_ids = all_ids
        self.original_points = original_points
        self.macs_tablet = macs_tablet
        self.names_tablet = names_tablet
        
        
    def draw(self):        
        mac_id = self.all_ids[self.counter]
        self.ax.cla()
        x = np.array([p["frac"] for p in self.original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        y = np.array([p["stats"][mac_id][1] for p in self.original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        color = [p["color"] for p in self.original_points if p["stats"].has_key(mac_id) and p.has_key("frac")]
        
        for i in range(len(x)):
            self.ax.plot(x[i], y[i], '.', color = color[i])  
        self.ax.set_title("{:},{:},{:}".format(mac_id,self.macs_tablet[mac_id],self.names_tablet[mac_id]))
        self.ax.set_xlim(0, 1) 
        self.ax.set_ylim(-100, -30) 
        
        x=x[y>=-90]
        y=y[y>=-90]

        if len(x)>30:
            density = len(x)/(max(x)-min(x))
            self.ax.text(0.8, -35, density, fontsize=10)
            x2 = np.arange(min(x),max(x),1.0/100)
            y2 = fitted(x2, np.array(x), np.array(y))
            self.ax.plot(x2, y2, color="black")
        
        plt.draw()
        
    def press(self, event):
        self.counter+=1
        if self.counter<len(self.all_ids):
            self.draw()
            
def interp_path(frac, path_lr):
    x = 1076 + frac*(1807-1076)
    y = 614 + frac *(502-614)
    return (x,y)

""" For each mac address plot signal strength as function of fraction of path
"""    
def plot_fits(all_ids, original_points, macs_tablet, names_tablet):
    fig, (ax) = plt.subplots(1, 1)
    d = drawer(ax, all_ids, original_points, macs_tablet, names_tablet)
    fig.canvas.mpl_connect('key_press_event', d.press)
    d.draw()
    
def create_location_summaries(path_lr, original_points, all_ids):
    """
    If fit then for each x in range make summary
    """
    N = 21
    location_summaries = []
    for i in range(N):
        frac = float(i)/(N-1)
        (x, y) = interp_path(frac, path_lr)
        summary = {"x":x, "y":y, "level":level, "stats":{}, "frac":frac}        
        location_summaries.append(summary)
        
    valid_macs = []
    for mac_id in all_ids:
        x = np.array([p["frac"] for p in original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        y = np.array([p["stats"][mac_id][1] for p in original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        x=x[y>=-90]
        y=y[y>=-90]

        if len(x)>30:
            valid_macs.append(mac_id)
            density = len(x)/(max(x)-min(x))
            res = fit(x,y)
            for summary in location_summaries:
                if summary["frac"] >= min(x) and summary["frac"] <= max(x):
                    summary["stats"][mac_id] = [density, float(func5(summary["frac"],*res.x)), 0]    
                    
    return (location_summaries, valid_macs)

if __name__ == "__main__":
    path_lr = [[1076, 614], [1251, 629], [1551,579], [1807,502]]
    level = 1
    # tablet time
    walks = [{"start":datetime.datetime(2016,5,16,12,42,24), "length":140752,"direction":-1, "color":"Red", "color2":"orange"},
              {"start":datetime.datetime(2016,5,16,12,59,24), "length":141406,"direction":1, "color":"Green", "color2":"lightgreen"},
               {"start":datetime.datetime(2016,5,16,13,02,12), "length":144976,"direction":-1, "color":"Blue","color2":"lightblue"}]
               
    for walk in walks:
        walk["end"] = walk["start"] + datetime.timedelta(milliseconds=walk["length"])           
    
    
    phone_offset = 5.5 # phone time = tablet time -5.5s
    folder_phone = "C:\\Dev\\data\\greenstone20160516\\phone"
    folder_tablet = "C:\\Dev\\data\\greenstone20160516\\tablet"
    
    (names_phone, macs_phone) = process_android.get_macs(folder_phone+ "/" + "greenstone_macs.txt")
    (names_tablet, macs_tablet) = process_android.get_macs(folder_tablet+ "/" + "greenstone_macs.txt")
    
    date_range1 = datetime.datetime(2016,5,16,0,0,0)
    date_range2 = datetime.datetime(2016,5,16,23,59,59)
    
#==============================================================================
# Get points from files
#==============================================================================
    #original_points = process_android.get_paths(folder_tablet, macs_tablet, macs_tablet, date_range = [date_range1, date_range2])
    #phone_points = process_android.get_paths(folder_phone, macs_tablet, macs_phone, date_range = [date_range1, date_range2])
    #for point in phone_points:
    #    point["phone"] = True
    #    point["time"] = point["time"] + datetime.timedelta(seconds=phone_offset)
    #original_points = original_points + phone_points
    

#==============================================================================
# Assign color and fraction to each point
#==============================================================================
    all_ids = set()
    for point in original_points:
        # check which walk it was in
        all_ids = all_ids.union(point["stats"].keys())
        for (j, walk) in enumerate(walks):
            if (point["time"]>=walk["start"] and point["time"]<=walk["end"]):
                point["frac"] = (point["time"]-walk["start"]).total_seconds()/(walk["length"]/1000.0)                
                if point.has_key("phone"):
                    point["color"] = walk["color2"]
                else:
                    point["color"] = walk["color"]
                if walk["direction"]<0:
                    point["frac"] = 1 - point["frac"]
    all_ids = list(all_ids)

#plot_fits(all_ids, original_points, macs_tablet, names_tablet)
(location_summaries, valid_macs) = create_location_summaries(path_lr, original_points, all_ids)

#==============================================================================
# Process and view a single path 
#==============================================================================
#path = process_android.get_paths(folder_tablet, macs_tablet, macs_tablet, fname = "greenstone_continuous_20160516_124224.txt")
#new_path = process_android.process_path(path, location_summaries, valid_macs)
#visualize_greenstone_path.show([new_path])       
            