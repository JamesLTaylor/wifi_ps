import json
import numpy as np
import math
from operator import itemgetter

"""
distance between a point and a line segment

http://stackoverflow.com/a/6853926/5890940   
""" 
def p_dist(x, y, x1, y1, x2, y2):

  A = x - x1;
  B = y - y1;
  C = x2 - x1;
  D = y2 - y1;

  dot = A * C + B * D;
  len_sq = C * C + D * D;
  param = dot / len_sq;

  if (param < 0):
    xx = x1;
    yy = y1;
  
  elif (param > 1):
    xx = x2;
    yy = y2;  
  else:
    xx = x1 + param * C;
    yy = y1 + param * D;
  

  dx = x - xx;
  dy = y - yy;
  return (math.sqrt(dx * dx + dy * dy), xx, yy)


class Path(object):
    def __init__(self, path_data, px_per_m):
        self.px_per_m = px_per_m
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
        
    def get_reg_spaced(self, space):
        l = self.len/self.px_per_m
        n = np.round(l/space)
        new_path = np.zeros((0,2))
        for i in range(int(n)+1):
            new_path = np.vstack((new_path, self.interp(i/n)))
            
        return new_path
            
        
        

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
    
def get_closest_shop(shops, x, y, level, excluding=None):
    best_dist = 1e9
    for shop in shops:
        if shop["level"]==level and not shop["name"]==excluding:
            dist = get_dist([x,y,0], [shop["x"], shop["y"], 0])
            if dist<best_dist:
                best_dist = dist
                return_shop = shop
                
    return return_shop
    
def get_route_shops(path, shops, level, shop_separation_px):
    descriptions = []
    for shop in shops:
        if shop["level"]==level:            
            (d, frac) = path.closest(shop["x"], shop["y"])
            #print("{},{}".format(shop["name"], d))
            if d<5*4.2:
                descriptions.append([shop["name"],d, frac])
                
    descriptions = sorted(descriptions, key=itemgetter(2))
    #print(descriptions)
    route_shops = [descriptions[0]]
    separation = shop_separation_px / path.len
    for i in range(1,len(descriptions)):
        if (descriptions[i][2]- route_shops[-1][2])>separation:
            route_shops.append(descriptions[i])
            
    if not route_shops[-1][0]==descriptions[-1][0]:
        #route_shops.pop()
        route_shops.append(descriptions[-1])
        
        
    return route_shops
    
def get_angle(x1, y1, x2, y2, x3, y3):
    x1 -= x2
    x3 -= x2
    y1 -= y2
    y3 -= y2    
    l1 = math.sqrt(x1**2+y1**2)
    l3 = math.sqrt(x3**2+y3**2)
    x1 /= l1
    y1 /= l1
    x3 /= l3
    y3 /= l3
    
    #theta1 = np.arccos((x1*x3) + (y1*y3))
    theta = np.arctan2(y1,x1) - np.arctan2(y3,x3)
    theta *= 180/np.pi
    if theta>360:
        theta-=360
    elif theta<0:
        theta+=360
    return theta
    
def get_turns(path, new_path):
    turns = []    
    
    # get angles
    for i in range(1, len(new_path)-1):
        theta = get_angle(new_path[i-1][0], new_path[i-1][1],
                          new_path[i][0], new_path[i][1],
                          new_path[i+1][0], new_path[i+1][1])
    
        #print(theta)
    
        if theta>210:
            turns.append(["** HEAD  LEFT **", path.reverse_interp(new_path[i][0], new_path[i][1])])
        if theta<150:
            turns.append(["** HEAD  RIGHT **", path.reverse_interp(new_path[i][0], new_path[i][1])])
        
    return turns
    
    
def get_route_description(nodes, shops, route):
    px_p_m = 4.2
    turn_spacing = 5.0
    shop_spacing = 10.0

    path_data1 = []
    path_data2 = []
    start_level = nodes[route[0]]["level"]
    end_level = nodes[route[-1]]["level"]
    for node in route:
        if nodes[node]["level"]==start_level:
            path_data1.append([nodes[node]["x"], nodes[node]["y"]])
        else:
            path_data2.append([nodes[node]["x"], nodes[node]["y"]])

            
    path = Path(path_data1, px_p_m)
    new_path = path.get_reg_spaced(turn_spacing)
    route_shops = get_route_shops(path, shops, start_level, px_p_m * shop_spacing)    
    turns = get_turns(path, new_path)    
    next_turn = 0
    prev = 0
    
    for route_shop in route_shops:
        if len(turns)>next_turn and turns[next_turn][1]<route_shop[2]:
            d = int(5 * np.round(0.2*(turns[next_turn][1]-prev)*path.len/px_p_m))
            print(str(d) + "m")
            print(turns[next_turn][0])
            next_turn += 1
        
        d = int(5 * np.round(0.2*(route_shop[2]-prev)*path.len/px_p_m))
        prev = route_shop[2]
        print(str(d) + "m to: " + route_shop[0])
        
    if len(path_data2)>0:        
        d = int(5 * np.round(0.2*(1-prev)*path.len/px_p_m))
        print(str(d) + "m to: escalator")
            
        if start_level==0:
            print("** HEAD UP THE ESCALATOR **")
        else: 
            print("** HEAD DOWN THE ESCALATOR **")
        prev = 0.0
        path = Path(path_data2, px_p_m)
        new_path = path.get_reg_spaced(turn_spacing)
        route_shops = get_route_shops(path, shops, end_level, px_p_m * shop_spacing)    
        turns = get_turns(path, new_path)    
        next_turn = 0
        
        for route_shop in route_shops:
            if len(turns)>next_turn and turns[next_turn][1]<route_shop[2]:
                d = int(5 * np.round(0.2*(turns[next_turn][1]-prev)*path.len/px_p_m))
                print(str(d) + "m")
                print(turns[next_turn][0])
                next_turn += 1
            
            d = int(5 * np.round(0.2*(route_shop[2]-prev)*path.len/px_p_m))
            prev = route_shop[2]
            print(str(d) + "m to: " + route_shop[0])
            
            
            
    d = int(5 * np.round(0.2*(1-prev)*path.len/px_p_m))
    print(str(d) + "m to: destination")
    
    

if __name__ == "__main__":    

    #Game FoodCo,L008,,362.0,270.0,0
    #Bread Basket,L077,,1638.0,433.0,0
    start = [1638.0,433.0,0]
    #Sportscene,U040,,1245.0,609.0,1
    #Volpes The Linen Company,L089/90,,1348.0,379.0,0
    end = [493.0,791.0,1]
    #Jimmy Jungles,U115E,,493.0,791.0,1
    #ABSA - Branch,L065,,1781.0,251.0,0    
    #Cape Town Fish Market,L105,,958.0,529.0,0
    #Mr Price Sport,U066,,1650.0,416.0,1
    
    nodes = load_map()
    shops = load_shops()
    (dist, route) = get_route(nodes, start, end)
    get_route_description(nodes, shops, route)
    
            
        
        

    

    
                
                #print("{},{},{}".format(shop["name"],d, frac))
    
    #shop1 = get_closest_shop(shops, new_path[0,0], new_path[0,1], start_level)
    #shop2 = get_closest_shop(shops, new_path[1,0], new_path[1,1], start_level, excluding = shop1["name"])
    
    
    

    



        
        
        