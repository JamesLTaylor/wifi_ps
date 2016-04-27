"""
This could be useful:
http://stackoverflow.com/questions/1192376/wlan-api-for-getting-signal-strenth

"""
import subprocess
import datetime
import time
import csv
import numpy as np

def dbprint(string):
    #print(string)
    pass


def get_single_reading(count):
    reading = {'count':0, 'network_data':{}}
    for i in range(count):
        reading['count'] += 1
        if i==0:
            result = subprocess.check_output(["GetWifiInfo","scan=no"])
        else:
            result = subprocess.check_output(["GetWifiInfo","scan=yes"])
        lines = result.split('\r\n')
        for line in lines:            
            if len(line)>0:
                cols = line.split(',')
                mac = cols[2]
                strength = float(cols[1])
            
                if mac not in reading['network_data'].keys():
                    reading['network_data'][mac] = []
                
                reading['network_data'][mac].append(strength)
    add_summary(reading)        
    return reading
    
    
def get_reading_custom(location, level, x, y, obs_time, time_offset):
    """
    Args:



        obs_time:
        offset:
    """
    data = []
    result = subprocess.check_output(["GetWifiInfo","scan=yes"])
    lines = result.split('\r\n')
    for line in lines:
        if len(line)>0:
            cols = line.split(',')
            data.append([location, level, x, y, obs_time, time_offset, cols[0], cols[1], cols[2]])
    return data

    
    
def reset_netsh():    
    subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=disabled"])
    time.sleep(0.2)
    subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=enabled"])
    
    
def get_reading_netsh(obs_id, location, obs_time, reset=False):
    if reset:
        reset_netsh()
    result = subprocess.check_output(["netsh", "wlan", "show", "NETWORKS", "MODE=BSSID"])
    dbprint(result)
    ssid_ind = result.find("SSID")
    data = []
    while ssid_ind > 0:
        end_ind = result.find("\n", ssid_ind)
        name = result[ssid_ind+9 : end_ind].strip()
        print(name)
        
        mac_ind = result.find("BSSID", end_ind)
        mac_ind = result.find(":", mac_ind)
        end_ind = result.find("\n", mac_ind)
        mac = result[mac_ind+2:end_ind].strip()
        dbprint(mac)
        
        signal_ind = result.find("Signal", end_ind)
        signal_ind = result.find(":", signal_ind)
        end_ind = result.find("%", signal_ind)
        signal = float(result[signal_ind+2:end_ind].strip())
        dbprint(signal)
    
        data.append([obs_id, location, obs_time, name, mac, signal])    
        
        ssid_ind = result.find("SSID", end_ind)
        
    return data
    
def make_readings(filename, location, level, x, y, N):

    fd = open(filename, "ab")
    csvwriter = csv.writer(fd)

    start_time = datetime.datetime.now()
    for i in range(N):
        print(str(i) + " of " + str(N))
        elapsed = (datetime.datetime.now() - start_time)
        dbprint("working on " + str(i+1) + " of " + str(N) + ": " + str(elapsed.total_seconds()) + "s")    
        data = get_reading_custom(location, level, x, y, start_time, elapsed.total_seconds())
        dbprint(data)
        for row in data:
            csvwriter.writerow(row)
    
    fd.close()
    
   
        
#==============================================================================
#     
#==============================================================================

def add_summary(reading):
    reading['summary'] = {}
    for (network_key, network_data) in reading['network_data'].iteritems():
        p = float(len(network_data))/reading['count']
        mu = np.mean(network_data)
        if len(network_data)>5:                
            sigma = np.std(network_data)
        else:
            sigma = 3
        reading['summary'][network_key] = [p, mu, sigma]         
        
def make_summary(fname):
    fd = open(fname,'r')
    lines = fd.readlines()
    fd.close()
    
    locations = {}
    networks = {}     
