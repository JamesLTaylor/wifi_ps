import os
import datetime
import math
import numpy as np
import copy

import fix_path
import visualize_greenstone_path



""" finds the nearest aggregate in the list or makes a new one.

Ensures the structure is:
mx:
my:
allx: 
ally:
N:
allreadings:  macnum1:   [vector or readings]
              macnum2:   [vector or readings]
              ...
"""
def get_aggregate(aggregates, x, y, level):    
    for aggregate in aggregates:
        dist = math.sqrt((aggregate["mx"]-x)**2+(aggregate["my"]-y)**2)
        if level==aggregate["level"] and dist<min_dist_px:
            aggregate["all_x"].append(x)
            aggregate["all_y"].append(y)
            aggregate["mx"] = np.mean(aggregate["all_x"])
            aggregate["my"] = np.mean(aggregate["all_y"])
            return aggregate
    
    new_aggregate = {"mx":x, "my":y, "level": level, "all_x":[x], "all_y":[y], "N":0, "all_readings":{}}
    aggregates.append(new_aggregate)
    return new_aggregate
    
""" Writes a summary file and returns a list of summaries:

    x: 
    y:
    level:
    stats:    mac_id_1:    [p, mu, sigma]
              mac_id_2:    [p, mu, sigma]
              ...
    

"""    
def process_readings_write_summary(folder, date_range, write=False):    
    aggregates = []
    allfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    
    #==============================================================================
    # Create aggregates
    #==============================================================================
    for filename in allfiles:
        parts = filename[:-4].split("_",2)
        if parts[1]=="readings":
            date = datetime.datetime.strptime(parts[2], "%Y%m%d_%H%M%S")
            if date>=date_range[0] and date<=date_range[1]:
                f = open(os.path.join(folder, filename), "r")
                lines = f.readlines()
                f.close()
                for line in lines:
                    parts = line.split(',')
                    try: 
                        mac_num = int(parts[0])
                        is_int = True
                    except ValueError:
                        is_int = False
                    if parts[0]=="NEW":                
                        this_aggregate = get_aggregate(aggregates, float(parts[1]), float(parts[2]), int(parts[3]))
                        all_readings = this_aggregate["all_readings"]
                    elif parts[0]=="OFFSET":
                        this_aggregate["N"] += 1
                    elif is_int:
                        
                        if not all_readings.has_key(mac_num):
                            all_readings[mac_num] = [float(parts[1])]
                        else:
                            all_readings[mac_num].append(float(parts[1]))
                    
    #==============================================================================
    # Create summary                
    #==============================================================================
                    
    summaries = []
    now_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")
    if write: f = open(os.path.join(folder, location + "_summary_" + now_str + ".txt"), "w")
    for aggregate in aggregates:        
        this_summary = {"x":aggregate["mx"], "y":aggregate["my"], "level":aggregate["level"], "stats":{}}
        if write: f.write("LOCATION,"+"{:.1f}".format(aggregate["level"])+","+"{:.1f}".format(aggregate["mx"])+","+"{:.1f}".format(aggregate["my"]) + "\n")
        all_readings = aggregate["all_readings"]
        N = float(aggregate["N"])
        for (key, data) in all_readings.iteritems():
            p = len(data)/N
            mu = np.mean(data)
            std = np.std(data)
            this_summary["stats"][key] = [p, mu, std]            
            if write: f.write(str(key) + "," + "{:.1f}".format(p) + "," + "{:.1f}".format(mu) + "," + "{:.1f}".format(std) + "\n")
        summaries.append(this_summary.copy())
    if write: f.close()
    return summaries
    
""" Get the readings from a file.
 return as a list of readings like this:
 
    x: 
    y:
    level:
    readings:    mac_id_1:    reading1
                 mac_id_2:    reading2
                 ...
"""
def get_single_readings(filename):
    f = open(os.path.join(folder, filename), "r")
    lines = f.readlines()
    f.close()
    all_readings = []
    for line in lines:
        parts = line.split(',')
        try: 
            mac_num = int(parts[0])
            is_int = True
        except ValueError:
            is_int = False
        if parts[0]=="NEW":
            x = float(parts[1])
            y = float(parts[2])
            level = int(parts[3])        
        elif parts[0]=="OFFSET":
            this_reading = {"x":x, "y":y, "level":level, "readings":{}}      
            all_readings.append(this_reading)
        elif is_int:
            this_reading["readings"][mac_num] = float(parts[1])
    return all_readings
    
