"""
This could be useful:
http://stackoverflow.com/questions/1192376/wlan-api-for-getting-signal-strenth

"""
import subprocess
import datetime
import time
import csv

def get_reading(obs_id, location, obs_time):
    result = subprocess.check_output(["netsh", "wlan", "show", "NETWORKS", "MODE=BSSID"])
    print(result)
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
        print(mac)
        
        signal_ind = result.find("Signal", end_ind)
        signal_ind = result.find(":", signal_ind)
        end_ind = result.find("%", signal_ind)
        signal = float(result[signal_ind+2:end_ind].strip())
        print(signal)
    
        data.append([obs_id, location, obs_time, name, mac, signal])    
        
        ssid_ind = result.find("SSID", end_ind)
        
    return data

fd = open('readings.csv','ab')
csvwriter = csv.writer(fd)
obs_id = "00005"
location = "upstairs desk2"
for i in range(30):    
    subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=disabled"])
    time.sleep(0.2)
    subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=enabled"])
    time.sleep(0.8)
    obs_time = str(datetime.datetime.now())    
    
    data = get_reading(obs_id, location, obs_time)
    print(data)
    for row in data:
        csvwriter.writerow(row)
    

fd.close()