#      0         1         2   3                   4            5     6      7        8
#Greenstone,Lower Level,850.0,361.0,2016-04-25 10:27:07.861000,0.0,AlwaysOn,-64,2c-e6-cc-08-18-2c    
    for line in lines:
        cols = line.split(',')
        mac = cols[8].translate(None, '\n\r')
        ssid = cols[6]
        strength = float(cols[7])
        location = str(cols[1])+":"+str(cols[2])+":"+str(cols[3])
        time_and_offset = cols[4] + "," + cols[5]
        if location not in locations.keys():
            locations[location] = {'count':0, 'network_data':{}, 'times':[]}
        
        if mac not in networks.keys():
            networks[mac] = ssid
            
        if mac not in locations[location]['network_data'].keys():
            locations[location]['network_data'][mac] = []
        
        if time_and_offset not in locations[location]['times']:
            locations[location]['count'] += 1
            locations[location]['times'].append(time_and_offset)
        
        locations[location]['network_data'][mac].append(strength)
        
    # Create summaries
    for (location_key, location) in locations.iteritems():
        location['summary'] = {}
        for (network_key, network_data) in location['network_data'].iteritems():
            p = float(len(network_data))/location['count']
            mu = np.mean(network_data)
            if len(network_data)>5:                
                sigma = np.std(network_data)
            else:
                sigma = 3
            location['summary'][network_key] = [p, mu, sigma]
            
    return (networks, locations)
    
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
            score -= w1 * abs(loc_stats[1] - obs[loc_mac_key][1]) * loc_stats[0]
            dbprint("in both: ")
            dbprint(loc_stats)
            dbprint(obs[loc_mac_key])
        else:
            # in fingerprint but not in obs
            score -= w2 * loc_stats[0] * abs(-90-loc_stats[1])
            dbprint("not in obs: ")
            dbprint(loc_stats)
            
    for obs_mac_key, obs_stats in obs.iteritems():
        if obs_mac_key not in location.keys():
            # in obs but not fingerprint
            score -= w3 * obs_stats[0] * abs(-90-obs_stats[1])
            dbprint("not in fingerprint: ")
            dbprint(obs_stats)
    dbprint(score)        
    dbprint(weighting)
    return score/weighting         
    
    
def analyse_fingerprint_data(locations, fname):
    """ Iterates over a large set of readings to see how well they are matched 
    to their known positons
    """
    fd = open(fname,'r')
    lines = fd.readlines()
    fd.close()
    time_count = 1
    for (i, line) in enumerate(lines):
        #if i>400: break
        cols = line.split(',')        
        prev_line = lines[i-1].split(',')
        
        mac = cols[8].translate(None, '\n\r')
        #ssid = cols[6]
        strength = float(cols[7])
        location = str(prev_line[1])+":"+str(prev_line[2])+":"+str(prev_line[3])
        
        if i==0:
            reading = {'count':0, 'network_data':{}}
        elif cols[5]!=prev_line[5]:
            time_count+=1
            reading['count']+=1
            
        if time_count>=2:
            time_count=1
            # start of new reading
            add_summary(reading)
            #print("*******************************")
            #dbprint("processing " + str(reading))
            print(location + " matched to " + find_best_match(reading["summary"], locations))
            reading = {'count':0, 'network_data':{}}
        
        if mac not in reading['network_data'].keys():
            reading['network_data'][mac] = []
        reading['network_data'][mac].append(strength)  
        
        
            
def find_best_match(obs, locations):
    scores = []
    keys = []        
    for location_key, location in locations.iteritems():
        dbprint("")
        dbprint(location_key)
        score = get_diff(obs, location['summary'])
        dbprint(score)
        scores.append(score)
        keys.append(location_key)
    
#    for row in zip(keys, scores):
#        print(row)

    return keys[np.argmax(scores)]
        
    

if __name__ == "__main__":
    fname = 'greenstone1.csv'
    #make_readings('greenstone1.csv', "Greenstone", "Lower Level", 100.0, 23, 20)
    (networks, locations) = make_summary('greenstone1.csv');
    #reading = get_single_reading(1)
    
    #obs = reading["summary"]
    #match = find_best_match(obs, locations)
    #print(match)
    
    #analyse_fingerprint_data(locations, fname)
    
    

        
        

            
        
            
                
            
        
        
    
    