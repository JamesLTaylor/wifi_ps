import process_android
import datetime
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize
import visualize_greenstone_path
import sys
import os
import math

import route_finding

sys.path.append(".\\mall_data")
import path_source



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
    
    mids = np.arange(0.05,1,0.05)
    means = np.zeros(mids.shape)
    for (i,mid) in enumerate(mids):
        subset = y[np.logical_and(x>=mid-0.05, x<=mid+0.05)]
        if len(subset)>1:
            means[i] = np.mean(subset)
        else:
            means[i] = -100

    max_ind = np.argmax(means)
    x0 = [means[max_ind], mids[max_ind], 1, 25, 1, 25]
    
    bounds = ((-80, 0),
            (min(x), max(x)),
            (0, 100),
            (20, None),
            (0, 100),
            (20, None))
            
    res = minimize(func5_res, x0, args=(x,y), method = "L-BFGS-B", bounds = bounds, options={'gtol': 1e-6, 'disp': False})
    return res.x
    
    
""" Fitted y
"""
def fitted(x2, x, y):
    res = fit(x,y)
    y2 = func5(x2,*res)
    return y2

class Drawer(object):
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
    if frac >= (1-1e-9):
        return (path_lr[-1][0], path_lr[-1][1])
    elif frac <= (1e-9):
        return (path_lr[0][0], path_lr[0][1])
        
    p = np.array(path_lr)
    cum_length = np.cumsum(np.append([0], np.sqrt((p[1:,0]-p[:-1,0])**2 + (p[1:,1]-p[:-1,1])**2)))
    cum_frac = cum_length/cum_length[-1]
    left_ind = np.where(cum_frac<=frac)[0][-1]
    w = (frac - cum_frac[left_ind])/(cum_frac[left_ind+1]-cum_frac[left_ind])
    
    x = p[left_ind, 0] + w * (p[left_ind+1, 0] - p[left_ind, 0])
    y = p[left_ind, 1] + w * (p[left_ind+1, 1] - p[left_ind, 1])

    return np.array([[x,y]])
    
    

""" For each mac address plot signal strength as function of fraction of path
"""    
def plot_fits(all_ids, original_points, macs_tablet, names_tablet):
    fig, (ax) = plt.subplots(1, 1)
    d = Drawer(ax, all_ids, original_points, macs_tablet, names_tablet)
    fig.canvas.mpl_connect('key_press_event', d.press)
    d.draw()
    
    
    
