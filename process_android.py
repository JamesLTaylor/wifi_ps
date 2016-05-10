import os
import datetime
import math
import numpy as np



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

"""   
def get_diff(obs, location):
    score = 0
    w1 = 1
    w2 = 1
    w3 = 2
    weighting = 0
    for loc_mac_key, loc_stats in location.iteritems():
        weighting += loc_stats[0]
        if loc_mac_key in obs.keys():
            # in fingerprint and in obs
            d = abs(loc_stats[1] - obs[loc_mac_key][1])
            d = max(0, d-0)
            score -= w1 * d * loc_stats[0]
        else:
            # in fingerprint but not in obs
            score -= w2 * loc_stats[0] * abs(-90-loc_stats[1])
            
    for obs_mac_key, obs_stats in obs.iteritems():
        if obs_mac_key not in location.keys():
            score -= w3 * obs_stats[0] * abs(-90-obs_stats[1])
            # in obs but not fingerprint

    return score/weighting         
    
    
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
    mac = macs_from[i]
    for (num, name) in macs_to.iteritems():
        if name==mac:        
            return num
    
    return 10000+i
    
"""
"""
def get_paths(folder, date_range, macs_tab, macs_phone):
    allfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    all_points = []
    for filename in allfiles:
        parts = filename[:-4].split("_",2)
        if parts[1]=="continuous":
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
                    if parts[0]=="OFFSET":                        
                        this_point = {}
                        this_point["time"] = date + datetime.timedelta(milliseconds=float(parts[1]))
                        this_point["stats"] = {}
                        all_points.append(this_point)
                    elif is_int:
                        new_mac_num = translate_mac(mac_num, macs_phone, macs_tab)
                        this_point["stats"][new_mac_num] = [1, float(parts[1]), 0]
                
    return all_points
    
def process_path(all_points, location_summaries):
    old_score = - 1000
    old_x = 0
    old_y = 0
    old_level = 0
    age = 0
    for point in all_points:
        diffs = [get_diff(point["stats"], location_summary["stats"]) for location_summary in location_summaries]
        ind = np.argmax(diffs)
        score = np.max(diffs)
        if score>(old_score+1.5-age*0.5):
            age = 0
            old_score = score
            old_x = location_summaries[ind]["x"]
            old_y = location_summaries[ind]["y"]
            old_level = location_summaries[ind]["level"]
        age+=1
        point["score"] = old_score
        point["x"] = old_x
        point["y"] = old_y
        point["level"] = old_level
            
    
        
        

if __name__ == "__main__":
    folder_tablet = "C:/Dev/data/greenstone20160508/tablet"
    folder_phone = "C:/Dev/data/greenstone20160508/phone"
    location = "greenstone"
    #pixel_per_meter = 38.0 # Home
    pixel_per_meter = 4.20 # Greenstone
    min_dist_m = 2.0
    min_dist_px = min_dist_m*pixel_per_meter

    #date_range1 = datetime.datetime(2016,5,8,0,0,0)
    #date_range2 = datetime.datetime(2016,5,8,23,59,59)
    
    location_summaries = process_readings_write_summary(folder_tablet, [date_range1, date_range2], write=True)
    #(names_tab, macs_tab) = get_macs(folder_tablet+ "/" + "greenstone_macs.txt")
    #(names_phone, macs_phone) = get_macs(folder_phone+ "/" + "greenstone_macs.txt")
    
    #all_points = get_paths(folder_phone, [date_range1, date_range2], macs_tab, macs_phone)
    #process_path(all_points, location_summaries)
      
    #filename = "home_readings_20160506_170235.txt"
    #all_readings = get_single_readings(filename)    
    #single_obs_summaries = make_summaries_from_single(all_readings)
    #compare_single_readings(single_obs_summaries, location_summaries)
    
    #diff = get_diff(summaries1[0]["stats"], location_summaries[0]["stats"])
    #diffs = [get_diff(summaries1[1]["stats"], location_summary["stats"]) for location_summary in location_summaries]
    

        



