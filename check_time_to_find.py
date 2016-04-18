import subprocess
import datetime
import time
import csv

subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=disabled"])
time.sleep(0.1)
subprocess.call(["netsh", "interface", "set", "interface", "name=\"Wireless Network Connection\"", "admin=enabled"])
for i in range(20):
    result = subprocess.check_output(["netsh", "wlan", "show", "NETWORKS", "MODE=BSSID"])
    print(result)
    time.sleep(0.1)

    