def update_location_summaries(path_points, obs_points, all_ids, summary_points, location_summaries, path_name, spacing_px, px_p_m):
    """
    If fit then for each x in range make summary
    """
    map_nodes = route_finding.load_map()
    path_obj = route_finding.Path(route_finding.convert_points_to_np(map_nodes, path_points), px_p_m)
 
    all_x = np.array([p["frac"] for p in obs_points])
    distances = get_ds(summary_points, path_obj)
    for mac_id in all_ids:
        x = np.array([p["frac"] for p in obs_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        y = np.array([p["stats"][mac_id][1] for p in obs_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
        x=x[y>=-90]
        y=y[y>=-90]

        if len(x)>30:
            res = fit(x,y)
        else:
            res = None
            
        for (i, (distance, path_frac)) in enumerate(distances):
            if distance<spacing_px/2: # close to a summary point so add to that summary point
                summary_dict = location_summaries[i]
                if not summary_dict["aggs"].has_key(mac_id):
                    summary_dict["aggs"][mac_id] = {}
                l = max(0, path_frac-(spacing_px/2)/ path_obj.len)
                r = min(1, path_frac+(spacing_px/2)/ path_obj.len)
                total = np.sum(np.logical_and(all_x>=l, all_x<=r))
                if not res is None:
                    count = np.sum(np.logical_and(x>=l, x<=r))
                    summary_dict["aggs"][mac_id][path_name] = [total, count, float(func5(path_frac,*res)), 0.0]
                else:
                    summary_dict["aggs"][mac_id][path_name] = [total, 0, 0, 0.0]

            
            
                    
    #return (location_summaries, valid_macs)
    
def fit_path_old():    
    path_lr = [[1076, 614], [1251, 629], [1551,579], [1807,502]]

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
    original_points = process_android.get_paths(folder_tablet, macs_tablet, macs_tablet, date_range = [date_range1, date_range2])
    phone_points = process_android.get_paths(folder_phone, macs_tablet, macs_phone, date_range = [date_range1, date_range2])
    for point in phone_points:
        point["phone"] = True
        point["time"] = point["time"] + datetime.timedelta(seconds=phone_offset)
    original_points = original_points + phone_points
    

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
    (location_summaries, valid_macs) = update_location_summaries(path_lr, original_points, all_ids)
    
    (old_location_summaries, valid_macs) = process_android.read_summary("C:/Dev/data/greenstone20160513" + "/" + "greenstone_summary_20160513_105108.txt")
    new_location_summaries = location_summaries + old_location_summaries
    process_android.write_summary("c:\\dev\\data\\summaries","greenstone",new_location_summaries)
    
    #==============================================================================
    # Process and view a single path 
    #==============================================================================
    #path = process_android.get_paths(folder_tablet, macs_tablet, macs_tablet, fname = "greenstone_continuous_20160516_124224.txt")
    #new_path = process_android.process_path(path, location_summaries, valid_macs)
    #visualize_greenstone_path.show([new_path])       
   



"""
Returns matrix same length as summary points
Each row contains:
distance to nearest segment | fraction of path corresponding to nearest point 
"""  
def get_ds(summary_points, path):
    result = np.zeros((len(summary_points),2))    
    for (i, row) in enumerate(summary_points):        
        result[i,:] = path.closest(row[0], row[1])
        
    return result
    
    
    
""" Creates points from all the paths attempting to not get any that are too 
close to each other
"""
def make_summary_points(path_points_map, spacing_px, px_p_m): 
    summary_points = np.zeros((0,2))
    location_summaries = []    
    map_nodes = route_finding.load_map()
    for key, path_point_data in path_points_map.iteritems():
        path = route_finding.Path(route_finding.convert_points_to_np(map_nodes, path_point_data), px_p_m)
        fracs_to_use = []
        spacing = spacing_px/path.len
        if len(summary_points)==0:            
            points = np.arange(0.5*spacing, 1-0.5*spacing, spacing)
            for point in points:
                path_point = path.interp(point)
                summary_points = np.vstack((summary_points, path_point))
                summary = {"x":path_point[0,0], "y":path_point[0,1], "level":1, "stats":{}, "aggs":{}}        
                location_summaries.append(summary)
        else:
            distances = get_ds(summary_points, path)
            ind = np.argmin(distances[:,0])
            while distances[ind,0]<spacing_px/2:
                fracs_to_use.append(distances[ind,1])
                distances[ind,0] = 1e9
                ind = np.argmin(distances[:,0])
                
            if len(fracs_to_use)==0:
                points = np.arange(0.5*spacing, 1-0.5*spacing, spacing)
                for point in points:
                    path_point = path.interp(point)
                    summary_points = np.vstack((summary_points, path_point))
                    summary = {"x":path_point[0,0], "y":path_point[0,1], "level":1, "stats":{}, "aggs":{}}        
                    location_summaries.append(summary)
            else:                
                fracs_to_use = np.sort(fracs_to_use)
                if fracs_to_use[0]>0: fracs_to_use = np.hstack((0,fracs_to_use))
                if fracs_to_use[-1]<1: fracs_to_use = np.hstack((fracs_to_use,1))
                new_fracs = np.array([])
                for i in range(len(fracs_to_use)-1):
                    #new_fracs = np.hstack((new_fracs, fracs_to_use[i]))
                    separation = fracs_to_use[i+1] - fracs_to_use[i]
                    if separation>spacing:
                        npoints = np.floor(separation/spacing)
                        new_space = separation/(npoints+1)
                        shifts = np.arange(new_space, separation, new_space)                    
                        new_fracs = np.hstack((new_fracs, fracs_to_use[i]+shifts))
                    
                for point in new_fracs:
                    path_point = path.interp(point)
                    summary_points = np.vstack((summary_points, path_point))
                    summary = {"x":path_point[0,0], "y":path_point[0,1], "level":1, "stats":{}, "aggs":{}}        
                    location_summaries.append(summary)
    return (summary_points, location_summaries)
    
    
    
""" Form the union of all macs observed.
dictionaries modified in place
"""    
def combine_macs(full_macs, full_names, new_macs, new_names):
    for (key, mac) in new_macs.iteritems():
        if not mac in full_macs.values():
            n = len(full_macs.keys())
            full_macs[n] = mac
            full_names[n] = new_names[key]
            
    
    
    
    
""" Process the whole folder into workable data
"""    
def get_all_data():
    all_data = {}
    full_macs = {}
    full_names = {}  
    folder = "C:\\Dev\\wifi_ps\\walks_greenstone"
    allfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]    
    for filename in allfiles:       
        parts = filename[:-4].split("_")
        if len(parts)>=5 and parts[4]=="path":            
            record_date = datetime.datetime.strptime(parts[1]+"_"+parts[2], "%Y%m%d_%H%M%S")            
            f = open(os.path.join(folder, filename), "r")
            lines = f.readlines()
            f.close()
            parts = lines[1].split(",")
            if not parts[0]=="DESCRIPTION":
                raise Exception("2nd line should start with 'DESCRIPTION' " + filename)
            else:
                description=parts[1][:-1]
            parts = lines[2].split(",")
            if not parts[0]=="DIRECTION":
                raise Exception("3nd line should start with 'DIRECTION' " + filename)
            else:
                direction=int(float(parts[1]))
            if not all_data.has_key(description):
                all_data[description] = []
            
            new_path = {"direction":direction,"datetime":record_date}
            fname_macs = filename[:-8] + "macs.txt"
            (names, macs) = process_android.get_macs(os.path.join(folder, fname_macs))            
            combine_macs(full_macs, full_names, macs, names)
            new_path["fname"] = filename
            #start = datetime.datetime.now()
            #path = process_android.get_paths(folder, macs, macs, fname=filename)
            #print(datetime.datetime.now()-start).total_seconds()
            path = []
            new_path["path"] = path            
            new_path["macs"] = macs            
            all_data[description].append(new_path)
            
    for (key, paths) in all_data.iteritems():
        
        for path in paths:
            path["path"] = process_android.get_paths(folder, full_macs, path["macs"], fname=path["fname"])
    
    return (all_data, full_macs, full_names)
    
    
    
""" Fit curves and add interpolated data to the location_summaries
"""    
def create_location_summaries(path_points_map, all_data, full_macs, summary_points, location_summaries, spacing_px, px_p_m):
    colors = ["Red", "orange", "Green", "lightgreen", "Blue", "lightblue"]
    
#    for path_name in ["TRUWORTHS/ENT-WW"]:    
    for path_name in all_data.keys():        
        data1 = all_data[path_name]
        print("Processing " + str(len(data1)) + " paths in " + path_name)
        combined_points = []
        for (i, path_data) in enumerate(data1):
            total_time = float(path_data["path"][-1]["offset"])
            for point in path_data["path"]:
                frac = point["offset"]/total_time
                if path_data["direction"] < 0: 
                    frac = 1-frac
                point["frac"] = frac
                point["color"] = colors[i]
                
            combined_points+=path_data["path"]
            
#        plot_fits(full_macs.keys(), combined_points, full_macs, full_names)
#        plot_fits([173], combined_points, full_macs, full_names)
            
        update_location_summaries(path_points_map[path_name], combined_points, full_macs.keys(), 
                              summary_points, location_summaries, path_name, spacing_px, px_p_m)


def convert_aggs_to_stats():
    # convert aggregates into summary stats                              
    for summary in location_summaries:
        for mac_id in summary["aggs"]:
            total = 0
            count = 0
            sum_means = 0
            for (path_name, values) in summary["aggs"][mac_id].iteritems():
                sum_means += values[1]*values[2]
                total += values[0]
                count += values[1]
                
            if count>0:
                summary["stats"][mac_id] = [float(count)/total, sum_means/count, 0]
                
                
                

if __name__ == "__main__":
    
    # read all the paths to find common summary points
    path_points_map = path_source.greenstone()
    px_p_m = 4.2
    spacing_px = 5*px_p_m
    #(summary_points, location_summaries) = make_summary_points(path_points_map, spacing_px, px_p_m)
    #(all_data, full_macs, full_names) = get_all_data()
    create_location_summaries(path_points_map, all_data, full_macs, summary_points, location_summaries, spacing_px, px_p_m)
#    
    convert_aggs_to_stats()
    process_android.write_summary("c:\\dev\\data", "greenstone", location_summaries)
    process_android.write_macs("c:\\dev\\data", "greenstone", full_macs, full_names)