"""
Single obs

1. If you see a network that is in the finger print penalize by the difference between means weighted by prob of in fingerprint.
2. If you don't see a network that is in the fingerprint penalize by prob in finger print * w1 * (maybe a measure of strength if p=1)
3. If you see a network that is not in the fingetprint penalize by -90 -strenth * (prob in obs)

Multiple obs

Make it such that no reading gets -100
"""   
def get_diff(obs, location, valid_macs):
    score = 0
    w1 = 1
    w2 = 1
    w3 = 2
    weighting = 0
    for loc_mac_key, loc_stats in location.iteritems():
        weighting += w2 * loc_stats[0] * abs(-90-loc_stats[1])
        if loc_mac_key in obs.keys():
            # in fingerprint and in obs
            d = abs(loc_stats[1] - obs[loc_mac_key][1])
            d = max(0, d-0)
            score -= w1 * d * loc_stats[0]
        else:
            # in fingerprint but not in obs
            score -= w2 * loc_stats[0] * abs(-90-loc_stats[1])
            
    for obs_mac_key, obs_stats in obs.iteritems():
        if obs_mac_key in valid_macs and obs_mac_key not in location.keys():
            score -= w3 * obs_stats[0] * abs(-90-obs_stats[1])
            # in obs but not fingerprint

    return 100.0 * score/weighting         
    
    
""" make a list of summaries as if each reading was the whole observation
"""    
def make_summaries_from_single(all_readings):
    summaries = []
    for reading in all_readings:
        this_summary =  {"x":reading["x"], "y":reading["y"], "level":reading["level"], "stats":{}}
        for key, value in reading["readings"].iteritems():
            this_summary["stats"][key] = [1, value, 0]
        summaries.append(this_summary)
    return summaries
    
""" randomly pick n readings and make a summary
"""    
def make_summaries_from_rand_n(all_readings, n):    
    pass


"""
"""
def compare_single_readings(single_obs_summaries, location_summaries):
    for (i, s) in enumerate(single_obs_summaries):
        #if i >10: break
            
        diffs = [get_diff(s["stats"], location_summary["stats"]) for location_summary in location_summaries]
        ind = np.argmax(diffs)
        print(str(i) + "   :" + str(s["level"]) + "," + str(s["x"]) + "," +str(s["y"]) + " mapped to:  " + 
                str(location_summaries[ind]["level"]) + "," + str(location_summaries[ind]["x"]) + 
                "," +str(location_summaries[ind]["y"])) 
         
""" Returns a dictionary with keys as ints used in the recordings and values 
as the names of the APs
"""
def get_macs(fname):
    f=open(fname,'r')
    lines = f.readlines()
    f.close 
    rows = [line[:-1].split(',') for line in lines]
    int_to_name = {}
    int_to_mac = {}
    for row in rows:
        int_to_name[int(row[2])] = row[1]
        int_to_mac[int(row[2])] = row[0]
    
    return int_to_name, int_to_mac
    
def translate_mac(i, macs_from, macs_to):
    if macs_from.has_key(i):
        mac = macs_from[i]
    else:
        return 10000+i
    for (num, name) in macs_to.iteritems():
        if name==mac:        
            return num
    
    return 10000+i
    
"""
"""
def get_paths(folder, macs_summaries, macs_path, **kwargs):    
    date_range = []
    fname = ""
    if len(kwargs)>1:
        raise Exception("Provide only one of 'fname' or 'date_range'")
    for key in kwargs:
        if key == "fname":
            fname = kwargs[key]
        elif key == "date_range":
            date_range = kwargs[key]
        else:
            raise Exception("Provide only one of 'fname' or 'date_range'")
    
    allfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    all_points = []
    for filename in allfiles:
        parts = filename[:-4].split("_",2)
        if parts[1]=="continuous":
            date = datetime.datetime.strptime(parts[2], "%Y%m%d_%H%M%S")
            if ( (len(fname)>0 and filename==fname) or 
                 (len(date_range)>0 and date>=date_range[0] and date<=date_range[1]) ):
            
                f = open(os.path.join(folder, filename), "r")
                lines = f.readlines()
                f.close()
                for line in lines:
                    parts = line.split(',')
                    try: 
                        mac_num = int(parts[0])
                        is_int = True
                    except ValueError:
                        is_int = False
                    if parts[0]=="OFFSET":                        
                        this_point = {}
                        this_point["time"] = date + datetime.timedelta(milliseconds=float(parts[1]))
                        this_point["offset"] = float(parts[1])
                        this_point["stats"] = {}
                        all_points.append(this_point)
                    elif is_int:
                        new_mac_num = translate_mac(mac_num, macs_path, macs_summaries)
                        this_point["stats"][new_mac_num] = [1, float(parts[1]), 0]
                
    return all_points
    
