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
def process_readings_write_summary(date_range, write=False):    
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
        if write: f.write("LOCATION,"+str(aggregate["level"])+","+str(aggregate["mx"])+","+str(aggregate["my"]) + "\n")
        all_readings = aggregate["all_readings"]
        N = float(aggregate["N"])
        for (key, data) in all_readings.iteritems():
            p = len(data)/N
            mu = np.mean(data)
            std = np.std(data)
            this_summary["stats"][key] = [p, mu, std]            
            if write: f.write(str(key) + "," + str(p) + "," + str(mu) + "," + str(std) + "\n")
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
 

if __name__ == "__main__":
    folder = "C:\Dev\data"
    location = "home"
    meters_per_pixel = 38.0
    min_dist_m = 2.0
    min_dist_px = min_dist_m*meters_per_pixel

    date_range1 = datetime.datetime(2016,5,1,0,0,0)
    date_range2 = datetime.datetime(2016,5,6,17,0,0)
    
    #location_summaries = process_readings_write_summary([date_range1, date_range2], write=False)
      
    filename = "home_readings_20160506_170235.txt"
    #all_readings = get_single_readings(filename)    
    #summaries1 = make_summaries_from_single(all_readings)
    
    #diff = get_diff(summaries1[0]["stats"], location_summaries[0]["stats"])
    diffs = [get_diff(summaries1[1]["stats"], location_summary["stats"]) for location_summary in location_summaries]
    
    for (i, s) in enumerate(summaries1):
        #if i >10: break
            
        diffs = [get_diff(s["stats"], location_summary["stats"]) for location_summary in location_summaries]
        ind = np.argmax(diffs)
        print(str(i) + "   :" + str(s["level"]) + "," + str(s["x"]) + "," +str(s["y"]) + " mapped to:  " + 
                str(location_summaries[ind]["level"]) + "," + str(location_summaries[ind]["x"]) + 
                "," +str(location_summaries[ind]["y"]))
        



