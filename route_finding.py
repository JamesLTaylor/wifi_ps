import json
import numpy as np

class Path(object):
    def __init__(self, path_data):
        self.p = np.array(path_data)
        self.len = np.sum(np.sqrt((self.p[1:,0]-self.p[:-1,0])**2 + (self.p[1:,1]-self.p[:-1,1])**2))
        self.cum_length = np.cumsum(np.append([0], np.sqrt((self.p[1:,0]-self.p[:-1,0])**2 + (self.p[1:,1]-self.p[:-1,1])**2)))
        self.cum_frac = self.cum_length/self.cum_length[-1]
        
    def interp(self, frac):
        if frac >= (1-1e-9):
            return np.array([[self.p[-1][0], self.p[-1][1]]])
        elif frac <= (1e-9):
            return np.array([[self.p[0][0], self.p[0][1]]])
            
        left_ind = np.where(self.cum_frac<=frac)[0][-1]
        w = (frac - self.cum_frac[left_ind])/(self.cum_frac[left_ind+1]-self.cum_frac[left_ind])
        
        x = self.p[left_ind, 0] + w * (self.p[left_ind+1, 0] - self.p[left_ind, 0])
        y = self.p[left_ind, 1] + w * (self.p[left_ind+1, 1] - self.p[left_ind, 1])
    
        return np.array([[x,y]])
    
    def reverse_interp(self, x, y):
        for i in range(len(self.p)-1):        
            if (x>=self.p[i,0] and x<=self.p[i+1,0]) or (x>=self.p[i+1,0] and x<=self.p[i,0]):
                if (y>=self.p[i,1] and y<=self.p[i+1,1]) or (y>=self.p[i+1,1] and y<=self.p[i,1]):
                    dx = x - self.p[i,0]
                    dy = y - self.p[i,1]                    
                    frac = self.cum_frac[i] + np.sqrt(dx*dx + dy*dy)/self.len
                    return frac
        raise Exception("supplied point does not lie on the path")
        
    def closest(self, x, y):
        d = 1e9   
        for i in range(len(self.p)-1):
            (new_d, new_close_x, new_close_y) = p_dist(x, y, self.p[i,0], self.p[i,1], self.p[i+1,0], self.p[i+1,1])
            frac = self.reverse_interp(new_close_x, new_close_y)
            if new_d<d:
                d = new_d
                close_x = new_close_x
                close_y = new_close_y                
                
        frac = self.reverse_interp(close_x, close_y)
        return (d, frac)

def get_dist(a, b):
    dist = np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2) + 100 * (a[2]-b[2])
    return dist
    
def get_route(nodes, start, end):    
    min_d_start = 1e9
    min_d_end = 1e9
    
    for (key, node) in nodes.iteritems():
        node["dist"] = 1e9
        node["route"] = []
        node["done"] = False        
        ds = get_dist(start, [node["x"], node["y"], node["level"]])
        de = get_dist(end, [node["x"], node["y"], node["level"]])
        if ds < min_d_start and node["level"]==start[2]:
            min_d_start = ds
            start_ind = key
        if de < min_d_end and node["level"]==end[2]:
            min_d_end = de
            end_ind = key
    
    vertex_set = nodes.keys()
    nodes[start_ind]["dist"] = 0
    nodes[start_ind]["route"] = [start_ind]
    
    while not len(vertex_set)==0:
        min_dist = 1e9
        for i in vertex_set:
            if nodes[i]["dist"]<min_dist:
                current = i
                min_dist = nodes[i]["dist"]
                
        if current==end_ind:
            break
                
        node_a = nodes[current]
        for to in nodes[current]["to"]:
            node_b = nodes[to]
            d = node_a["dist"] + get_dist([node_a["x"], node_a["y"], node_a["level"]], [node_b["x"], node_b["y"], node_b["level"]])
            if d<node_b["dist"]:            
                node_b["dist"] = d
                new_route = node_a["route"] + [to]
#                print("shorter route found to " + str(to))
#                print(node_b["route"])
#                print(new_route)            
#                print("")
                node_b["route"] = new_route
        vertex_set.remove(current)    
        
    return (nodes[end_ind]["dist"], nodes[end_ind]["route"])


def load_shops():
    fname = "C:\\Dev\\wifi_ps\\mall_data\\ShopLocations.csv"
    f = open(fname)
    lines = f.readlines()
    f.close()
    shops = []

    for (i, line) in enumerate(lines):
        cols = line[:-1].split(',')
        x = float(cols[3])
        y = float(cols[4])                

        level = int(float(cols[5]))
        shop = {"name":cols[0], "alt":cols[2], "number":cols[1], "x":x,"y":y,"level":level}

        shops.append(shop)
        
    return shops
    
def load_map():    
    fname = "C:\\Dev\\wifi_ps\\mall_data\\map.json"
    f = open(fname,'r')
    nodes = json.loads(f.read()) 
    f.close()
    
    for key in nodes.keys():
        int_key = int(key)
        nodes[int_key] = nodes.pop(key)
    
    return nodes
    

if __name__ == "__main__":    

    start = [647.0,381.0,1]
    end = [896.0,511.0,1]
    
    nodes = load_map()
    shops = load_shops()
    
    route = get_route(nodes, start, end)
    

    



        
        
        