""" Take the n point average of all the points in a path.
"""
def get_paths_n(n, all_points):
    avg_points = []
    for i in range((n-1), len(all_points)):
        this_point = {}
        this_point["time"] = all_points[i]["time"]
        this_point["offset"] = all_points[i]["offset"]
        this_point["stats"] = {}
        avg_points.append(this_point)
        all_keys = set()
        for j in range(n):
            all_keys = all_keys.union(all_points[i-j]["stats"].keys())        
        
        for key in all_keys:
            means = []
            for j in range(n):
                if all_points[i-j]["stats"].has_key(key):
                    means.append(all_points[i-j]["stats"][key][1])
            this_point["stats"][key] = [float(len(means))/n, np.mean(means), 0]
                
    return avg_points    
    
    
""" Takes a path from:
        get_paths
    and adds location information to each point.
"""    
def process_path(all_points, location_summaries, valid_macs):
    px_per_meter = 4.20 # Greenstone
    walking_pace = 2.0 # FAST: 7.6km/h
    augmented_points = copy.deepcopy(all_points)
    age = 0
    old_score = - 1001
    old_ind = 0
    old_t = 0
    old_x = 0
    old_y = 0
    old_level = 0
    connection_points = [[[530, 320],[570, 660]],
                        [[1020,425],[1100,690]]]
    old_close_conn = 0

    for (i, point) in enumerate(augmented_points):
        if i==len(augmented_points)-1:
            aaa = 1
        print ("")
        print (str(i))
        print (age)
        diffs = [get_diff(point["stats"], location_summary["stats"], valid_macs) for location_summary in location_summaries]
        
        print("currently at {:},{:},{:} with score {:}".format(old_level, old_x, old_y, diffs[old_ind]))        
        ind = np.argmax(diffs)
        score = np.max(diffs)        
        print("new best score = {:3.0f} at {:},{:},{:}".format(score, location_summaries[ind]["x"], location_summaries[ind]["y"], location_summaries[ind]["level"]))
        print("time elapsed {:}".format((point["offset"] - old_t)/1000))
        update = False
        if old_score<=-1000: # first point
            update = True
        elif (score<(diffs[old_ind]+5) and age<3):
            update = False
        elif ind==old_ind:
            update = True
            print("same place")
        else:
            x = location_summaries[ind]["x"]
            y = location_summaries[ind]["y"]
            level = location_summaries[ind]["level"]
            if level==old_level:
                dist_px = math.sqrt((x-old_x)**2 + (y-old_y)**2)
            else:
                x0 = connection_points[old_close_conn][old_level][0]
                y0 = connection_points[old_close_conn][old_level][1]
                x1 = connection_points[old_close_conn][level][0]
                y1 = connection_points[old_close_conn][level][1]                
                dist_px = math.sqrt((x0-old_x)**2 + (y0-old_y)**2) + math.sqrt((x1-x)**2 + (y1-y)**2)
            
            # Could one have got this far? Deduct the 20 since we could be wrong about our current location
            time_to_there = (((dist_px / px_per_meter)-20) / walking_pace)
            print("time to get there: {:}".format(time_to_there))
            if time_to_there*1000 < (point["offset"] - old_t):
                update=True
                #print("close enough")
                
        if update:
            age = 0
            old_ind = ind
            old_t = point["offset"]
            old_score = score
            old_x = location_summaries[ind]["x"]
            old_y = location_summaries[ind]["y"]
            old_level = location_summaries[ind]["level"]
            d_best = 1e9
            for (i, conn_point) in enumerate(connection_points):
                x0 = conn_point[old_level][0]
                y0 = conn_point[old_level][1]
                d = math.sqrt((x0-old_x)**2 + (y0-old_y)**2)
                if d<d_best:
                    old_close_conn = i
                    d_best = d
            print("UPDATED: closest connection = {:}".format(old_close_conn))
        else:
            age += 1
                    
        point["score"] = old_score
        point["x"] = old_x
        point["y"] = old_y
        point["level"] = old_level        
        
    return augmented_points
        

""" Directly read a summary from a file

Summary is made by one of:
    process_readings_write_summary
    add_interp_points then write_summary
"""
def read_summary(fname):
    f = open(fname, "r")
    lines = f.readlines()
    f.close()
    valid_macs = set()
    new_summary_list = []
    for line in lines:
        parts = line.split(',')
        try: 
            mac_num = int(parts[0])
            is_int = True
        except ValueError:
            is_int = False
        if parts[0]=="LOCATION":
            new_summary = {}
            new_summary_list.append(new_summary)
            new_summary["level"] = int(np.round(float(parts[1])))
            new_summary["x"] = float(parts[2])
            new_summary["y"] = float(parts[3])
            new_summary["stats"] = {}
        elif is_int:
            valid_macs.add(mac_num)
            new_summary["stats"][mac_num] = [float(parts[1]), float(parts[2]), float(parts[3])]
    return (new_summary_list, valid_macs)
        
        

if __name__ == "__main__":
    folder_tablet1 = "C:/Dev/data/greenstone20160508/tablet"
    folder_tablet2 = "C:/Dev/data/greenstone20160510"
    folder_tablet3 = "C:/Dev/data/greenstone20160511"
    folder_tablet4 = "C:/Dev/data/greenstone20160513"
    folder_phone = "C:/Dev/data/greenstone20160508/phone"
    location = "greenstone"
    #pixel_per_meter = 38.0 # Home
    pixel_per_meter = 4.20 # Greenstone
    min_dist_m = 2.0
    min_dist_px = min_dist_m*pixel_per_meter

    date_range1 = datetime.datetime(2016,5,8,0,0,0)
    date_range2 = datetime.datetime(2016,5,10,23,59,59)
    
#==============================================================================
#   Produce a walkthough from 11 May data:     
#==============================================================================    
    #(location_summaries, valid_macs) = read_summary(folder_tablet1 + "/" + "greenstone_summary_20160510_160200.txt")
    (location_summaries, valid_macs) = read_summary(folder_tablet4 + "/" + "greenstone_summary_20160513_105108.txt")    
    (names_tab, macs_tab) = get_macs(folder_tablet2+ "/" + "greenstone_macs.txt")
    
    #original_points = get_paths(folder_tablet2, macs_tab, macs_tab, date_range = [date_range1, date_range2])
    original_points = get_paths(folder_tablet3, macs_tab, macs_tab, fname="greenstone_continuous_20160511_130140.txt")    
    #original_points = get_paths(folder_tablet3, macs_tab, macs_tab, fname="greenstone_continuous_20160511_130351.txt")
    
    original_points_processed = process_path(original_points, location_summaries, valid_macs)
    smooth_points = fix_path.fix_path(original_points_processed, level=1)
    avg_points = get_paths_n(3, original_points)
    avg_points_processed = process_path(avg_points, location_summaries, valid_macs)
    #smooth_avg_points = fix_path.fix_path(avg_points_processed)
    visualize_greenstone_path.show([smooth_points, original_points_processed, avg_points_processed])
    
    
    #location_summaries_old = process_readings_write_summary(folder_tablet1, [date_range1, date_range2], write=False)
    #location_summaries = process_readings_write_summary(folder_tablet2, [date_range1, date_range2], write=False)
#    (names_tab, macs_tab) = get_macs(folder_tablet+ "/" + "greenstone_macs.txt")
#    (names_phone, macs_phone) = get_macs(folder_phone+ "/" + "greenstone_macs.txt")
    
    #filename = "home_readings_20160506_170235.txt"
    #all_readings = get_single_readings(filename)    
    #single_obs_summaries = make_summaries_from_single(all_readings)
    #compare_single_readings(single_obs_summaries, location_summaries)
    
    #diff = get_diff(summaries1[0]["stats"], location_summaries[0]["stats"])
    #diffs = [get_diff(summaries1[1]["stats"], location_summary["stats"]) for location_summary in location_summaries]
    

        



